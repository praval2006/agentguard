# AgentGuard Evaluation Set 2 — Frozen Protocol

Protocol date: 2026-09-28. Architecture baseline: `56d7cf8`.
Recorded regression baseline: 283/283 passing; not rerun for this documentation checkpoint.

## Purpose and scope

Determine whether post-Day-6 architecture changes improve fresh acceptance
executability while preserving conservative abstention. This is a new evaluation,
not a rerun or repair of Day-6. Historical Day-6 remains permanently 21 planner
scenarios: 0 PASS, 0 FAIL, 21 UNVERIFIED.

This checkpoint freezes methodology only. No case fixtures, task repositories,
reasoning outputs, or execution results are created here. No defects are planted.
Production code, tests, and historical Day-5, Day-6, and registered-check smoke
artifacts remain unchanged and are not rerun.

# 1. Evaluation question

Freeze this primary question:

"After the post-Day-6 architecture changes, can AgentGuard independently execute and
verify materially more acceptance behavior on fresh cases without weakening its
repository-evidence boundary?"

Secondary questions:

- Does the planner still identify useful acceptance behavior?
- Can grounding convert more planned behavior into executable representations?
- Do composite scenarios improve multi-observation acceptance checks?
- Can registered checks provide bounded repository-local execution outside the
  original sample-app policy?
- Does AgentGuard still abstain when evidence or capability is insufficient?
- When execution is possible, does deterministic verification distinguish PASS,
  FAIL, and UNVERIFIED from observed evidence?

Do not define a required success rate.

# 2. Freeze five case categories

Evaluation Set 2 will contain exactly five fresh cases.

Freeze these categories before any fixture is designed:

CASE 1 — INCLUSIVE BOUNDARY

A task containing an explicitly inclusive valid range or equivalent two-boundary
requirement.

Purpose:
Test whether one planner behavior can be conservatively grounded as a bounded
composite with independent lower/upper observations where repository evidence
supports them.

CASE 2 — MULTIPLE REQUIRED OBSERVABLE PROPERTIES

A task where one acceptance behavior requires multiple related observable
properties.

Purpose:
Test whether AgentGuard can preserve one requirement while collecting multiple
required observations using current assertions/composite representation.

Do not require stateful output chaining.

CASE 3 — REGISTERED REPOSITORY CHECK

A fresh domain outside the original sample_app where repository-local trusted
acceptance coverage can be registered before AgentGuard reasoning.

Purpose:
Test the registered-check path as generalized bounded execution rather than the
historical sample-app command allowlist.

Coverage authorization must remain separate and trusted.

Do not allow the model to create or authorize the registered check.

CASE 4 — INSUFFICIENT EVIDENCE / PRODUCT AMBIGUITY

A task containing at least one meaningful acceptance question that cannot safely be
turned into an executable expectation from the supplied task/repository evidence.

Purpose:
Test conservative abstention.

A correct outcome may be UNVERIFIED.

Do not add hidden hints telling the grounder to abstain.

CASE 5 — BEYOND CURRENT CAPABILITY

A meaningful requirement requiring a capability AgentGuard intentionally does not
support, such as a bounded but genuinely stateful/multi-step observation that cannot
be represented as independent composite children.

Purpose:
Test that increased expressiveness does not cause invented workflows or false PASS.

A correct outcome may be UNVERIFIED.

# 3. Freshness constraints

All five cases must be fresh.

Do NOT reuse:

- subscription cancellation;
- Day-2 planner cases;
- Day-5 fixture;
- Day-6 work orders;
- Day-6 room reservations;
- Day-6 warehouse dispatch;
- Day-6 class waitlist;
- Day-6 scheduled messages;
- registered-check document-archiving smoke domain.

Choose unrelated domains when fixture creation begins.

Do not choose domains because a known implementation bug is easy to plant.

# 4. No target verdict distribution

Freeze this rule:

The evaluation has NO required number of PASS, FAIL, or UNVERIFIED results.

Fixture implementations must be plausible small implementations.

Do not intentionally insert defects merely to produce FAIL.

Do not repair implementations merely to produce PASS.

Natural implementation mistakes are allowed to remain once the fixture is frozen,
but fixture creation must not be driven by a desired AgentGuard verdict.

# 5. Freeze-before-reasoning sequence

The evaluation must use this order:

A. Freeze protocol.
B. Create all five tasks/repository fixtures.
C. Run their existing implementation-side tests.
D. Freeze all fixtures and task/context artifacts in one checkpoint.
E. Only after fixture freeze, run planner reasoning.
F. Freeze first valid planner outputs.
G. Run grounding against only the permitted frozen inputs.
H. Freeze first valid grounding outputs.
I. Execute the frozen grounded scenarios once.
J. Preserve results before analysis.
K. Perform postmortem only after execution results are frozen.

No fixture or task edits after planner output is observed.

No scenario repair after execution outcomes are observed.

