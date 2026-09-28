# Next steps after Evaluation Set 2

These proposals follow the frozen 18-scenario classifications (context 9, schema 7,
registered coverage 2). They neither change this evaluation nor predict new verdicts.

| Candidate | Relevant frozen scenarios | Trust/safety implications | Complexity / capability |
|---|---|---|---|
| Bounded derived/synthetic test inputs | Roast rejection; parcel normalized label, blank fields, absent/non-text fields; unknown practice IDs only with separate absence evidence | Derive only from evidenced domains; preserve product oracle, prohibit invented real identities/auth/state; freeze provenance and inputs before execution | Moderate; core grounding capability, not just convenience |
| Trusted registered-check resolution/binding | Payroll regular/overtime and zero; other payroll obligations only with independently reviewed sufficient coverage | Exact grounded identity, caller-only trust, source freshness/provenance; no model self-authorization or broad coverage inference; future protocol must resolve authorization timing explicitly | Moderate to high; core end-to-end coverage integration |
| Bounded array assertions | Tournament inclusion/points, descending order and empty standings | Fixed bounded array operations, no arbitrary expressions; expectations still require grounded input and tie policy | Moderate; core assertion capability |
| Bounded stateful workflow/output references | Practice answer retrieval and isolation | Requires lifecycle/isolation contracts, bounded steps and typed references; risks cross-request state/auth leakage; does not automatically solve Python object nonmutation | High; substantial core capability with testing-framework scope risk |
| Stronger semantic grounding validation | Roast range composite; fixture-specific question equality; inferred nonmutation obligation review | Review decomposition and evidence provenance without letting a model assign verdicts; cannot promise semantic proof or silently repair outputs | Moderate to high; core trust/quality gate, potentially human-assisted |

## One recommended final architectural improvement

Recommend a bounded derived/synthetic test-value policy before productization.
It addresses a repeated limitation across unrelated stateless features without
adding sessions, workflows, arbitrary code execution or a general-purpose testing
language. It would make a small real demo more representative of ordinary feature
validation while retaining independent expected behaviors from the task.

Scope a future design around finite, provenance-recorded candidates from evidenced
input domains: immediate integer neighbors of explicit bounds, empty/whitespace
text, permitted length-bounded ordinary text and disallowed primitive types. Freeze
chosen values before execution; do not regenerate after results. Expected values
must derive from explicit requirements or reviewed inference, not from observing
implementation responses. Preserve the existing scenario/executor bounds and
unsupported behavior when a complete faithful check cannot be represented.

Do not synthesize authentication, live object IDs, tenant identities, guaranteed
absence, or reset/isolation claims. Quiz unknown-ID behavior is therefore not promised
by this recommendation. No improvement to side-effect observability, arrays, registered
binding or workflows is claimed. Tests remain finite evidence, not exhaustive proof.
A trusted domain policy and auditable derivation matter more than arbitrary free-text
model generation. Validate any future design on fresh tasks; do not optimize for
retrospective PASS counts or rerun frozen Set 2 as a repaired evaluation.

Defer the other architecture candidates for this MVP. In particular, do not conceal
the registered-path gap: current execution infrastructure and exact authorization do
not yet constitute automatic scenario-to-coverage binding. A future trust procedure
would need explicit approval and a new protocol; this one is not amended.

## Productization priorities after that bounded checkpoint

1. Automated LLM provider integration: preserve injected contracts, raw responses,
   instruction/input versions, single-attempt provenance and clear validation errors.
   Separate reasoning from execution and caller-held trust.
2. Simple CLI: explicit task/context/target configuration, staged freezes, deterministic
   reports, no hidden retries or automatic authorization.
3. Coherent end-to-end demo: show observed evidence, abstention and trust limitations;
   label controlled examples and hand-authored trusted coverage honestly.
4. README: installation, commands, supported capabilities and current limitations.
5. Architecture/trust-boundary diagram: task/context to planner to grounder to frozen
   actions to executor/verifier; trusted configuration enters separately.
6. Technical report: reproducible frozen checkpoints, taxonomy and semantic concerns,
   with post-hoc source findings separated from detected evidence.
7. Hackathon/project presentation: concise user problem, real observed demo, honest
   limits, and clear next step without benchmark accuracy or general correctness claims.

No recommendation is implemented in this checkpoint.
