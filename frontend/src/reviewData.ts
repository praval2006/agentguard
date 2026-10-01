import { demo, type Evidence, type Verdict } from "./data";

// Separate illustrative proposal for a shorter task. NOT a historical planner
// output, backend artifact, or revision of the original subscription requirement.
export type ReviewState = "PENDING" | "ACCEPTED" | "DISMISSED";
export type ReviewItem =
  | { origin: "explicit"; state: "INCLUDED"; included: true }
  | { origin: "inferred"; state: "PENDING" | "DISMISSED"; included: false }
  | { origin: "inferred"; state: "ACCEPTED"; included: true };
export interface ReviewedEvidence extends Evidence {
  origin: "explicit" | "inferred";
  humanDecision?: "ACCEPTED";
  behavior: string;
}
export interface ControlledReport {
  overall: Verdict;
  counts: string;
  results: readonly ReviewedEvidence[];
}
export const reviewExample = {
  task: "Add subscription cancellation.",
  explicit: {
    title: "Subscription cancellation",
    behavior:
      "Cancelling an active subscription changes its status to cancelled.",
  },
  suggestion: {
    title: "Premium access revocation",
    behavior: "A cancelled subscription no longer retains premium access.",
    rationale:
      "Premium access is associated with an active subscription. Consider whether cancellation should also end that entitlement.",
  },
};
const state: ReviewedEvidence = {
  ...demo.evidence[0],
  title: reviewExample.explicit.title,
  behavior: reviewExample.explicit.behavior,
  origin: "explicit",
};
const access: ReviewedEvidence = {
  ...demo.evidence[1],
  title: reviewExample.suggestion.title,
  behavior: reviewExample.suggestion.behavior,
  origin: "inferred",
  humanDecision: "ACCEPTED",
};
// Fixed illustrative outcomes selected by an explicit decision. No frontend
// aggregation, assertion evaluation, or new execution evidence is performed.
export const reviewedReports = {
  ACCEPTED: {
    overall: "FAIL",
    counts: "2 selected · 1 PASS · 1 FAIL · 0 UNVERIFIED",
    results: [state, access],
  },
  DISMISSED: {
    overall: "PASS",
    counts: "1 selected · 1 PASS · 0 FAIL · 0 UNVERIFIED",
    results: [state],
  },
} as const satisfies Record<Exclude<ReviewState, "PENDING">, ControlledReport>;