If an infrastructure defect prevents evaluation, document it separately rather than
silently changing the case.

# 6. First-valid-output rule

For planner and grounder:

- use the first structurally valid provider output;
- no prompt tuning based on desired semantic outcome;
- no regeneration because output is inconvenient;
- no regeneration because it produces unsupported scenarios;
- no regeneration after seeing execution results.

Malformed output may be retried only according to an explicitly documented
protocol rule, and any retry must be recorded.

If using the existing Codex conversation as the reasoning provider, explicitly
record that this is NOT an independently blinded model evaluation because the model
has prior project context.

# 7. Information boundaries

Planner receives only:

- frozen task text;
- bounded frozen repository context.

Planner must not receive:

- runtime results;
- hidden expected verdicts;
- fixture bug annotations;
- implementation-test analysis;
- grounder outputs.

Grounder receives only:

- frozen planner output;
- the same permitted frozen repository context.

Grounder must not receive:

- runtime results;
- expected verdicts;
- postmortem;
- hidden defect annotations.

Execution receives only the frozen grounded scenarios plus trusted caller
configuration required by the existing executors.

# 8. Registered-check case boundary

For Case 3:

The trusted registered check, registry metadata, coverage ID, and coverage
authorization must be created and frozen BEFORE planner/grounder reasoning.

The model must not:

- write the registered test;
- choose whether its own test is trusted;
- create coverage authorization;
- modify the registry;
- authorize semantic coverage.

Record clearly that trusted registered checks are part of repository/evaluation
setup, not autonomous AgentGuard-generated acceptance tests.

# 9. Metrics

Record metrics separately by pipeline stage.

PLANNER METRICS:
- total planner scenarios;
- explicit vs inferred source counts;
- ambiguities identified;
- qualitative repository relevance;
- whether scenarios introduce unsupported product decisions.

Do not create a subjective numeric quality score.

GROUNDING METRICS:
- total grounded top-level scenarios;
- standalone HTTP count;
- standalone test-command count;
- standalone registered-check count if supported by current grounding contract;
- composite count;
- unsupported count;
- total composite children;
- executable leaf count;
- unsupported leaf count.

Also record:
- percentage of planner scenarios represented by at least one executable observation;
- percentage wholly unsupported.

These are executability metrics, NOT correctness/coverage scores.

EXECUTION METRICS:
- top-level PASS count;
- top-level FAIL count;
- top-level UNVERIFIED count;
- overall verdict per case;
- composite child PASS/FAIL/UNVERIFIED counts separately;
- registered-check outcomes separately where applicable.

Do not treat child counts as independent planner requirements.

# 10. Postmortem taxonomy

After results are frozen, classify every wholly or partially UNVERIFIED scenario
using one primary category:

- CONTEXT_EVIDENCE_GAP
- SCHEMA_CAPABILITY_GAP
- EXECUTOR_POLICY_GAP
- PRODUCT_AMBIGUITY
- GROUNDING_CONSERVATISM
- REGISTERED_COVERAGE_GAP
- INFRASTRUCTURE_FAILURE
- OTHER

Define each category in the protocol.

Do not classify before execution.

For FAIL results, distinguish:

- observed implementation contradiction;
- fixture/infrastructure defect;
- invalid expectation discovered after freeze.

Do not silently reinterpret FAIL.

# 11. Historical comparison rule

Evaluation Set 2 may later be compared descriptively with Day-6.

Permitted comparison:

- Day-6 executability was 0/21 planner scenarios;
- Evaluation Set 2 fresh executability is X/Y;
- architecture differs and case sets differ;
- therefore this is NOT a controlled apples-to-apples benchmark improvement claim.

Do NOT claim:

"AgentGuard improved from 0% to X% accuracy."

Do NOT present cross-dataset PASS rate as an accuracy improvement.

The meaningful comparison is architectural/failure-mode evidence, not benchmark
score.

# 12. Evaluation integrity

Freeze these rules:

- no case-specific production-code changes after protocol freeze;
- no executor allowlist expansion for an individual evaluation case;
- no schema expansion after seeing a case fail;
- no grounding prompt change after seeing case outputs;
- no fixture repair after reasoning begins;
- no hidden expected-answer file exposed to planner/grounder;
- no post-hoc scenario deletion;
- preserve all first valid artifacts;
- preserve negative results.

# 13. Stop conditions

Stop and document rather than repair if:

- production code would need a case-specific exception;
- execution requires weakening a safety boundary;
- a frozen fixture is materially invalid;
- the provider cannot produce structurally valid output under the documented retry
  rule;
- an infrastructure issue makes the result uninterpretable.

A stopped case remains part of the evaluation record.

## Operational definitions frozen with this protocol

### Provider attempts and artifact preservation

