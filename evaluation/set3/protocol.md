# AgentGuard Evaluation Set 3 — Frozen protocol

Architecture: `0e50d12` (Add bounded synthetic test derivations).
Stage: protocol and case specifications only. Date: 2026-09-28.
This is the final planned fresh architecture evaluation before core freeze and
productization. It does not authorize further architecture work during evaluation.

## Question and limits

“After adding bounded, provenance-recorded derived/synthetic test values, how much
acceptance behavior can AgentGuard independently turn into trustworthy executable
observations on fresh software tasks?”

This is descriptive engineering evaluation, not an accuracy benchmark. There is
no desired percentage, executable count, PASS count or verdict distribution. Do not
plant defects, tune cases for an outcome, or repair natural mistakes to improve
results. Preserve whatever results occur, including negative and stopped cases.

## Frozen case specifications

Exactly five cases, each specified under cases/<case_id>/spec.md:

1. 01_profile_display_name — update and store normalized free-form display text.
2. 02_shipping_weight_quote — inclusive whole-gram limits and a shipping tariff.
3. 03_catalog_lookup — name filtering, collection results and preserved fields.
4. 04_promo_preview — a published promotion, preview totals and non-commitment.
5. 05_notification_preferences — validated partial boolean updates and preserved state.

The user specified these domains. Some overlap broad historical subjects, but all
implementations must be fresh: no Set-2 implementation reuse or retroactive repair.
Do not remove collections or natural persistence/side-effect obligations to fit
current capabilities. Specifications are product requirements, not scenario lists.
Concrete tariff and promotion values define business policy; no example customer
names or request payloads are supplied merely to help reasoning.

## Ordered freeze gates

1. Freeze this protocol, five specifications, manifest and review.
2. In a later checkpoint, implement all five fresh small deterministic repositories
   using the standard library/minimal existing dependencies and ordinary tests.
   Record test commands/results, bounded context and trusted setup; freeze together.
3. One planner provider attempt per case, using frozen task/context only.
4. Preserve first responses and validated planner outputs; freeze.
5. One grounding provider attempt per case, using frozen planner/context and the
   existing caller-reviewed policy mechanism only.
6. Preserve first responses and validated grounded outputs/provenance; freeze.
7. Execute exact frozen scenarios once per case through existing run_acceptance.
8. Preserve/hash exact results and lifecycle/configuration before interpretation.
9. Conduct postmortem only after result freeze.

Malformed provider output stops the affected case/stage. No retries, semantic
regeneration, scenario deletion or repairs between stages. Record errors, raw first
responses and stopped cases without fabricating outputs or verdicts. A material
fixture validity problem, required production exception, safety relaxation or
uninterpretable infrastructure failure stops the affected work and is documented;
no silent repair/rerun. Do not edit a specification after this freeze or a fixture
once reasoning has begun. Any protocol change requires a separately disclosed
new decision, not retroactive rewriting of this evaluation.

## Future fixture and context construction

No fixtures are implemented in this checkpoint. Future fixtures must be small,
plausible, deterministic and local, with ordinary implementation-side tests. Do not
intentionally omit tests to hide a planted defect or author tests to guarantee an
AgentGuard result. Freeze validity-test results separately from acceptance evidence.

A future task.md must preserve the frozen spec requirements without strengthening
or weakening them for executability; preserve the source relationship explicitly.
Bounded context is at most the existing 32,000-character input limit and may contain
relevant route/method, request/response shape, source excerpts/signatures, ordinary
test commands, local configuration and validation facts. It must describe the
interface accurately, including state lifecycle where relevant. Source excerpts
are repository facts, not proof of product correctness.

Context must exclude expected scenarios/verdicts, defect annotations, implementation
run results/analysis, hidden behavior, postmortem judgments, synthetic-rule coaching,
and claims of test coverage not actually established. No additional source lookup
to fill gaps during reasoning. Do not selectively conceal normal interface facts
or insert benchmark hints. Freeze context with fixtures before any reasoning.

## Derivation trust and fairness

Use the unmodified opt-in DerivationPolicy/InputConstraint mechanism. A trusted
fixture/setup author reviews ordinary task/context evidence before reasoning and
freezes any policies with the fixture: exact context hash, quotation, field target,
constraint and semantic class. The review must justify its meaning and exclude
identity/domain/state-dependent fields. Record authorship honestly; Codex setup is
role-separated preparation, not independently human-authored trust. Policy records
are separate trusted configuration, not model output and not planner context.

Planner receives only the frozen task/context and existing instructions. Grounder
receives frozen planner/context and existing instructions; copied derivation_facts
are supplied only through the current API from the already-frozen caller policy.
This is an explicit trusted-configuration channel, not unrestricted extra evidence.
Do not tailor policies to planner/grounder outputs or add authority after a rejection.
A context hash and quotation bind a review but do not prove source meaning.

