# Registered-check smoke validation

This minimal document-archiving fixture checks the generalized trusted execution
path outside sample_app. It is separate from the frozen Day-5 and Day-6 evaluations.

Requirements frozen before execution:

- Archiving sets archived to true.
- Archiving sets editable to false.

The implementation deliberately sets only archived. The first acceptance assertion
is satisfied; the second is deliberately contradicted by the retained editable
flag. Both checks use ordinary unittest assertions on the same simple input shape.

The implementation, tests, registry, scenarios, and explicit caller authorizations
were written before execution. authorizations.json binds each exact canonical
scenario to its check and coverage ID. These are trusted fixture-author approvals,
not model-generated authority. The harness loads them unchanged and delegates to
run_acceptance; it neither invokes the verifier directly nor calculates verdicts.

Execution command, from the project root:

```bash
python3 -B -m evaluation.registered_check_smoke.run_smoke
```

The harness preserves the first complete returned result in result.json and refuses
to overwrite it. Scenario definitions are in scenarios.json; result.json retains
check/coverage IDs, authorization matches, structured counts/status, and deterministic
verdicts. No stdout scraping is used. Regression testing is separate.

This demonstrates only controlled trusted-check integration. It is not autonomous
bug discovery, autonomous test generation, arbitrary repository support, semantic
completeness, secure sandboxing, proof of correctness, or an independent benchmark.
