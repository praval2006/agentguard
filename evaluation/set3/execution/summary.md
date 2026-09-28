# Evaluation Set 3 — Final acceptance execution

Frozen checkpoints: protocol fa4193c, fixtures 58f8ead, planner 9e88f5e,
grounding b981480; architecture under evaluation 0e50d12.

Exactly one run_acceptance call per case consumed the unchanged frozen JSON.
Each case ran in a separate process to isolate repository-local imports. Only
profile, shipping and preferences needed a fixture server; each used its existing
application_server context manager, ephemeral numeric loopback URL, and default
application. All three context managers exited cleanly. Catalog and promotion
required no server because every scenario was unsupported.

| Case | PASS | FAIL | UNVERIFIED | Existing orchestrator overall |
| --- | ---: | ---: | ---: | --- |
| Profile | 1 | 0 | 3 | UNVERIFIED |
| Shipping | 2 | 0 | 2 | UNVERIFIED |
| Catalog | 0 | 0 | 5 | UNVERIFIED |
| Promotion | 0 | 0 | 5 | UNVERIFIED |
| Preferences | 1 | 0 | 4 | UNVERIFIED |
| Top-level total | 4 | 0 | 19 | Not provided across cases |

The orchestrator supplies per-case overall verdicts only. No invented cross-case
verdict or extra orchestration pass was added. Composite children: 6 PASS, 0 FAIL,
0 UNVERIFIED. Seven HTTP observations were actually attempted and established:
one standalone plus six children. The three composite parents each retain their
ordered child evidence and deterministic aggregate. Every declared child ran once.
No infrastructure failure, timeout, truncated body or unavailable JSON was observed.
All five case processes exited 0. Unsupported records were normally processed by
the existing verifier, not skipped, reinterpreted or assigned model verdicts.

Grounding executability remains 4/23 (17.39%). Execution outcomes are 4/0/19.
Neither is accuracy or general correctness. Profile's synthetic input provenance
is preserved in execution.input_derivations; status evidence, not provenance,
produced its assertion verdict. Full unchanged result envelopes preserve all
observations, assertion evidence, explanations and nested children.

After the acceptance pass, the full regression suite ran exactly once:
`python3 -m unittest discover -s tests -p 'test_*.py' -v`.
Result: **304 tests, OK, exit code 0**, reported runtime 5.673 seconds.
The exact combined log and attempt/result records are retained separately.
Regression tests are not additional Set-3 evaluation attempts.

No planner/grounder call, repair, scenario retry, fixture modification, policy
change or new capability occurred. Frozen input hashes were checked before and
after work; only this execution directory and the appended CODEX entry change.
No further evaluation or architecture work is initiated. This is the final Set-3
execution checkpoint; the experimental core remains unchanged for freeze.
