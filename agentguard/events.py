"""Serializable flight recorder event contract."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal

Status = Literal["started", "succeeded", "failed", "blocked"]


@dataclass(frozen=True)
class Event:
    run_id: str
    step_id: str
    kind: str
    status: Status
    summary: str
    dependency_ids: tuple[str, ...] = ()
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tool: str | None = None
    path: str | None = None
    before_hash: str | None = None
    after_hash: str | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["dependency_ids"] = list(self.dependency_ids)
        return data
