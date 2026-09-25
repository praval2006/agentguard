# Codex update

## Changes implemented

- Added a JSON Lines recorder in [agentguard/recorder.py](agentguard/recorder.py). It appends a serialized `Event` as a single JSON object per line.
- Added the allowlisted file reader in [agentguard/tools.py](agentguard/tools.py). `read_file("profile.py")` is only allowed when the resolved path stays under `sample_app`; any path outside that directory raises `ValueError`.
- Added coverage in [tests/test_flight_recorder.py](tests/test_flight_recorder.py) for:
  - successful JSONL persistence
  - successful access to `sample_app/profile.py`
  - rejection of a path outside `sample_app`

## Saved event example

```json
{"run_id":"run-1","step_id":"step-1","kind":"tool_result","status":"succeeded","summary":"profile read succeeded","dependency_ids":[],"timestamp":"2026-09-26T00:00:00+00:00"}
```

## Verification

Executed:

```bash
cd /Users/pratik/Desktop/agentguard
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

Result: all existing tests passed.

- `tests`: 4/4 passed
- `sample_app/tests`: 2/2 passed

The feature stops here; no `write_file` or `run_tests` tool was added.


## 2. 2026-09-26 — Append-only work log and README refresh

### Changes

- Adopted an append-only policy for this work log: preserve every existing entry exactly as written, and add each new update as the next numbered entry at the bottom with its date, changes, tests, and result. Never replace or summarize earlier entries. Recover missing entries from Git history before appending when available.
- Preserved the original unnumbered entry above verbatim; it counts as entry 1 without changing its text.
- Checked all available Git history for `CODEX.md` and `Codex.md`. The only committed version (`bef2875`) is empty, so Git contains no earlier entry to restore. The original work-log text is already present in the working file.
- Updated `README.md` to describe the current recorder and bounded reader, provide a runnable example that reads before recording success, and document the work-log policy.
- Checked the current files: the event contract has no tool/path fields, and the current tests do not include a symlink test. This entry reports the current checkout rather than claiming those previous-turn changes are present.

### Tests

Executed from the repository root:

```bash
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 4/4 passed.
- `sample_app/tests`: 2/2 passed.
- Verified that the work log retains its original bytes as an unchanged prefix.

### Result

Both test suites passed. Existing log text is preserved, and future updates must append numbered entries. No `write_file` or `run_tests` tool was added.


## 3. 2026-09-26 — Reader event metadata and symlink verification

### Changes

- Reviewed `agentguard/tools.py`: `read_file` resolves the requested path before checking containment within `sample_app`. The existing implementation rejects an outside-pointing symlink; no reader code change was needed.
- Added optional `tool` and `path` fields to `Event`, preserving existing constructor arguments. The reader example records `read_file` and `profile.py` without file contents.
- Expanded recorder coverage to check persisted metadata, the event field set, and absence of file contents. Added a real symlink inside `sample_app` pointing to a temporary file outside it, and verified `ValueError`. Temporary fixtures are cleaned up automatically.
- Updated `README.md` with a runnable example that reads before recording success and prints only event metadata. Recording remains explicit.
- Checked Git history for `CODEX.md` and `Codex.md`: the only committed log is empty, so there are no missing entries recoverable from Git. Preserved all existing working-file entries byte-for-byte and appended this entry.

### Tests

Executed from the repository root:

```bash
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 5/5 passed, including symlink rejection and saved-event metadata checks.
- `sample_app/tests`: 2/2 passed.
- Executed the README example, read its saved JSONL event back from disk, and verified its tool/path metadata and absence of file contents.
- Verified the entire pre-existing work log is an unchanged byte prefix after appending.

### Result

Both suites passed. No `write_file` or `run_tests` tool was added. Actual event appended to `agentguard/events.jsonl`:

```json
{"run_id":"run-1","step_id":"step-1","kind":"tool_result","status":"succeeded","summary":"profile read succeeded","dependency_ids":[],"timestamp":"2026-09-25T19:36:07.198796+00:00","tool":"read_file","path":"profile.py"}
```


## 4. 2026-09-26 — Automatic read_file outcome recording

### Changes

- Updated `read_file` to create and append its own outcome event on success, rejected paths, and other read errors, using `succeeded`, `blocked`, and `failed` respectively. The existing return value and path rejection remain intact when recording succeeds; recorder errors propagate.
- Events identify `read_file` and the requested path relative to `sample_app`, preserving symlink names. File contents and exception details are not stored.
- Added optional recorder, run ID, and step ID keyword arguments. Default calls write to the repository's `agentguard/events.jsonl` and generate IDs per call.
- Reworked tests to call the reader without manually constructing events. Coverage checks automatic default recording, appended success/rejection events, outside-pointing symlink rejection, missing-file failure, absolute-to-relative path metadata, and absence of contents. Test logs use temporary directories.
- Updated and executed the README example, which calls the reader twice and prints the two automatically saved events.
- Appended this entry while preserving all earlier work-log bytes exactly.

### Tests

Executed:

```bash
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 6/6 passed.
- `sample_app/tests`: 2/2 passed.

