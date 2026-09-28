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


## 9. 2026-09-26 — Bounded state-based decision loop

### Changes

- Replaced the fixed sequence on `feature/agent-loop` with an explicit run state and `decide_next` policy evaluated after each tool result. Successful reads lead to the selected edit, successful writes lead to tests, and passing tests lead to `completed`; failed or blocked results stop as `failed`.
- Preserved the success/failure CLI commands, scenario edits, unique run IDs, linked tool step IDs, and temporary-copy isolation. Kept the fixed maximum of three tool calls; reaching the cap records a failed final outcome instead of making another call.
- Added a final `run_result` event with `step_id="run-end"`, terminal status, dependency on the last tool step, and the action/reason decision trace. The final event does not consume a tool call. Existing tool events retain their outcome statuses.
- Updated CLI output and README to describe decisions and terminal events. Tests verify both CLI outcomes, persisted events, the cap, and stopping immediately after a failed read without writing or running tests.
- Preserved every prior work-log byte while appending this entry. No retries, automatic repair, LLM, or recovery were added.

### Tests

```bash
python3 -m unittest discover -s tests -v && python3 -m unittest discover -s sample_app/tests -v
```

- `tests`: 23/23 passed.
- Checked-in `sample_app/tests`: 2/2 passed.
- Executed both scenarios: success tests exited 0 and recorded `completed`; failure tests exited 1 and recorded `failed`.

### Result

Actual final events and decision traces from the two runs:

```json
{"run_id":"cc90f98d-a127-4a12-b13b-823f039a7c00","step_id":"run-end","kind":"run_result","status":"completed","summary":"tests passed","dependency_ids":["step-3"],"timestamp":"2026-09-25T21:40:27.405604+00:00","tool":null,"path":null,"before_hash":null,"after_hash":null,"exit_code":null,"output":null,"output_truncated":false,"timed_out":false,"decisions":["read_file: file has not been read","write_file: read succeeded; apply selected edit","run_tests: write succeeded; verify the edit","completed: tests passed"]}
{"run_id":"5ba2866c-1371-481f-8115-e75f5ac98a8d","step_id":"run-end","kind":"run_result","status":"failed","summary":"run_tests failed or was blocked","dependency_ids":["step-3"],"timestamp":"2026-09-25T21:40:27.448861+00:00","tool":null,"path":null,"before_hash":null,"after_hash":null,"exit_code":null,"output":null,"output_truncated":false,"timed_out":false,"decisions":["read_file: file has not been read","write_file: read succeeded; apply selected edit","run_tests: write succeeded; verify the edit","failed: run_tests failed or was blocked"]}
```


## 10. 2026-09-27 — Acceptance Verification MVP direction and Day-1 fixture

### Acceptance Verification MVP

AgentGuard is evolving from the original FlightRecorder / bounded scripted-agent
prototype into an independent acceptance-verification layer for AI coding agents.
A coding agent may interpret a task, implement the feature, write tests based on
its own interpretation, run those tests, and declare completion. Incomplete
interpretation or coverage can make green tests create false confidence.
The new MVP introduces an independent verification path:

```text
Original Task
    ↓
Repository Context
    ↓
Independent Acceptance Planner
    ↓
Structured Acceptance Scenarios
    ↓
Independent Verifier
    ↓
PASS / FAIL / UNVERIFIED
    ↓
Execution Evidence
```

The MVP does not claim to prove arbitrary software correct. Its goal is to
independently derive or receive acceptance behaviours, execute the behaviours it
supports, and provide concrete evidence about whether the finished implementation
satisfies them.

### Existing infrastructure to preserve and reuse

The existing work is not discarded. Preserve and reuse where appropriate:

- `agentguard/events.py`: event model.
- `agentguard/recorder.py`: JSONL evidence recorder.
- `agentguard/tools.py`: bounded file/test execution infrastructure.
- `agentguard/runner.py`: bounded orchestration concepts; may later be refactored.
- `sample_app/profile.py`: original FlightRecorder demo, unchanged in this task.
- `sample_app/tests/test_profile.py`: original profile tests, unchanged in this task.
- `tests/`: existing AgentGuard regression tests.
- `docs/demo_scenario.md`: retained unchanged for now; to be updated later.

Future components are expected to include `agentguard/planner.py`,
`agentguard/scenarios.py`, and `agentguard/verifier.py`. None are created now.

### Verdict semantics for the future MVP

- `PASS`: a supported verification check executed and observed the expected behaviour.
- `FAIL`: a supported verification check executed and observed behaviour that contradicts the expected behaviour.
- `UNVERIFIED`: the behaviour may be relevant, but AgentGuard cannot reliably verify it with its current capabilities.

Prefer UNVERIFIED over inventing evidence or pretending certainty.

### Development principles

- Preserve existing working behaviour.
- Keep changes small and reviewable.
- Do not implement future roadmap components unless explicitly requested.
- Do not silently fix unrelated issues.
- Do not invent product requirements.
- Distinguish explicit requirements from inferred behaviours.
- Prefer actual execution evidence over LLM assertions.
- Keep existing regression tests passing.
- Add tests for new behaviour.
- Prefer simple implementations over premature abstractions.
- Do not add browser automation, production authentication, billing, broad security scanning, or universal repository support during this MVP unless explicitly requested.

### Seven-day direction

1. Day 1: establish a controlled acceptance-verification fixture.
2. Day 2: build and evaluate the independent Acceptance Planner; this is a go/no-go gate.
3. Day 3: introduce structured acceptance scenarios and grounding rules.
4. Day 4: build the independent verification engine.
5. Day 5: connect task → planner → scenarios → verifier → evidence.
6. Day 6: build/polish the result presentation and test unfamiliar scenarios.
7. Day 7: freeze features, test reliability, document limitations, and prepare the demo and submission.

If the Day-2 Acceptance Planner performs poorly, retain the architecture. The
fallback product accepts user-defined acceptance criteria and independently
executes supported verification checks. AI-generated acceptance suggestions
become optional.

### Day-1 changes

The fictional original product requirement is:

> Add subscription cancellation. When a user cancels an active subscription, the subscription should become cancelled and the user should no longer have access to premium features. Repeated cancellation should not crash the application.

- Created `sample_app/subscription.py` as a controlled development fixture.
  `cancel_subscription(subscription)` changes status to `cancelled`, returns the
  same dictionary, and deliberately leaves `premium_access` unchanged. An active
  subscription with `premium_access=True` therefore retains premium access after
  cancellation: the known acceptance gap is intentional.
- Created `sample_app/tests/test_subscription.py` with exactly two implementation-side
  tests: cancellation status and returned object identity. Premium-access revocation
  and repeated cancellation are intentionally outside this test coverage. Green
  implementation-side tests do not mean the original requirements are fully satisfied.
- Updated the existing clean-copy regression assertion in `tests/test_run_tests.py`
  from `Ran 2 tests` to `Ran 4 tests` to account for the added subscription tests.
  This is a fixture-count adjustment; no runner or FlightRecorder implementation changed.
- Reviewed the existing repository and work log before editing. Checked historical
  `CODEX.md` versions: all are preserved as prefixes, with no missing entries to recover.
  Appended this entry without changing any pre-existing work-log bytes.
- No acceptance test, planner, scenarios module, verifier, dependencies, or repository
  redesign were introduced. README and the original demo documentation are unchanged.

### Tests

Executed from the repository root:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard regression suite: 23/23 passed.
- Sample-app suite: 4/4 passed (two original profile tests and two subscription tests).

### Result

The controlled Day-1 fixture has green implementation-side tests while intentionally
retaining the premium-access acceptance gap. The original profile demo and tests,
FlightRecorder implementation, and bounded runner architecture remain unchanged.
No changes were committed or pushed.


## 11. 2026-09-27 — Independent subscription task artifact

### Changes

- Created `tasks/subscription_cancellation.md` with the original fictional developer request and acceptance intent, independently of the implementation and its tests.
- This artifact is the source-of-truth input for future acceptance planning.
- No implementation or tests were changed or added. No planner, scenario model, or verifier was created. All existing work-log content is preserved exactly.

### Tests and result

- `python3 -m unittest discover -s tests -p "test_*.py" -v`: 23/23 passed.
- `python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v`: 4/4 passed.
- The independent task artifact is ready for review. No changes were committed.


## 12. 2026-09-27 — Day-2 Acceptance Planner prototype

### Changes and contract

- Created `agentguard/planner.py` with `plan_acceptance(task_text, repository_context, *, reasoning_provider)`. The caller supplies selected repository context as text; no indexing or file access is performed by the planner.
- The injected callable receives one dictionary containing `instructions`, `task_text`, and `repository_context`, and returns structured Python data. The provider owns any model transport or JSON parsing. There is no default provider, external SDK, API-key requirement, retry, or fixture-specific planning rule. Provider errors propagate.
- Generic instructions distinguish explicit behaviours directly stated by the original task from inferred behaviours suggested by context or consequences of requirements. Unresolved product decisions belong in `ambiguities` and must not silently become acceptance failures. Current implementation behaviour is not the source of product requirements.
- Output has exactly `explicit_requirements`, `inferred_behaviors`, `ambiguities`, and `scenarios`. The first three are lists of nonempty strings. Each scenario has exactly `name`, `behavior`, `reason`, and `source`, all nonempty strings; source is `explicit` or `inferred`. The reason explains grounding.
- At most five scenarios are accepted, in provider-assigned highest-priority-first order. Excess scenarios fail validation rather than being silently truncated. Empty lists are allowed. Unknown fields are rejected, including extra verdict fields.
- Input assumptions: task and context must be strings, task must be nonblank, and each input is limited to 32,000 characters. Empty context is allowed. Oversized text is rejected without truncation. This is a prototype character bound, not a model token budget.
- Malformed output raises a descriptive `ValueError`. Validation covers required/exact keys, container and entry types, nonempty text, scenario count, and allowed source labels. It does not establish semantic grounding, coverage, or truth.
- No verdicts or acceptance checks are executed. Existing implementation, fixtures, tests, runner, and recorder remain unchanged. No verifier or formal Day-3 scenario module was created.

### Tests

Created `tests/test_planner.py` with 10 tests covering generic request forwarding, preserved priority and grounding categories, the subscription smoke pipeline, empty plans/context, five/six-scenario boundaries, missing/extra fields, malformed field and scenario types, source labels, invalid inputs, text-size boundaries, and provider failure propagation without retries.

The subscription smoke test reads `tasks/subscription_cancellation.md` and supplies the subscription function code with explanatory fixture-answer docstrings omitted. Its deterministic fake provider returns the three explicit task behaviours: cancelled state, removal of premium access, and safe repeated cancellation. It does not execute these behaviours.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 33/33 passed (23 existing and 10 new planner tests).
- Sample-app suite: 4/4 passed.

### Result and limitations

Fake-provider tests establish engineering correctness of the planner pipeline and contract, not real planner intelligence. The product hypothesis—useful, independently grounded scenarios for unfamiliar tasks—remains unevaluated and requires separate real-model evaluation across multiple tasks. Previous work-log bytes are preserved exactly. No changes were committed or pushed.


## 13. 2026-09-27 — Blind planner evaluation inputs

### Changes

- Created `evaluation/planner_cases/` with 10 compact task/context pairs: subscription cancellation, password reset, cart quantity, account deletion, session logout, email change, file upload, API pagination, notification preferences, and resource deletion. Requests vary in detail and repository context.
- Case 01 copies `tasks/subscription_cancellation.md` exactly and includes the subscription function without experiment-revealing docstrings. The other contexts contain representative fictional code and repository notes.
- Anti-leakage rule: cases are input only. No expected answers, hidden acceptance scenarios, interpretation labels, judgments, scores, or hints about what the model should discover are included. No answer keys exist yet; evaluation judgments will be created only after real-model plans are produced.
- Created `evaluation/planner_results.md` with empty fields for each case: model output, grounded observations, useful observations, speculative/unsupported observations, ambiguities handled well or poorly, testability, and reviewer notes. No judgments are pre-filled and no numeric benchmark is introduced.
- This dataset supports future blind evaluation of real-model reasoning separately from the unit-tested planner infrastructure. No real-model evaluation was performed in this task, and no product-quality conclusion is claimed.
- No production code, sample-app implementation, existing tests, or dependencies changed. No API provider, verifier, or scenario module was added. All previous work-log bytes are preserved exactly.

