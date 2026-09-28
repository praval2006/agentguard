# Evaluation Set 3 — Frozen grounding stage

Protocol fa4193c; fixtures 58f8ead; planner 9e88f5e; architecture 0e50d12.
One Codex manual injected-provider response per case was saved before invoking the
unchanged ground_scenarios API once with that case's frozen caller derivation policy.
All five responses validated on the first attempt, preserving 23 ordered identities.
No retry, output repair, planner call, acceptance execution, HTTP request, registered
check, fixture test or regression run occurred. Recorded regression baseline: 304/304.

The exact requests (including existing instructions and copied trusted facts), raw
responses, compiled outputs, input/output hashes and attempt results are preserved.
The policy is separate frozen caller configuration, not authority authored by the
provider. This uses the existing project conversation, not independent blinding or
an external model API. Input restrictions do not erase prior project knowledge.

| Case | HTTP | Composite | Unsupported | Represented / planner scenarios |
| --- | ---: | ---: | ---: | ---: |
| Profile display name | 1 | 0 | 3 | 1/4 |
| Shipping weight quote | 0 | 2 | 2 | 2/4 |
| Catalog lookup | 0 | 0 | 5 | 0/5 |
| Promotion preview | 0 | 0 | 5 | 0/5 |
| Notification preferences | 0 | 1 | 4 | 1/5 |
| Total | 1 | 3 | 19 | 4/23 |

Test-command and registered-check counts are zero throughout. The three composites
contain six HTTP children and no unsupported children. There are seven HTTP leaves,
but children do not increase the 23-scenario denominator.

**4/23 (17.39%)** have at least one potentially executable observation: documented
routes, methods and bodies fit the existing HTTP mechanism with the fixture's
caller-supplied loopback URL. No actual connection or execution has been attempted.
This is executability, not accuracy, correctness, success rate or verification rate.
Read-only review records semantic coverage concerns; these counts do not certify
complete preservation of the planner's behavioral scope.

| Derivation rule | Requests | Accepted | Rejected |
| --- | ---: | ---: | ---: |
| neutral_nonblank_text | 1 | 1 | 0 |
| below_inclusive_lower_bound | 0 | 0 | 0 |
| above_inclusive_upper_bound | 0 | 0 | 0 |
| blank_string | 0 | 0 | 0 |
| whitespace_string | 0 | 0 | 0 |
| wrong_primitive_type | 0 | 0 | 0 |
| Total | 1 | 1 | 0 |

The deterministic compiler supplied the single neutral display-name input and its
full provenance. No generated value or provenance was supplied by the provider.
Accepted provenance is input-generation metadata, not authorization or runtime
assertion evidence. No rejection path or other derivation rule was exercised.

Unsupported outputs retain limitations concerning state comparison, preservation,
atomicity, collections/order, absence of side effects, unavailable domain inputs
and complete decompositions exceeding three children. Ordinary implementation test
commands were not substituted for semantic coverage. Planner ambiguities were empty;
no new product decision was silently resolved.

All pre-existing tracked files matched 9e88f5e byte-for-byte before the log append.
Only this grounding directory and a new append-only CODEX entry change. Frozen
protocol, fixtures, policies, planner outputs, production code, derivation code,
Set 2 and historical artifacts remain unchanged. Stage metadata is local in
stage_manifest.json, following the planner-stage convention. No runtime verdicts
are predicted. Stop here before acceptance execution.