### Result

Both suites passed. No `write_file` or `run_tests` tool was added. The README example saved these two events:

```json
{"run_id":"reader-demo","step_id":"step-1","kind":"tool_result","status":"succeeded","summary":"file read succeeded","dependency_ids":[],"timestamp":"2026-09-25T20:00:27.138294+00:00","tool":"read_file","path":"profile.py"}
{"run_id":"reader-demo","step_id":"step-2","kind":"tool_result","status":"blocked","summary":"path rejected outside sample_app","dependency_ids":[],"timestamp":"2026-09-25T20:00:27.139763+00:00","tool":"read_file","path":"../README.md"}
```


## 5. 2026-09-26 — Existing-file writes with content hashes

### Changes

- Implemented `write_file` on `feature/flight-recorder` for existing files inside `sample_app`. Resolved paths outside the root, including escaping symlinks, are rejected before access. Missing files are not created.
- Added automatic write outcome events with the tool name, relative requested path, status, and SHA-256 `before_hash`/`after_hash` of file bytes. File contents are never included. Unavailable hashes are null; read events also serialize null hash fields.
- Writes use UTF-8 and truncate existing files to the new length. The writer supports optional recorder/run/step arguments like the reader. Recorder errors propagate without rollback.
- Added tests for successful writes and exact hashes, shorter UTF-8 replacement, outside paths and escaping symlinks with untouched targets, and missing-file rejection. The wrong `username` edit and its expected `KeyError` are tested only in a temporary copy with a subprocess running that copy's tests.
- Updated and executed the README temporary-copy write example. Preserved all previous work-log bytes while appending this entry.

### Tests

```bash
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 11/11 passed, including the expected failure of the deliberately edited temporary app.
- Checked-in `sample_app/tests`: 2/2 passed.
- `git diff --check`: passed.
- `git diff --exit-code -- sample_app`: passed; the checked-in app is unchanged.

### Result

Implemented only the requested write tool; no `run_tests` tool was added. Actual saved event from writing the temporary copy:

```json
{"run_id":"write-demo","step_id":"step-1","kind":"tool_result","status":"succeeded","summary":"file write succeeded","dependency_ids":[],"timestamp":"2026-09-25T20:09:43.215097+00:00","tool":"write_file","path":"profile.py","before_hash":"7c10fc5c64cdca88bb7b86587c91e4a54f07ff3918be1eb04217a52fe400babe","after_hash":"9c87c16196898379cb222b047c8d06f5bb65bbcc8543b94dea7b34071635bb38"}
```


## 6. 2026-09-26 — Fixed sample_app test runner

### Changes

- Implemented only `run_tests` on `feature/flight-recorder`, using the current Python executable with `-B -m unittest discover -s sample_app/tests -v`, a fixed 10-second timeout, and `shell=False`. No command or test-path arguments are accepted.
- Automatically records and returns the event with exit code, succeeded/failed status, timeout flag, and at most the first 4096 bytes of combined output decoded as UTF-8. A truncation flag identifies clipped output. Capture uses a temporary file to avoid unlimited memory buffering. Timeout or launch failure records a null exit code. Recorder errors propagate.
- Added tests for a clean passing temporary copy, a failing temporary copy with the wrong `username` edit, actual timeout, output truncation, launch failure, and rejection of arbitrary command arguments. Updated the existing event field contract test.
- Updated and executed the README example to save one passing and one failing event using separate temporary copies. No checked-in sample app files were edited.
- Appended this entry without modifying any prior work-log bytes.

### Tests

```bash
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 17/17 passed.
- Checked-in `sample_app/tests`: 2/2 passed.
- `git diff --check`: passed.
- `git diff --exit-code -- sample_app`: passed; checked-in app unchanged.

### Result

Both suites passed. The temporary clean copy returned exit code 0; the deliberately broken copy returned exit code 1 with `KeyError: 'username'`. No agent loop was built. Actual saved events:

