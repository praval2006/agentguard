# Evaluation Set 2 planner-stage review

Fixture checkpoint: `7c2ab34`. Protocol checkpoint: `af01992`.
Freeze identifier: commit titled `Freeze Evaluation Set 2 planner outputs`.

## Method and provenance

Codex supplied exactly one structured response per case in the existing project
conversation. A manual injected callable returned that response to the unchanged
plan_acceptance() function. Each response was saved before validation, then saved
as validated output immediately on success. Provider response and validated output
files are byte-identical. No repair, regeneration, retry, external model API call,
or second provider attempt occurred. Structural validation establishes shape only.

This is NOT an independently blinded model evaluation. Codex has prior project and
fixture-authoring context. For this stage, reasoning evidence was limited to each
case's frozen task.md and context.md; prior knowledge is not additional evidence.
The administrative protocol and fixture integrity checks were not passed as planner
inputs. Input references and SHA-256 hashes, exact planner instructions and their
hash, provider provenance, attempt counts, and validation status are recorded in
stage_manifest.json. No fixture manifest, test results, evaluation categories, or
other repository source was included in the injected request.

## Planner metrics

| Case | Scenarios | Explicit | Inferred | Ambiguity entries | Attempts | Validation |
|---|---:|---:|---:|---:|---:|---|
| 01_roast_temperature | 4 | 4 | 0 | 1 | 1 | valid |
| 02_parcel_label | 4 | 3 | 1 | 0 | 1 | valid |
| 03_payroll | 4 | 4 | 0 | 0 | 1 | valid |
| 04_tournament | 4 | 3 | 1 | 1 | 1 | valid |
| 05_quiz_attempt | 4 | 4 | 0 | 2 | 1 | valid |
| Total | 20 | 18 | 2 | 4 | 5 | all valid |

All five cases completed; none stopped. Counts describe the frozen outputs, not a
numeric quality score. Ambiguity counts count list entries, not their example
interpretations. No grounding executability or acceptance metrics were calculated.

## Qualitative review against task/context only

- Roast temperature: captures inclusive acceptance, returned unit/value, rejection,
  and lack of equipment effects. Separates integral decimal representation from
  the explicit numeric range rather than letting the source's integer type check
  settle the product question.
- Parcel label: keeps the requested label transformations together and retains the
  prohibition on purchasing postage. The additional rejection of absent/non-text
  fields is directly supported by contextual validation and labelled inferred.
  It is a proposed input-validation expectation, not an explicit task statement.
- Payroll: reflects the stated regular/overtime formula, zero hours, input domain,
  and gross-pay constraint. Zero and no-tax scenarios overlap the general formula
  but remain separate in the frozen output. Contextual registry metadata is not
  converted into an execution selection or trust decision.
- Tournament: retains entrant completeness, descending points and empty behavior.
  Tie fairness is recorded as an explicit requirement and unresolved ambiguity,
  but no concrete tied-score policy scenario is supplied. This limits concrete
  treatment of that requirement without silently choosing a policy. Preview-input
  nonmutation is a context-supported inference, not a stated product requirement;
  it relies partly on the copied-record implementation and deserves reviewer
  scrutiny as a proposed expectation rather than mandatory product policy.
- Arithmetic practice: preserves attempt creation, submission followed by retrieval,
  answer isolation and unknown-attempt behavior. Correctness relates to the question
  rather than assuming a new question-selection policy. Repeat submissions and
  pre-submission presentation remain unresolved instead of copying current behavior
  into requirements.

No unsupported product decision was identified as an explicit requirement in this
review. The two inferred expectations are grounded in context but are not independent
product mandates; their classification and the nonmutation caveat remain visible.
No frozen response was edited on account of this review. No claims about runtime
behavior, future representation, or acceptance outcomes are made.

## Integrity and boundaries

Before reasoning, every file in the frozen Set-2 tree and the protocol was compared
byte-for-byte with fixture checkpoint 7c2ab34. They matched. After artifact creation,
those frozen files were checked again unchanged. Production code/tests, Case-3
check and registry, shared fixture adapter, fixture manifest, and historical Day-5,
Day-6 and registered-check smoke artifacts remain unchanged.

No Set-2 grounding, action schemas, acceptance execution, registered-check execution,
or fixture test rerun occurred. Exact scenario authorization remains unavailable;
none was created. Existing tests were not rerun for this artifacts/documentation
checkpoint; recorded regression baseline remains 283/283, not a new test result.
