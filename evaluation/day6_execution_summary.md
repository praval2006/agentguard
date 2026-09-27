# Day 6 Deterministic Execution Observations

## Frozen inputs

- Protocol: `13a2b5c`
- Fixtures: `817cfc7`
- Planner outputs: `725532c`
- Grounding outputs: `45ae069`

## Execution

`python3 -B -m evaluation.day6_execute` completed on its first and only run
with exit code 0. Each frozen grounded list was loaded unchanged and passed to
`agentguard.acceptance.run_acceptance`. Complete returned results were serialized
without filtering into the corresponding `caseXX_acceptance.json` files.
No reasoning provider, fixture HTTP server, or fixture test command was invoked
by this acceptance run. Verdicts below are copied from the saved pipeline results.

### case01

Overall verdict: UNVERIFIED.

- Start a queued work order: UNVERIFIED.
- Starting an in-progress order is harmless: UNVERIFIED.
- Reject starting a completed order: UNVERIFIED.

### case02

Overall verdict: UNVERIFIED.

- Accept both duration limits: UNVERIFIED.
- Accept interior duration increments: UNVERIFIED.
- Reject out-of-range durations: UNVERIFIED.
- Reject fractional and off-increment durations: UNVERIFIED.
- Preserve existing reservations on rejection: UNVERIFIED.

### case03

Overall verdict: UNVERIFIED.

- Dispatch updates shipment and both inventory counts: UNVERIFIED.
- Reject empty tracking without state changes: UNVERIFIED.
- Reject insufficient stock without state changes: UNVERIFIED.
- Repeated dispatch does not deduct inventory again: UNVERIFIED.

### case04

Overall verdict: UNVERIFIED.

- Fill one vacancy from the waiting list: UNVERIFIED.
- Leave a full class unchanged: UNVERIFIED.
- Leave a class with no waiting attendees unchanged: UNVERIFIED.
- Support both membership types: UNVERIFIED.

### case05

Overall verdict: UNVERIFIED.

- Schedule a future UTC announcement: UNVERIFIED.
- Deliver at the due time and never early: UNVERIFIED.
- Repeated scheduler checks do not duplicate delivery: UNVERIFIED.
- Withdraw a pending announcement before it is due: UNVERIFIED.
- Withdrawal is limited to the selected announcement: UNVERIFIED.

## Scenario totals

- PASS: 0
- FAIL: 0
- UNVERIFIED: 21

## Separate regression validation

After preserving acceptance results, ran:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

AgentGuard regression suite: 172/172 passed, unittest OK, exit code 0.
Approved escalation provided loopback access for the existing regression tests.

Then ran the five fixture commands exactly as recorded in the frozen manifest:

```bash
(cd evaluation/day6_cases/case01 && python3 -B -m unittest discover -s tests -v)
```

case01: 4/4 tests passed, unittest OK, exit code 0.

```bash
(cd evaluation/day6_cases/case02 && python3 -B -m unittest discover -s tests -v)
```

case02: 3/3 tests passed, unittest OK, exit code 0.

```bash
(cd evaluation/day6_cases/case03 && python3 -B -m unittest discover -s tests -v)
```

case03: 3/3 tests passed, unittest OK, exit code 0.

```bash
(cd evaluation/day6_cases/case04 && python3 -B -m unittest discover -s tests -v)
```

case04: 3/3 tests passed, unittest OK, exit code 0.

```bash
(cd evaluation/day6_cases/case05 && python3 -B -m unittest discover -s tests -v)
```

case05: 4/4 tests passed, unittest OK, exit code 0.

Fixture total: 17/17 tests passed. These separate implementation-test results
did not alter the preserved acceptance results.

## Failures and deviations

- Execution/harness failures: none.
- Infrastructure repairs: none.
- Protocol deviations: none.
- No frozen inputs, implementation, existing tests, or CODEX.md were modified.
- No commits or pushes were made.

This record contains observations only; it makes no architecture-quality claim.