### Validation and results

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 33/33 passed.
- Sample-app suite: 4/4 passed.
- Verified exactly 10 case directories, each containing exactly `task.md` and `context.txt` (20 input files total), and 70 empty review fields across 10 results sections.
- Reviewed all case inputs for answer leakage and confirmed the subscription task matches its source byte-for-byte.
- No changes were committed or pushed. Dataset is ready for review.


## 14. 2026-09-27 — Completed Day-2 planner evaluation and GO decision

### Changes and findings

- Updated `evaluation/planner_results.md` with qualitative reviews of all 10 completed cases, covering grounding, usefulness, unsupported observations, ambiguity handling, testability, and reviewer notes. No numeric scores were introduced.
- All 10 cases produced generally grounded and useful acceptance scenarios. Repository-aware inference extended beyond task paraphrasing: password-reset credential persistence, cart persistence with detached dictionaries, normalized email uniqueness, blob + SQL cleanup, and timestamp-tie traversal were strong examples. Account-deletion and notification security-alert ambiguity handling were also particularly useful.
- Case 05 revealed mild over-inference: CSRF preservation was repository-grounded but potentially peripheral to the logout request. Day-3 grounding work should require both repository support and direct relevance to the requested change. The planner generally kept unresolved product decisions separate from acceptance requirements.
- Decision: GO to Day 3 scenario schema and grounding work. This is an engineering validation set, not an independent benchmark, because Codex helped generate the cases and responses were produced in the same conversation. Day 6 should include genuinely unfamiliar tasks with fresh context.
- Reviews use the completed conversation responses; case 07 uses the later complete-context response. Raw model-output sections were empty in the repository and remain empty. No outputs were fabricated or reconstructed, and no new model evaluation or acceptance execution occurred during this documentation update.
- Only evaluation documentation and this appended entry changed. Production code, planner behavior, evaluation inputs, and tests remain unchanged. Historical work-log versions were checked and already preserved; all prior bytes remain intact.

### Validation

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 33/33 passed.
- Sample-app suite: 4/4 passed.

### Result

Completed the qualitative Day-2 review and recorded the GO decision with its limitations. No implementation-correctness or independent-benchmark claim is made. No changes were committed or pushed.


## 15. 2026-09-27 — Day-3 strict scenario schema checkpoint

### Files and public API

- Created `agentguard/scenarios.py` and `tests/test_scenarios.py`.
- `validate_scenario(scenario)` returns None on valid dictionaries and raises descriptive ValueError on malformed input, without mutation or execution.
- `unsupported_scenario(name=..., source=..., reason=..., explanation=...)` constructs and validates a non-executable record.

### Exact schema and design boundaries

- Common required keys: `name`, `source`, `reason`, `action`. Name and reason are nonblank strings; source is exactly `explicit` or `inferred`. Optional `variables` is a dictionary with nonblank string keys and opaque values. No substitution is performed.
- HTTP action: `type="http_request"`, method in GET/POST/PUT/PATCH/DELETE, and nonblank path beginning with `/`. Optional `json` must be a dictionary; optional `headers` must be a dictionary of string keys and string values. Payload contents are not interpreted.
- HTTP scenarios require a nonempty `assertions` list. Status assertions contain exactly `type="status"` and integer `equals` in 100–599, excluding booleans. JSON-field assertions contain exactly `type="json_field"`, a nonblank dotted `path` with nonblank segments, and scalar `equals` (string, integer, finite float, boolean, or None). No expression evaluation or array-path language is introduced.
- Test-command action: exactly `type="test_command"` and `command`, a nonempty list of nonblank string arguments. Assertions are forbidden, including empty lists. Validation establishes representation only, not command safety or availability.
- Unsupported representation: common fields plus `action={"type": "unsupported", "explanation": <nonblank string>}`. Optional variables remain allowed; assertions are forbidden. This is a descriptive non-executable variant, not a third executable capability or a verdict.
- Extra fields are rejected at scenario, action, and assertion schema levels. Header names, JSON payload keys, and variable names are data rather than schema fields.
- No scope deviations. The unsupported action representation and return-None validation API are concrete choices where the request left representation open. Nonblank text and finite scalar numbers clarify strict validation.
- No filesystem, network, subprocess, environment, or API access occurs in the module. No planner changes, conversion, execution, verifier, verdict logic, dependencies, evaluation-input changes, fixture changes, or infrastructure redesign were introduced.

### Tests and results

Added 21 unit tests covering valid action/assertion variants, placeholder preservation, unsupported records, missing and extra fields, malformed containers, source labels, HTTP methods/paths, assertion requirements, status boundaries, scalar/path validation, command representation, variables, headers, and payload types.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 54/54 passed (33 existing and 21 new tests).
- Sample-app suite: 4/4 passed.
- Historical work-log entries were checked and already preserved. This entry is appended with all prior bytes unchanged.

### Result

The first Day-3 schema checkpoint is ready for review. Existing behavior remains unchanged. No changes were committed or pushed.


## 16. 2026-09-27 — Day-3 conservative grounding boundary

### Files and API

- Created `agentguard/grounding.py` and `tests/test_grounding.py`; appended this entry only to existing files.
- Public API: `ground_scenarios(planner_output, repository_context, *, grounding_provider)` returns validated scenario dictionaries. The injected callable receives `instructions`, `planner_output` (including ambiguities), and `repository_context`. No other evidence is supplied or discovered.
- Reused the existing planner validator and maximum constants without editing planner.py. Checkpoint-A scenarios.py remains unchanged; no integration defect required a schema modification.

### Validation and relationship guarantees

- Validate the exact planner dictionary shape, required scenario name/behavior/reason/source strings, valid source labels, and nonempty string entries in requirements, inferences, and ambiguities.
- Reject inputs before the provider call when context is not a string, provider is not callable, or bounds are exceeded. Context allows 32,000 characters, aggregate planner value text allows 32,000 characters, non-scenario lists allow 100 entries each, and scenarios allow the planner maximum of five. Nothing is truncated.
- Invoke the provider once, including for empty scenario lists. Provider exceptions propagate without retries. Require a list with exactly one result per input scenario; validate each candidate through `validate_scenario` and compare name/source/reason exactly at each position. Invalid contracts raise ValueError; no partial result is returned.
- Pass a defensive copy to the provider and retain a separate comparison baseline so request mutation cannot alter caller inputs or bypass identity preservation.
- Provider instructions distinguish WHAT from HOW, forbid invented execution details and silent ambiguity resolution, require evidence for HTTP requests/assertions and explicitly documented existing test commands, and prefer unsupported when details or capabilities are missing. They preserve inferred labels and require relevance as well as grounding.
- Only the existing HTTP, test-command, and unsupported representations are used. No verdicts, execution, natural-language parsing, repository discovery, variable substitution, external provider, or additional DSL capabilities were implemented.
- Deterministic checks establish structure and positional metadata correspondence, not semantic evidence support, behavioral equivalence, or command safety. Scenarios with identical preserved metadata cannot be distinguished by metadata comparison alone. Those reasoning obligations remain with the provider; fake-provider tests do not prove real-model grounding quality.

### Tests and results

Added 22 tests for evidenced HTTP and existing-command representations, unsupported retrieval without a supplied route, provider request contents, failures without retry, missing/added/reordered results, name/source/reason changes, malformed inputs and results, schema-validation delegation, size/count boundaries, empty scenarios, mutation isolation, and absence of execution/external reads.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 76/76 passed (54 existing and 22 new tests).
- Sample-app suite: 4/4 passed.
- Checked historical work-log prefixes and preserved all pre-existing bytes exactly.

### Result

Checkpoint B is ready for review with no scope deviations. No existing production files changed, including the planner and Checkpoint-A schema. Existing tests, evaluation inputs, and sample fixtures remain unchanged. No changes were committed or pushed.


## 17. 2026-09-27 — Final Day-3 qualitative grounding validation

### Changes and observations

- Created `evaluation/day3_grounding_validation.md` using only frozen case 08 (API pagination), case 10 (resource deletion), and case 01 (subscription cancellation) task/context inputs as application evidence. Recorded fresh planner-style outputs, grounded representations, missing evidence, unresolved ambiguities, and Day-4 implications.
- Considered 11 scenarios: four pagination, four resource deletion, and three subscription cancellation. Results: 0 HTTP, 0 test-command, 11 unsupported representations. Explicit/inferred distinctions, order, and name/source/reason were preserved.
- Pagination SQL and handler names do not establish a public route. The resource task requests DELETE /reports/{id}, but context does not evidence a bound delete route, authentication inputs, or fixtures; the detail handler's 404 cannot substitute for deletion evidence. Subscription context supplies only a Python function, which is outside current execution capabilities. None supplies an existing test command.
- Preserved useful acceptance intent instead of inventing endpoints, commands, identifiers, or runtime values. Symbolic variables cannot establish missing mechanisms or fixture guarantees. Multi-step and collection checks also exceed the current single-action/scalar-assertion representation unless a supported existing command covers them.
- This is qualitative engineering validation, not an independent benchmark or proof of correctness. It demonstrates conservative abstention in these authored outputs, not successful execution or general real-provider grounding reliability. Day 4 needs explicitly evidenced execution contracts and setup for executable demonstrations while preserving honest unsupported handling.

### Validation and results

- Validated three planner outputs through `plan_acceptance` and three grounding lists through `ground_scenarios`, using local injected callables returning the recorded dictionaries. Separately validated all 11 representations with `validate_scenario`. No external provider was added and no represented HTTP or command action was executed.
- Ran the existing suites after creating the document:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard: 76/76 passed.
- Sample app: 4/4 passed.
- Historical log prefixes were checked; all previous bytes were preserved exactly before appending.

### Result

Final Day-3 validation is documented. No deviations from scope: production code, planner/schema/grounding behavior, existing tests, sample app, and frozen evaluation inputs remain unchanged. No changes were committed or pushed.


## 18. 2026-09-27 — Day-4 deterministic result/assertion core

### Files and API

- Created `agentguard/verifier.py` and `tests/test_verifier.py`. No existing production modules, tests, fixtures, or evaluation inputs changed.
- Public API: `verify_observation(scenario, observation=None) -> dict`. Calls existing `validate_scenario` first; malformed scenarios raise its validation errors. Observations are supplied by the caller; the core performs no execution, I/O, environment access, substitution, discovery, or recorder integration, and does not mutate inputs.

### Observation and result contracts

- HTTP observations are plain dictionaries with exactly `type="http_response"`, integer `status` in 100–599, and optional parsed `json`. Missing/invalid status or envelope makes the HTTP observation unestablished. Optional invalid/unavailable JSON makes JSON assertions unobservable while retaining valid status evidence.
- Command observations contain exactly `type="test_result"` and integer `returncode`. Booleans are rejected as status/return codes. No output logs or extra observation-envelope fields are accepted.
- JSON observation traversal accepts only built-in JSON value types with finite floats, string dictionary keys, at most 10,000 nodes, depth 32, and 32,000 aggregate string/key characters. Invalid, cyclic, or oversized JSON produces unavailable JSON evidence. Dotted traversal uses dictionaries only, without array indexing or evaluation.
- Results always contain `name`, `source`, `verdict`, `assertions`, and `reason` (None unless explanatory information is needed). HTTP assertion entries contain `type`, `expected`, `verdict`, `reason`, optional `path`, and `observed` when available. Missing observations omit `observed`; observed null retains `observed=None`. Observed containers contradict scalar expectations and are summarized as `observed_type` object/array without copying their unrelated contents.
- Expected/observed strings are limited to 512 evidence characters with corresponding `expected_truncated`/`observed_truncated` flags; comparisons occur on full values. Command results add `expected=0` and valid `observed` return code, with an empty assertions list. Unsupported results preserve the full scenario explanation as reason and require no observation.
- Evidence includes only assertion-selected values, not complete responses, headers, request bodies, variables, command logs, environment state, or unrelated fields. Callers must avoid selecting sensitive values for reportable assertions; this core does not infer whether arbitrary selected scalar text is a secret.

