# Evaluation Set 2 grounding-stage freeze

Planner checkpoint: `7197b14`; fixture checkpoint: `7c2ab34`.
Freeze identifier: commit titled `Freeze Evaluation Set 2 grounding outputs`.

## Method

Codex in the existing project conversation supplied one structured response per
case. This is NOT independently blinded; prior project context exists. Grounding
evidence was restricted to the frozen validated planner output and same-case
context.md. No task, category, fixture manifest, planner review, test results, or
additional fixture source was passed to the injected callable.

Each first response was saved before one call to unchanged ground_scenarios(),
then immediately saved as validated output. All five were structurally valid; none
stopped, retried, repaired or regenerated. Paired response/output JSON files are
byte-identical. stage_manifest.json preserves paths/hashes, exact instructions and
their hash, attempts, validation and per-case counts. Structural validity is not
semantic grounding validation. No external API call or execution occurred.

## Representation metrics

| Case | Planner/top-level | HTTP | Test command | Registered | Composite | Unsupported | HTTP children | Unsupported children |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 01_roast_temperature | 4/4 | 1 | 0 | 0 | 1 | 2 | 2 | 1 |
| 02_parcel_label | 4/4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| 03_payroll | 4/4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| 04_tournament | 4/4 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| 05_quiz_attempt | 4/4 | 1 | 0 | 0 | 0 | 3 | 0 | 0 |
| Total | 20/20 | 2 | 0 | 0 | 1 | 17 | 2 | 1 |

Three composite children total. Across standalone and composite representations:
4 executable leaves and 18 unsupported leaves. Children are not additional planner
requirements. Three of 20 planner scenarios (15%) have at least one executable
observation; 17/20 (85%) are wholly unsupported. Per-case represented counts:
2/4, 0/4, 0/4, 0/4, 1/4. One represented parent retains a required unsupported child.
These are structural executability metrics only, not correctness, semantic coverage,
acceptance coverage, accuracy, or a success rate. They do not establish policy
approval or runtime availability, and include the semantic concern below unchanged.

## Frozen-output review

- Temperature: endpoint method/path, field name, 160/240 values, response status,
  returned temperature and unit are visible in supplied context and planner intent.
  Requests are independent per context. The composite keeps the same parent behavior
  and an unsupported remainder instead of claiming endpoint checks prove the whole
  range. However, its explanation says the remaining values cannot fit the child
  bound. This appears in tension with the explicit instruction to use whole-parent
  unsupported when faithful decomposition requires more than three observations.
  Structural validation did not catch that semantic issue. Preserve the response;
  do not count validation as evidence that decomposition is contract-compliant.
  The separate return-value scenario samples only one documented accepted setting;
  it does not establish behavior across every possible input. Rejection remains
  unsupported rather than choosing the integral-decimal policy or inventing concrete
  invalid examples. That interpretation of input evidence may be conservative.
- Parcel label: all scenarios remain unsupported. The response requires concrete
  supported text examples for normalization and individually discriminating invalid
  inputs; context provides field types/transformations but no sample recipient/code.
  No postage-purchase observable is supplied. This is a strict interpretation of
  the request-value evidence rule, not proof that the feature has no usable interface.
  The inferred absent/non-text scenario receives the same evidence standard.
- Payroll: exposed callable and registry metadata are preserved as facts, not
  converted into a newly invented command or registered selection. Current grounding
  instructions do not advertise registered-check selection. General implementation
  test-command presence is not treated as proof of behavior-specific coverage.
  No registry/check modification, trust assignment, or coverage authorization was
  performed. Exact-identity authorization remains pending/unavailable independently
  of these frozen unsupported representations; no execution outcome is predicted.
- Tournament: array inclusion/order and empty-array comparison exceed the supplied
  dictionary-only scalar assertion vocabulary. Presence is not substituted for
  emptiness. No tied-score policy is chosen. Input nonmutation requires observing
  caller-owned objects, not merely the HTTP response. The request's reference to
  Parcel Label nonmutation does not match the frozen planner: nonmutation belongs
  to Tournament; Parcel Label's inferred scenario is absent/non-text validation.
  The actual frozen identities were preserved, not rewritten to match that wording.
- Practice attempts: creation uses the documented method/path, empty object, status,
  and string response fields without predicting an identifier. The exact question
  assertion comes from the supplied source, not a product mandate for that particular
  arithmetic question; it is coupled to the documented fixture question. The source
  supports it as a concrete interface expectation, but it would be too restrictive
  as a general question-selection requirement. Submission/retrieval and isolation
  remain unsupported because they require runtime identifiers and state continuity.
  Unknown-attempt handling does not invent a guaranteed absent identifier.

No invented endpoint, identifier, header or executable command was identified.
Concrete executable request values appear in supplied evidence. The composite
semantic concern and fixture-specific question expectation above remain visible;
no output was edited after review. Missing observables are not replaced by related
checks. Planner ambiguity policies are not resolved, workflows are not disguised
as independent children, and inferred identity/source fields remain unchanged.
No postmortem taxonomy or execution verdicts are assigned at this stage.

## Integrity and verification

All frozen Set-2 fixture/planner files and the protocol matched commit 7197b14
byte-for-byte before reasoning and after artifact creation. Production code/tests,
Case-3 trusted check/registry, task/context files, fixture manifest, shared adapter,
and Day-5/Day-6/smoke artifacts are unchanged. Legacy standalone shapes retain no
behavior field; the composite retains exact planner behavior and all top-level
name/source/reason/order values are preserved.

No grounding output was used for execution. No fixture server, registered check,
acceptance engine, fixture implementation suite, or historical harness ran.
No Set-2 acceptance result artifact exists. Regression tests were not rerun;
283/283 remains the recorded baseline, not a fresh result.
