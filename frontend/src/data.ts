// Illustrative playback of the existing controlled subscription demonstration.
// These records are presentation data, NEVER results of a live frontend request.
export type Verdict = "PASS" | "FAIL" | "UNVERIFIED";
export interface Evidence {
  id: string;
  title: string;
  verdict: Verdict;
  observation: string;
  expected?: string;
  observed?: string;
  reason: string;
}
export const demo = {
  kind: "illustrative-controlled-playback" as const,
  task: "Add subscription cancellation",
  implementationTests: "2 / 2", // subscription-specific tests, not the full sample suite
  overall: "FAIL" as Verdict,
  endpoint: "POST /subscriptions/1/cancel",
  evidence: [
    {
      id: "state",
      title: "Subscription becomes cancelled",
      verdict: "PASS",
      observation: 'HTTP 200 · status="cancelled"',
      expected: 'status = "cancelled"',
      observed: 'status = "cancelled"',
      reason: "The supported status assertion matched the observed response.",
    },
    {
      id: "access",
      title: "Premium access is revoked",
      verdict: "FAIL",
      observation: "HTTP 200 · premium_access=true",
      expected: "premium_access = false",
      observed: "premium_access = true",
      reason: "The observed access flag contradicted the acceptance assertion.",
    },
    {
      id: "repeat",
      title: "Repeated cancellation is safe",
      verdict: "UNVERIFIED",
      observation: "Insufficient supported observation",
      reason:
        "The available controlled HTTP interface does not preserve the same subscription across requests.",
    },
  ] satisfies Evidence[],
};
export const phases = [
  "Reading requirements",
  "Planning acceptance scenarios",
  "Grounding executable checks",
  "Executing observations",
  "Collecting evidence",
];
export const stages = [
  {
    name: "PLAN",
    description:
      "AgentGuard proposes explicit and inferred behaviours. You review suggestions before grounding.",
    label: "INPUT → ACCEPTANCE INTENT",
    code: "task: subscription cancellation\ncontext: selected repository facts\n\nexplicit: cancellation changes status\nsuggestion: revoke premium access\nreview: PENDING → human decision",
  },
  {
    name: "GROUND",
    description:
      "After human selection, it maps accepted behaviours to supported observations without inventing repository facts.",
    label: "INTENT → SUPPORTED CHECK",
    code: "action:\n  type: http_request\n  method: POST\n  path: /subscriptions/1/cancel\nassertion:\n  premium_access equals false",
  },
  {
    name: "EXECUTE",
    description: "Bounded deterministic execution performs supported checks.",
    label: "CHECK → OBSERVATION",
    code: 'target: controlled loopback interface\nmethod: POST\n\nHTTP 200\n{\n  "status": "cancelled",\n  "premium_access": true\n}',
  },
  {
    name: "EVIDENCE",
    description: "Observed results produce PASS, FAIL, or UNVERIFIED.",
    label: "OBSERVATION → VERDICT",
    code: "assertion: premium_access\nexpected:  false\nobserved:  true\n\nverdict: FAIL\nsource: deterministic verifier",
  },
];
export const meanings: Record<Verdict, string> = {
  PASS: "Expected supported behavior was observed.",
  FAIL: "Observed behavior contradicted an acceptance assertion.",
  UNVERIFIED:
    "AgentGuard lacked sufficient supported evidence to make the claim.",
};
export const github = "https://github.com/praval2006/agentguard";

// A separate story track, not a live coding-agent integration.
export const codingStory = {
  kind: "controlled-coding-agent-replay" as const,
  task: "Add subscription cancellation.",
  introduction: "When a user cancels an active subscription:",
  requirements: [
    "The subscription should become cancelled.",
    "The user should no longer have access to premium features.",
    "Repeated cancellation should not crash the application.",
  ],
  activity: [
    "Reading repository…",
    "Implementing cancellation…",
    "Updating tests…",
    "Running tests…",
  ],
  code: 'def cancel_subscription(subscription):\n    subscription["status"] = "cancelled"\n    return subscription',
  tests: [
    "test_active_subscription_becomes_cancelled",
    "test_returns_same_subscription_object",
  ],
};