### Verdict rules and boundaries

- Any observed assertion contradiction yields FAIL, even if another assertion is unobservable. Otherwise any UNVERIFIED assertion yields UNVERIFIED; only all-PASS assertions produce PASS.
- Missing fields/parsed JSON and invalid observations do not become FAIL. Existing null is distinguishable from a missing path. JSON booleans differ from numbers; integers/floats compare as JSON numbers.
- Valid command return code 0 produces PASS and nonzero produces FAIL. Missing/malformed command evidence produces UNVERIFIED. Unsupported always produces UNVERIFIED.
- No scope deviations. Strict envelope keys, bounded JSON validation/evidence, and result-key names are implementation choices within the requested core. Observation authenticity and association with the scenario are caller obligations; structural validation is not proof that execution occurred. The reasoning model does not assign verdicts.

### Tests and results

Added 28 focused unit tests covering assertion outcomes, dotted traversal, null versus missing values, aggregation precedence, commands, unsupported explanation preservation, malformed scenarios/observations, status boundaries, boolean exclusion, numeric equality, containers, cycles, bounds, truncation, nonmutation, deterministic results, and no external access.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 104/104 passed (76 existing and 28 new tests).
- Sample-app suite: 4/4 passed.
- Historical work-log prefixes were checked; all prior bytes are preserved exactly.

### Result

The first Day-4 checkpoint is ready for review. No HTTP request or represented command was executed by the verifier. No dependencies or provider were added. No changes were committed or pushed.


## 19. 2026-09-27 — Day-4 allowlisted test execution

### Changes and reuse

- Created `agentguard/execution.py` and `tests/test_execution.py`. Public API: `execute_test_scenario(scenario, *, recorder=None)`.
- Inspected tools.py, runner.py, and their existing tests. Reused `tools.run_tests` unchanged rather than adding subprocess code: it already provides fixed-command execution, timeout, file-backed output capture, bounded recorded evidence, and automatic recording. Reused its scoped root ContextVar, resetting it in finally. The old runner and recorder schemas remain unchanged.
- Exact allowlist contains only `python3 -m unittest discover -s sample_app/tests -v`, the existing narrow form. No other executable, options, pattern, directory, shell syntax, or Python module is permitted. Actual execution uses the tool's current `sys.executable` with `-B`, never PATH lookup of a model-selected executable. Root `tests` is deliberately not enabled in this checkpoint; only the existing sample-app primitive is exposed.
- Fixed working directory is the repository root derived from the execution module, not supplied by a caller. Preflight resolves the sample package, test root, and descendants and rejects missing paths or paths escaping the repository. Symlinked package/test roots are rejected even within the repository. Existing ContextVar overrides cannot redirect this API's execution. No public root override was added; tests patch the private root for controlled temporary fixtures.
- Reused bounds: 10-second timeout, shell=False, stdin disabled, combined output captured to a temporary file, and first 4096 bytes retained by the existing recorder with truncation flag. These are bounded evidence/runtime measures, not a disk quota or a sandbox for Python test behavior. Preflight assumes no concurrent repository mutation. Trusted tests may themselves import code or perform side effects; policy does not prove semantic acceptance coverage.

### Result and failure semantics

- Return keys: `execution`, `observation`, `result`. Execution fields are `established`, `reason`, `command`, `returncode`, `timed_out`, and `output_truncated`. Rejected command text is not echoed. The new envelope does not copy raw output; the existing recorder retains its usual bounded test output and may include traceback source lines.
- Established executions create exactly `{"type": "test_result", "returncode": <integer>}` and delegate to `verify_observation`; zero yields PASS and actual nonzero yields FAIL.
- Policy rejection, timeout, launch failure, malformed evidence, unavailable paths, and capture/recording OSError produce no fabricated return code: observation is None and the verifier produces UNVERIFIED with a concise infrastructure reason. The wrapper conservatively catches recording failures; the underlying tool's behavior remains unchanged. Scope restoration occurs even on errors.
- Malformed or non-test scenarios raise ValueError. No HTTP execution, new dependencies, planner/grounding/schema changes, frozen-input edits, or fixture changes were introduced.

### Tests and results

Added 18 tests covering real passing/failing execution with verifier delegation, recorded evidence, forbidden executables/shell forms/Python code/modules/paths, escaping symlinks, timeout, launch failure, bounded output, invalid scenarios, nonmutation, fixed cwd/no shell, root-scope restoration, malformed evidence, and recorder failure. Controlled temporary fixtures keep the sample app unchanged. An initial failure-fixture typo was corrected before final verification.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 122/122 passed (104 existing and 18 new tests).
- Sample-app suite: 4/4 passed.
- Historical work-log prefixes checked; all prior bytes preserved exactly.

### Result

The narrow existing sample-app command is executable through the deterministic verifier. No scope deviations: the permitted equivalent existing command form was chosen to reuse the safe primitive rather than broaden command execution. No existing production file changed. No changes were committed or pushed.


## 20. 2026-09-27 — Controlled loopback HTTP execution

### Files, API, and policy

- Created `agentguard/http_execution.py` and `tests/test_http_execution.py`. Public API: `execute_http_scenario(scenario, *, base_url)`. Existing test executor, planner, grounding, schema, verifier, recorder, fixtures, and evaluation inputs remain unchanged.
- Base URL must match exactly `http://127.0.0.1:<port>`, with decimal port 1–65535 and no leading zero. HTTPS, other hosts, DNS names, userinfo, URL paths, queries, fragments, and alternate loopback spellings are rejected. Direct numeric IPv4 socket connection avoids DNS and environment proxy discovery.
- Scenario path remains origin-form: it must begin with a single slash, be ASCII without whitespace/control characters, backslashes, fragments, or unresolved braces, and contain at most 2048 characters. No substitutions, inferred authentication, endpoint discovery, or cookie/session state.
- Only existing GET/POST/PUT/PATCH/DELETE methods are used. http.client never follows redirects; 3xx responses are observed directly, including cross-origin Location headers, without fetching the destination.
- Header policy rejects case-insensitive Host, Content-Length, Transfer-Encoding, Connection, Proxy-Authorization, Proxy-Connection, Keep-Alive, TE, Trailer, Upgrade, Expect, Accept-Encoding, Cookie, Cookie2, and all proxy-prefixed headers. Invalid names, case-duplicate names, control/non-ASCII values, and aggregate header text above 8192 bytes are rejected. The client calculates framing; JSON defaults to application/json unless a safe explicit Content-Type is supplied. Accept-Encoding is fixed to identity.

### Bounds and evidence

- One 2-second shared deadline covers connect/send/response reads. A deadline-aware binary socket reader checks remaining time before every underlying receive, preventing indefinitely renewed read timeouts. Response-header parsing retains standard-library line/count limits. Response body reads retain at most 32768 bytes plus one overflow-detection byte; request JSON is capped at 32768 bytes and uses the verifier's built-in JSON structure bounds.
- Return envelope: `execution`, `observation`, `result`. Execution metadata contains established, reason, method, status, body_truncated, and json_available. Path/query, authorization values, cookies, and full raw request/response bodies are not copied into metadata. No recorder integration was added.
- Established observation contains type=http_response and integer status. Only complete, bounded, valid parsed JSON is added as json; invalid/duplicate-key/nonfinite/oversized JSON, incomplete bodies, or unsupported content encoding omit it. Parsed observation JSON can itself contain sensitive application data and is for verification, not automatic logging; reportable assertion evidence remains selected/bounded by the existing verifier.
- A real 404/500 is an established response and may produce PASS or FAIL according to the assertions. Policy rejection, connection failure, timeout before response establishment, or invalid response framing yields no observation and UNVERIFIED with a concise infrastructure reason. Missing/incomplete body data preserves reliable status evidence and leaves JSON assertions UNVERIFIED. All verdicts are delegated to verify_observation.
- No external dependency, remote-target support, schema broadening, multistep behavior, or semantics claim beyond observed assertions. No scope deviations; an isolated HTTP helper avoids redesigning the existing test-execution module.

### Tests and results

Added 25 tests using an in-process loopback server: status/JSON outcomes, nested fields, real error statuses, JSON request bodies, custom headers and methods, dangerous headers, URL/path rejection, redirect non-following, timeout/refusal, oversized/non-JSON/malformed/incomplete bodies, nonmutation, verdict delegation, and DNS/proxy independence. An oversized-body test exposed response-stream socket ownership; fixed by giving the reader its own socket handle, closed with the response.

The sandbox initially denied loopback bind. Tests were rerun with approved escalation so the local server could bind; no external network service was used.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 147/147 passed (122 existing and 25 new tests).
- Sample-app suite: 4/4 passed.
- Historical work-log prefixes checked; all previous bytes preserved exactly.

### Result

Controlled HTTP execute → observe → verify is ready for review. Existing execution behavior remains intact. No changes were committed or pushed.


## 21. 2026-09-27 — Day-5 controlled subscription integration proof

### Files and controlled interface

- Created `sample_app/subscription_http.py`, `agentguard/subscription_demo.py`, and `tests/test_subscription_demo.py`.
- The demo-only standard-library HTTP fixture binds to numeric IPv4 loopback on an ephemeral port. Only POST /subscriptions/1/cancel performs cancellation. Each request creates {"status": "active", "premium_access": True}, calls the existing subscription.cancel_subscription function, and returns its result as JSON with HTTP 200. The context manager stops and closes the server even on errors. No persistence, authentication, unrelated feature routes, framework, or dependency was added.
- The original subscription.py and implementation-side tests remain unchanged. The intentional premium-access defect is preserved; cancellation is not reimplemented in the handler.

### Frozen scenario, execution, and report

- `acceptance_scenario()` returns a fresh dictionary for the frozen explicit requirement: POST /subscriptions/1/cancel; assert HTTP 200, JSON status equals cancelled, and JSON premium_access equals False. Cancellation/access intent comes from the original task; the concrete route, controlled ID, and HTTP status come from the newly supplied fixture contract.
- `run_demo()` reuses execute_test_scenario with its exact existing allowlisted sample-app command and a temporary JSONL recorder, then starts the fixture and calls execute_http_scenario. No new HTTP client, command execution, verdict calculation, planner/provider integration, or policy broadening was introduced.
- Run `python3 -m agentguard.subscription_demo` for a structured JSON report. It contains implementation_tests, acceptance, acceptance_execution, repeated_cancellation, and a scope statement. Assertion expected/observed values and verdicts come from the verifier; raw response bodies and test output logs are not copied into the report. Temporary test recording is cleaned up.
- Repeated cancellation is represented separately as unsupported and passed to verify_observation, producing UNVERIFIED with the fresh-state/single-request limitation. No repeated-cancellation PASS is claimed and no multi-step mechanism is added.

### Actual observations and validation

The real HTTP observation established by the integration test was:

```json
{"type":"http_response","status":200,"json":{"status":"cancelled","premium_access":true}}
```

- HTTP status: expected 200, observed 200 → PASS.
- JSON status: expected cancelled, observed cancelled → PASS.
- JSON premium_access: expected false, observed true → FAIL.
- Overall acceptance verdict: FAIL, calculated by the existing verifier from contradictory observation.
- Existing implementation-test result: PASS with actual return code 0.

Added 7 integration tests covering frozen scenario validation/fresh copies, real endpoint/function delegation, loopback binding, exact response and assertion outcomes, verifier delegation, scenario nonmutation, green existing-test contrast, preserved defect/object identity, non-reimplemented handler behavior, unrelated route rejection, reporting delegation, and repeated-cancellation non-claim.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 154/154 passed (147 existing and 7 new tests).
- Sample-app implementation suite: 4/4 passed, unchanged.
- Loopback regression tests ran with approved sandbox escalation; no external service was used.
- Historical log prefixes checked; all existing work-log bytes preserved exactly.

