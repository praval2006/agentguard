# Set 3 fixture-stage review and trusted setup

This is administrative setup documentation, not planner/grounder context.
Specifications/protocol/original manifest remain frozen at fa4193c. The new
fixture_manifest.json extends stage metadata without rewriting those originals.

## Implementation and leakage review

All task.md files are byte-identical copies of their spec.md. Reviewed source,
interfaces, contexts, comments and tests against those specs before freeze.

- Profile updates the caller-owned dictionary and returns the stored normalized
  name. Blank/non-string requests preserve state; unrelated fields are retained.
  The default Guest label is an ordinary initial profile value, not a sample request
  added to facilitate reasoning. Test names/values remain ordinary developer data.
- Shipping uses exact integer grams and started-kilogram arithmetic, preserving both
  specified limits and rejecting booleans/non-integers without clamping. Its tariff
  and response fields come from the spec. There is no shipment/payment integration.
- Catalog keeps arrays, ordering, empty matches and copies of records; stationery
  records are ordinary deterministic inventory, not expected-answer annotations.
- Promo uses the specified LOCAL10 configuration, whole-cent downward rounding,
  input validation and repeatable calculation without stored orders/payments.
- Preferences validates the full patch before updating the caller-owned record;
  false, omitted channels and daily_digest_hour retain their specified meanings.
  Persistence and isolation are normal application behavior, not special check routes.

No intentional defects, hidden outcomes, expected acceptance scenarios/verdicts,
coverage annotations or outcome targets were introduced. No requirements were
weakened to fit HTTP scalar assertions or synthetic derivations. Source excerpts
in context match app.py/server.py exactly; normal INTERFACE.md is included unchanged.
Implementation-test examples/results are not included in context; only filenames
and the ordinary test command are supplied. No implementation corrections were needed
after the first successful test runs.

Keyword scan of task/context/repository files for intentional, bug, broken,
AgentGuard, expected verdict, should catch, PASS, FAIL, UNVERIFIED and deriv found
only the word 'passes' in neutral transport documentation. Manual review found no
benchmark coaching or equivalent leakage. All five contexts are below 32,000 chars.

## Pre-reasoning caller-reviewed policies

Codex authored these policies in the fixture/setup role under the frozen protocol.
They are not independently human-authored, model-produced trust, or an independent
blinding claim. Files are cases/<id>/derivation_policy.json, separate from task/context.
No provider has seen these fixtures in an evaluation call, and no rule/scenario
selection, concrete derived value, or expected acceptance assertion was generated.

Each JSON file contains only context_sha256 and constraints. A trusted future caller
may deserialize constraints with InputConstraint(**record), then construct
DerivationPolicy(context_sha256, tuple(constraints)). Ordinary structure validation
and validate_context were performed now; no derive/materialize/grounding call ran.

Reviewed constraints:

- Display name: explicitly free-form, nonblank, no format/domain/identity meaning;
  arbitrary_text bound to PATCH /profile and display_name.
- Weight: inclusive 100..30000 integer quantity, plain_scalar bound to
  POST /shipping/quote and weight_grams.
- Catalog: empty policy. Search terms select repository catalog information;
  no authority to invent lookup values is supplied.
- Promo: nonnegative integer subtotal quantity only, bound to
  POST /promotions/preview and subtotal_cents. No constraint for the domain promo
  code and no authority to invent recognized/unrecognized code identities.
- Preferences: two plain_scalar boolean constraints for PATCH /preferences,
  email_enabled and push_enabled. These are channel choices, not user identities.

All five policies include exact context hashes and literal quotations; the two
preference constraints share an interface quote. Five constraints total. No policy
records concern response expectations, headers, identifiers, ownership, state,
side-effect absence or coverage authorization. Policy structure validation does not
prove source meaning; this recorded review is the trusted pre-reasoning step.
Do not add/alter authority based on later reasoning or execution outcomes.

## Test evidence and boundary

Each repository ran python3 -B -m unittest discover -s . -p 'test_*.py' -v:
6/6 passed (five core application methods and one transport method), 30/30 total.
Transport tests use standard-library HTTP clients against local servers to verify
normal transport, route rejection and JSON-object handling. They are implementation
suite checks, not AgentGuard acceptance evaluation. Each server closes on context exit.

Separate existing regression: 304/304 passed. Approved loopback escalation was used
for fixture transport and existing regression tests. No external network/services,
new dependencies, registered checks or acceptance coverage metadata were added.
No Set-3 planner, grounder or acceptance execution occurred. Existing regression
exercises its own components; it is not Set-3 reasoning. No historical harness ran.
