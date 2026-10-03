import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReviewDemo } from "./ReviewDemo";
import { accountReports, selectedFixture } from "./accountDemoData";
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
function decide(id: "session" | "profile", accept = true) {
  const card = screen.getByLabelText(
    id === "session"
      ? "Existing sessions invalidated"
      : "Profile inaccessible after deletion",
  );
  fireEvent.click(
    within(card).getByRole("button", {
      name: accept ? /Add to verification/ : /^Dismiss$/,
    }),
  );
}
function contract() {
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
    expect(screen.getAllByText("PENDING")).toHaveLength(2);
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
    expect(screen.getAllByText("ACCEPTED BY YOU")).toHaveLength(2);
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
    expect(screen.getAllByText("PENDING")).toHaveLength(2);
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
      selectedFixture({ session: "PENDING", profile: "ACCEPTED" }),
    ).toBeNull();
    expect(selectedFixture({ session: "ACCEPTED", profile: "ACCEPTED" })).toBe(
      accountReports.AA,
    );
    expect(selectedFixture({ session: "ACCEPTED", profile: "DISMISSED" })).toBe(
      accountReports.AD,
    );
    expect(selectedFixture({ session: "DISMISSED", profile: "ACCEPTED" })).toBe(
      accountReports.DA,
    );
    expect(
      selectedFixture({ session: "DISMISSED", profile: "DISMISSED" }),
    ).toBe(accountReports.DD);
    expect(accountReports.AA.results.map((r) => r.verdict)).toEqual([
      "PASS",
      "FAIL",
      "FAIL",
    ]);
  });
});
