# Evaluation Set 2 formal postmortem

Evidence checkpoint: `0160faa`. This analysis was written after result freeze.
No planner, grounder, application, test or acceptance execution was rerun. No verdict,
scenario or fixture was repaired. This is qualitative engineering diagnosis, not an
independently blinded benchmark: Codex authored fixtures and supplied reasoning in
the existing project conversation. Case-3 trusted setup was explicitly authorized
role-separated Codex authorship, not independently human-authored coverage.

## Method and denominator

Primary classifications use frozen planner intent, bounded context, grounding
explanations/review and observed result envelopes. Each of the 18 top-level
UNVERIFIED scenarios has exactly one primary category in classifications.json.
Secondary factors are explanatory and are not counted twice. Source/tests were
inspected consistently across all five fixtures only after classifications were
written; post-hoc findings below are not AgentGuard observations.

Frozen result: 20 top-level scenarios, 2 PASS / 0 FAIL / 18 UNVERIFIED. All five
case-level verdicts are UNVERIFIED. Children are never additional planner scenarios.

## Taxonomy counts

| Primary category | Count |
|---|---:|
| CONTEXT_EVIDENCE_GAP | 9 |
| SCHEMA_CAPABILITY_GAP | 7 |
| REGISTERED_COVERAGE_GAP | 2 |
| EXECUTOR_POLICY_GAP | 0 |
| PRODUCT_AMBIGUITY | 0 |
| GROUNDING_CONSERVATISM | 0 |
| INFRASTRUCTURE_FAILURE | 0 |
| OTHER | 0 |

## Scenario register

Paths below are relative to evaluation/set2. For each case, evidence is the same-name
planner/<case>.json, grounding/<case>.json and execution/<case>.result.json, plus
<case>/context.md and task.md. Exact names join these artifacts without renaming.

| Case | Exact frozen scenario name | Primary category | Immediate cause |
|---|---|---|---|
| 01_roast_temperature | Accept the inclusive temperature range | SCHEMA_CAPABILITY_GAP | The required remaining-range child has no representable complete observation within the composite bound, so its lack of evidence keeps the parent unverified despite two observed endpoints. |
| 01_roast_temperature | Reject invalid temperature settings | CONTEXT_EVIDENCE_GAP | The frozen grounding abstains because no concrete invalid inputs or behavior-specific coverage were supplied under the strict request-value evidence rule. |
| 01_roast_temperature | Validate without equipment effects | CONTEXT_EVIDENCE_GAP | The context exposes only temperature/unit responses, with no equipment-state or roast-start observable and no documented side-effect check. |
| 02_parcel_label | Produce one normalized label | CONTEXT_EVIDENCE_GAP | The context supplies transformations and fields but no concrete valid recipient/postal-code pair; the current evidence policy does not authorize generating it. |
| 02_parcel_label | Reject blank label fields | CONTEXT_EVIDENCE_GAP | No supported valid counterpart values are supplied to isolate each blank-field rejection. Both-blank rejection alone would not establish both obligations. |
| 02_parcel_label | Preview without purchasing postage | CONTEXT_EVIDENCE_GAP | No purchase-state observable or behavior-specific side-effect coverage is supplied; a preview response does not establish the absence of a purchase. |
| 02_parcel_label | Reject absent or non-text label fields | CONTEXT_EVIDENCE_GAP | Discriminating absent/non-text cases need a valid counterpart that is not concretely supplied; the inferred scenario receives the same strict evidence policy. |
| 03_payroll | Calculate regular and overtime gross pay | REGISTERED_COVERAGE_GAP | Registered metadata explicitly describes regular/overtime calculation, but grounding selection integration and legitimate exact-identity authorization cannot bind this scenario to that coverage. |
| 03_payroll | Handle zero hours | REGISTERED_COVERAGE_GAP | Registered metadata explicitly includes zero hours, yet no legitimate registered selection and exact scenario authorization association exists. |
| 03_payroll | Reject inputs outside the pay contract | CONTEXT_EVIDENCE_GAP | The exposed registered coverage describes calculations on allowed inputs, not rejection of all invalid inputs; the general test command provides no behavior-specific coverage evidence. |
| 03_payroll | Preserve gross pay without tax deduction | CONTEXT_EVIDENCE_GAP | Calculation metadata is relevant but does not explicitly establish a separate no-deduction obligation; the frozen input has no behavior-specific test evidence for that full scenario. |
| 04_tournament | Include entrants and points | SCHEMA_CAPABILITY_GAP | The response is an array; existing dictionary-only scalar assertions cannot establish its entrant membership and points preservation. |
| 04_tournament | Order by descending points | SCHEMA_CAPABILITY_GAP | Array ordering and comparisons between positions are not expressible by the current assertions. |
| 04_tournament | Show empty standings | SCHEMA_CAPABILITY_GAP | The assertions cannot compare an empty array or assert array length; field presence is insufficient. |
| 04_tournament | Preserve preview input | SCHEMA_CAPABILITY_GAP | The required before/after observation of caller-owned in-memory objects is outside the HTTP/scalar independent-observation model. |
| 05_quiz_attempt | Revisit the submitted answer and correctness | SCHEMA_CAPABILITY_GAP | The behavior needs a runtime-created identifier and submission followed by retrieval of continuous state; output references/workflows are unsupported. |
| 05_quiz_attempt | Keep attempt answers separate | SCHEMA_CAPABILITY_GAP | Multiple runtime identifiers and before/after continuous state across attempts are required, not independent composite requests. |
| 05_quiz_attempt | Report unknown attempts | CONTEXT_EVIDENCE_GAP | No concrete identifier is guaranteed absent under supplied running-state evidence. Inventing an identifier is not permitted and freshness must be established rather than assumed. |

