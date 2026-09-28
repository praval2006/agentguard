# Evaluation Set 3 planner freeze

Protocol: fa4193c. Fixtures: 58f8ead. Architecture: 0e50d12.
Freeze identifier: commit titled Freeze Evaluation Set 3 planner results.

Codex supplied one structured response per case in the existing project conversation.
A manual injected callable returned it once to unchanged plan_acceptance(). Each
response was saved before validation; each valid output was immediately preserved
byte-identically. No repair, retry, regeneration or external model API call occurred.
This is not independently blinded: Codex has prior project/fixture context. Reasoning
evidence was restricted to the same-case frozen task/context; policies, test results,
other repositories and evaluation administration were not passed in the request.

The manifest preserves exact planner instructions/hash, input references/hashes,
response hashes, attempt counts and validation status. Structural validity establishes
representation only, not semantic completeness or quality.

| Case | Scenarios | Explicit | Inferred | Ambiguities | Attempts | Validation |
|---|---:|---:|---:|---:|---:|---|
| 01_profile_display_name | 4 | 4 | 0 | 0 | 1 | valid |
| 02_shipping_weight_quote | 4 | 4 | 0 | 0 | 1 | valid |
| 03_catalog_lookup | 5 | 5 | 0 | 0 | 1 | valid |
| 04_promo_preview | 5 | 5 | 0 | 0 | 1 | valid |
| 05_notification_preferences | 5 | 5 | 0 | 0 | 1 | valid |
| Total | 23 | 23 | 0 | 0 | 5 | all valid |

All cases completed, none stopped. These are descriptive counts, not quality scores.
Zero ambiguity entries reports provider output, not proof that product specifications
are unambiguous. No executability estimate or future representation/verdict is assigned.

## Frozen scenario names

### 01_profile_display_name

- Store and return the normalized display name
- Reject invalid names without changing the stored name
- Preserve unrelated profile fields
- Accept free-form nonblank display labels

### 02_shipping_weight_quote

- Accept the inclusive whole-gram range
- Reject invalid weights without coercion
- Return the correctly priced quote
- Quote without creating shipments or payments

### 03_catalog_lookup

- Find all matching products after term normalization
- Preserve product fields and code ordering
- Return an empty collection for no matches
- Reject invalid search terms
- Leave the catalog unchanged

### 04_promo_preview

- Return a normalized and correctly calculated promotion preview
- Reject invalid promotion codes
- Accept only nonnegative integer subtotals
- Preview without committing a purchase or consuming the promotion
- Allow repeated promotion previews

### 05_notification_preferences

- Store and return supplied boolean choices
- Preserve omitted and unrelated preferences
- Reject malformed preference values
- Reject empty updates and unknown fields
- Keep invalid updates atomic

## Integrity and scope

Frozen evaluation artifacts matched 58f8ead before reasoning and after preservation.
Task/spec copies, contexts, policies, fixture tests/source, Set-3 protocol/manifests,
Set 2 and historical evaluations remain unchanged. Only planner artifacts and an
appended CODEX entry changed; production code and tests are unchanged.
No grounding, synthetic requests, action schemas, registered checks, HTTP acceptance
checks, acceptance execution or fixture repair occurred. No test suite was rerun;
the previous recorded regression baseline remains 304/304. This checkpoint stops
before grounding.
