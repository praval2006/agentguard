import type { Verdict } from "./data";
export type Decision = "PENDING" | "ACCEPTED" | "DISMISSED" | "CLARIFICATION";
export type SuggestionId = "session" | "profile" | "external";
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
  {
    id: "external",
    title: "External personal data disassociated",
    behavior:
      "Personal data stored in external services should no longer remain associated with the deleted account.",
    rationale:
      "The illustrative application also associates personal data with an external service.",
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
  behavior: string;
  chain: readonly { label: string; value: string }[];
  reason: string;
  codeNote?: string;
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
  behavior: "Account is permanently deleted.",
  chain: [
    { label: "BEFORE", value: "GET account → available" },
    { label: "ACTION", value: "DELETE /account → success" },
    { label: "AFTER", value: "GET account → 404 / unavailable" },
  ],
  reason:
    "The controlled before/after observation establishes that the account is no longer retrievable after deletion. This does not establish removal from every other system.",
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
  behavior: suggestions[0].behavior,
  chain: [
    { label: "ACTION", value: "DELETE /account → success" },
    { label: "OBSERVATION", value: "Existing session → GET /me" },
    { label: "ACTUAL", value: "HTTP 200 · protected request authorized" },
    {
      label: "EXPECTED",
      value: "Unauthorized response, such as HTTP 401 / 403",
    },
  ],
  reason:
    "Account deletion completed, but the previously authenticated session remained valid and continued to authorize GET /me. That contradicts the accepted session-invalidation behavior.",
  codeNote:
    "This excerpt deletes the account record and returns. No session invalidation step is shown. The observed authorization response—not the excerpt alone—establishes the contradiction.",
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
  behavior: suggestions[1].behavior,
  chain: [
    { label: "ACTION", value: "DELETE /account → success" },
    { label: "OBSERVATION", value: "GET /profile/<deleted-user>" },
    { label: "ACTUAL", value: "HTTP 200 · profile data returned" },
    { label: "EXPECTED", value: "HTTP 404 / profile unavailable" },
  ],
  reason:
    "The explicit account deletion check succeeded, but profile data remained accessible through the profile retrieval path. That contradicts the accepted profile-inaccessibility behavior.",
  codeNote:
    "This excerpt removes the account record without showing profile removal or invalidation. The returned profile data is the contradictory evidence.",
};
const external: AccountEvidence = {
  id: "external",
  title: "External personal data disassociated",
  source: "inferred",
  expected: "External personal data no longer associated with the account",
  observed: "External-service state not observable in this run",
  operation: "EXTERNAL OBSERVATION BOUNDARY",
  response: "No supported observation",
  verdict: "UNVERIFIED",
  behavior: suggestions[2].behavior,
  chain: [
    { label: "LOCAL ACTION", value: "DELETE /account → success" },
    {
      label: "REQUIRED OBSERVATION",
      value: "Inspect external-service account/data state",
    },
    {
      label: "AVAILABLE EVIDENCE",
      value: "No authorized supported observation is available",
    },
  ],
  reason:
    "The accepted behaviour depends on external-service state that is not observable through the supported evidence available in this verification run.",
};
export const implementationExcerpt = [
  {
    tokens: [
      { text: "def", kind: "keyword" },
      { text: " delete_account(user, db):", kind: "plain" },
    ],
  },
  { tokens: [{ text: "    db.users.delete(user.id)", kind: "call" }] },
  {
    tokens: [
      { text: "    return", kind: "keyword" },
      { text: ' {"deleted": True}', kind: "plain" },
    ],
  },
] as const;
export interface AccountReport {
  overall: Verdict;
  selected: number;
  pass: number;
  fail: number;
  unverified: number;
  results: readonly AccountEvidence[];
}
// Eight explicitly authored presentation outcomes. Never compute verdicts/counts
// from response values. These are not backend artifacts or fresh evaluation runs.
export const accountReports = {
  AAD: {
    overall: "FAIL",
    selected: 3,
    pass: 1,
    fail: 2,
    unverified: 0,
    results: [account, session, profile],
  },
  ADD: {
    overall: "FAIL",
    selected: 2,
    pass: 1,
    fail: 1,
    unverified: 0,
    results: [account, session],
  },
  DAD: {
    overall: "FAIL",
    selected: 2,
    pass: 1,
    fail: 1,
    unverified: 0,
    results: [account, profile],
  },
  DDD: {
    overall: "PASS",
    selected: 1,
    pass: 1,
    fail: 0,
    unverified: 0,
    results: [account],
  },
  AAA: {
    overall: "FAIL",
    selected: 4,
    pass: 1,
    fail: 2,
    unverified: 1,
    results: [account, session, profile, external],
  },
  ADA: {
    overall: "FAIL",
    selected: 3,
    pass: 1,
    fail: 1,
    unverified: 1,
    results: [account, session, external],
  },
  DAA: {
    overall: "FAIL",
    selected: 3,
    pass: 1,
    fail: 1,
    unverified: 1,
    results: [account, profile, external],
  },
  DDA: {
    overall: "UNVERIFIED",
    selected: 2,
    pass: 1,
    fail: 0,
    unverified: 1,
    results: [account, external],
  },
} as const satisfies Record<string, AccountReport>;
export function selectedFixture(
  decisions: Record<SuggestionId, Decision>,
): AccountReport | null {
  if (suggestions.some(({ id }) => decisions[id] === "PENDING")) return null;
  const key =
    `${decisions.session === "ACCEPTED" ? "A" : "D"}${decisions.profile === "ACCEPTED" ? "A" : "D"}${decisions.external === "ACCEPTED" ? "A" : "D"}` as keyof typeof accountReports;
  return accountReports[key];
}
