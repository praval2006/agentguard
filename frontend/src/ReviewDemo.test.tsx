import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReviewDemo } from "./ReviewDemo";
import {
  accountReports,
  selectedFixture,
  suggestions,
  type Decision,
  type SuggestionId,
} from "./accountDemoData";
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
function mount(reduced = true) {
  vi.stubGlobal("scrollTo", vi.fn());
  vi.stubGlobal("matchMedia", () => ({
    matches: reduced,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
  render(<ReviewDemo />);
}
function click(name: RegExp | string) {
  fireEvent.click(screen.getByRole("button", { name }));
}
function review() {
  click(/Analyze acceptance/);
}
function decide(id: SuggestionId, accept = true) {
  const card = screen.getByLabelText(
    suggestions.find((s) => s.id === id)!.title,
  );
  fireEvent.click(
    within(card).getByRole("button", {
      name: accept ? /Add to verification/ : /^Dismiss$/,
    }),
  );
}
function contract() {
  const external = screen.queryByLabelText(
    "External personal data disassociated",
  );
  if (external?.textContent?.includes("PENDING")) decide("external", false);
  click(/Review acceptance contract/);
}
function run() {
  click(/Run independent verification/);
}
describe("account deletion reviewed demo", () => {
  it("starts at intro then includes explicit and holds both suggestions pending", () => {
    mount();
    expect(screen.getByText(/permanently delete their account/)).toBeVisible();
    review();
    expect(screen.getByLabelText("Explicit requirement")).toHaveTextContent(
      "INCLUDED",
    );
    expect(
      within(screen.getByLabelText("Explicit requirement")).queryByRole(
        "button",
      ),
    ).toBeNull();
    expect(screen.getAllByText("○ PENDING")).toHaveLength(3);
    expect(
      screen.getByRole("button", { name: /Review acceptance contract/ }),
    ).toBeDisabled();
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
  });
  it("requires both decisions and accepts without changing origin or running", () => {
    mount();
    review();
    decide("session");
    expect(
      screen.getByRole("button", { name: /Review acceptance contract/ }),
    ).toBeDisabled();
    decide("profile");
    expect(screen.getAllByText("✓ ADDED · ACCEPTED BY YOU")).toHaveLength(2);
    contract();
    const c = screen.getByLabelText("Acceptance contract");
    expect(c).toHaveTextContent("3 SELECTED");
    expect(c).toHaveTextContent("INFERRED · ACCEPTED BY YOU");
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
  });
  it("dismisses visibly without assigning verdicts and supports reconsideration", () => {
    mount();
    review();
    decide("session", false);
    const card = screen.getByLabelText("Existing sessions invalidated");
    expect(card).toHaveTextContent("DISMISSED");
    expect(card).not.toHaveTextContent(/PASS|FAIL|UNVERIFIED/);
    decide("session");
    expect(card).toHaveTextContent("ACCEPTED BY YOU");
  });
  it("plays accepted-both fixed evidence and assembles the selected report", () => {
    mount();
    review();
    decide("session");
    decide("profile");
    contract();
    run();
    const results = screen.getByLabelText("Selected verification results");
    expect(
      within(results).getByLabelText("Account permanently deleted"),
    ).toHaveTextContent("✓ PASS");
    expect(
      within(results).getByLabelText("Existing sessions invalidated"),
    ).toHaveTextContent("× FAIL");
    expect(
      within(results).getByLabelText("Profile inaccessible after deletion"),
    ).toHaveTextContent("× FAIL");
    expect(screen.getByTestId("story-payoff")).toBeInTheDocument();
    click(/Assemble verification report/);
    const summary = screen.getByLabelText("Verification summary");
    expect(summary).toHaveTextContent(
      "OVERALL× FAIL3SELECTED1PASS2FAIL0UNVERIFIED",
    );
    expect(screen.getByLabelText("Unresolved ambiguity")).toHaveTextContent(
      "No verdict",
    );
  });
  it("both dismissed results contain only explicit behavior and narrower PASS", () => {
    mount();
    review();
    decide("session", false);
    decide("profile", false);
    contract();
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "1 SELECTED",
    );
    expect(screen.getByLabelText("Review history")).toHaveTextContent(
      "DISMISSED · not included · no verdict",
    );
    run();
    const results = screen.getByLabelText("Selected verification results");
    expect(
      within(results).queryByLabelText("Existing sessions invalidated"),
    ).toBeNull();
    expect(
      within(results).queryByLabelText("Profile inaccessible after deletion"),
    ).toBeNull();
    click(/Assemble verification report/);
    expect(screen.getByLabelText("Verification summary")).toHaveTextContent(
      "OVERALL✓ PASS1SELECTED1PASS0FAIL0UNVERIFIED",
    );
  });
  it("decision changes clear stale results before another run", () => {
    mount();
    review();
    decide("session");
    decide("profile");
    contract();
    run();
    click("Change decision");
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
    expect(screen.queryByTestId("story-payoff")).toBeNull();
    decide("session", false);
    contract();
    run();
    expect(
      within(
        screen.getByLabelText("Selected verification results"),
      ).queryByLabelText("Existing sessions invalidated"),
    ).toBeNull();
  });
  it("reset cancels playback and restores all pending decisions", () => {
    vi.useFakeTimers();
    mount(false);
    review();
    act(() => vi.advanceTimersByTime(1600));
    decide("session");
    decide("profile");
    contract();
    run();
    click(/Reset demo/);
    act(() => vi.advanceTimersByTime(10000));
    expect(
      screen.getByRole("button", { name: /Analyze acceptance/ }),
    ).toBeEnabled();
    review();
    act(() => vi.advanceTimersByTime(1600));
    expect(screen.getAllByText("○ PENDING")).toHaveLength(3);
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
  });
  it("shows evidence before verdict and replay removes completed payoff", () => {
    vi.useFakeTimers();
    mount(false);
    review();
    act(() => vi.advanceTimersByTime(1600));
    decide("session");
    decide("profile");
    contract();
    run();
    expect(screen.queryByText("Account unavailable")).toBeNull();
    act(() => vi.advanceTimersByTime(800));
    expect(screen.getByText("Account unavailable")).toBeVisible();
    expect(screen.queryByText("✓ PASS")).toBeNull();
    act(() => vi.advanceTimersByTime(800));
    expect(screen.getByText("✓ PASS")).toBeVisible();
    for (let i = 0; i < 5; i++) act(() => vi.advanceTimersByTime(800));
    expect(screen.getByTestId("story-payoff")).toBeInTheDocument();
    click(/Replay verification/);
    expect(screen.queryByTestId("story-payoff")).toBeNull();
    expect(screen.queryByText("Account unavailable")).toBeNull();
  });
  it("provides focusable controls, status and ambiguity outside verification", () => {
    mount();
    review();
    const card = screen.getByLabelText("Existing sessions invalidated");
    const accept = within(card).getByRole("button", {
      name: /Add to verification/,
    });
    accept.focus();
    expect(accept).toHaveFocus();
    expect(accept).toHaveAttribute("aria-pressed", "false");
    fireEvent.click(accept);
    expect(accept).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    const ambiguity = screen.getByLabelText("Unresolved ambiguity");
    expect(within(ambiguity).queryByRole("button")).toBeNull();
    expect(ambiguity).not.toHaveTextContent(/PASS|FAIL|UNVERIFIED/);
  });
  it("selects explicit fixtures for every decision combination without inferring verdicts", () => {
    expect(
      selectedFixture({
        session: "PENDING",
        profile: "ACCEPTED",
        external: "DISMISSED",
      }),
    ).toBeNull();
    expect(
      selectedFixture({
        session: "ACCEPTED",
        profile: "ACCEPTED",
        external: "DISMISSED",
      }),
    ).toBe(accountReports.AAD);
    expect(
      selectedFixture({
        session: "ACCEPTED",
        profile: "DISMISSED",
        external: "DISMISSED",
      }),
    ).toBe(accountReports.ADD);
    expect(
      selectedFixture({
        session: "DISMISSED",
        profile: "ACCEPTED",
        external: "DISMISSED",
      }),
    ).toBe(accountReports.DAD);
    expect(
      selectedFixture({
        session: "DISMISSED",
        profile: "DISMISSED",
        external: "DISMISSED",
      }),
    ).toBe(accountReports.DDD);
    expect(accountReports.AAD.results.map((r) => r.verdict)).toEqual([
      "PASS",
      "FAIL",
      "FAIL",
    ]);
  });
});

it("all three added use the canonical fixed 4/1/2/1 report and explanatory evidence", () => {
  mount();
  review();
  for (const s of suggestions) decide(s.id);
  contract();
  expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
    "4 SELECTED",
  );
  run();
  const results = screen.getByLabelText("Selected verification results");
  const external = within(results).getByLabelText(
    "External personal data disassociated",
  );
  expect(external).toHaveTextContent("? UNVERIFIED");
  expect(external).not.toHaveTextContent("× FAIL");
  expect(external).toHaveTextContent(accountReports.AAA.results[3].reason);
  expect(screen.getAllByText("CONTROLLED IMPLEMENTATION EXCERPT")).toHaveLength(
    2,
  );
  expect(screen.getByText("Existing session → GET /me")).toBeVisible();
  expect(screen.getByText("GET /profile/<deleted-user>")).toBeVisible();
  expect(screen.getByText("GET account → available")).toBeVisible();
  expect(screen.getByText("GET account → 404 / unavailable")).toBeVisible();
  click(/Assemble verification report/);
  expect(screen.getByLabelText("Verification summary")).toHaveTextContent(
    "OVERALL× FAIL4SELECTED1PASS2FAIL1UNVERIFIED",
  );
  expect(screen.getByLabelText("Unresolved ambiguity")).not.toHaveTextContent(
    /PASS|FAIL|UNVERIFIED/,
  );
});
it("clarification resolves review for this run but gives no contract entry or verdict", () => {
  mount();
  review();
  for (const s of suggestions) {
    const card = screen.getByLabelText(s.title);
    fireEvent.click(
      within(card).getByRole("button", { name: "Needs clarification" }),
    );
    expect(card).toHaveTextContent("? NEEDS CLARIFICATION");
    expect(card).not.toHaveTextContent(/PASS|FAIL|UNVERIFIED/);
    expect(
      within(card).getByRole("button", { name: "Needs clarification" }),
    ).toHaveAttribute("aria-pressed", "true");
  }
  contract();
  expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
    "1 SELECTED",
  );
  expect(screen.getByLabelText("Review history")).toHaveTextContent(
    "NEEDS CLARIFICATION · not included · no verdict",
  );
  run();
  for (const s of suggestions)
    expect(
      within(
        screen.getByLabelText("Selected verification results"),
      ).queryByLabelText(s.title),
    ).toBeNull();
  expect(screen.queryByText("CONTROLLED IMPLEMENTATION EXCERPT")).toBeNull();
});
it("changing accepted external data to clarification clears its stale UNVERIFIED", () => {
  mount();
  review();
  decide("session", false);
  decide("profile", false);
  decide("external");
  contract();
  run();
  expect(screen.getByLabelText("Controlled result summary")).toHaveTextContent(
    "? UNVERIFIED",
  );
  click("Change decision");
  expect(screen.queryByLabelText("Selected verification results")).toBeNull();
  fireEvent.click(
    within(
      screen.getByLabelText("External personal data disassociated"),
    ).getByRole("button", { name: "Needs clarification" }),
  );
  contract();
  run();
  expect(screen.getByLabelText("Controlled result summary")).toHaveTextContent(
    "✓ PASS",
  );
  expect(
    within(
      screen.getByLabelText("Selected verification results"),
    ).queryByLabelText("External personal data disassociated"),
  ).toBeNull();
});
it("all 27 resolved review combinations select an authored fixture by inclusion only", () => {
  const states: Decision[] = ["ACCEPTED", "DISMISSED", "CLARIFICATION"];
  for (const session of states)
    for (const profile of states)
      for (const external of states) {
        const decisions = { session, profile, external };
        const key = statesForKey(decisions);
        expect(selectedFixture(decisions)).toBe(accountReports[key]);
        for (const s of suggestions)
          expect(
            selectedFixture(decisions)!.results.some((r) => r.id === s.id),
          ).toBe(decisions[s.id] === "ACCEPTED");
      }
  expect(
    selectedFixture({
      session: "ACCEPTED",
      profile: "ACCEPTED",
      external: "PENDING",
    }),
  ).toBeNull();
});
function statesForKey(
  d: Record<SuggestionId, Decision>,
): keyof typeof accountReports {
  return `${d.session === "ACCEPTED" ? "A" : "D"}${d.profile === "ACCEPTED" ? "A" : "D"}${d.external === "ACCEPTED" ? "A" : "D"}` as keyof typeof accountReports;
}