### Result

The controlled integration demonstrates green implementation tests alongside a real acceptance failure. This is a downstream integration proof, not evidence of general effectiveness or live model planning quality. No scope deviations, existing execution/verification changes, frozen-input changes, or subscription repair. No changes were committed or pushed.


## 22. 2026-09-27 — Day-5B deterministic acceptance orchestrator

### Files and API

- Created `agentguard/acceptance.py` and `tests/test_acceptance.py`; appended this log entry without changing prior bytes.
- Public API: `run_acceptance(scenarios, *, base_url=None, recorder=None) -> dict`, returning `{"verdict": ..., "results": [execution envelopes in input order]}`.
- Accepts only a list of at most five already-grounded scenario dictionaries, using the existing planner maximum constant. Validates every scenario before any execution, so a malformed later entry cannot cause earlier actions to execute. Invalid containers/scenarios and oversized lists fail clearly without truncation.

### Dispatch and aggregation

- HTTP scenarios use execute_http_scenario with the supplied base_url. Missing, blank, or non-string target configuration produces a no-observation verifier result and bounded execution metadata explaining target unavailability. Nonblank URL policy decisions remain entirely with the existing HTTP executor.
- Test-command scenarios use execute_test_scenario with the supplied recorder, without changing command policy or implementing subprocess execution.
- Unsupported scenarios invoke verify_observation without execution, normalized into execution established=False, bounded explanation, observation=None, and the unmodified verifier result. Metadata explanations over 512 characters have a truncation flag; original verifier explanations remain preserved in results.
- Individual scenario/assertion verdicts remain exclusively owned by existing executors/verifier. The orchestrator reads their final verdicts, preserves envelopes/order without duplicating raw logs, and only aggregates: FAIL takes precedence over UNVERIFIED, otherwise a nonempty all-PASS list is PASS. An empty list returns UNVERIFIED with empty results.
- Unknown returned verdict labels fail clearly; unexpected executor exceptions propagate rather than silently dropping scenarios. Inputs are read only. No model/planner/grounder calls, provider, reasoning, retries, variable substitution, or multi-step scenario behavior was introduced.
- Frozen demo, execution/verification modules, runner, fixtures, evaluation inputs, and existing tests are unchanged. No compatibility defect required modification of frozen components.

### Tests and results

Added 18 tests for empty/unsupported behavior, aggregation combinations, dispatch and recorder forwarding, verdict ownership, order/nonmutation, validation before side effects, scenario-count bounds, missing and invalid HTTP configuration, preserved infrastructure inability, bounded metadata, error handling, and a real controlled subscription HTTP integration.

The integration observes cancelled status and premium_access=True through the existing fixture and executor. The verifier returns PASS/PASS/FAIL for its assertions; the orchestrator preserves that FAIL, preserves the separate unsupported UNVERIFIED, and aggregates overall FAIL without assigning an individual verdict.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard suite: 172/172 passed (154 existing and 18 new tests).
- Sample-app implementation suite: 4/4 passed, unchanged.
- Loopback tests used approved sandbox escalation; no external network dependency.
- Historical work-log prefixes checked and all pre-existing bytes preserved exactly.

### Result

The generic deterministic orchestration checkpoint is ready for review. No scope deviations, planner/grounder/model changes, intentional defect repair, or product-effectiveness claims. No changes were committed or pushed.


## 23. 2026-09-27 — Day-5C end-to-end acceptance reasoning proof

### Methodology

This was a controlled end-to-end reasoning experiment for the subscription-cancellation task. The original task remained the source of product requirements. `evaluation/day5c_subscription_context.md` supplied bounded neutral repository/interface context without revealing the runtime premium_access value after cancellation, identifying the intentional defect, or stating an expected AgentGuard verdict.

Codex acted manually as the injected reasoning provider for the planner and grounder. AgentGuard did not autonomously call a model API. Planner output was frozen before grounding; grounding output was frozen before execution. Both outputs were subsequently saved unchanged as JSON before execution. Neither reasoning artifact was regenerated or revised after observing runtime behavior.

The reasoning calls were instructed to use only their supplied inputs. This was performed in the existing project conversation, so it was not an independently blinded evaluation free of prior project context.

### Planner result

The planner independently proposed three explicit acceptance behaviors from the task:

1. Active subscription becomes cancelled.
2. Cancellation removes premium access.
3. Repeated cancellation remains safe and consistent.

It specifically proposed checking that premium_access becomes false, while distinguishing that observable state field from broader premium-feature enforcement that the supplied context could not establish.

### Grounding result

- “Active subscription becomes cancelled” used the documented POST /subscriptions/1/cancel interface, with HTTP 200 and status == "cancelled" assertions.
- “Cancellation removes premium access” used the same endpoint, with HTTP 200 and premium_access == false assertions.
- “Repeated cancellation remains safe and consistent” became unsupported: each documented HTTP request creates fresh state, and the current schema has no justified same-subscription multi-step mechanism or supplied existing test command for this behavior.

No endpoint, command, multi-step capability, or verdict was invented. Scenario names, sources, reasons, and order were preserved between the reasoning outputs.

### Deterministic execution

The minimal harness loaded the frozen grounded scenarios unchanged and passed them to the existing `run_acceptance(...)` pipeline with the existing loopback subscription server. The pipeline validated the scenario dictionaries and used its existing executors and verifier. The existing fixture produced the real HTTP observation:

```json
{"status":"cancelled","premium_access":true}
```

- Active subscription becomes cancelled → PASS.
  - HTTP status: expected 200, observed 200.
  - status: expected "cancelled", observed "cancelled".
- Cancellation removes premium access → FAIL.
  - HTTP status: expected 200, observed 200.
  - premium_access: expected false, observed true.
- Repeated cancellation remains safe and consistent → UNVERIFIED.
  - Current evidence/execution capability cannot establish repeated cancellation of the same subscription.

Overall AgentGuard acceptance verdict: FAIL. Individual verdicts came from the existing deterministic verifier and aggregation from the existing orchestrator; neither the reasoning model nor the execution harness assigned them. The harness ran once and its exact JSON result was preserved.

### Green-test contrast

The unchanged sample-app implementation suite ran 4/4 PASS after the experiment. This controlled experiment therefore demonstrates green implementation tests alongside an independently derived acceptance failure. The intentional subscription behavior and existing tests were not modified.

### Artifacts

- `evaluation/day5c_subscription_context.md`
- `evaluation/day5c_planner_output.json`
- `evaluation/day5c_grounded_scenarios.json`
- `evaluation/day5c_execute.py`
- `evaluation/day5c_acceptance_result.json`

### Claim boundary

This is a controlled end-to-end reasoning proof: a real reasoning model produced useful planning/grounding artifacts, and AgentGuard validated the grounded scenario representations and executed the supported checks. Schema validation does not itself prove semantic grounding. This is not evidence of general effectiveness across arbitrary repositories and is not an autonomous model-provider integration. Fresh unfamiliar tasks are still required for broader validation.

### Documentation checkpoint validation

This checkpoint appends documentation only. No Day-5C artifact or implementation/test file was modified; reasoning outputs were not regenerated and the Day-5C harness was not rerun. No model/API integration was added, and nothing was committed or pushed. Regression results are recorded below after running the requested suites.

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard regression suite: 172/172 passed.
- Sample-app implementation suite: 4/4 passed, unchanged.
- Loopback regression tests used approved sandbox escalation.
- All historical work-log prefixes were checked; entries 1–22 and every pre-existing byte remain unchanged.
- No scope deviations. No changes were committed or pushed.


## 24. 2026-09-28 — Registered-check trust foundation

### Changes

- Added the registered_check scenario action with exactly type and check_id,
  bounded to 128 characters. Assertions and extra action authority fields are
  rejected. Existing scenario variants are unchanged. A reference is not execution
  authorization or proof of coverage.
- Added agentguard/check_registry.py with explicit parse_registry(text,
  repository_root=...) and load_registry(repository_root=..., registry_path=...).
  Registry locations are caller-approved repository-relative strings; no automatic
  configuration discovery occurs. Returned frozen dataclasses contain tuples and
  immutable coverage records.
- Strict version-1 JSON requires exact fields, unique check and coverage IDs,
  unittest runner, and a conservative module.Class.test_method target. Bounds:
  100 checks, 128-character IDs, 512-character cwd/target, 2048-character coverage
  description, and 262144 UTF-8 bytes. Duplicate JSON keys are rejected.
- Paths reject absolute/drive/UNC syntax, traversal, backslashes, malformed
  components, symlink cwd/registry components, missing paths, and wrong file types.
  Cwd '.' is supported. Paths resolve beneath the trusted caller's canonical root.
- Coverage metadata is descriptive provenance only. No target imports, subprocess
  execution, verdicts, filesystem writes, or snapshot/coverage approvals occur in
  the registry module. No execution integration is implemented in this phase.

### Validation

Added 21 tests in tests/test_check_registry.py covering schema references and
injected authority, immutable registry data, exact shapes, version/type/size bounds,
unique IDs, duplicate keys, target/runner restrictions, path confinement, symlinks,
missing files, and no subprocess execution during parsing/loading.

- Focused: python3 -B -m unittest discover -s tests -p test_check_registry.py -v
  — 21/21 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 193/193 passed (172 existing, unchanged; 21 new).
- Full regression used approved loopback escalation for existing HTTP tests.
- Verified no diff under evaluation; Day-5 and Day-6 artifacts were untouched.
- Historical CODEX.md versions were verified as prefixes before appending; all
  previous bytes remain unchanged.

### Limitations and result

This is path confinement, not a sandbox or proof of trust. Caller approval is
required; filesystem checks assume no concurrent mutation and must be repeated
before future execution. Target syntax does not prove a method exists or selects
exactly one test. The verifier, acceptance orchestrator, and grounder remain
unchanged: registered_check is not yet supported by those execution pathways.
Legacy test_command execution and its sample-app exact allowlist remain unchanged.
Coverage metadata does not establish acceptance coverage or cause PASS.
No Day-6 rerun, LLM integration, or capability beyond this foundation was added.


## 25. 2026-09-28 — Bounded registered unittest execution

### Changes and trust boundary

- Added agentguard/registered_execution.py with execute_registered_check(scenario,
  repository_root=..., registry=...). Only check_id comes from the scenario;
  registration fields are revalidated from the trusted immutable in-memory registry.
  Unknown IDs and ordinary preflight/process failures return structured facts.
- Added agentguard/check_runner.py. The fixed invocation uses sys.executable,
  -I, -B, the absolute AgentGuard runner path, the registered dotted target, and
  a parent-owned result descriptor. The runner explicitly adds only approved cwd
  to the isolated interpreter's import path. Target module and class origins must
  resolve within cwd; selection must contain exactly one unittest test.
- Shell is disabled, stdin is disabled, cwd comes from registration, and no
  scenario-controlled environment/options are accepted. No arbitrary Python
  expressions or command strings are interpreted.
- Revalidate root identity, registered cwd containment and symlink components,
  and reject symlinks throughout the selected cwd tree immediately before launch.
  Tests run in a new POSIX session; the process group is killed on cleanup,
  including timeout. Limits are 10 seconds, 4096 retained stdout/stderr bytes,
  and 2048 structured-result bytes. Output text is not verdict evidence and is
  omitted from observations; truncation is reported.

### Observations and scope

- Parent-owned temporary descriptors separate structured JSON from stdout/stderr;
  result keys, count types/bounds, statuses, and success/failure consistency are
  validated. Duplicate keys, oversized/missing results, crashes, and launch
  errors cannot become successful test observations. Temporary files are cleaned.
- Facts include check/coverage/target identity, status, counts, returncode,
  timed_out, and output_truncated. Status distinguishes success, assertion_failure,
  test_error, load_error, skipped, expected_failure, unexpected_success,
  zero_tests, multiple_tests, malformed_result, process_crash, timeout,
  unknown_check, configuration_error, and execution_error. No acceptance verdict
  is calculated. The runner exits normally for reported test outcomes; its process
  returncode is distinct from assertion success.
