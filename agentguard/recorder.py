"""JSON Lines recorder for flight events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .events import Event


class JSONLRecorder:
    """Append a serialized event to a JSON Lines file."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def record(self, event: Event) -> dict[str, Any]:
        payload = event.to_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, separators=(",", ":")))
            handle.write("\n")
        return payload
