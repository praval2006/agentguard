# Day 6 Evaluation Protocol

## Purpose and baseline

Evaluate whether the existing AgentGuard architecture remains useful on fresh,
unfamiliar tasks rather than another environment designed around the subscription
demonstration. Test the frozen architecture; do not optimize examples for
impressive outcomes. Day 5 is frozen at `600a9b6` (Record end-to-end acceptance
reasoning proof).

This checkpoint defines methodology only. It creates no concrete cases and runs
no reasoning, execution, or tests.

## Evaluation set

Create five fresh cases in the next checkpoint, one for each category:

1. Straightforward state-transition behavior.
2. Boundary/validation behavior.
3. Interaction between multiple related state fields.
4. Behavior containing a genuine product ambiguity.
5. Behavior that may exceed current execution capability.

Do not reuse the subscription example or any Day-2 planner case. Explicitly
excluded topics are subscription cancellation, password reset, cart quantity,
account deletion, session logout, email change, file upload, API pagination,
notification preferences, and resource deletion.

## Pre-registration rules

- Freeze all five task/implementation/test/context fixtures before any AgentGuard
  reasoning begins. Identify the frozen versions in the evaluation record.
- Do not require every implementation to contain a defect or intentionally choose
  only examples expected to produce FAIL. Existing implementation tests may pass
  whether the implementation is correct or incomplete.
- Once frozen, do not modify a case's task, implementation, tests, or neutral
  repository context because of AgentGuard's result.
- Use the first valid planner output and the first valid grounding output. Do not
  regenerate reasoning because a result is uninteresting.
- Record reasoning, schema, or provider failures explicitly. Do not silently
  retry until successful. The first-valid-output rule does not authorize erasing
  failed attempts; any subsequent attempt must retain the failure record and
  disclose why it occurred.
- Do not tell the reasoning provider which cases contain defects or supply an
  expected PASS, FAIL, or UNVERIFIED result.
- Produce and freeze planner output before grounding. Freeze grounding output
  before execution.
- Do not include runtime observations in planner or grounding context when they
  would reveal the behavior being evaluated. Keep implementation-test results
  and execution observations in the evaluation record, separate from neutral
  reasoning inputs.
- Unsupported execution remains UNVERIFIED; do not fabricate PASS or FAIL.
- Do not add case-specific AgentGuard capabilities after observing a result to
  improve that case.

## Existing-conversation limitation

Codex may act manually as the injected reasoning provider because AgentGuard has
no autonomous model-provider integration. Reasoning inside the existing AgentGuard
project conversation is not a fully independent blinded evaluation: the model may
possess prior project context. Keep this limitation visible in Day-6 results and
their interpretation. Do not claim independently blinded evaluation.

## Per-case evaluation record

For every case, preserve:

- Original task.
- Neutral repository context.
- Existing implementation-test result.
- Frozen planner output.
- Frozen grounding output.
- Execution result.
- Overall AgentGuard verdict.
- Planner requirement coverage.
- Whether grounding invented unsupported execution details.
- Whether verdicts were supported by actual observations.
- Whether AgentGuard exposed behavior not covered by existing tests.
- Limitations or ambiguities.

If a stage fails before producing an output or verdict, record that failure and
the unavailable downstream artifacts rather than inventing them. Review coverage
and usefulness qualitatively. Do not create numeric scores, rankings, grades, or
a leaderboard.

## Interpretation

PASS, FAIL, and UNVERIFIED are all legitimate outcomes. The number of FAIL verdicts
is not a measure of AgentGuard quality.

- PASS: supported acceptance behavior was actually observed to satisfy the
  requirement. It does not establish untested requirements or overall correctness.
- FAIL: actual execution contradicted an acceptance requirement.
- UNVERIFIED: the requirement matters, but available repository evidence or
  current execution capability cannot establish it.

Primarily assess:

1. Whether planner reasoning is relevant to the task.
2. Whether grounding is conservative and repository-supported.
3. Whether verdicts are backed by real observations.
4. Whether AgentGuard exposes useful information beyond existing implementation
   tests.

Keep unresolved product decisions visible rather than silently converting them
into acceptance requirements. Distinguish infrastructure or reasoning failures
from observed contradictions of product requirements.

## Scope freeze

During the initial five-case evaluation, do not modify:

- Planner semantics.
- Grounding semantics.
- Scenario schema.
- Verifier semantics.
- Acceptance aggregation.
- HTTP execution policy.
- Test-command allowlist.
- Existing subscription demo.
- Existing Day-5 artifacts.

Document genuine architecture limitations for later work rather than repairing
them case by case.

## Next checkpoint

Day 6B will create all five concrete evaluation fixtures before any AgentGuard
planner or grounding reasoning is run against them. All five fixtures will then
be frozen before evaluation begins. No fixtures are created in this checkpoint.