- No verifier, acceptance dispatch, aggregation, planner, grounder, coverage
  approvals, or LLM integration changed. Legacy tools/execution and HTTP behavior
  remain unchanged. A separate small process path preserves the legacy recorder
  contract rather than generalizing its hardcoded sample-app runner in this phase.

### Tests and results

Added 24 tests using unfamiliar temporary repositories: real single-test success,
assertion failure, load/setup/runtime errors, skip/expected failure/unexpected
success, zero/multiple selection, timeout, crash, missing/malformed/oversized
results, stdout spoofing, output bounds, launch failure, unknown registry entries,
model-field injection, fixed process construction, cwd/root and symlink checks.

- Focused: python3 -B -m unittest discover -s tests -p test_registered_execution.py -v
  — 24/24 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 217/217 passed (193 existing unchanged and 24 new).
- Approved escalation allowed existing regression HTTP loopback tests to bind.
- No diff under evaluation; frozen Day-5/Day-6 artifacts were not changed or rerun.
- All historical work-log versions remain byte-for-byte prefixes.

### Limitations

This is POSIX bounded execution of trusted repository code, not a sandbox or
network restriction. Tests can perform side effects, spawn detached children, or
forge their own result channel; process-group cleanup does not contain malicious
code. Filesystem preflight assumes no concurrent mutation. Registry data is an
in-memory approved snapshot, not a live manifest or digest approval mechanism;
semantic code/configuration changes cannot be detected without future snapshot
binding. Temporary capture bounds retained evidence, not total disk usage.
Coverage metadata is descriptive only and cannot establish acceptance coverage.
No final registered-check verifier/orchestrator integration exists yet.


## 26. 2026-09-28 — Registered-check acceptance verification

### Changes

- Added coverage_authorization.py: frozen CoverageAuthorizations stores at most
  100 immutable identity/check/coverage triples. scenario_identity uses canonical
  JSON of the complete validated grounded scenario, including optional variables,
  bounded to 32000 characters. IDs are bounded to 128 characters; duplicate or
  noncanonical identities are rejected. No repository digest infrastructure added.
- Authorization is supplied separately by a trusted caller. Exact scenario identity,
  selected check ID, and trusted registry coverage ID must match. Model JSON cannot
  self-authorize via extra action/scenario fields. Missing or mismatched authority
  prevents registered execution and produces UNVERIFIED.
- Added registered-check handling in verify_observation, with optional registry and
  coverage_authorizations arguments. Strict Phase-2 observation fields, identity,
  target, count types/bounds, return code, timeout, and outcome consistency are checked.
  Exactly one ordinary successful authorized test yields PASS. Exactly one authorized
  test with ordinary assertion failure yields FAIL. Missing/malformed observations,
  errors, skips, expected failures, unexpected successes, timeout, crash, and
  configuration failures remain UNVERIFIED. The verifier performs no execution/I/O.
- run_acceptance accepts optional repository_root, registry, and
  coverage_authorizations, dispatches registered actions only through the Phase-2
  executor, and delegates verdicts to the verifier. Existing envelopes/order,
  prevalidation, nonmutation, five-scenario cap, empty behavior, and aggregation
  precedence remain intact. Evidence contains bounded provenance/counts, not logs.

### Tests and results

Added 14 tests in tests/test_registered_acceptance.py covering temporary-repository
PASS/FAIL, missing/mismatched/stale authorizations, changed scenario identity or
selected check, injected model authority, immutable bounded associations, skipped
and errored tests, timeout/crash/configuration failures, malformed evidence,
verifier no-I/O, prevalidation before execution, and mixed aggregation.

- Focused: python3 -B -m unittest discover -s tests -p test_registered_acceptance.py -v
  — 14/14 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 231/231 passed (217 existing unchanged and 14 new).
- Existing security/process tests passed unchanged, including shell-free invocation.
- Approved escalation allowed existing HTTP regression tests to bind loopback.
- Frozen evaluation files have no diff; no Day-5/Day-6 evaluation was rerun.
- All prior work-log bytes and historical prefixes preserved exactly.

### Boundary and limitations

Trusted association is not mathematical proof of coverage. Identity covers the
current grounded representation, not omitted planner behavior; the caller must
review the full intended requirement before authorizing. No observation authenticity,
repository snapshot, source freshness, or reviewer/digest mechanism is claimed.
A same-ID code change is not detected by this association. Tests and registry inputs
remain trusted executable/configuration data. No planner/grounder/API integration,
legacy allowlist change, HTTP semantic change, or frozen-artifact modification.


## 27. 2026-09-28 — Fresh registered-check acceptance smoke validation

### Purpose and methodology

Created evaluation/registered_check_smoke/ with a minimal document archive fixture,
explicit requirements, two unittest acceptance checks, checks.json, scenarios.json,
trusted authorizations.json, and run_smoke.py. All fixture inputs and requirements
were written before the first execution and were not changed after observing it.
The controlled implementation sets archived to true but deliberately retains editable.
This fixture is outside sample_app and separate from Day-5/Day-6 historical inputs.

The harness calls only the actual run_acceptance integration to obtain results;
it does not invoke the verifier directly or calculate verdicts. First returned
results are preserved in result.json; the harness refuses to overwrite them.

### First execution and evidence

Executed once: python3 -B -m evaluation.registered_check_smoke.run_smoke.
The first run completed without infrastructure failure or repair.

- document.archive_flag / document.archive_flag.v1: authorization matched;
  status success, tests_run=1, failures=0, errors=0, skips=0; verdict PASS.
- document.archive_readonly / document.archive_readonly.v1: authorization matched;
  status assertion_failure, tests_run=1, failures=1, errors=0, skips=0; verdict FAIL.
- Both runner processes returned 0, reporting their distinct test outcomes through
  the private structured channel. Neither timed out or truncated output.
- Overall deterministic acceptance verdict: FAIL.

Scenario identities and coverage provenance are preserved alongside counts and
statuses. No stdout parsing or manually assigned verdicts were used.

### Regression and limitations

After preserving the smoke result, ran separately:
python3 -m unittest discover -s tests -p 'test_*.py' -v — 231/231 passed.
Approved escalation allowed existing HTTP regression tests to bind loopback.
The smoke assertions are not counted as regression tests.

This is controlled trusted-check execution validation, not autonomous missing-test
invention, autonomous bug discovery, arbitrary repository support, semantic
completeness, secure sandboxing, proof of correctness, or independent benchmark
success. The acceptance tests and exact scenario associations were explicitly
trusted for this smoke exercise. No implementation tuning or repeated smoke run
occurred. Day-5/Day-6 artifacts have no diff and were not rerun. No production code
changed. Historical work-log prefixes and all prior bytes are preserved exactly.


## 28. 2026-09-28 — JSON existence and primitive-type assertions

### Changes and semantics

- Added exact json_exists {type, path} and json_type {type, path, equals} HTTP
  assertion schemas. New paths use existing dictionary-only dotted-path rules,
  with a 32000-character bound for these new forms. Legacy schemas are unchanged.
- json_exists observes presence, including explicit null. Missing paths or a
  non-object intermediate produce FAIL only with valid available JSON. Unavailable,
  invalid, or policy-rejected JSON and unusable HTTP observations yield UNVERIFIED.
- json_type accepts string, number, integer, boolean, null only. Integer includes
  integral finite floats; number includes finite integer/fractional values; boolean
  is distinct from both. These are parsed-value semantics, not lexical token
  validation, and retain existing parser precision limitations.
- Present wrong types yield FAIL; missing paths/non-object intermediates yield
  UNVERIFIED for json_type. Objects/arrays are reportable observed types but are
  not permitted expected types. json_field missing-path behavior is unchanged.
- New evidence records presence or semantic type without selected values. Paths
  are bounded to 512 evidence characters with truncation flags; comparison/traversal
  uses the full validated path. HTTP transport, duplicate-key rejection, JSON
  bounds, status evidence, aggregation, registered checks, planner, and grounding
  behavior are unchanged. No composite scenarios added.

### Tests and results

Added 12 tests in tests/test_json_shape_assertions.py with parameterized coverage
of null/presence, missing and non-object paths, the primitive type matrix including
booleans and integral floats, unavailable/invalid/oversized JSON, exact schema keys,
invalid expected types, path limits, bounded non-disclosing evidence, combined
assertion precedence, legacy equality/status behavior, and duplicate-key policy.

- Focused: python3 -B -m unittest discover -s tests -p test_json_shape_assertions.py -v
  — 12/12 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 243/243 passed (231 existing unchanged and 12 new).
- Approved escalation allowed existing HTTP regression loopback tests.
- No evaluation directory diff: Day-5, Day-6, and registered-check smoke artifacts
  remain unchanged and were not rerun. All historical log prefixes were verified
  and every pre-existing byte preserved before this append.


## 29. 2026-09-28 — Bounded composite schema and pure aggregation

### Changes

- Added strict composite parent fields: name, source, reason, behavior, action.
  Action contains exactly type=composite and children. No parent assertions or
  variables; behavior remains unnecessary on existing standalone forms.
- Each parent has 2–3 independent required children with unique nonblank labels
  of at most 64 characters. Only HTTP and unsupported actions are permitted.
  Nesting, registered-check/test-command children, optional/retry/workflow fields,
  child identity/source/reason/behavior/variables, and extra authority are rejected.
- HTTP children reuse unchanged standalone HTTP validation and all four assertion
  forms. They allow at most 8 assertions. Unsupported children forbid assertions.
  Compact serialization with ensure_ascii=False is limited to 32000 UTF-8 bytes;
  cyclic/non-JSON/nonfinite payloads are rejected. No truncation occurs.
- Added aggregate_composite_results(scenario, child_results) in verifier.py.
  Exact ordered label/verdict records must match every validated required child.
  Malformed, missing, duplicated, unexpected, reordered, or unknown-verdict
  results raise ValueError. Any FAIL dominates; otherwise any UNVERIFIED dominates;
  only all-PASS produces PASS. No execution, I/O, or semantic coverage claim.
- Existing five-parent limit is unchanged, allowing at most 15 leaves once future
  composite execution exists. No acceptance dispatch or grounding changes were
  made: schema representation and aggregation are available, execution is not.

### Tests and results

Added 14 tests in tests/test_composites.py covering valid 2/3-child structures,
unsupported children, count/label/assertion/byte bounds, forbidden actions/fields,
non-JSON/cyclic payloads, exact parent shapes, all verdict combinations, result
identity/cardinality validation, nonmutation, and pure aggregation without I/O.

- Focused: python3 -B -m unittest discover -s tests -p test_composites.py -v
  — 14/14 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 257/257 passed (243 existing unchanged and 14 new).
- Approved escalation allowed existing HTTP regression loopback tests.
- Existing standalone HTTP, registered, test-command, unsupported and JSON
  assertion behavior remains unchanged. No frozen evaluation diff: Day-5, Day-6,
  and registered-check smoke artifacts are untouched and were not rerun.
- Historical work-log versions were checked as prefixes; all prior bytes remain
  unchanged. No composite execution, grounder emission support, state transfer,
  or new registered-check capability was implemented.


## 30. 2026-09-28 — Bounded composite execution and nested evidence

### Changes

- run_acceptance now dispatches composite parents. It validates all top-level
  scenarios/children before side effects, deep-copies the collection, and validates
  the internal snapshot. Caller mutations during execution cannot change its child
  set. Concurrent mutation during copying is outside the supported contract.
- HTTP children use execute_http_scenario and its existing verifier; unsupported
  children use the existing no-execution verifier normalization. All required
  children are processed once in declared order, including children after a FAIL.
  Missing HTTP configuration yields UNVERIFIED safely. No retries or early verdict
  short-circuiting. Unexpected programming errors still propagate.
- Parent verdicts delegate to aggregate_composite_results with exact ordered
  label/verdict records. No HTTP verdict logic or parent precedence is duplicated.
  The unchanged top-level aggregation consumes only each parent's verdict.
