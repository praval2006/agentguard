"""Three-step scripted failure demonstration in a disposable sample app."""

import json
from pathlib import Path
from uuid import uuid4

from . import tools
from .recorder import JSONLRecorder

MAX_STEPS = 3


class _RunRecorder(JSONLRecorder):
    def __init__(self, path):
        super().__init__(path)
        self.events = []

    def record(self, event):
        payload = super().record(event)
        self.events.append(payload)
        return payload


def run_script(*, log_path: str | Path | None = None) -> list[dict]:
    """Read, make one controlled wrong edit, then test; never recover or retry."""
    recorder = _RunRecorder(log_path if log_path is not None else tools._DEFAULT_EVENT_PATH)
    run_id = str(uuid4())
    step_count = 0

    def call(tool, *args):
        nonlocal step_count
        if step_count >= MAX_STEPS:
            raise RuntimeError("Scripted run step limit reached")
        previous = (f"step-{step_count}",) if step_count else ()
        step_count += 1
        return tool(*args, recorder=recorder, run_id=run_id,
                    step_id=f"step-{step_count}", dependency_ids=previous)

    with tools.temporary_sample_app():
        contents = call(tools.read_file, "profile.py")
        original = 'return profile["user_name"]'
        if contents.count(original) != 1:
            raise ValueError("Expected exactly one controlled edit location")
        wrong = contents.replace(original, 'return profile["username"]', 1)
        call(tools.write_file, "profile.py", wrong)
        call(tools.run_tests)
    return recorder.events


if __name__ == "__main__":
    events = run_script()
    for event in events:
        print(json.dumps(event, separators=(",", ":")))
    print("\nActual test output:")
    print(events[-1]["output"], end="")
