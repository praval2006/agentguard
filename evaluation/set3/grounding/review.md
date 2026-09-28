# Post-freeze read-only grounding review

This review was written after all five first responses had been preserved and
validated. No output was repaired or regenerated. Schema validation establishes
structure and identity, not faithful semantic coverage. Only the same frozen
planner/context evidence and policy records are used here; no additional fixture
source or test coverage was inspected to strengthen grounding.

## Executable representations

### Profile scenario 4 — Accept free-form nonblank display labels

PATCH /profile and display_name are documented. The raw body omits display_name and
requests neutral_nonblank_text using display-name-text. The unchanged compiler
accepts it and records the context hash, exact constraint, field, rule and generated
value in the compiled action and derivations.json. HTTP 200 is the documented
successful response. No header, identity, secret or runtime state is invented.

**Semantic concern:** one neutral label and status 200 can observe acceptance of that
label, but cannot establish absence of vocabulary, format, uniqueness or identity
restrictions generally. The selected label may happen to satisfy an undisclosed
restriction. This is narrower evidence than the broad planner wording; exact name,
source and reason preservation does not cure this potential semantic weakening.
No persistence or normalization claim should be inferred from this check. The output
remains frozen for later postmortem rather than being improved here.

### Shipping scenario 1 — Accept the inclusive whole-gram range

Two independent POST /shipping/quote children submit the documented bounds 100 and
30000, each asserting documented success status 200. These are supplied domain
bounds, not manually manufactured synthetic values. The context describes a
stateless quote; neither child depends on the other, a reset or a previous output.

**Semantic concern:** both endpoints are checked but the interior range is not.
The planner says "throughout" the range. This finite boundary selection is useful
but does not establish that broader wording; complete-decomposition fidelity is a
postmortem concern even though both children are structurally valid. No unsupported
filler or assertion about interior values is inserted. The frozen result is unchanged.

### Shipping scenario 3 — Return the correctly priced quote

Two independent POST /shipping/quote children use the same supplied bounds. Both
assert status 200, returned weight equal to submitted weight, integer total_cents,
and currency AUD. Expected totals follow the explicitly supplied tariff:
100 grams is one started kilogram, so 500 + 100 = 600 cents; 30000 grams is thirty,
so 500 + 3000 = 3500 cents. This arithmetic applies an evidenced rule; the input
compiler did not synthesize expected response values. Response paths are documented.

**Semantic concern:** these two examples observe partial- and whole-kilogram prices
but not every tariff transition or valid weight. A broader correctness claim would
exceed the evidence. This is a sampling/coverage limitation and possible mismatch
with complete-decomposition expectations, not a structural-validation failure.
No array comparison, persistence or side-effect absence is claimed.

### Preferences scenario 4 — Reject empty updates and unknown fields

Both children use documented PATCH /preferences. The empty JSON object directly
represents the explicitly prohibited empty update. The second submits
{"daily_digest_hour": 9}: this field and value are explicitly present in the
context, while only email_enabled and push_enabled are editable. It is therefore a
context-evidenced noneditable field, not an invented key or generated runtime value.
Both assert the documented 400 response and exact documented error text.

These are independent rejection observations, not a before/after sequence. No
stored value is asserted and no default state continuity is assumed. The two
children represent the two named rejection categories. **Limitation:** one supplied
noneditable field samples the wider unknown-field domain; it is not exhaustive.
The check does not establish invalid-update atomicity (a separate unsupported
planner scenario). No fabricated unknown identifier was introduced.

## Cross-cutting review

- All seven HTTP leaves use supplied methods/routes. Bodies use supplied bounds,
  an explicitly empty update, a supplied noneditable field/value, or the single
  policy-compiled neutral text. Expected statuses, error text, scalar response
  values and integer type are supported by the context/tariff.
- The single derivation stays within reviewed arbitrary text. Provenance is retained;
  it is neither runtime evidence nor authority to assert broad semantic coverage.
- No cookies, authentication, IDs, output chaining, workflow, reset or dynamic
  fixture state is assumed. The mutating profile check has no dependent child.
- No field-existence assertion substitutes for array equality, ordering, atomicity,
  preservation or side-effect absence. Those behaviors remain unsupported.
- Composites carry exact planner behavior and two required children each. Legacy
  standalone shapes remain unchanged. The shipping sampling concerns above mean
  structural success must not be reported as proven semantic completeness.
- Over-conservatism is also possible: broad invalid-input scenarios were declined
  rather than selecting incomplete primitive categories within three children.
  Catalog has no reviewed derivation facts. No coverage conclusion about normal
  implementation commands was invented. These choices remain available for later
  postmortem; no additional grounding attempt was made.

No acceptance verdict, runtime success, defect detection or general architecture
improvement is claimed. This is an engineering evaluation with existing-conversation
and fixture-author exposure, not independent benchmark evidence.
