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