- Each parent retains one execution/observation/result envelope. Parent observation
  is None; result preserves name/source/reason/behavior, verdict, empty assertions,
  child_counts, and ordered children. Each child has its exact label and existing
  leaf envelope once. Raw JSON is not duplicated at the parent level; no logs or
  percentage coverage scores are introduced.
- No workflow/state/output propagation, isolation guarantee, reset, or HTTP lifecycle
  added. Existing 2–3 child and five-parent bounds remain. Registered/test-command
  children and nesting remain forbidden. Grounding remains unchanged and has not
  been taught to emit composites.

### Tests and results

Added 12 tests in tests/test_composite_execution.py using a local controlled HTTP
fixture: 2/3 children passing, partial and failed evidence, every-child order/count,
continuation after failure, unsupported/missing-target outcomes, nested evidence,
nonmutation and caller mutation resistance, all-input prevalidation, top-level
aggregation, parent-helper delegation, unknown verdict rejection, and exception
propagation without retries.

- Focused: python3 -B -m unittest discover -s tests -p test_composite_execution.py -v
  — 12/12 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 269/269 passed (257 existing unchanged and 12 new).
- Approved escalation allowed the local loopback tests to bind.
- Standalone/registered execution, authorization, HTTP semantics, and grounding
  files remain unchanged. Frozen Day-5/Day-6/smoke artifacts have no diff and were
  not rerun. All prior CODEX.md bytes and historical prefixes are preserved.

### Limitations

Sequential independent observations do not prove state isolation or complete
semantic coverage. The existing per-child HTTP bounds apply, and nested reports
retain each executor's bounded observation; parsed JSON may contain sensitive data.
No grounder integration or broader child capabilities were introduced.


## 31. 2026-09-28 — Conservative composite grounding support

### Changes and compatibility constraint

- Extended grounding-provider instructions to permit one planner scenario to become
  one composite with 2–3 required independent HTTP/unsupported children. Parent
  name/source/reason/order remain exact; composite behavior is additionally checked
  against the defensive planner baseline. No splitting/merging top-level scenarios.
- Applied the user's explicit compatibility exception: composite parents retain
  behavior, while legacy standalone grounded result shapes remain unchanged.
  No standalone behavior field, parallel metadata wrapper, or schema migration.
- Documented json_exists/json_type with evidence-backed response shape and existing
  dotted dictionary-only paths. Composite expressiveness does not authorize guessed
  endpoints, request values, identifiers, headers, expected values, or capabilities.
- Instructions require complete decomposition of the same behavior, never omission
  to fit the three-child limit. Missing evidence remains unsupported; an unsupported
  child must represent a genuinely required part alongside executable independent
  observations, never filler. Unrepresentable parents remain wholly unsupported.
- Explicitly prohibit workflows, output chaining, cookies/session propagation,
  state-continuity assumptions, retries, branches, loops, setup/teardown, speculative
  interpretations, and unrelated/new child requirements. No nesting or registered/
  test-command children. Existing schema enforces structural restrictions unchanged.
- Provider still called once; malformed output fails without repair/retry. No
  execution, filesystem/network/API access, semantic keyword heuristics, or second
  planning layer was added.

### Tests and results

Added 14 tests in tests/test_composite_grounding.py covering 2/3-child composites,
exact identity including behavior, child/top-level ordering, split/merge rejection,
byte-compatible standalone shapes, insufficient-evidence/ambiguity forwarding,
unsupported children, new assertion validation, action/count/label/size restrictions,
workflow-field rejection, conservative instructions, defensive copies/no I/O, and
invalid-output rejection without retry.

- Focused: python3 -B -m unittest discover -s tests -p test_composite_grounding.py -v
  — 14/14 passed.
- Full: python3 -m unittest discover -s tests -p 'test_*.py' -v
  — 283/283 passed (269 existing unchanged and 14 new).
- Approved escalation allowed existing regression HTTP loopback tests.
- Execution, verifier, schema, registered execution/authorization, and HTTP files
  have no diff. Day-5/Day-6/smoke artifacts are untouched and were not rerun.
- All previous CODEX.md bytes and historical prefixes remain preserved exactly.

### Limitations

Fake-provider tests establish contract/validation behavior, not real-model evidence
support or semantic completeness. Prose-level workflow dependence, unrelated child
intent, and completeness remain provider obligations; no semantic validator is
claimed. Composite PASS establishes only that all represented frozen required
children passed. Historical Day-6 remains 0 PASS / 0 FAIL / 21 UNVERIFIED.
No fresh evaluation set or model API integration was started.


## 32. 2026-09-28 — Evaluation Set 2 protocol freeze

### Scope and methodology

- Created evaluation/evaluation_set_2_protocol.md, freezing the primary/secondary
  questions, exactly five fresh case categories, excluded prior domains, ordered
  artifact freezes, information boundaries, and first-valid-output policy.
- No target verdict distribution or success rate. One provider attempt per stage
  per case; malformed outputs stop the affected case without retries. Preserve
  negative results and stopped cases. Existing-conversation reasoning is not an
  independently blinded evaluation.
- Defined separate planner, grounding, and execution metrics, denominator rules,
  postmortem categories, FAIL attribution, integrity rules, and stop conditions.
- Documented the registered-check constraint: current grounding instructions do
  not advertise check selection, and trusted authorization requires an exact
  scenario identity frozen before reasoning. No post-hoc authorization, model
  trust assignment, prompt expansion, or forced executable output is permitted.
- Historical Day-6 remains 21 scenarios: 0 PASS / 0 FAIL / 21 UNVERIFIED.
  Future cross-set comparison is descriptive, not an accuracy improvement claim.

### Verification and boundary

Only the new protocol and this appended entry changed. All previous work-log bytes
and historical prefixes were preserved exactly. No fixtures, task repositories,
reasoning outputs, or execution results were created. No production code or tests
changed. Day-5, Day-6, and registered-check smoke artifacts remain untouched and
were not rerun. Regression tests were not rerun for this documentation-only change;
the recorded baseline remains 283/283. No evaluation result is claimed.


## 33. 2026-09-28 — Evaluation Set 2 fixture freeze

### Fixtures and methodology

Created evaluation/set2/ with exactly five fresh case directories, each containing
separate task/context artifacts, a small Python repository, and ordinary tests:
1. Coffee roast temperature — inclusive boundary.
2. Parcel label preview — multiple related observable properties.
3. Weekly hourly pay — repository-local registered check.
4. Tournament standings — product ambiguity concerning tied scores.
5. Arithmetic practice attempts — stateful submission and result retrieval.

Shared http_server.py provides a standard-library loopback JSON adapter for four
repositories. No dependencies, external services, injected defects, or target
verdict distribution. fixture_manifest.md records commands, results, bounded
contexts, file hashes, provenance, and the freeze commit identifier convention.

Case 3 includes acceptance_checks.py and checks.json with check payroll.weekly_gross
and coverage payroll.weekly_gross.v1. Strict registry validation passed without
executing the check. Exact scenario authorization remains pending/unavailable;
no future grounded identity or authorization artifact was invented.

Case 3's trusted registered check and registry metadata were authored by Codex during the explicitly authorized pre-reasoning fixture-construction phase. They were frozen before AgentGuard planner/grounder reasoning. Therefore this evaluates the registered-check trust architecture under role-separated setup; it does not demonstrate independently human-authored acceptance coverage.

The user's clarification is recorded without modifying the protocol. Reasoning
roles cannot subsequently modify or self-authorize any frozen trusted setup.

### Tests and audit

For each repository, ran once:
python3 -B -m unittest discover -s . -p 'test_app.py' -v
Each of the five suites: 3/3 passed, exit 0 (15 total). Exact cwd commands are in
the manifest. No subsequent implementation/test repairs. The registered check
was not executed and is not counted as an implementation test.

Separate existing regression:
python3 -m unittest discover -s tests -p 'test_*.py' -v
283/283 passed, exit 0. Approved escalation enabled existing loopback tests.
New Python files parsed; contexts match source and remain below 32,000 characters.
Keyword search and manual review of comments/test names found no outcome leakage
in planner-visible materials. Administrative methodology is kept in the manifest.

### Boundaries

No Evaluation Set 2 planner/grounder reasoning, scenario artifacts, or acceptance
execution occurred. No production AgentGuard code, existing tests, sample app,
frozen protocol, Day-5, Day-6, or registered-check smoke artifacts changed; historical
evaluation harnesses were not rerun. All previous work-log bytes and historical
prefixes are preserved exactly. No AgentGuard evaluation result is claimed.


## 34. 2026-09-28 — Evaluation Set 2 planner freeze

### Method and artifacts

Created evaluation/set2/planner/ with exact first provider responses, byte-identical
validated outputs for all five cases, stage_manifest.json, and a planner-only
qualitative review. Codex acted as the manual injected reasoning provider for the
unchanged plan_acceptance(). Each callable received only existing instructions and
the case's frozen task/context. Exactly one response and validation call per case;
all valid, none stopped, no retries, repairs, or regeneration.

Input paths/hashes and exact instructions/hash are preserved. Existing-conversation
reasoning is not independently blinded: Codex retains prior project/fixture context.
No external model API call or independent authorship claim is made.

### Planner metrics and observations

Each case produced four scenarios. Total: 20 scenarios, 18 explicit, 2 inferred,
4 ambiguity entries. Per-case explicit/inferred/ambiguities:
01: 4/0/1; 02: 3/1/0; 03: 4/0/0; 04: 3/1/1; 05: 4/0/2.

Outputs retain task behavior including equipment/postage side-effect prohibitions,
pay calculation, entrant completeness, and answer retrieval/isolation. Integral
numeric representation, tied-score policy, and repeat/pre-submission answer behavior
remain unresolved. Tournament has no concrete tied-policy scenario. Inferred label
input validation and preview-input nonmutation are context-supported proposals,
not explicit product mandates; the review flags nonmutation's dependence on current
source behavior. No unsupported decision was identified as an explicit requirement.
Outputs remain unchanged after review; no numeric quality score was assigned.

### Integrity and boundaries

Frozen fixture/protocol bytes match 7c2ab34 before and after artifact creation.
Case-3 check/registry and all production code/tests remain unchanged. No Set-2
grounding, action schemas, acceptance execution, check selection, authorization,
registered-check execution, or fixture test rerun occurred. Historical Day-5,
Day-6 and smoke artifacts were untouched and not rerun. Regression tests were not
rerun; the recorded baseline remains 283/283. All previous work-log bytes and
historical prefixes are preserved exactly. No acceptance result is claimed.


## 35. 2026-09-28 — Evaluation Set 2 grounding freeze

### Method and artifacts

Created evaluation/set2/grounding/ with first provider responses, byte-identical
validated outputs, stage_manifest.json and review.md. Codex supplied one manual
injected response per case to unchanged ground_scenarios(). All five structurally
valid; none stopped, repaired, retried or regenerated. Inputs were only each frozen
planner output and context plus existing instructions. Exact input/instruction
hashes and attempts are recorded. Existing-conversation reasoning is not
independently blinded; prior project context remains a methodology limitation.

### Representation metrics

20 top-level scenarios: 2 standalone HTTP, 0 test-command, 0 registered-check,
1 composite, 17 unsupported. The composite has 3 children: 2 HTTP and 1 unsupported.
Across all leaves: 4 executable and 18 unsupported. Per-case HTTP/composite/unsupported:
01: 1/1/2; 02: 0/0/4; 03: 0/0/4; 04: 0/0/4; 05: 1/0/3.
3/20 (15%) have an executable observation; 17/20 (85%) are wholly unsupported.
These are representation executability metrics, not correctness or coverage scores.

### Qualitative observations

Executable details are visible in supplied context. Temperature endpoints remain
independent and creation uses documented response fields without predicting an ID.
The temperature composite's unsupported remainder raises a semantic concern: its
explanation invokes the child bound, while instructions require whole-parent
unsupported if faithful decomposition needs more than three observations. Structural
validation does not resolve this concern; the first response is preserved unchanged.
The exact practice question assertion is context-supported but fixture-specific,
not a general product question-selection requirement. Review records this limitation.