```json
{"run_id":"tests-demo","step_id":"passing","kind":"tool_result","status":"succeeded","summary":"tests passed","dependency_ids":[],"timestamp":"2026-09-25T20:18:14.346626+00:00","tool":"run_tests","path":"tests","before_hash":null,"after_hash":null,"exit_code":0,"output":"test_accepts_another_profile (test_profile.ProfileTests.test_accepts_another_profile) ... ok\ntest_displays_name_from_actual_schema (test_profile.ProfileTests.test_displays_name_from_actual_schema) ... ok\n\n----------------------------------------------------------------------\nRan 2 tests in 0.000s\n\nOK\n","output_truncated":false,"timed_out":false}
{"run_id":"tests-demo","step_id":"failing","kind":"tool_result","status":"failed","summary":"tests failed","dependency_ids":[],"timestamp":"2026-09-25T20:18:14.427803+00:00","tool":"run_tests","path":"tests","before_hash":null,"after_hash":null,"exit_code":1,"output":"test_accepts_another_profile (test_profile.ProfileTests.test_accepts_another_profile) ... ERROR\ntest_displays_name_from_actual_schema (test_profile.ProfileTests.test_displays_name_from_actual_schema) ... ERROR\n\n======================================================================\nERROR: test_accepts_another_profile (test_profile.ProfileTests.test_accepts_another_profile)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/tmp2ccjhk1e/sample_app/tests/test_profile.py\", line 11, in test_accepts_another_profile\n    self.assertEqual(display_name({\"user_name\": \"Alex\"}), \"Alex\")\n                     ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/tmp2ccjhk1e/sample_app/profile.py\", line 7, in display_name\n    return profile[\"username\"]\n           ~~~~~~~^^^^^^^^^^^^\nKeyError: 'username'\n\n======================================================================\nERROR: test_displays_name_from_actual_schema (test_profile.ProfileTests.test_displays_name_from_actual_schema)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/tmp2ccjhk1e/sample_app/tests/test_profile.py\", line 8, in test_displays_name_from_actual_schema\n    self.assertEqual(display_name(PROFILE), \"Pratik\")\n                     ~~~~~~~~~~~~^^^^^^^^^\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/tmp2ccjhk1e/sample_app/profile.py\", line 7, in display_name\n    return profile[\"username\"]\n           ~~~~~~~^^^^^^^^^^^^\nKeyError: 'username'\n\n----------------------------------------------------------------------\nRan 2 tests in 0.001s\n\nFAILED (errors=2)\n","output_truncated":false,"timed_out":false}
```


## 7. 2026-09-26 — Three-step scripted temporary-copy runner

### Changes

- Implemented `agentguard.runner` on `feature/agent-loop`: read `profile.py`, make exactly one controlled wrong `username` edit, then run tests. The runner generates one run ID and ordered step IDs, and enforces a fixed three-call cap before each tool call.
- Added optional `dependency_ids` to all three tool APIs and passed them through to recorded events. The chain is `[]`, `["step-1"]`, `["step-2"]`.
- Added a scoped temporary-copy context using a context variable, with automatic root restoration and cleanup on success or error. The checked-in app remains unchanged.
- Added integration coverage for three persisted linked events, the actual expected test failure, the step cap, and cleanup on error. Updated README usage for `python3 -m agentguard.runner`.
- Preserved every earlier work-log byte and appended this entry.

### Tests

Executed the scripted runner and both suites:

