"""Filesystem helpers for the bounded sample app runner."""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SAMPLE_APP_ROOT = (_REPO_ROOT / "sample_app").resolve()


def read_file(path: str) -> str:
    """Read a file only when it remains inside the sample_app directory."""
    safe_root = _SAMPLE_APP_ROOT.resolve()
    requested = (_SAMPLE_APP_ROOT / path).resolve()

    try:
        requested.relative_to(safe_root)
    except ValueError as exc:
        raise ValueError(f"Path is outside the allowed sample_app directory: {path}") from exc

    if not requested.is_file():
        raise FileNotFoundError(f"File not found inside sample_app: {path}")

    return requested.read_text(encoding="utf-8")
