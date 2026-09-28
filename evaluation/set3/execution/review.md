# Read-only evidence review

Written after preserving the first result envelopes and their hashes. No expectation,
scenario, derivation, fixture or result was changed. Verdicts below come from the
existing orchestrator and verifier; this review does not recalculate or override them.

## Exact scope of the four top-level PASS results

1. **Profile — Accept free-form nonblank display labels.** PATCH /profile submitted
   the policy-materialized display_name `agentguard-test`. Status 200 was observed
   and was the only asserted condition. The retained JSON also contains that name
   and language `en`, but these were not asserted. This does not establish arbitrary
   label acceptance, absence of hidden vocabulary/uniqueness constraints, persistence,
   normalization or unrelated-field preservation. The frozen grounding concern
   about one-label/status-only sampling remains unresolved.
2. **Shipping — Accept the inclusive whole-gram range.** Two children submitted
   100 and 30000 grams to POST /shipping/quote and each observed the asserted 200.
   This supports acceptance of exactly the two tested bounds. It does not establish
   acceptance throughout the interior range, invalid-input rejection or every
   tariff transition. The parent PASS reflects only these two required children.
3. **Shipping — Return the correctly priced quote.** Separate children submitted
   100 and 30000 grams. Observations matched every assertion: 200; returned weights
   100/30000; integer total_cents 600/3500 respectively; currency AUD. This establishes
   those two concrete tariff samples only. It does not establish the formula over
   all permitted weights, side-effect absence or the full broad planner behavior.
   The repeated weight values belong to different frozen scenarios; none was retried.
4. **Preferences — Reject empty updates and unknown fields.** PATCH /preferences
   with `{}` and, separately, `{"daily_digest_hour": 9}` returned 400 and exact error
   `Provide one or both boolean channel preferences`. Both child assertions matched.
   This supports those two rejected requests. It does not establish rejection of
   every unknown key, persistence preservation or atomicity after mixed updates.

No FAIL occurred, so there is no observed contradictory assertion to report.
No conclusion of defect absence or complete acceptance follows from this result.

## Why the nineteen records remain UNVERIFIED

All nineteen were frozen unsupported scenarios. Each has no runtime observation
and retains its original explanation through the normal verifier. Exact per-record
names and reasons are also preserved in unverified_reasons.json and result envelopes.

- **Profile (3):** stored normalized value/response relationship, preservation on
  invalid input, and preservation of unrelated fields need before/after state or
  trusted coverage; single-response observations cannot establish these relations.
- **Shipping (2):** the invalid-input decomposition exceeded the frozen child bound;
  shipment/payment absence had no supported runtime observable.
- **Catalog (5):** filtering/all-matches and ordered preserved fields require array
  comparisons; no-match additionally lacks a supplied input and empty-array assertion;
  invalid search values have no reviewed derivation authority; nonmutation needs
  state-aware observation. None was replaced with a status or field-existence check.
- **Promotion (5):** the full normalization scenario lacks permitted variants;
  invalid domain codes lack supplied/authorized values; subtotal categories exceed
  the child bound; non-commitment has no side-effect observable; repeated previews
  require a workflow. These frozen limitations were not reinterpreted at execution.
- **Preferences (4):** actual storage, preservation and invalid-update atomicity need
  state comparisons; the malformed primitive decomposition exceeded three children.

These are explanations of the frozen representations, not a new formal postmortem
classification or a claim that no alternative grounding could ever exist.

## Evidence and boundaries

Seven HTTP leaves were established without timeout, truncation or infrastructure
failure. The one synthetic-input provenance record matches the frozen input metadata;
it supplies no verdict or semantic authority. Six composite child verdicts were
retained in declared order and all three parent verdicts came from existing aggregation.
No cookies, output propagation, state reset or workflow was added by the harness.

The limited-sampling concerns remain material even though the selected assertions
passed. Executability and successful sampled assertions are not accuracy, proof of
complete decomposition or independent benchmark evidence. Existing-conversation and
fixture-author methodology remain as previously disclosed. No repair follows review.
