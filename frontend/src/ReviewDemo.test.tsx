import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ReviewDemo } from "./ReviewDemo";
import { reviewedReports, type ReviewItem } from "./reviewData";

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
function mount(reduced = false) {
  vi.stubGlobal("matchMedia", () => ({
    matches: reduced,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
  const complete = vi.fn();
  render(<ReviewDemo onComplete={complete} />);
  return complete;
}
function choose(name = "Add to verification") {
  fireEvent.click(screen.getByRole("button", { name }));
}
function run() {
  fireEvent.click(screen.getByRole("button", { name: /Run verification/ }));
}
describe("human acceptance boundary", () => {
  it("starts pending, includes only explicit intent and disables execution", () => {
    const complete = mount();
    expect(screen.getByLabelText("Explicit requirement")).toHaveTextContent(
      "INCLUDED",
    );
    expect(
      within(screen.getByLabelText("Explicit requirement")).queryByRole(
        "button",
      ),
    ).toBeNull();
    expect(screen.getByLabelText("AgentGuard suggestion")).toHaveTextContent(
      "PENDING",
    );
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "1 behaviour selected",
    );
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "Pending · not included",
    );
    expect(
      screen.getByRole("button", { name: /Run verification/ }),
    ).toBeDisabled();
    run();
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
    expect(complete).not.toHaveBeenCalledWith(true);
  });
  it("accepts without changing origin or starting playback", () => {
    mount();
    choose();
    const card = screen.getByLabelText("AgentGuard suggestion");
    expect(card).toHaveTextContent("ACCEPTED");
    expect(card).toHaveTextContent("ORIGIN · AGENTGUARD SUGGESTION");
    expect(card).toHaveTextContent("This was not explicitly requested.");
    expect(
      screen.getByRole("button", { name: "Add to verification" }),
    ).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "2 behaviours selected",
    );
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "Accepted by you",
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      "Added to acceptance contract",
    );
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
  });
  it("dismisses visibly without inventing a verdict and allows reconsideration", () => {
    mount();
    choose("Dismiss");
    const card = screen.getByLabelText("AgentGuard suggestion");
    expect(card).toHaveTextContent("DISMISSED");
    expect(card).not.toHaveTextContent(/PASS|FAIL|UNVERIFIED/);
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "Dismissed · not included",
    );
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
    choose();
    expect(card).toHaveTextContent("ACCEPTED");
    choose("Dismiss");
    expect(card).toHaveTextContent("DISMISSED");
  });
  it("plays the accepted fixture only on explicit run", () => {
    mount(true);
    choose();
    run();
    const report = screen.getByLabelText("Selected verification results");
    expect(report).toHaveTextContent("2 selected · 1 PASS · 1 FAIL");
    expect(report).toHaveTextContent("Expected: premium_access = false");
    expect(report).toHaveTextContent("Observed: premium_access = true");
    expect(report).toHaveTextContent("AGENTGUARD SUGGESTION · ACCEPTED BY YOU");
    expect(report).not.toHaveTextContent("Repeated cancellation");
  });
  it("dismissed fixture has no premium result or false failure payoff", () => {
    mount(true);
    choose("Dismiss");
    run();
    const report = screen.getByLabelText("Selected verification results");
    expect(report).toHaveTextContent("1 selected · 1 PASS · 0 FAIL");
    expect(report).not.toHaveTextContent("Premium access revocation");
    expect(report).not.toHaveTextContent("premium_access");
    expect(screen.getByLabelText("Acceptance contract")).toHaveTextContent(
      "Dismissed · not included",
    );
  });
  it("changing a completed decision removes old evidence before a new run", () => {
    mount(true);
    choose();
    run();
    choose("Change decision");
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
    choose("Dismiss");
    run();
    expect(
      screen.getByLabelText("Selected verification results"),
    ).not.toHaveTextContent("premium_access");
  });
  it("reset cancels playback and restores pending rather than silently retaining approval", () => {
    vi.useFakeTimers();
    const complete = mount();
    choose();
    run();
    choose("Reset");
    act(() => vi.advanceTimersByTime(10000));
    expect(screen.getByRole("status")).toHaveTextContent("Review incomplete");
    expect(
      screen.getByRole("button", { name: /Run verification/ }),
    ).toBeDisabled();
    expect(screen.queryByLabelText("Selected verification results")).toBeNull();
    expect(complete).not.toHaveBeenCalledWith(true);
  });
  it("provides native focusable review controls and meaningful announcements", () => {
    mount();
    const accept = screen.getByRole("button", { name: "Add to verification" });
    accept.focus();
    expect(accept).toHaveFocus();
    expect(accept.tagName).toBe("BUTTON");
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
    expect(
      screen.getByRole("button", { name: /Run verification/ }),
    ).toHaveAttribute("aria-describedby", "review-progress");
  });
  it("keeps excluded review data structurally separate from fixed result fixtures", () => {
    const excluded: ReviewItem = {
      origin: "inferred",
      state: "DISMISSED",
      included: false,
    };
    const invalid: ReviewItem = {
      origin: "inferred",
      state: "PENDING",
      included: false,
      // @ts-expect-error Excluded review items cannot carry a verification verdict.
      verdict: "UNVERIFIED",
    };
    void invalid;
    expect(excluded).not.toHaveProperty("verdict");
    expect(reviewedReports.DISMISSED.results.map((r) => r.id)).toEqual([
      "state",
    ]);
    expect(reviewedReports.ACCEPTED.results.map((r) => r.id)).toEqual([
      "state",
      "access",
    ]);
  });
});
