# Evaluation Set 2 execution freeze

Executed once from frozen grounding checkpoint `66b4de6`:
`python3 -B evaluation/set2/execution/run_execution.py`.
Freeze identifier: commit titled `Freeze Evaluation Set 2 execution results`.

## Preservation and method

The harness checked all frozen Set-2 and protocol bytes against 66b4de6 before
execution, recorded their SHA-256 hashes in run_started.json, and created an
exclusive marker that prevents reruns. Each case received one run_acceptance call
with its loaded frozen scenarios unchanged. No retries, scenario repair, manual
verdict calculation, grounding or planner regeneration occurred.

Each *.result.json is the complete returned run_acceptance structure, serialized
once without alteration. Its SHA-256 was recorded immediately, before subsequent
analysis. Each *.execution.json records the attempt, input hash, caller configuration,
server lifecycle and result hash. execution_manifest.json collects these records.
Only after all five results were saved and hashed were mechanical metrics computed
in metrics.json and this summary written. No result file was overwritten.

## Mechanical results

| Case | Top-level PASS | FAIL | UNVERIFIED | Overall |
|---|---:|---:|---:|---|
| 01_roast_temperature | 1 | 0 | 3 | UNVERIFIED |
| 02_parcel_label | 0 | 0 | 4 | UNVERIFIED |
| 03_payroll | 0 | 0 | 4 | UNVERIFIED |
| 04_tournament | 0 | 0 | 4 | UNVERIFIED |
| 05_quiz_attempt | 1 | 0 | 3 | UNVERIFIED |
| Total | 2 | 0 | 18 | — |

All 20 frozen scenarios appear in order. All five cases completed; none stopped.
Composite children are separate: 2 PASS, 0 FAIL, 1 UNVERIFIED, processed once in
frozen order. Parent child_counts retains required=3, pass=2, fail=0, unverified=1;
parent verdict is UNVERIFIED. Child counts are not added to the 20-scenario total.
Registered-check executions: 0. Payroll has no registered representation, and no
check, registry, authorization or trusted configuration was attached to its outputs.
No metric here is an accuracy, correctness percentage or semantic coverage claim.

## HTTP lifecycle and infrastructure

Only the two cases containing HTTP actions started their existing
repository/server.py:application_server() context managers. Case repository paths
were temporarily placed on sys.path for the existing app imports; modules were
removed from the import cache between cases, without editing source. Only the
yielded base_url was passed as trusted execution configuration. No readiness probes,
extra HTTP requests, state changes or fixture-specific assertions were added.

- Roast: http://127.0.0.1:50066, startup and shutdown succeeded.
- Practice: http://127.0.0.1:50070, startup and shutdown succeeded.
- Other cases: no server required or started.

The existing adapter chose ephemeral loopback ports. Approved escalation permitted
local binding. No infrastructure errors were recorded. HTTP evidence was established
for all four executable leaves and remains bounded in the exact result envelopes.
No external service, registered check, implementation-side test rerun or historical
evaluation harness was used. Bytecode was disabled; no fixture runtime cleanup was
needed. Ephemeral practice state ended with the fixture context.

## Previously recorded issues: observed effect only

The unchanged temperature composite returned two passing endpoint children and one
unsupported child, making its parent UNVERIFIED under existing aggregation. Its
potential grounding-contract issue remains unresolved; execution does not validate
its semantic decomposition. No child was removed or repaired.

The practice creation result includes the frozen question assertion: expected and
observed both '7 + 5', assertion PASS and scenario PASS. The fixture-specific
expectation caused no observed contradiction in this run, but execution does not
establish it as a general product requirement. No counterfactual rerun was performed.
Full postmortem classification is deferred.

## Regression and integrity

After all acceptance results were saved and hashed, separately ran:
`python3 -m unittest discover -s tests -p 'test_*.py' -v`.
283 tests, OK, exit 0; approved escalation allowed existing loopback regression tests.
This regression is not part of the Set-2 acceptance evidence.

Frozen inputs matched before execution and after shutdown. Final audit also confirms
unchanged protocol, manifest, fixtures, task/context, planner/grounding artifacts,
Case-3 check/registry, production AgentGuard code, existing tests and historical
Day-5/Day-6/smoke artifacts. Only this new execution directory and an appended CODEX
entry changed. No fixture implementation suite was rerun or used to override results.
