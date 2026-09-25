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

From the repository root, run this to record a successful read and a rejected path:

```bash
python3 - <<'EXAMPLE'
from agentguard.tools import read_file

contents = read_file("profile.py", run_id="reader-demo", step_id="step-1")
try:
    read_file("../README.md", run_id="reader-demo", step_id="step-2")
except ValueError:
    pass

from pathlib import Path
for line in Path("agentguard/events.jsonl").read_text().splitlines()[-2:]:
    print(line)
EXAMPLE
```

Every call automatically appends an outcome event to `agentguard/events.jsonl`
under the repository root. Status is `succeeded` for a read, `blocked` for a path
outside `sample_app`, and `failed` for other read errors (such as a missing file).
The reader still returns contents or raises the original read/path exception
when recording succeeds. Recorder errors propagate to the caller.

Events contain the tool name and requested path relative to `sample_app`,
including `../` for outside paths and the requested symlink name. Neither file
contents nor exception details are stored. Callers do not create events manually.
Optional `recorder=JSONLRecorder(...)` selects a different log; optional `run_id`
and `step_id` associate calls with a run. Omitted IDs are generated per call.

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
