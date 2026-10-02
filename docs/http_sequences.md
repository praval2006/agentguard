# Bounded HTTP observation sequences

A standalone `http_sequence` represents one accepted behavior observed through
2–4 ordered HTTP operations against the same configured base URL. It uses the
existing HTTP executor and deterministic verifier. No model participates during
execution. Existing standalone scenarios and independent composites are unchanged.

## Exact schema

```json
{
  "name": "Preserve label while changing state",
  "source": "explicit",
  "reason": "The supplied requirement preserves the label during this transition",
  "action": {
    "type": "http_sequence",
    "steps": [
      {
        "name": "before",
        "action": {"type": "http_request", "method": "GET", "path": "/record"},
        "assertions": [
          {"type": "status", "equals": 200},
          {"type": "json_field", "path": "state", "equals": "open"}
        ]
      },
      {
        "name": "update",
        "action": {"type": "http_request", "method": "PATCH", "path": "/record", "json": {"state": "closed"}},
        "assertions": [{"type": "status", "equals": 200}]
      },
      {
        "name": "after",
        "action": {"type": "http_request", "method": "GET", "path": "/record"},
        "assertions": [
          {"type": "status", "equals": 200},
          {"type": "json_field", "path": "state", "equals": "closed"}
        ]
      }
    ]
  },
  "assertions": [
    {
      "type": "json_equal",
      "left": {"observation": "after", "path": "label"},
      "right": {"observation": "before", "path": "label"}
    }
  ]
}
```

This is an illustrative interface, not a discoverable repository capability.
Actual grounding needs evidence for every endpoint, request, identifier, status,
field and comparison relationship. Missing evidence makes the whole scenario
unsupported; structural validation cannot prove semantic completeness.

Parent keys are exactly `name`, `source`, `reason`, `action`, `assertions`.
Name/reason are nonblank, source is `explicit` or `inferred`. Parent behavior and
variables are absent, following the legacy standalone identity convention.
Action keys are exactly `type`, `steps`; step keys exactly `name`, `action`,
`assertions`. Each step uses the existing HTTP action schema (including optional
JSON, headers and deterministically compiled derivations). No other action kinds,
nesting, optional steps or request substitution are permitted.

Each step has 1–8 existing status/json_field/json_exists/json_type assertions,
including at least one expected status. These implement literal comparisons and
preconditions without introducing another literal assertion language. The parent
has 0–8 `json_equal` assertions with exactly `type`, `left`, `right`; each reference
has exactly `observation`, `path`. Empty parent assertions are useful for transitions
or deletion readback fully expressed by required step assertions.

## Bounds and semantics

- 2–4 required steps; at most 8 assertions per step and 8 cross assertions (40 total).
- Unique names match `[A-Za-z][A-Za-z0-9_]{0,63}`.
- All sequence assertion paths: at most 256 characters and 8 nonblank dotted
  dictionary segments. No array indexing, collection comparison or expressions.
- Entire compact sequence: at most 32,000 UTF-8 bytes of finite JSON.
- Existing HTTP policy: numeric loopback target, no redirects/cookies/proxies,
  2-second network deadline per request, 32,768-byte request/response body caps.
  At most four such deadlines; there is no new overall wall-clock guarantee.
- Existing JSON bounds (10,000 nodes, depth 32, 32,000 text/key characters) and
  selected string evidence truncation (512 characters) remain in effect.

`execute_http_sequence(scenario, *, base_url=None)` is dispatched automatically
by `run_acceptance`. All inputs are validated and snapshotted before execution.
Steps run once in order. The first non-PASS required step stops further requests;
this is fixed fail-closed behavior, not user-defined branching. No retries or
repairs occur, and unexpected programming errors propagate.

The observation envelope is exactly `{"type":"http_sequence_result","steps":[...]}`.
Each record is exactly `{"name":...,"observation":...}` with an existing HTTP
observation or null, in declared order. It is a prefix when execution stopped.
Malformed envelopes or mismatched names/order yield unavailable evidence.
`verify_observation` validates the scenario and independently computes step and
cross-assertion results; it accepts no supplied step verdicts. Successful required
steps expose named JSON observations. Unexecuted steps remain UNVERIFIED.

Cross equality compares actual scalar values: JSON numbers compare numerically,
booleans are distinct from numbers, and null differs from a missing field. Missing,
invalid, oversized, or non-scalar evidence yields UNVERIFIED. Both present scalars
produce PASS if equal and FAIL otherwise. Right-hand values appear as `expected`,
left-hand values as `observed`, with both references retained. Full values are
compared before evidence truncation. Any required contradiction yields overall
FAIL; otherwise any missing evidence yields UNVERIFIED; only all required checks
passing yields PASS. Contradictory preconditions remain FAIL with later checks
UNVERIFIED, rather than executing against an unestablished starting state.

The result retains ordered child step results and cross-assertion evidence.
Parsed responses appear once in the observation envelope, not in child results.
Execution metadata retains per-step HTTP provenance/reasons, without copying raw
logs. Parsed JSON can contain sensitive data; callers control storage/reporting.
Observation authenticity remains a trusted caller obligation for direct verifier use.

## Boundaries and generalization

The executor does not reset the application between steps. It does not provide
isolation, rollback, cleanup, durable persistence, authentication/session transfer,
returned-ID chaining, or target lifecycle management. A failed sequence can leave
mutations behind. Different scenarios may also affect each other. Targets and
execution authorization remain caller responsibilities.

The grounder may propose this primitive only for complete, evidence-backed ordered
observations. Caller-reviewed input derivations retain their existing authority;
if a step's derivation cannot be justified, the whole sequence becomes unsupported.
Planner/review identity, human intent decisions and registered coverage authority
are unchanged. The OpenAI serialization reference describes the same schema;
there is no live-model quality claim.

Potentially representable classes include scalar before/after preservation, rejection
without scalar state change, evidenced state transitions, repeated fixed operations,
and deletion followed by a documented readback. Missing endpoints, unknown IDs,
collection-wide invariants, hidden state and authentication workflows remain limits.
Frozen Set 3 was not changed or rerun; no measured coverage improvement is claimed.