## Case analysis and stage diagnosis

Roast has one schema limitation and two context limitations. The full-range parent
retains an unobservable remainder. Invalid-input checks lack authorized concrete
negative examples under the strict frozen request-value rule. The integral-decimal
ambiguity is secondary: it does not prevent defining rejection of clearly out-of-range
integers, but such input construction was not authorized. Equipment non-effects lack
an observable channel; reading a stateless function is not runtime side-effect evidence.

All four Parcel scenarios encounter context limitations. Three lack supported sample
or counterpart values for independently discriminating checks; the fourth lacks a
purchase-state observable. A documented route does not alone supply all evidence for
normalization or non-effects. The inferred malformed-field scenario is not granted
weaker standards than explicit behavior.

Payroll requires careful separation:

| Scenario | Metadata relevance and extent | Binding diagnosis |
|---|---|---|
| Calculate regular and overtime gross pay | Directly names both bands and the transition; descriptive coverage is not proof of completeness | Registered selection and exact authorization are the primary missing integration |
| Handle zero hours | Explicitly names zero hours | Same registered binding limitation |
| Reject inputs outside the pay contract | Valid-input calculation coverage does not establish rejection coverage | Context coverage evidence remains insufficient even if selection is enabled |
| Preserve gross pay without tax deduction | Gross calculation is relevant, but no separate no-tax obligation or behavior-specific evidence is established by the supplied description | Context gap primary; selection/authorization secondary |

The no-tax classification is a judgment boundary: exact gross arithmetic samples may
provide relevant evidence, but their full assertions were not supplied to grounding.
Do not infer semantic authorization or general no-deduction coverage from a metadata
label. Post-hoc sample assertions do not retroactively broaden supplied evidence.
Registered execution infrastructure exists; legitimate binding from these planner
scenarios to trusted coverage does not. No registered action was selected or executed.
The frozen exact-identity authorization was unavailable and is not manufactured now.

Tournament has four schema limitations: array membership, array order, empty-array
checks, and caller-owned object nonmutation. Tie fairness remains unresolved in the
planner, but no executable tie policy was silently chosen. Descending order could
be checked for unequal scores if representation existed, so product ambiguity is not
its immediate blocker. Nonmutation is an inferred proposal rather than an explicit
product mandate; it still cannot be observed through the supplied response vocabulary.

Practice has two workflow limitations and one context limitation. Submission/retrieval
and answer isolation require runtime identifiers and continuous state. Unknown-attempt
handling requires trustworthy absence, not merely an invented string. Starting an
attempt alone was observed; that does not establish subsequent retrieval or isolation.

The dominant bottlenecks precede execution: context/evidence policy (9), schema
expressiveness (7), and registered binding (2). Planner identification captured useful
behavior but had overlap (pay scenarios), an inferred nonmutation proposal, and no
concrete tie-policy scenario. Counts do not prove planner completeness. No otherwise
supported action was blocked by executor policy in this run. No infrastructure failure
was recorded. Zero primary ambiguity/conservatism classifications does not mean those
concerns are absent; they were secondary or constrained by intentional policy.

## Composite concern and observed aggregation

For 'Accept the inclusive temperature range', observed children are lower endpoint
PASS, upper endpoint PASS, remaining range UNVERIFIED. Counts are required=3, pass=2,
fail=0, unverified=1. Existing aggregation correctly produced parent UNVERIFIED.
The schema accepted a valid flat three-child shape. Semantic review identified a
possible contract violation: the grounder described the remainder as needing more
observations than the bound while retaining it as one unsupported child, contrary
to the whole-parent-unsupported rule for an unrepresentable decomposition.

Primary diagnosis is the complete-range representation gap, not faulty runtime
aggregation. There is also a test-design tension: treating every interior integer
as a required observation demands exhaustive checking, whereas the separate return
scenario samples one setting. Sampling adequacy was not specified. This does not
justify repairing the frozen child set or claiming endpoints prove the entire range.
Structural validation proves neither decomposition completeness nor semantic validity.

