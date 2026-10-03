import type { Verdict } from "./data";
export type Decision = "PENDING" | "ACCEPTED" | "DISMISSED";
export type SuggestionId = "session" | "profile";
export const accountTask =
  "Add a feature that lets users permanently delete their account.";
export const ambiguity =
  "What should happen to user-created content after account deletion?";
export const suggestions = [
  {
    id: "session",
    title: "Existing sessions invalidated",
    behavior:
      "Existing authenticated sessions should no longer authorize requests after account deletion.",
    rationale:
      "The application contains authenticated sessions associated with the user.",
  },
  {
    id: "profile",
    title: "Profile inaccessible after deletion",
    behavior: "The deleted user’s profile should no longer be retrievable.",
    rationale: "The application exposes a profile associated with the user.",
  },
] as const;
export interface AccountEvidence {
  id: "account" | SuggestionId;
  title: string;
  source: "explicit" | "inferred";
  expected: string;
  observed: string;
  operation: string;
  response: string;
  verdict: Verdict;
}
const account: AccountEvidence = {
  id: "account",
  title: "Account permanently deleted",
  source: "explicit",
  expected: "Account unavailable after deletion",
  observed: "Account unavailable",
  operation: "CHECK ACCOUNT",
  response: "404 · Not found",
  verdict: "PASS",
};
const session: AccountEvidence = {
  id: "session",
  title: "Existing sessions invalidated",
  source: "inferred",
  expected: "Existing session unauthorized",
  observed: "Existing session remained authorized",
  operation: "CHECK EXISTING SESSION",
  response: "200 · Authorized",
  verdict: "FAIL",
};
const profile: AccountEvidence = {
  id: "profile",
  title: "Profile inaccessible after deletion",
  source: "inferred",
  expected: "Profile unavailable",
  observed: "Profile remained retrievable",
  operation: "CHECK PROFILE",
  response: "200 · Profile returned",
  verdict: "FAIL",
};
export interface AccountReport {
  overall: Verdict;
  selected: number;
  pass: number;
  fail: number;
  unverified: number;
  results: readonly AccountEvidence[];
}
// Four explicitly authored presentation outcomes. Never compute verdicts/counts
// from response values. These are not backend artifacts or fresh evaluation runs.
export const accountReports = {
  AA: {
    overall: "FAIL",
    selected: 3,
    pass: 1,
    fail: 2,
    unverified: 0,
    results: [account, session, profile],
  },
  AD: {
    overall: "FAIL",
    selected: 2,
    pass: 1,
    fail: 1,
    unverified: 0,
    results: [account, session],
  },
  DA: {
    overall: "FAIL",
    selected: 2,
    pass: 1,
    fail: 1,
    unverified: 0,
    results: [account, profile],
  },
  DD: {
    overall: "PASS",
    selected: 1,
    pass: 1,
    fail: 0,
    unverified: 0,
    results: [account],
  },
} as const satisfies Record<string, AccountReport>;
export function selectedFixture(
  decisions: Record<SuggestionId, Decision>,
): AccountReport | null {
  if (decisions.session === "PENDING" || decisions.profile === "PENDING")
    return null;
  const key =
    `${decisions.session === "ACCEPTED" ? "A" : "D"}${decisions.profile === "ACCEPTED" ? "A" : "D"}` as keyof typeof accountReports;
  return accountReports[key];
}