Use one provider attempt per case per stage. There are no malformed-output retries
in this evaluation. Preserve the raw attempt and validation error if malformed,
mark the affected case stopped, and retain it in the evaluation record. Provider
transport/infrastructure failures are recorded separately and are not silently
retried. Structural validation does not establish semantic grounding or quality.
The first structurally valid output is frozen unchanged even if semantically weak,
unsupported, or inconvenient. Record provider identity, supplied instructions,
input checkpoint identifiers, and attempt provenance with future outputs.

If the existing Codex project conversation supplies reasoning, it is NOT an
independently blinded model evaluation: prior project context cannot be erased by
instructions. Input restrictions still apply, but do not prove blindness. Record
fixture authorship and provider provenance. This is qualitative engineering
validation, not an independent benchmark or proof of general correctness.

### Current registered-check constraint

The existing grounding instructions advertise HTTP, test-command, unsupported,
and composite representations; they do not advertise standalone registered-check
selection. Schema/executor support alone is not permission to extend the grounding
prompt during this evaluation. Record registered-check selections, if any, and
review compliance with the frozen contract; do not force a registered selection.

Coverage authorization matches the canonical complete grounded scenario identity,
check ID, and coverage ID. Trusted setup must freeze exact authorizations before
reasoning as required above; it cannot authorize a future scenario using a wildcard,
a check ID alone, or a post-reasoning association. Any setup identities are trusted
configuration, not planner answers to expose to the reasoning provider. The actual
reasoning output must remain unchanged. An unmatched identity must remain
unauthorized; do not edit the output or add authorization after seeing it.

The trusted setup actor, separate from the reasoning provider, must supply the
registered test, registry and authorization. The reasoning model cannot create or
approve them. If compliant setup cannot be supplied, stop and document Case 3;
do not relax the trust rule. A stopped or unexecutable Case 3 is an evaluation
limitation, not evidence that registered execution was exercised. No contract
change is authorized by this protocol.

### Metric counting conventions

Count each planner scenario and grounded parent once. Composite children are
observations, never additional planner requirements. Count executable leaves as
HTTP, test-command, or registered-check representations; count unsupported leaves
as standalone unsupported scenarios plus unsupported children. These are structural
representation counts, not claims that executor policy, authorization, runtime
availability, or semantic coverage is established. Record such limitations separately.

For a case with Y planner scenarios, X is the number represented by at least one
executable leaf; report X/Y and 100*X/Y. W is the number whose complete grounded
representation has no executable leaf; report W/Y and 100*W/Y as wholly unsupported.
If Y is zero, report percentages as N/A. Missing grounding due to a stopped stage
is reported separately as unavailable, not fabricated as unsupported. Report stage
completion and denominators alongside aggregate metrics so stopped cases remain
visible. A partial composite counts once in X, but its unsupported children and
incomplete evidence remain explicit. Do not equate representation with successful
execution or acceptance coverage.

Execution metrics use the unchanged engine's top-level and child verdicts, with
registered statuses/count evidence separately. Preserve stopped cases as stopped;
do not manufacture verdicts for runs that did not occur. Preserve all artifacts
before qualitative analysis, including contradictory or negative observations.

### Postmortem category definitions

Apply only after results are frozen. Review every wholly or partially UNVERIFIED
scenario, including an overall FAIL composite with an UNVERIFIED child. Assign one
primary category to the parent, explain the decisive cause and affected children,
and describe secondary contributors in prose without double-counting parents.

- CONTEXT_EVIDENCE_GAP: supplied context lacks necessary execution details or
  observable evidence, such as a route, identifier, or response contract.
- SCHEMA_CAPABILITY_GAP: required behavior cannot be faithfully represented by
  current actions/assertions or bounded independent composites.
- EXECUTOR_POLICY_GAP: a represented action is blocked by existing execution policy,
  such as command or target restrictions.
- PRODUCT_AMBIGUITY: required expected behavior depends on an unresolved product
  decision that supplied requirements do not settle.
- GROUNDING_CONSERVATISM: sufficient supplied evidence and supported capability
  existed, but grounding abstained; justify this finding against frozen inputs.
- REGISTERED_COVERAGE_GAP: trusted check coverage or exact scenario/check/coverage
  authorization is missing, mismatched, or insufficient.
- INFRASTRUCTURE_FAILURE: a technical failure prevents interpretable execution or
  observation, rather than establishing a product contradiction.
- OTHER: a cause outside these definitions; provide a concrete explanation.

For FAIL, retain the deterministic verdict and separately classify the evidence as
an observed implementation contradiction, fixture/infrastructure defect, or invalid
expectation discovered after freeze. Do not repair or silently reinterpret the
result. Where attribution is unresolved, state that uncertainty explicitly.

## Freeze record

Only this protocol and an appended CODEX.md entry are included in the protocol
checkpoint. The commit titled `Freeze Evaluation Set 2 protocol` is its freeze
identifier. No five-case directories are created here. Future phases must follow
the ordered gates above; this document reports no evaluation outcomes.
