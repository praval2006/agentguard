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
