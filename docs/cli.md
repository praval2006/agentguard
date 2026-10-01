# Verification CLI

From the checkout, install in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e .
export OPENAI_API_KEY='your-key'
export AGENTGUARD_MODEL='gpt-5.6-terra'  # optional; provider default is gpt-4.1-mini
agentguard --help
agentguard verify --task task.md --context context.md
# Equivalent from the checkout:
python3 -m agentguard verify --task task.md --context context.md
```

Both files must be readable nonblank UTF-8, at most 32000 characters each. Reads
stop at limit + 1 characters; oversized input is rejected without truncation.
Supply only the context you intend to send to OpenAI. There is no crawling, context
discovery, dotenv loading or model-selected file access. Blank context is a CLI
input error even though the lower-level planner permits it.

A completed invocation makes one OpenAI planner request and one grounder request,
using the same provider instance. Existing planner and grounding validation must
succeed before run_acceptance receives the grounded scenarios unchanged. No retry
or repair occurs. This command spends API credit and then executes supported
checks; use trusted context and an appropriate local target.

`--base-url http://127.0.0.1:PORT` forwards a caller-selected target to the existing
HTTP executor. The CLI does not start a server. Existing loopback-only URL, method,
header, size, timeout and redirect restrictions remain. Missing or rejected target
configuration retains the executor's UNVERIFIED result. Commands retain the fixed
sample-app allowlist, source-checkout root and normal JSONL recording behavior;
editable installation is recommended for that legacy capability. Installing the
package elsewhere does not enable tests in arbitrary projects. There is no CLI
registry/coverage authorization or derivation-policy configuration in this version.

The report shows task path, scenario count, each existing verdict and selected
assertion evidence (expected, observed, type, reason and truncation flags where
present). Composite children remain nested under their parent. Raw response bodies,
headers and command logs are not dumped. Selected assertion values can still contain
sensitive application data; terminal control characters are escaped. No evidence
is invented when a value is unavailable, and observed null stays distinguishable
from missing evidence.

`--show-reasoning` adds explicit requirements, inferred behaviors, ambiguities and
grounded action types. These are structured public model outputs, not chain-of-thought.
Default output prioritizes verification evidence. The formatter never aggregates or
changes verdicts: existing run_acceptance/verifier own both individual and overall
results. PASS means represented assertions passed, FAIL means observed contradiction,
and UNVERIFIED means the represented behavior was not reliably established.

Exit codes: **0 PASS**, **1 FAIL**, **2 UNVERIFIED**, **3 operational error**.
Help exits 0. Argument/input/configuration/provider/schema/unexpected runtime errors
exit 3 with a stage-specific message, without raw exceptions or an invented verdict.
Existing executor outcomes (including safely unestablished execution) are preserved;
they are not converted into operational exceptions. A schema failure prevents execution.
No key or environment dump is printed. Frozen evaluation artifacts are not used.

## Explicit reviewed workflow

The existing `verify` command remains the legacy automatic plan → ground → execute
path. The new two-stage path requires human decisions for inferred scenarios.
Neither path changes execution policies or verifier authority.

Prepare a review (one planner request; no grounding or execution):

```sh
python3 -m agentguard review --task task.md --context context.md --output review.json
```

The output file must not already exist. The command prints EXPLICIT, AGENTGUARD
SUGGESTION and AMBIGUITY sections. Reasons are **model rationale**, not verified
repository evidence. Exit 0 means preparation succeeded, not a verification PASS.

Inspect `review.json` and create `decisions.json` manually. Its entire value is a
JSON list of unchanged Phase-1 decision records, for example:

```json
[
  {
    "revision": "<copy revision from review.json>",
    "scenario_id": "<copy an inferred scenario_id from reviews>",
    "state": "ACCEPTED"
  }
]
```

States are ACCEPTED, DISMISSED or PENDING. Omitted inferred scenarios remain PENDING.
Explicit scenarios require no decision and reject decision records. `[]` is valid;
there is no automatic acceptance of suggestions. Do not edit the review artifact to
record decisions. Selection does not clarify ambiguities.

Resume (one grounder request, no planner request, then existing bounded execution):

```sh
python3 -m agentguard verify-reviewed --review review.json --decisions decisions.json \
  --context context.md --base-url http://127.0.0.1:8000
```

Both commands use the existing OpenAI configuration and spend API credit when run
with the real provider. No retry/fallback is added. Only selected scenarios are
sent to grounding, preserving original order and source labels. The unlinked
`inferred_behaviors` list is withheld from the grounder because no validated mapping
exists between its entries and accepted scenarios. Its full original content stays
in review/report metadata. Explicit requirement and ambiguity lists remain supplied
to grounding; their text is not a validated coverage mapping.

Empty selection still calls the existing grounder with zero scenarios and uses
existing acceptance empty-set semantics: overall UNVERIFIED, empty results. Pending
and dismissed items never receive a verification verdict. Resume exits with the
existing codes: 0 PASS, 1 FAIL, 2 UNVERIFIED, 3 operational error. Invalid artifacts,
decisions and changed/missing context fail before the grounding request.

### Artifact and backend API

`agentguard.reviewed_workflow` exports:

- `prepare_review(task_text, repository_context, *, reasoning_provider)`
- `validate_review(artifact, repository_context)` → reconstructed PlanningProposal
- `resume_reviewed(artifact, decisions, repository_context, *, grounding_provider,
  base_url=None, recorder=None, repository_root=None, registry=None,
  coverage_authorizations=None, derivation_policy=None)`

Review JSON has exactly `schema` (`agentguard.review.v1`), `proposal` (the complete
original planner dictionary), `revision`, `context_sha256`, and `reviews` (Phase-1
default scenario review records). Revision and review metadata are recomputed from
the proposal on resume; inconsistent changes are rejected. The context hash binds
the same UTF-8 text, including whitespace. JSON reads are capped at 1,048,576
characters and reject duplicate keys/nonfinite constants. Existing grounder input
bounds also apply at preparation. No timestamps, random IDs or credential/config
fields are added. Planner prose may contain sensitive caller data; these are local
artifacts, not automatically shareable reports.

Resume returns `revision`, `proposal`, `contract`, `grounded`, and `verification`.
The contract contains all reviews and the Phase-1 selected_plan; verification is
exactly the existing acceptance result. Original metadata remains separate from
results. There is no frontend connection or full report model yet.

Integrity hashes are not signatures or human authentication: someone able to
rewrite the proposal and every matching hash/decision can produce a consistent new
artifact. The caller must obtain decisions from the human and protect stored files.
Approval grants product-intent authority only; it does not grant registered-check
coverage, input derivation, HTTP policy bypass or verdict authority. Separate core
configuration remains separately supplied. The CLI exposes only the HTTP base URL,
not new registry/derivation authority flags.
