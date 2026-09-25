# AgentGuard and FlightRecorder

Day 1 scaffold for the LovHack MVP. The `sample_app` is the small repository the agent will later inspect and edit. Its data uses `user_name`; displaying `username` instead will produce a real failing test.

## Start here

Requires Python 3.10 or newer. No packages are needed for the scaffold.

```bash
cd agentguard
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s sample_app/tests -v
python3 -m sample_app.profile
```

Both test commands should pass initially. During the failure demo, the agent will change `sample_app/profile.py`, and the sample app test will fail until that change is corrected or restored.

## Layout

- `sample_app/`: tiny profile application and its real test.
- `agentguard/`: event contract, JSONL recorder, and bounded file reader.
- `tests/`: tests for event serialization, recording, and file access boundaries.
- `docs/`: scenario and completion criteria.

## Flight recorder and safe read tool

This branch keeps the scope intentionally narrow: it adds a JSON Lines event recorder and a bounded `read_file("profile.py")` helper that only allows access within `sample_app`.

From the repository root, run this to read `profile.py` and print its saved event:

```bash
python3 - <<'PY'
import json
from agentguard.events import Event
from agentguard.recorder import JSONLRecorder
from agentguard.tools import read_file

recorder = JSONLRecorder("agentguard/events.jsonl")
contents = read_file("profile.py")
event = Event(
    run_id="run-1",
    step_id="step-1",
    kind="tool_result",
    status="succeeded",
    summary="profile read succeeded",
    tool="read_file",
    path="profile.py",
)
print(json.dumps(recorder.record(event), separators=(",", ":")))
PY
```

The example records success after reading, appending one event to
`agentguard/events.jsonl`. The event identifies the tool and path relative to
`sample_app`; file contents remain in `contents` and are not recorded or printed.
Recording is explicit, not automatic.

The reader resolves paths before checking containment and opening the file.
A symlink inside `sample_app` pointing outside it is also rejected:

```python
read_file("profile.py")  # allowed
read_file("../README.md")  # raises ValueError
```

This is intentionally the stopping point for the requested feature. The codebase does not add `write_file` or `run_tests` yet.

## Work log

[CODEX.md](CODEX.md) is append-only. Preserve every existing entry exactly as
written, and append new work as the next numbered entry with the date, changes,
tests, and result. Never replace or summarize earlier entries. Recover missing
entries from Git history when available before appending. Update this README
normally to reflect the current project.