Text-input evidence, absent observables, arrays and caller-owned object observation
produce conservative unsupported representations. Ambiguities remain unresolved;
stateful retrieval/isolation are not encoded as independent workflows. Both inferred
scenarios retain evidence standards. Nonmutation belongs to the frozen Tournament
planner, despite the request referring to Parcel Label; no identity was rewritten.
Case 3 does not select a registered action under the existing grounding instructions;
exact authorization remains unavailable and no trust or registry change was made.

### Integrity and boundaries

Frozen fixture/planner/protocol bytes match 7197b14 before and after creation.
Production code/tests and historical Day-5/Day-6/smoke artifacts are unchanged.
No acceptance execution, fixture server, registered check, test rerun, or historical
harness ran; no acceptance result artifact was created. Regression was not rerun;
recorded baseline remains 283/283. All previous CODEX.md bytes and historical
prefixes are preserved exactly. No runtime acceptance results are claimed.


## 36. 2026-09-28 — Evaluation Set 2 execution result freeze

### Execution and preservation

Created evaluation/set2/execution/ with a one-shot harness, exclusive run marker,
exact complete per-case results, lifecycle records, input/result hashes, manifest,
mechanical metrics and summary. Each of five cases received exactly one unchanged
run_acceptance call; all completed, none stopped or retried. Results were serialized
and hashed before metrics or interpretation. No scenario repair or regeneration.

### Deterministic results

Top-level PASS/FAIL/UNVERIFIED by case:
01 roast: 1/0/3; 02 label: 0/0/4; 03 payroll: 0/0/4;
04 tournament: 0/0/4; 05 practice: 1/0/3.
Total across 20: 2 PASS, 0 FAIL, 18 UNVERIFIED. Every case overall UNVERIFIED.
Composite children separately: 2 PASS, 0 FAIL, 1 UNVERIFIED; parent UNVERIFIED.
All required children and original evidence/order/counts are retained.
Registered-check execution count: zero. No coverage authorization was created.

Roast and practice existing application_server context managers started and shut
down successfully on numeric loopback ports 50066 and 50070. Other cases needed no
server. Approved escalation permitted local binding; no infrastructure errors.
No fixture modifications or generated fixture artifacts required cleanup.

The previously flagged composite issue was not repaired: its unsupported child
remains and determines parent UNVERIFIED. The frozen practice question assertion
matched '7 + 5' and did not cause a contradiction. These observations do not settle
the grounding concerns or establish semantic correctness. Full postmortem deferred.

### Validation and boundaries

After result preservation, the unchanged regression command
python3 -m unittest discover -s tests -p 'test_*.py' -v
completed 283/283, OK, exit 0. It is separate from acceptance evidence.

All frozen Set-2/protocol bytes match 66b4de6 before execution and after shutdown.
Production code/tests, fixtures, planner/grounding artifacts, Case-3 check/registry
and historical Day-5/Day-6/smoke artifacts are unchanged. No implementation-test or
historical evaluation rerun occurred. Prior CODEX.md bytes and historical prefixes
remain preserved exactly. Results are bounded observed evidence, not a benchmark
accuracy or semantic completeness claim.


## 37. 2026-09-28 — Evaluation Set 2 formal postmortem

Created evaluation/set2/postmortem/classifications.json, summary.md and next_steps.md.
Exactly 18 top-level UNVERIFIED records: CONTEXT_EVIDENCE_GAP 9,
SCHEMA_CAPABILITY_GAP 7, REGISTERED_COVERAGE_GAP 2; all other frozen categories 0.
Primary causes are counted once; secondary ambiguities/limitations remain separate.
No planner, grounder, acceptance, fixture or test reruns; no repairs or verdict changes.

Context/synthetic-value restrictions and schema expressiveness dominate. Payroll
regular/overtime and zero have directly relevant registered metadata but no legitimate
binding. Invalid-input and separate no-tax coverage are not established by supplied
metadata; enabling selection alone does not prove them. No executor-policy block or
infrastructure failure was observed. Strict evidence policy is not labelled a grounder
mistake merely because a human could invent sample inputs.

Two top-level PASS results retain their narrow runtime evidence: temperature 160/C
and practice creation with string id/question, including json_exists/json_type.
Composite children remain 2 PASS / 0 FAIL / 1 UNVERIFIED, parent UNVERIFIED.
Aggregation was correct; the accepted structural shape does not resolve the possible
semantic-contract violation concerning its unsupported remaining-range child.
Exact practice question equality remains fixture-specific. No result was repaired.

Day 6 remains 0/0/21 and Set 2 remains 2/0/18 (PASS/FAIL/UNVERIFIED).
Fresh cases demonstrated some executable observations; different datasets and
architecture preclude accuracy or general-improvement claims.

Candidates considered: bounded synthetic inputs, trusted registered binding, arrays,
stateful workflows and semantic grounding validation. Recommend at most one final
architecture improvement: bounded provenance-recorded derived/synthetic test values,
without inventing repository facts, authorization, identifiers or state guarantees.
Then prioritize LLM provider integration, CLI, coherent demo, README, trust-boundary
diagram, technical report and presentation. No implementation was started.

After classifications were written, consistent read-only fixture/test inspection found
no clear task/implementation contradiction. Concrete tests and source observations
are explicitly labelled POST-HOC FIXTURE FINDINGS — NOT AGENTGUARD-DETECTED FAILURES.
This is neither proof of correctness nor newly detected acceptance evidence.

All frozen evaluation bytes match 0160faa before and after analysis. Production/tests,
protocol, fixtures, planner/grounding/results and historical artifacts are unchanged.
All prior log bytes/historical prefixes are preserved. Regression was not rerun;
recorded baseline remains 283/283. Existing-conversation/fixture-author methodology
is not independently blinded, and trusted setup is not independently human-authored.


## 38. 2026-09-28 — Bounded provenance-recorded input derivations

### Starting point and trust boundary

Started clean on feature/acceptance-mvp at 3c9a0518f12120eaffe37a353b75a5e5374f9e55.
Motivated by frozen Set-2 input-evidence restrictions; no evaluation was repaired.
Added agentguard/derivations.py with immutable InputConstraint and DerivationPolicy
records, a deterministic derive function, provenance consistency validation and
provider-request materialization. A separate trusted caller reviews source meaning
and excludes identity/domain/state-dependent fields. The policy binds exact context
SHA-256, source quotation, method/path and top-level JSON field. Model-emitted policy
JSON is not authority. Context hashes and quotes do not prove semantic truth.

Allowed rules: below_inclusive_lower_bound, above_inclusive_upper_bound,
blank_string, whitespace_string, wrong_primitive_type, neutral_nonblank_text.
Arithmetic uses inclusive integers only, bounded along with results to ±(2**31-1).
Blank and whitespace return empty text / three ASCII spaces; neutral text is exactly
agentguard-test, only for reviewed arbitrary nonblank text. Fixed incompatible
primitive representatives: string agentguard-test, integer 0, number 0.5, boolean
false, null. Integer is compatible with number; 0.5 is incompatible with integer.
At most 32 reviewed constraints and 8 derivations per HTTP action. Quotes are bounded
to 512 characters, field/fact IDs to 128, concrete paths to 2048.

Forbidden: invented existing/absent IDs, resource references, users/auth/credentials,
enums or domain/format-specific values, filenames/filesystem state, secrets, paths,
methods/endpoints, headers, expected responses, business/tie policy, state continuity,
output chaining, commands, test coverage and registered authorization. No fresh-ID
rule. Caller review must not mislabel those fields as ordinary scalar/text inputs.

### Grounding, provenance and execution

Extended ground_scenarios with optional derivation_policy. The provider gets copied
facts and may request exact field/rule/fact_id (plus representative for wrong type).
It cannot supply a source bound, concrete value, replacement fact or finished
provenance. Concrete JSON fields must be omitted until deterministic construction;
collisions, unknown rules, malformed requests and unavailable justification produce
unsupported leaves without retry. Invalid/stale caller policy fails before provider
invocation. Existing non-derived shapes and identity/order validation remain intact.

HTTP actions may retain derivations records: kind, rule, field, fact_id, constraint,
context_sha256, value, plus source_value for arithmetic / representative for type
substitution. Schema checks generated arithmetic/types/target/body consistency.
The existing HTTP executor sends only concrete JSON and copies provenance into
execution.input_derivations; acceptance preserves it on unavailable target config.
Composite children keep their existing evidence envelopes. Provenance is descriptive,
not an authorization token, and never counts as application observation. The verifier,
HTTP safety policy, aggregation, registered trust and workflow semantics are unchanged.

Changed files: agentguard/derivations.py (new), agentguard/grounding.py,
agentguard/scenarios.py, agentguard/http_execution.py, agentguard/acceptance.py,
tests/test_derivations.py (new), README.md, and this appended log entry.

### Tests and results

Added 21 focused tests for all six rules, primitive compatibility, integer bounds
and overflow, forbidden semantic classes/rules/targets, nonblank justification,
immutable bounded policy, stale context/absent quotation, provider authority/value
injection, collisions/duplicates/count bounds, provenance tampering, defensive copies,
legacy shapes, composite propagation, no-observation behavior and real HTTP delivery.
The HTTP test confirms amount=9 is transmitted and verifies observed PASS, FAIL and
policy-rejected UNVERIFIED without assigning verdicts from provenance.

python3 -B -m unittest discover -s tests -p test_derivations.py -v
21/21 passed with approved loopback escalation. The initial sandbox run had 20 passing
tests and a loopback-bind PermissionError; no application assertion failure occurred.

python3 -m unittest discover -s tests -p 'test_*.py' -v
304/304 passed (283 existing unchanged plus 21 new), exit 0. Approved escalation
allowed local loopback tests. No dependencies or external services were added.

### Limitations and integrity

Trusted source review is required; no automatic constraint extraction, semantic
proof, source freshness beyond supplied context, or credential/domain inference is
claimed. Serialized provenance is not authenticated, and direct callers can already
supply concrete JSON without grounding. This feature does not authorize such callers
or establish correctness. Reviewed quotations/fixed generated values are reportable;
callers must use non-sensitive constraint text. Expected assertions and behavioral
completeness remain grounding obligations, not derivation guarantees.

All frozen evaluation bytes remain unchanged, including Set 2/postmortem, Day-5,
Day-6 and smoke artifacts. None were rerun; no retrospective score is claimed.
No arrays, workflows, registered binding or Evaluation Set 3 was started. All prior
CODEX.md bytes and historical prefixes are preserved exactly.


## 39. 2026-09-28 — Evaluation Set 3 protocol and specification freeze

Created evaluation/set3/protocol.md, manifest.json, leakage_review.md and five
cases/<id>/spec.md files: profile display name, shipping weight quote, catalog lookup,
promo preview and notification preferences. This is the final planned fresh
architecture evaluation before core freeze/productization, evaluating 0e50d12.
No fixtures, task/context implementations, reasoning outputs or execution exist yet.

Frozen stages: protocol/specs, fixture/setup freeze, one planner attempt/freeze,
one grounding attempt/freeze, one execution/result freeze, then postmortem. Malformed
provider output stops the case; no retries or between-stage repairs. Existing-context
reasoning is not independently blinded. Caller-reviewed derivation policies must be
frozen with future fixture setup before reasoning, separate from model authority.
No new capabilities or policy tuning based on outcomes are permitted.

Metrics cover planner sources, grounded actions, actually attemptable observation
counts/proportions, derivation requests accepted/rejected by rule, top-level and
case verdicts, separate child verdicts and infrastructure failures. Exact Set-2
taxonomy is retained for post-result diagnosis. No desired percentage, executable
count or verdict distribution is encoded. Historical comparisons are descriptive.

Pre-freeze leakage review found no expected scenarios/verdicts or hidden behavior.
Concrete weight/tariff/promotion values are product rules; no example display name
was inserted for grounding. Arrays, state preservation and side-effect requirements
remain; cases were not weakened to fit current assertions. Domains are user-selected
and new implementations are required, with historical subject overlap disclosed.

