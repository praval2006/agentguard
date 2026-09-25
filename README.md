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

Both test commands should pass initially. The failure demo changes only a temporary copy of `sample_app/profile.py`; the checked-in app remains unchanged.

## Layout

- `sample_app/`: tiny profile application and its real test.
- `agentguard/`: event contract, JSONL recorder, and bounded file reader/writer.
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

## Bounded write tool

`write_file(path, contents)` replaces an existing file within `sample_app` using
UTF-8 text and returns `None`. It accepts the same optional recorder/run/step
arguments as the reader and automatically records a `write_file` event.
Outside paths and escaping symlinks raise `ValueError` (`blocked`); missing files
are not created and raise `FileNotFoundError` (`failed`). Successful writes use
`succeeded`. Events contain `before_hash` and `after_hash`: SHA-256 hex digests
of the actual file bytes, never file contents. Hashes are null when unavailable,
including blocked paths, whose contents are never read. Read events have null
hash fields. Recorder errors propagate; they do not roll back a completed write.

Try the wrong `username` edit safely in a temporary copy from the repository root.
The root override below is test/demo scaffolding, not a caller-supplied tool argument:

```bash
python3 - <<'WRITE_EXAMPLE'
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
from agentguard.recorder import JSONLRecorder
from agentguard.tools import write_file

recorder = JSONLRecorder("agentguard/events.jsonl")
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory) / "sample_app"
    shutil.copytree("sample_app", root, ignore=shutil.ignore_patterns("__pycache__"))
    text = (root / "profile.py").read_text()
    wrong = text.replace('return profile["user_name"]', 'return profile["username"]')
    with patch("agentguard.tools._SAMPLE_APP_ROOT", root):
        write_file("profile.py", wrong, recorder=recorder,
                   run_id="write-demo", step_id="step-1")
print(recorder.path.read_text().splitlines()[-1])
WRITE_EXAMPLE
```

The writer tests run the copied app's tests and confirm the wrong edit triggers
`KeyError: 'username'`. Both normal suites should pass.

## Fixed sample app test runner

`run_tests()` runs only `[sys.executable, "-B", "-m", "unittest", "discover",
"-s", "sample_app/tests", "-v"]` from the sample app's parent directory, with
`shell=False` and a fixed 10-second timeout. It accepts only optional recorder,
run ID, and step ID arguments; callers cannot supply commands or test paths.

It returns the automatically saved event. Exit code 0 means `succeeded`; other
exit codes, timeout, or launch failure mean `failed`. Timeout and launch failure
have a null exit code; `timed_out` distinguishes timeout. The event records the
first 4096 bytes of combined stdout/stderr, decoded as UTF-8 with replacement,
and flags `output_truncated`. Output is captured to a temporary file rather than
buffered without limit in memory. Test output may include traceback source lines.
The event path `tests` is relative to `sample_app`. Recorder errors propagate.

Run passing and failing examples in separate temporary copies (the checked-in
app stays unchanged):

```bash
python3 - <<'TEST_EXAMPLE'
import json
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
from agentguard.recorder import JSONLRecorder
from agentguard.tools import run_tests

recorder = JSONLRecorder("agentguard/events.jsonl")
for label in ("passing", "failing"):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "sample_app"
        shutil.copytree("sample_app", root, ignore=shutil.ignore_patterns("__pycache__"))
        if label == "failing":
            profile = root / "profile.py"
            profile.write_text(profile.read_text().replace(
                'return profile["user_name"]', 'return profile["username"]'))
        with patch("agentguard.tools._SAMPLE_APP_ROOT", root):
            event = run_tests(recorder=recorder, run_id="tests-demo", step_id=label)
        print(json.dumps(event, separators=(",", ":")))
TEST_EXAMPLE
```

The root override is demo/test scaffolding. The scripted runner below adds only a fixed three-step demonstration.

## Scripted temporary-copy runner

From the repository root:

```bash
python3 -m agentguard.runner success
python3 -m agentguard.runner failure
```

The runner creates a fresh temporary copy of `sample_app`, reads `profile.py`,
makes the selected edit, and runs the fixed test command:

- `success` adds `# Use the profile schema key.` to the return line, preserving
  the `user_name` lookup. This changes the file bytes and hash while tests pass.
- `failure` keeps the original wrong `username` edit and produces failing tests.

Omitting the scenario defaults to `failure`. Each invocation gets its own run ID.
Unknown scenarios are rejected before any tool calls. Both paths require exactly
one matching edit location.
The checked-in app is never edited, and the temporary copy is removed even if
an error interrupts the script. Tool roots are scoped with a context variable.

Each run generates one run ID. The three tool calls use `step-1`, `step-2`, and
`step-3`; their `dependency_ids` are `[]`, `["step-1"]`, and `["step-2"]`.
A fixed cap of three tool calls is checked before every call. There are no
retries, recovery, or LLM calls. All three tools now accept optional
`dependency_ids`, defaulting to an empty tuple.

Events append to `agentguard/events.jsonl`. The command prints all three events
and the actual bounded test output. The success scenario records `succeeded`
with exit code 0; failure records `failed` with exit code 1 and
`KeyError: 'username'`. The demonstration command itself finishes normally for
both scenarios. Python callers can use
`run_script(scenario="success", log_path=...)` from `agentguard.runner` to select a log and receive
this run's three saved events.

## Work log

[CODEX.md](CODEX.md) is append-only. Preserve every existing entry exactly as
written, and append new work as the next numbered entry with the date, changes,
tests, and result. Never replace or summarize earlier entries. Recover missing
entries from Git history when available before appending. Update this README
normally to reflect the current project.