No scenario/rule-use assignment is preselected. Not every case must use derivation.
The provider may request only existing rules; deterministic code constructs concrete
values/provenance. It may not declare arbitrary concrete values synthetic. Derived
inputs never create endpoints, expected outputs, identities, absence guarantees,
authorization, state continuity or application evidence. Existing executor/schema
bounds and unsupported behavior remain. Do not add rules or capabilities mid-run.

## Information boundaries and methodology

Evaluation administration, case labels, manifests, implementation-test results,
reviews and previous-case outcomes are not reasoning input. Grounding must preserve
exact planner order/identity, including behavior only where the current schema
carries it; do not migrate legacy standalone shapes. Execution receives frozen
scenarios and trusted caller configuration, not new reasoning. Only observations
and the existing deterministic verifier determine acceptance verdicts.

Record exact requests/responses, input/instruction/policy hashes, provider identity,
attempt counts, validation and freeze commits. If the existing Codex conversation
is used, explicitly state it is NOT independently blinded because prior project and
fixture context exists. Input restrictions are obligations, not proof of blindness.
No external model provider or new integration is authorized in this checkpoint.

## Frozen metrics and counting

- Planner: total scenarios, explicit/inferred scenario counts; retain ambiguities.
- Grounding: top-level distribution across HTTP, test_command, registered_check,
  composite and unsupported; record children separately.
- Executable observation: a represented supported action that the existing executor
  can actually attempt under frozen trusted configuration/policy. Count a parent
  once if at least one leaf qualifies. Do not count merely schema-valid commands,
  unauthorizable references or policy-blocked targets as executable. Record known
  inability separately; later unexpected infrastructure errors remain execution facts.
- Report executable-observation numerator and proportion of all planner scenarios;
  retain stopped/unavailable cases and stage completeness. For zero denominator,
  use N/A. Missing outputs are not fabricated as unsupported or dropped from scope.
- Derivations: preserve raw provider request occurrences and compiled provenance;
  count accepted/rejected requests by rule. Accepted means materialized in a validated
  frozen action. If a leaf's batch is rejected, none of its requests are accepted,
  even if a member could individually derive. Unknown rules are recorded by name;
  malformed entries are counted separately. Stage validation failure/stopped output
  yields no accepted frozen requests; record unvalidated requests separately rather
  than claiming individual rejection by the derivation validator. Capture first
  artifacts without rerunning the provider or modifying production instrumentation.
- Execution: top-level PASS/FAIL/UNVERIFIED, case verdicts, composite child verdicts
  separately, infrastructure failures separately; record stopped cases without
  manufactured verdicts. Do not add children to the planner-scenario denominator.

Executability is not accuracy, correctness, success rate or verification rate.
Acceptance outcomes are not benchmark correctness labels. Report contextual limits;
no synthetic value or green implementation suite supplies acceptance evidence.

## Postmortem taxonomy

After frozen execution, assign exactly one primary category to every top-level
UNVERIFIED scenario. Record secondary contributors without double-counting.

- CONTEXT_EVIDENCE_GAP: insufficient supplied facts, values, observables or coverage.
- SCHEMA_CAPABILITY_GAP: required observation/interaction cannot be faithfully represented.
- EXECUTOR_POLICY_GAP: supported representation cannot execute under existing policy.
- PRODUCT_AMBIGUITY: unresolved product decision prevents a faithful expectation.
- GROUNDING_CONSERVATISM: sufficient permitted evidence/capability existed but grounding
  abstained; do not label intentional evidence restrictions as model mistakes.
- REGISTERED_COVERAGE_GAP: trusted coverage/selection/authorization binding is inadequate.
- INFRASTRUCTURE_FAILURE: unexpected infrastructure prevents otherwise supported evidence.
- OTHER: explain why none of the above applies.

Also describe unobservable children of other parents separately without adding
primary top-level counts. For FAIL, distinguish observed product contradiction,
fixture/infrastructure defect, and invalid frozen expectation. Preserve all verdicts.
Any post-hoc source findings must be marked as not AgentGuard-detected evidence.

## Historical comparison

Set 2 remains frozen: 20 scenarios; 2 PASS / 0 FAIL / 18 UNVERIFIED; 3/20 had an
executable observation during grounding. Primary diagnoses: context 9, schema 7,
registered coverage 2; other categories 0. Its historical executability number is
preserved as reported; disclose any counting-policy differences in future comparison.

No Set-3 results are filled in here. Different tasks/datasets prevent a controlled
accuracy comparison. Describe architecture/failure-mode evidence only; neither the
new feature nor a different outcome proves general improvement. Do not rerun Set 2
or estimate what it would score under this architecture.

## Integrity and stopping point

No production/test changes, schema/executor expansion, fixture mutation after
reasoning, outcome-driven policy edits, historical reruns or hidden repairs.
Preserve all first valid artifacts and negative outcomes. Check frozen file hashes
before and after each stage. Do not automatically begin the next stage.
This checkpoint ends with specifications; no fixture source, planner/grounder call
or acceptance execution is authorized. The final evaluation's eventual result will
inform core freeze/productization, not an automatic cycle of retrospective repairs.
