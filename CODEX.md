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