```bash
python3 -m agentguard.runner
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 20/20 passed.
- Checked-in `sample_app/tests`: 2/2 passed.
- The runner's temporary app returned exit code 1 with two `KeyError: 'username'` errors, as intended.

### Result

The scripted run stopped after three calls. No LLM, recovery, or retries were added. Actual recorded events:

```json
{"run_id":"34082bd2-8ff6-4e0f-835e-62198bf14cca","step_id":"step-1","kind":"tool_result","status":"succeeded","summary":"file read succeeded","dependency_ids":[],"timestamp":"2026-09-25T21:26:31.909658+00:00","tool":"read_file","path":"profile.py","before_hash":null,"after_hash":null,"exit_code":null,"output":null,"output_truncated":false,"timed_out":false}
{"run_id":"34082bd2-8ff6-4e0f-835e-62198bf14cca","step_id":"step-2","kind":"tool_result","status":"succeeded","summary":"file write succeeded","dependency_ids":["step-1"],"timestamp":"2026-09-25T21:26:31.910766+00:00","tool":"write_file","path":"profile.py","before_hash":"7c10fc5c64cdca88bb7b86587c91e4a54f07ff3918be1eb04217a52fe400babe","after_hash":"9c87c16196898379cb222b047c8d06f5bb65bbcc8543b94dea7b34071635bb38","exit_code":null,"output":null,"output_truncated":false,"timed_out":false}
{"run_id":"34082bd2-8ff6-4e0f-835e-62198bf14cca","step_id":"step-3","kind":"tool_result","status":"failed","summary":"tests failed","dependency_ids":["step-2"],"timestamp":"2026-09-25T21:26:31.985959+00:00","tool":"run_tests","path":"tests","before_hash":null,"after_hash":null,"exit_code":1,"output":"test_accepts_another_profile (test_profile.ProfileTests.test_accepts_another_profile) ... ERROR\ntest_displays_name_from_actual_schema (test_profile.ProfileTests.test_displays_name_from_actual_schema) ... ERROR\n\n======================================================================\nERROR: test_accepts_another_profile (test_profile.ProfileTests.test_accepts_another_profile)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/agentguard-z1cjxusy/sample_app/tests/test_profile.py\", line 11, in test_accepts_another_profile\n    self.assertEqual(display_name({\"user_name\": \"Alex\"}), \"Alex\")\n                     ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/agentguard-z1cjxusy/sample_app/profile.py\", line 7, in display_name\n    return profile[\"username\"]\n           ~~~~~~~^^^^^^^^^^^^\nKeyError: 'username'\n\n======================================================================\nERROR: test_displays_name_from_actual_schema (test_profile.ProfileTests.test_displays_name_from_actual_schema)\n----------------------------------------------------------------------\nTraceback (most recent call last):\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/agentguard-z1cjxusy/sample_app/tests/test_profile.py\", line 8, in test_displays_name_from_actual_schema\n    self.assertEqual(display_name(PROFILE), \"Pratik\")\n                     ~~~~~~~~~~~~^^^^^^^^^\n  File \"/private/var/folders/pm/q4lwk_sx7pgb44jjbjyztkw40000gn/T/agentguard-z1cjxusy/sample_app/profile.py\", line 7, in display_name\n    return profile[\"username\"]\n           ~~~~~~~^^^^^^^^^^^^\nKeyError: 'username'\n\n----------------------------------------------------------------------\nRan 2 tests in 0.001s\n\nFAILED (errors=2)\n","output_truncated":false,"timed_out":false}
```


## 8. 2026-09-26 — Selectable success and failure scenarios

### Changes

- Kept the existing failure scenario and default behavior on `feature/agent-loop`.
- Added a separate success scenario that adds a schema-key comment to the return line in a temporary copy of `profile.py`, continuing to read `user_name`. The real byte change produces different before/after hashes and passing tests.
- Added CLI selection: `python3 -m agentguard.runner success` or `failure`. Each invocation has a new run ID, three ordered linked step IDs, and the existing three-call cap. Unknown scenarios are rejected before tools run.
- Tested both CLI paths, distinct run IDs, dependency chains, changed hashes, expected exit codes/output, and preservation of the checked-in app. Updated README commands and behavior.
- Appended this entry while preserving all earlier work-log bytes.

### Tests

```bash
python3 -m agentguard.runner success
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 22/22 passed, including both scripted scenarios.
- Checked-in `sample_app/tests`: 2/2 passed.
- Successful demo: three succeeded events, final exit code 0, and `OK` from the copied app's two tests.

### Result

Both scenarios work in disposable copies; no LLM or recovery was added. Actual successful run events:

```json
{"run_id":"33fbc5a6-dc9c-49d4-8526-2985b77a42a3","step_id":"step-1","kind":"tool_result","status":"succeeded","summary":"file read succeeded","dependency_ids":[],"timestamp":"2026-09-25T21:34:02.214990+00:00","tool":"read_file","path":"profile.py","before_hash":null,"after_hash":null,"exit_code":null,"output":null,"output_truncated":false,"timed_out":false}
{"run_id":"33fbc5a6-dc9c-49d4-8526-2985b77a42a3","step_id":"step-2","kind":"tool_result","status":"succeeded","summary":"file write succeeded","dependency_ids":["step-1"],"timestamp":"2026-09-25T21:34:02.217055+00:00","tool":"write_file","path":"profile.py","before_hash":"7c10fc5c64cdca88bb7b86587c91e4a54f07ff3918be1eb04217a52fe400babe","after_hash":"d095da91fe0aac1adedbffe2994a3cc4644b9e436fd166b202bb09b10cc5abbd","exit_code":null,"output":null,"output_truncated":false,"timed_out":false}
{"run_id":"33fbc5a6-dc9c-49d4-8526-2985b77a42a3","step_id":"step-3","kind":"tool_result","status":"succeeded","summary":"tests passed","dependency_ids":["step-2"],"timestamp":"2026-09-25T21:34:02.346129+00:00","tool":"run_tests","path":"tests","before_hash":null,"after_hash":null,"exit_code":0,"output":"test_accepts_another_profile (test_profile.ProfileTests.test_accepts_another_profile) ... ok\ntest_displays_name_from_actual_schema (test_profile.ProfileTests.test_displays_name_from_actual_schema) ... ok\n\n----------------------------------------------------------------------\nRan 2 tests in 0.000s\n\nOK\n","output_truncated":false,"timed_out":false}
```
