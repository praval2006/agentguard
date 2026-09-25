"""Bounded state-based scripted scenarios in a disposable sample app."""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from . import tools
from .recorder import JSONLRecorder
from .events import Event
from dataclasses import dataclass

MAX_STEPS = 3


class _RunRecorder(JSONLRecorder):
    def __init__(self, path):
        super().__init__(path)
        self.events = []

    def record(self, event):
        payload = super().record(event)
        self.events.append(payload)
        return payload


@dataclass
class RunState:
    contents: str | None = None
    last_result: dict | None = None
    tool_calls: int = 0
    error: str | None = None


def decide_next(state: RunState) -> tuple[str, str]:
    """Choose one action from the latest observed result and call budget."""
    if state.error:
        return "failed", state.error
    result = state.last_result
    if result is not None:
        if result["status"] != "succeeded":
            return "failed", f"{result['tool']} failed or was blocked"
        if result["tool"] == "run_tests":
            if result["exit_code"] == 0 and not result["timed_out"]:
                return "completed", "tests passed"
            return "failed", "tests did not pass"
    if state.tool_calls >= MAX_STEPS:
        return "failed", "tool call limit reached"
    if result is None:
        return "read_file", "file has not been read"
    if result["tool"] == "read_file":
        return "write_file", "read succeeded; apply selected edit"
    if result["tool"] == "write_file":
        return "run_tests", "write succeeded; verify the edit"
    return "failed", "unexpected run state"


def run_script(*, scenario: str = "failure", log_path: str | Path | None = None) -> list[dict]:
    """Decide after every result; stop at a terminal outcome without retrying."""
    if scenario not in ("success", "failure"):
        raise ValueError("Scenario must be success or failure")
    recorder = _RunRecorder(log_path if log_path is not None else tools._DEFAULT_EVENT_PATH)
    run_id = str(uuid4())
    state = RunState()
    decisions = []
    with tools.temporary_sample_app():
        while True:
            action, reason = decide_next(state)
            decisions.append(f"{action}: {reason}")
            if action in ("completed", "failed"):
                recorder.record(Event(
                    run_id=run_id, step_id="run-end", kind="run_result",
                    status=action, summary=reason,
                    dependency_ids=(f"step-{state.tool_calls}",) if state.tool_calls else (),
                    decisions=tuple(decisions),
                ))
                break
            args = ()
            if action == "read_file":
                args = ("profile.py",)
            elif action == "write_file":
                original = 'return profile["user_name"]'
                if state.contents is None or state.contents.count(original) != 1:
                    state.error = "expected exactly one controlled edit location"
                    continue
                replacement = (
                    'return profile["user_name"]  # Use the profile schema key.'
                    if scenario == "success" else 'return profile["username"]'
                )
                args = ("profile.py", state.contents.replace(original, replacement, 1))
            previous = (f"step-{state.tool_calls}",) if state.tool_calls else ()
            state.tool_calls += 1
            try:
                result = getattr(tools, action)(
                    *args, recorder=recorder, run_id=run_id,
                    step_id=f"step-{state.tool_calls}", dependency_ids=previous,
                )
                if action == "read_file":
                    state.contents = result
            except (OSError, ValueError, RuntimeError):
                # Recording failures must propagate rather than claiming a saved outcome.
                if not recorder.events or recorder.events[-1]["step_id"] != f"step-{state.tool_calls}":
                    raise
                state.error = f"{action} raised an error"
            state.last_result = recorder.events[-1]
    return recorder.events


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", choices=("success", "failure"),
                        nargs="?", default="failure")
    args = parser.parse_args(argv)
    events = run_script(scenario=args.scenario)
    for event in events:
        print(json.dumps(event, separators=(",", ":")))
    print("\nDecisions:")
    print("\n".join(events[-1]["decisions"]))
    for event in events:
        if event["tool"] == "run_tests":
            print("\nActual test output:")
            print(event["output"], end="")


if __name__ == "__main__":
    main()
