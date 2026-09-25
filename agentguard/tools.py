"""Filesystem helpers for the bounded sample app runner."""

from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from contextvars import ContextVar
import subprocess
import sys
import tempfile
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from .events import Event
from .recorder import JSONLRecorder

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE_APP_ROOT = (_REPO_ROOT / "sample_app").resolve()
_DEFAULT_EVENT_PATH = _REPO_ROOT / "agentguard" / "events.jsonl"
_ACTIVE_SAMPLE_ROOT = ContextVar("sample_app_root", default=None)
_TEST_TIMEOUT_SECONDS = 10
_TEST_OUTPUT_LIMIT = 4096


def read_file(
    path: str,
    *,
    recorder: JSONLRecorder | None = None,
    run_id: str | None = None,
    step_id: str | None = None,
    dependency_ids: tuple[str, ...] = (),
) -> str:
    """Read within sample_app and record the outcome without file contents."""
    sample_root = _ACTIVE_SAMPLE_ROOT.get() or _SAMPLE_APP_ROOT
    recorder = recorder if recorder is not None else JSONLRecorder(_DEFAULT_EVENT_PATH)
    run_id = run_id if run_id is not None else str(uuid4())
    step_id = step_id if step_id is not None else str(uuid4())
    # Keep the requested symlink name, not its resolved target, in the event.
    relative_path = os.path.relpath(sample_root / path, sample_root)
    status = "failed"
    summary = "file read failed"
    try:
        safe_root = sample_root.resolve()
        requested = (sample_root / path).resolve()
        try:
            requested.relative_to(safe_root)
        except ValueError as exc:
            status = "blocked"
            summary = "path rejected outside sample_app"
            raise ValueError(f"Path is outside the allowed sample_app directory: {path}") from exc

        if not requested.is_file():
            raise FileNotFoundError(f"File not found inside sample_app: {path}")
        contents = requested.read_text(encoding="utf-8")
        status = "succeeded"
        summary = "file read succeeded"
        return contents
    finally:
        recorder.record(Event(
            run_id=run_id,
            step_id=step_id,
            dependency_ids=dependency_ids,
            kind="tool_result",
            status=status,
            summary=summary,
            tool="read_file",
            path=relative_path,
        ))


def write_file(
    path: str,
    contents: str,
    *,
    recorder: JSONLRecorder | None = None,
    run_id: str | None = None,
    step_id: str | None = None,
    dependency_ids: tuple[str, ...] = (),
) -> None:
    """Replace an existing sample_app file with UTF-8 text and record hashes."""
    sample_root = _ACTIVE_SAMPLE_ROOT.get() or _SAMPLE_APP_ROOT
    recorder = recorder if recorder is not None else JSONLRecorder(_DEFAULT_EVENT_PATH)
    relative_path = os.path.relpath(sample_root / path, sample_root)
    status = "failed"
    summary = "file write failed"
    before_hash = after_hash = None
    try:
        safe_root = sample_root.resolve()
        requested = (sample_root / path).resolve()
        try:
            requested.relative_to(safe_root)
        except ValueError as exc:
            status = "blocked"
            summary = "path rejected outside sample_app"
            raise ValueError(f"Path is outside the allowed sample_app directory: {path}") from exc
        if not requested.is_file():
            raise FileNotFoundError(f"Existing file not found inside sample_app: {path}")
        data = contents.encode("utf-8")
        # r+b cannot create a missing file and hashes the exact bytes on disk.
        with requested.open("r+b") as handle:
            before_hash = sha256(handle.read()).hexdigest()
            try:
                handle.seek(0)
                handle.write(data)
                handle.truncate()
                handle.flush()
            finally:
                handle.seek(0)
                after_hash = sha256(handle.read()).hexdigest()
        status = "succeeded"
        summary = "file write succeeded"
    finally:
        recorder.record(Event(
            run_id=run_id if run_id is not None else str(uuid4()),
            step_id=step_id if step_id is not None else str(uuid4()),
            dependency_ids=dependency_ids,
            kind="tool_result",
            status=status,
            summary=summary,
            tool="write_file",
            path=relative_path,
            before_hash=before_hash,
            after_hash=after_hash,
        ))


def run_tests(
    *,
    recorder: JSONLRecorder | None = None,
    run_id: str | None = None,
    step_id: str | None = None,
    dependency_ids: tuple[str, ...] = (),
) -> dict:
    """Run only sample_app unittest discovery and record a bounded result."""
    sample_root = _ACTIVE_SAMPLE_ROOT.get() or _SAMPLE_APP_ROOT
    recorder = recorder if recorder is not None else JSONLRecorder(_DEFAULT_EVENT_PATH)
    exit_code = None
    timed_out = False
    summary = "tests failed"
    # A file avoids buffering unlimited subprocess output in memory.
    with tempfile.TemporaryFile() as capture:
        try:
            result = subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover",
                 "-s", "sample_app/tests", "-v"],
                cwd=sample_root.parent,
                stdin=subprocess.DEVNULL,
                stdout=capture,
                stderr=subprocess.STDOUT,
                timeout=_TEST_TIMEOUT_SECONDS,
                shell=False,
            )
            exit_code = result.returncode
            if exit_code == 0:
                summary = "tests passed"
        except subprocess.TimeoutExpired:
            timed_out = True
            summary = "tests timed out"
        except OSError:
            summary = "test process could not start"
        capture.seek(0)
        raw_output = capture.read(_TEST_OUTPUT_LIMIT + 1)
    event = Event(
        run_id=run_id if run_id is not None else str(uuid4()),
        step_id=step_id if step_id is not None else str(uuid4()),
        dependency_ids=dependency_ids,
        kind="tool_result",
        status="succeeded" if exit_code == 0 and not timed_out else "failed",
        summary=summary,
        tool="run_tests",
        path="tests",
        exit_code=exit_code,
        output=raw_output[:_TEST_OUTPUT_LIMIT].decode("utf-8", errors="replace"),
        output_truncated=len(raw_output) > _TEST_OUTPUT_LIMIT,
        timed_out=timed_out,
    )
    return recorder.record(event)


@contextmanager
def temporary_sample_app():
    """Scope tool calls to a fresh disposable copy of the checked-in app."""
    with tempfile.TemporaryDirectory(prefix="agentguard-") as directory:
        root = Path(directory) / "sample_app"
        shutil.copytree(_SAMPLE_APP_ROOT, root,
                        ignore=shutil.ignore_patterns("__pycache__"))
        token = _ACTIVE_SAMPLE_ROOT.set(root)
        try:
            yield root
        finally:
            _ACTIVE_SAMPLE_ROOT.reset(token)
