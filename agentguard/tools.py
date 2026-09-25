"""Filesystem helpers for the bounded sample app runner."""

from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from .events import Event
from .recorder import JSONLRecorder

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE_APP_ROOT = (_REPO_ROOT / "sample_app").resolve()
_DEFAULT_EVENT_PATH = _REPO_ROOT / "agentguard" / "events.jsonl"


def read_file(
    path: str,
    *,
    recorder: JSONLRecorder | None = None,
    run_id: str | None = None,
    step_id: str | None = None,
) -> str:
    """Read within sample_app and record the outcome without file contents."""
    recorder = recorder if recorder is not None else JSONLRecorder(_DEFAULT_EVENT_PATH)
    run_id = run_id if run_id is not None else str(uuid4())
    step_id = step_id if step_id is not None else str(uuid4())
    # Keep the requested symlink name, not its resolved target, in the event.
    relative_path = os.path.relpath(_SAMPLE_APP_ROOT / path, _SAMPLE_APP_ROOT)
    status = "failed"
    summary = "file read failed"
    try:
        safe_root = _SAMPLE_APP_ROOT.resolve()
        requested = (_SAMPLE_APP_ROOT / path).resolve()
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
            kind="tool_result",
            status=status,
            summary=summary,
            tool="read_file",
            path=relative_path,
        ))