Only new Set-3 protocol/specification artifacts and this append-only entry changed.
Set 2, historical evaluations, production code/tests and derivation implementation
are unchanged. No fixture, planner, grounder, acceptance or test execution occurred.
Regression was not rerun; recorded baseline remains 304/304. All prior work-log bytes
and historical prefixes are preserved. Separate README credits request is deferred
to respect this checkpoint's explicit artifact-only commit scope.


## 40. 2026-09-28 — Evaluation Set 3 fixture freeze

Implemented five fresh deterministic standard-library repositories from frozen
protocol/spec checkpoint fa4193c, evaluating unchanged architecture 0e50d12.
Profile stores normalized names; shipping quotes integer grams with the stated
tariff; catalog preserves collection filtering/order/fields; promotion previews
LOCAL10 without committing purchases; preferences applies validated atomic patches
while preserving omitted channels and digest hour. Stateful applications retain
caller-owned records. Shared local transport provides ordinary JSON HTTP interfaces.

Added task.md copies byte-identical to specs, bounded context.md, app/server/interface
and README files, ordinary core/transport tests, plus separate pre-reasoning trusted
policy JSON for each case. Five reviewed constraints total: profile text, weight,
subtotal and two boolean channels. Catalog policy is empty; promo-code and lookup
identity semantics are not authorized for generation. Policy objects/context binding
were validated without derivation calls. Codex authored the caller/setup review;
independently human-authored trust or blinding is not claimed.

New fixture_manifest.json records frozen-stage metadata and hashes without modifying
the original frozen manifest. fixture_review.md documents spec fidelity, policy
review and leakage audit. Context lengths: 2546, 2108, 2627, 2550, 2705 characters.
Contexts contain ordinary interfaces/source and test commands, not test results,
scenario suggestions, derivation coaching, or invented coverage claims.

Each case ran from its repository:
python3 -B -m unittest discover -s . -p 'test_*.py' -v
01: 6/6; 02: 6/6; 03: 6/6; 04: 6/6; 05: 6/6 — all passed, total 30/30.
These include ordinary loopback transport tests, not acceptance evaluation.
No correction was needed after first suite runs. No intentional defects introduced.

Separate existing AgentGuard regression:
python3 -m unittest discover -s tests -p 'test_*.py' -v
304/304 passed, exit 0. Approved escalation enabled local loopback tests.

Keyword/manual review found no benchmark leakage; only neutral 'passes' matched the
PASS substring. Arrays, persistence, partial-update atomicity and side-effect intent
were not weakened for executability. No planner/grounder/Set-3 acceptance reasoning
or execution occurred, and no historical evaluation harness was rerun.

Only new fixture/evaluation files and this appended entry changed. All frozen Set-3
protocol/specification/original manifest bytes, Set 2/postmortem, historical artifacts,
production architecture and tests remain unchanged. All prior CODEX.md bytes and
historical prefixes are preserved exactly. No evaluation outcome is claimed.


## 41. 2026-09-28 — Evaluation Set 3 planner freeze

Protocol fa4193c, fixtures 58f8ead, architecture 0e50d12. Added evaluation/set3/planner/
with exact first provider responses, byte-identical validated outputs, stage manifest
and descriptive summary. Codex supplied one manual injected response per case to the
unchanged plan_acceptance API. All five valid; none stopped, repaired or retried.
Input/instruction/response hashes and provenance are recorded.

Per-case scenarios/explicit/inferred/ambiguities:
01 profile: 4/4/0/0; 02 shipping: 4/4/0/0; 03 catalog: 5/5/0/0;
04 promotion: 5/5/0/0; 05 preferences: 5/5/0/0.
Total 23 scenarios, 23 explicit, 0 inferred, 0 ambiguity entries; five provider calls.
Counts describe outputs, not semantic completeness or quality. No executability or
future outcome metrics were computed. Exact scenario names appear in the summary.

Reasoning used each frozen task/context and existing instructions only. Existing
project-conversation methodology is not independently blinded; prior fixture/project
context exists. No derivation policy, test result or evaluation metadata was passed
to the provider. No grounding, derived-value request, action schema, registered check,
HTTP acceptance check or acceptance execution occurred. No fixture repair.

Frozen evaluation bytes match 58f8ead before and after artifact creation, including
Set-3 specs/context/fixtures/policies/protocol, Set 2 and historical artifacts.
Production architecture, planner, derivations and existing tests are unchanged.
No regression rerun; recorded baseline remains 304/304. All prior CODEX.md bytes and
historical prefixes are preserved exactly. This checkpoint ends before grounding.


## 42. 2026-09-28 — Evaluation Set 3 grounding freeze

Preserved exact provider requests, raw first responses, compiled validated scenarios,
derivation provenance, attempt/hash metadata, metrics and post-freeze read-only review
under evaluation/set3/grounding/. Protocol fa4193c, fixtures 58f8ead and planner 9e88f5e
remain frozen; architecture is 0e50d12. Codex acted as a manual injected provider in
this existing conversation, not an independently blinded or external-API evaluation.
Each case used its frozen planner/context and separately frozen caller policy through
the unchanged ground_scenarios API exactly once. All five responses validated on the
first attempt; all 23 scenario identities/order and composite behaviors are preserved.
No retries, repairs, planner regeneration or semantic tuning followed validation.

Top-level distribution: 1 HTTP, 3 composite, 19 unsupported, 0 test-command and
0 registered-check. Four of 23 planner scenarios (17.39%) have at least one potentially
executable HTTP observation. Composites contain 6 HTTP children, 0 unsupported children.
Per-case HTTP/composite/unsupported: profile 1/0/3, shipping 0/2/2, catalog 0/0/5,
promotion 0/0/5, preferences 0/1/4. Executability is not accuracy or verification.
One neutral_nonblank_text derivation was requested and accepted with compiler-generated
provenance; zero rejected. All other rules have zero requests. This does not exercise
rejection behavior. Provenance supplies inputs only, never runtime evidence or trust.

Read-only review flags the free-form label's one-sample/status-only limitation and
shipping boundary/tariff sampling as potential weakening of broad planner intent;
structural validation does not prove complete decomposition. The preferences unknown-
field category also has one representative. These concerns are preserved without
repair for postmortem. State, arrays/order, preservation, atomicity and side-effect
absence were not replaced with weaker field-presence checks. No runtime verdicts
are predicted or assigned.

No acceptance/HTTP/registered execution, fixture tests or regression runs occurred.
Recorded regression baseline remains 304/304. Every pre-existing tracked file matched
9e88f5e before this append. Protocol, fixtures, policies, planner outputs, production,
derivation implementation, Set 2 and historical artifacts remain unchanged. Historical
work-log prefixes were checked; all prior CODEX bytes are preserved exactly. Only the
new grounding artifacts and this append are included in the grounding checkpoint.


## 43. 2026-09-28 — Final Evaluation Set 3 acceptance execution

Executed the frozen b981480 grounding outputs once per case through unchanged
run_acceptance; protocol fa4193c, fixtures 58f8ead, planner 9e88f5e, architecture
0e50d12. Preserved exact returned envelopes, ordered child evidence, first-attempt
metadata, hashes, process records, regression log and read-only review under
evaluation/set3/execution/. The retained harness refuses to overwrite attempts.
Five isolated processes each made one orchestrator call. Only profile, shipping and
preferences started their existing loopback fixture servers, all closed cleanly.
No planner/grounder calls, scenario retries, repairs, state chaining or new capability.

Per-case PASS/FAIL/UNVERIFIED: profile 1/0/3, shipping 2/0/2, catalog 0/0/5,
promotion 0/0/5, preferences 1/0/4. Every case overall verdict is UNVERIFIED.
Aggregate top-level counts are 4/0/19; composite children are 6/0/0. The existing
orchestrator supplies no cross-case overall verdict, so none was invented.
Seven HTTP leaves were actually attempted and established. Infrastructure failures:
zero. Grounding executability remains 4/23 (17.39%), separate from runtime outcomes.
The single neutral-text provenance record accompanies execution metadata; it did
not provide runtime evidence or award a verdict.

Read-only review limits PASS to profile status 200 for one generated label; shipping
200 at the two inclusive bounds and asserted 600/3500 integer-cent AUD quotes;
and preference rejection of the empty object and supplied noneditable digest field.
Free-form-label generality and shipping sampling concerns remain unrepaired. All
nineteen unsupported records retain their exact inability explanations for state,
array/order, input-evidence, side-effect or decomposition limitations. No FAIL or
proof of broad correctness is claimed. This remains engineering evaluation, not
independently blinded benchmark evidence.

After acceptance, ran the full regression once:
python3 -m unittest discover -s tests -p 'test_*.py' -v
304 tests passed, OK, exit code 0; reported duration 5.673 seconds. Approved escalation
permitted local loopback binding for acceptance and regression. No failed preliminary
execution or regression retry occurred.

All pre-existing tracked bytes matched b981480 after execution/regression and before
this append. Protocol, fixtures, task/context/specs, policies, planner, grounding,
derivations, production and Set 2 remain unchanged. Historical log prefixes checked;
all earlier CODEX bytes preserved exactly. Only execution artifacts and this append
change. This completes the final Set-3 execution checkpoint; no further evaluation
or architecture work was started, and no push was performed.

## 44. 2026-09-28 — Productization: OpenAI reasoning provider

Added agentguard/providers/openai_provider.py and package marker. OpenAIProvider()
serves both unchanged injected provider boundaries, forwarding their instructions
and caller-selected evidence (plus caller derivation facts for grounding). No tools,
repository crawling, execution, verdict logic, or core-contract changes. This starts
productization after frozen Set-3 execution 1e72cf9; no evaluation was rerun.

The official SDK Responses API uses JSON mode and existing AgentGuard validators,
not a duplicated strict API schema. An API-only scenarios envelope is unwrapped
into the existing grounder list without changing entries. JSON syntax is not schema
or semantic assurance. Core validators still reject model verdict fields and changed
identities; deterministic derivation policy still compiles requested inputs.

Required OPENAI_API_KEY; optional AGENTGUARD_MODEL defaults to gpt-4.1-mini. Blank
configuration raises OpenAIProviderError. Lazy SDK import keeps core use independent
of the optional dependency. Each invocation creates/closes a client and makes one
request: SDK max_retries=0, timeout 60 seconds, max_output_tokens 8192, store=False,
fixed official API origin, decoded-text bound 262144 characters. No retries, repair,
fallback reasoning or model substitution. API failures/refusals/incomplete responses,
malformed envelopes, duplicate keys and nonfinite JSON numbers raise sanitized
provider errors. Existing core validation errors remain unchanged.

No dependency manifest previously existed. Added minimal requirements.txt with
openai>=2.0.0,<3.0.0, placeholder .env.example, secret-file ignore rules and
 docs/openai_provider.md with installation, usage and trust limitations. Main README
unchanged. Consulted official documentation using the OpenAI Docs skill. No actual
.env/credentials were created, no CLI or live smoke script was added.

Added 16 offline tests covering both request/response contracts, configuration,
malformed/refused/incomplete outputs, API error/no-retry behavior, cleanup, input
bounds/nonmutation, deterministic derivation compilation, core verdict/identity
validation and absence of execution. Focused: 16/16 passed. Full regression:
python3 -m unittest discover -s tests -p 'test_*.py' -v — 320/320 passed
(304 unchanged plus 16 new). Sample-app suite: 4/4 passed. Approved escalation let
existing HTTP regression tests bind loopback. Also installed SDK 2.54.0 in a temporary
virtual environment and checked actual SDK response parsing plus 429/no-retry behavior
using httpx.MockTransport; both passed with no API network requests. Dependency
installation required network escalation after sandbox DNS denial. No paid API calls.

All pre-existing tracked files except the intentional .gitignore addition matched
1e72cf9 before appending, including all evaluation artifacts and core code/tests.
Historical CODEX prefixes checked; every prior byte preserved. Only provider,
dependency/config/docs, new tests and this log append change. No push.
