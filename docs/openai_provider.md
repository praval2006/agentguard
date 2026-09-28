# OpenAI reasoning provider

Install the optional integration from the repository root (Python 3.10+):

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
export OPENAI_API_KEY='your-key'
export AGENTGUARD_MODEL='gpt-4.1-mini'  # optional; this is the default
```

Do not commit keys. `.env.example` contains placeholders only; no dotenv loader is
provided. Missing/blank keys and explicitly blank model configuration raise
`OpenAIProviderError`. Configuration is captured when constructing the provider.
Model availability is account-dependent; choose a Responses API model supporting
JSON mode. No automatic model fallback occurs.

```python
from agentguard.providers.openai_provider import OpenAIProvider
from agentguard.planner import plan_acceptance
from agentguard.grounding import ground_scenarios

provider = OpenAIProvider()
# task_text and repository_context are explicitly selected strings from your caller.
plan = plan_acceptance(task_text, repository_context, reasoning_provider=provider)
scenarios = ground_scenarios(
    plan, repository_context, grounding_provider=provider,
    # derivation_policy=trusted_policy,  # optional, independently reviewed by caller
)
```

Each invocation makes one official SDK Responses request. A two-stage call therefore
makes two paid requests. Nothing runs on import; automated tests mock the boundary.
Use these existing entry points so their input limits and output validators apply;
the adapter itself is transport, not a replacement validator or repository reader.

The adapter uses JSON mode and the unchanged role instructions. It intentionally
retains existing Python validation instead of duplicating the evolving scenario
schema in a strict API schema (which would also constrain opaque JSON payloads).
JSON mode guarantees neither schema compliance nor semantic grounding. Grounding
uses an API-only `{"scenarios": [...]}` object envelope, unwrapped into the existing
list return value without altering entries. Planner returns its original dictionary.
There is no output repair, truncation, fallback reasoning or retry; SDK retries are
explicitly zero. Requests use a 60-second SDK timeout, 8192 output-token ceiling,
`store=False`, and the fixed official API origin. The decoded text is capped at
262144 characters. This is not an end-to-end memory quota or data-retention guarantee.
No tools, crawling, file loading, subprocesses, or execution results are supplied.

`OpenAIProviderError` reports missing SDK/configuration, API/network failure, refusal,
incomplete output, invalid JSON (including duplicate keys/nonfinite constants), or
invalid transport envelopes without echoing keys or raw request/response data.
Valid JSON that violates the planner/grounder schema is rejected by the existing
boundary's validation errors, unchanged. Credentials and supplied context are sent
to OpenAI; the adapter does not log them. SDK/HTTP debug logging configured externally
is outside this adapter. Clients are closed after every invocation.

The LLM proposes acceptance intent and representations only. Existing deterministic
code validates structures and identities, enforces derivation/execution policy,
observes behavior and assigns PASS/FAIL/UNVERIFIED. Model output cannot add verdict
fields to bypass validation. No automatic acceptance execution is part of this API.

References: [OpenAI JSON mode and Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini).

## Manual live reasoning smoke

After installing the dependency and exporting OPENAI_API_KEY, run from the repository
root (this spends API credit):

```sh
AGENTGUARD_MODEL=gpt-5.6-terra python3 -m scripts.live_openai_smoke
```

The model override uses the configuration reported manually verified for this project;
the provider default remains unchanged. The script uses a small embedded fictional
username task/context. A completed run makes exactly two model requests: one through
`plan_acceptance`, then one through `ground_scenarios` with the exact validated plan.
It prints each output only after its existing validation succeeds. No retries occur;
a configuration, API or validation failure stops immediately, potentially before
both requests are made. Planner output remains visible if grounding fails.

This is manual opt-in only, never part of automated tests. No application HTTP
request, command execution, acceptance engine or verdict code is invoked. Unsupported
scenarios are legitimate when the example lacks sufficient execution evidence; no
fixtures, sample values or derivation authority are added to force executability.

## Grounding contract compatibility

The first user-run live smoke validated its planner output, then rejected the
model's grounder output with `ValueError: action has missing or unexpected fields`.
That means an action's required/allowed key set was violated. The raw response was
not provided, so the particular missing/extra key and action variant are unknown.
Examples such as `body` instead of `json`, missing `method`, or assertions nested
inside action reproduce the class of error; they are not claims about that response.
The deterministic trust boundary rejected it before any execution.

The provider now appends a grounder-only exact-key reference: required/optional
fields, sibling assertion placement, forbidden aliases, omission rather than null,
standalone/composite distinctions, all assertion variants, and compiler-owned versus
model-requested derivation fields. The original grounding instructions still apply.
Planner request construction is unchanged. This improves explicitness but is not
proof of live-model conformance; the smoke has not been rerun for this fix.

Strict API Structured Outputs is **not** enabled. Its closed-object requirements
(`additionalProperties: false`) do not cleanly preserve arbitrary payload/header/
variable keys and opaque values in the existing contract. Unions alone are not the
obstacle. Restricting those objects, enumerating repository-specific keys or encoding
them into an alternate shape would change the contract or require coercion. We use
the allowed prompt-strengthening approach instead; JSON mode remains syntax-only.
See the [official supported-schema restrictions](https://developers.openai.com/api/docs/guides/structured-outputs#supported-schemas).
Existing ground_scenarios/validate_scenario validation is authoritative and unchanged.
Malformed output still raises; no retry, stripping fields, coercion or repair occurs.