## Two PASS observations (outside the classification denominator)

- 'Return the accepted temperature and unit': recorded HTTP 200, temperature 160,
  unit C matched all three frozen assertions. This establishes that single observed
  request, not all accepted temperatures or equipment safety.
- 'Start an identifiable practice attempt': recorded HTTP 201 with id '1' and
  question '7 + 5'. Existing json_exists/json_type assertions established the presence
  and string types of id/question; equality matched the frozen question text. No
  concrete runtime ID was asserted or chained. Exact question equality is fixture-
  specific and not a general requirement to always ask that question. It caused no
  contradiction here. The result does not establish answer persistence or isolation.

Composite children separately total 2 PASS / 0 FAIL / 1 UNVERIFIED. All case overall
verdicts remain UNVERIFIED. No FAIL attribution is needed because there are no FAIL
results. No unsupported scenario was awarded a source-inspection verdict.

## Synthetic-input question

Repository facts that cannot be invented include routes, methods, accepted field
names, response contracts, authentication/ownership, real identifiers, isolation and
absence guarantees. Product rules and expected transformations must remain grounded
in requirements rather than copied blindly from current behavior.

Potential test data is distinct: boundary +/- 1, fractional or wrong primitive values,
empty/whitespace strings, and bounded ordinary text can be derived/generated without
claiming new repository facts if a future policy explicitly authorizes that operation.
The frozen policy did not do so. Immediate affected scenarios are roast invalid
settings and parcel normalization, blank-field rejection, and absent/non-text rejection.
Thus these are context-evidence restrictions, not proved grounder mistakes.

Quiz's absent identifier is harder: synthesizing a string does not prove it absent.
A reserved namespace, documented allocation constraint, or trusted fresh-state
contract would be required. Do not confuse input generation with establishing state.
No synthetic values or new policy were used in this evaluation. These distinctions
motivate design work, not retrospective relabeling or projected verdicts.

## Descriptive Day-6 comparison

| Evaluation | Top-level scenarios | PASS | FAIL | UNVERIFIED |
|---|---:|---:|---:|---:|
| Day 6 | 21 | 0 | 0 | 21 |
| Set 2 | 20 | 2 | 0 | 18 |

Day 6 grounded all 21 as unsupported; its primary diagnosis was context 2, schema 7,
executor policy 12, other categories 0. Set 2 represented an executable observation
in 3/20 planner scenarios, including one partial composite; the count includes its
semantic concern unchanged. Day 6 produced no executable acceptance observations.
After changes targeting its diagnosed limitations, a separate fresh evaluation
showed some executable observations and two deterministic PASS results, while
conservative abstention still dominated. Case sets and architecture differ. This
is not a controlled comparison, accuracy improvement, or evidence of general gain.

## POST-HOC FIXTURE FINDINGS — NOT AGENTGUARD-DETECTED FAILURES

Read-only inspection covered app.py and test_app.py in all five repositories plus
payroll acceptance_checks.py/checks.json. No tests or applications were run.

- Roast tests contain 159/241, a fractional value, boolean, string and null rejection
  examples; these concrete tests were not in bounded context. Source checks the
  inclusive range and has no equipment integration. This is not observed safety.
- Parcel tests contain concrete recipient/postal text and blank-field examples not
  supplied as grounding evidence. Source applies the advertised transformations;
  no purchase integration appears in the small fixture.
- Payroll registered source checks exact gross totals for five valid input pairs,
  including zero, transition and overtime. These are relevant to undeducted gross
  samples, but it has no invalid-input checks. Ordinary implementation tests do have
  invalid inputs; their existence does not authorize selecting them after freeze.
- Tournament source returns sorted copied dictionaries. Its test checks input order
  only partially; source does not define a product tie-fairness policy. There is no
  basis to label stable tie ordering a defect against an unresolved requirement.
- Practice source stores answers per runtime ID and tests exercise retrieval and
  separation. These tests are not AgentGuard-observed acceptance evidence. Repeat
  answers and pre-submission display remain policy questions, not discovered defects.

No clear task/implementation contradiction was identified in this limited consistent
inspection. That is not proof of correctness; no new FAIL or verdict change follows.

## Limits and integrity

Before and after analysis, frozen evaluation bytes were compared with 0160faa.
Production code/tests, protocol, all fixture/planner/grounding/execution artifacts,
and historical Day-5/Day-6/smoke artifacts are unchanged. No repair or rerun occurred.
Regression was not rerun for this documentation-only checkpoint; baseline remains
283/283 from the prior execution checkpoint. Only new postmortem artifacts and an
append-only CODEX entry changed. Recommendations are proposals, not implemented work.
