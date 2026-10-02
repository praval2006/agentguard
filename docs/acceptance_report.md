# Acceptance Verification Report v1

`build_acceptance_report(outcome, *, task_text=None)` in
`agentguard.acceptance_report` projects the completed `resume_reviewed()` return.
It never calls a provider, planner, grounder, executor, verifier or verdict aggregator.
The reviewed workflow and its result schema remain unchanged. Legacy `verify`
continues to use its existing presentation.

## Schema

The exact top-level keys are:

- `schema`: `agentguard.acceptance-report.v1`
- `revision`: existing proposal revision
- `task`: `text` (string or null), `provenance` (`caller_supplied_unbound` or
  `not_retained_by_reviewed_workflow`)
- `discovery`: the original `explicit_requirements`, `inferred_behaviors`, `ambiguities`
- `requirement_mapping`: `state=NO_STRUCTURED_SCENARIO_LINKS`, `explanation`
- `reviews`: unchanged scenario review records: scenario_id, position, name,
  behavior, source, reason, review_state, included
- `contract`: `scenarios`, the ordered included review records
- `summary`: overall_verdict, selected_scenarios, verdict_counts (PASS/FAIL/UNVERIFIED),
  explicit_scenarios, accepted_inferred, dismissed_inferred, pending_inferred, ambiguities
- `verification`: overall_verdict, results; each entry contains scenario_id,
  position, action_type, execution, result
- `boundary`: PASS/FAIL/UNVERIFIED explanations and a limitations list

`result` preserves existing verifier evidence and verdicts. Composite children
retain labels, selected results and execution metadata, excluding observations.
Sequences retain ordered named step results and cross-comparison references/values;
execution metadata includes the attempted step prefix. Registered results preserve
coverage provenance and counts. No expected/observed value is synthesized. Evidence
truncation flags remain intact. Full responses, request bodies, headers, variables,
raw observation envelopes and logs are not exported. Selected evidence itself may
contain sensitive data; report storage remains the caller's responsibility.

## Authority and joins

The builder validates the proposal revision and compares the supplied contract to
existing deterministic review-contract construction with its supplied decisions.
It does not change those decisions. Selected review order, grounding order and
execution order are guaranteed by the reviewed workflow. Counts and exact
name/source/reason identities are checked before positional joining; results check
name/source and nested labels/order. No fuzzy matching or semantic correspondence
is inferred. Structurally inconsistent joins raise ValueError.

These checks do not authenticate input or establish semantic equality. Result
records do not contain a full grounded-scenario fingerprint; same-name/source
substitution or a coherently fabricated outcome cannot be detected. Use the trusted
completed workflow return, not independently assembled records from different runs.

Overall and individual verdicts are copied, never recomputed. Summary counts count
only selected top-level labels, not children. They do not determine the overall
verdict. PENDING and DISMISSED remain review states with no verification result.
Accepted inferred items remain inferred. Explicit items are automatically included.
Ambiguities remain separate and are not failures.

The current workflow retains neither original task text nor structured links from
requirement-list items to scenarios. Optional task text is clearly caller-supplied
and unbound to the revision; otherwise it is visibly unavailable. Planner prose is
not passed off as the original request. All requirement-list items remain visible,
including those without scenarios. Their coverage is unlinked/not established;
no item receives a fake UNVERIFIED verdict. The report cannot identify which
individual list items lack scenarios without a future authoritative mapping.

## CLI and deterministic JSON

```bash
python3 -m agentguard verify-reviewed \
  --review review.json --decisions decisions.json --context context.txt \
  --base-url http://127.0.0.1:8000 \
  --report-json acceptance-report.json
```

Optionally add `--task original-task.md` for caller-supplied task text. The existing
reviewed command still makes its normal grounding/execution calls; reporting adds
none. The terminal report is printed after the completed outcome. No live calls are
needed to build a report from an already returned Python outcome:

```python
from agentguard.acceptance_report import build_acceptance_report, report_json
report = build_acceptance_report(outcome)
text = report_json(report)
```

Serialization uses sorted keys, preserved list order, escaped ASCII, finite JSON,
a trailing newline and a 1,048,576-byte cap. Oversized reports fail instead of
silently truncating evidence. No timestamps or nondeterministic identifiers are
added. The returned report is detached from its inputs. Terminal formatting escapes
control characters and labels rationale as interpretation, not evidence.

The CLI checks for an existing report before provider creation and uses exclusive
file creation after completion to protect against races. Write/construction errors
use operational exit 3 and sanitized diagnostics. Verdict exit codes remain 0/1/2.
A write error after execution cannot undo execution and may leave a partial new
file; remove or choose a different output path after inspection. No silent retry.
No HTML/PDF export or frontend integration is provided.
