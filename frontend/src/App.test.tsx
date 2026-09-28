import { fireEvent, render, screen, act, within } from "@testing-library/react";
import { describe, it, expect, vi, afterEach } from "vitest";
import App from "./App";
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
describe("AgentGuard local presentation", () => {
  it("selects graph evidence and preserves the unsupported explanation", () => {
    render(<App />);
    const button = screen.getByRole("button", {
      name: /03 Repeated cancellation/,
    });
    fireEvent.click(button);
    expect(button).toHaveAttribute("aria-pressed", "true");
    expect(
      screen.getByText(
        "The available controlled HTTP interface does not preserve the same subscription across requests.",
      ),
    ).toBeInTheDocument();
  });
  it("plays all phases, reveals controlled results and resets", () => {
    vi.useFakeTimers();
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Run verification/ }));
    expect(screen.getByRole("status")).toHaveTextContent(
      "Reading requirements",
    );
    for (let i = 0; i < 8; i++)
      act(() => {
        vi.advanceTimersByTime(400);
      });
    expect(screen.getByRole("status")).toHaveTextContent("Playback complete");
    expect(
      screen.getByRole("button", { name: /Replay verification/ }),
    ).toBeEnabled();
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByRole("status")).toHaveTextContent("Ready");
    expect(
      screen.queryByText("Expected: premium_access = false"),
    ).not.toBeInTheDocument();
  });
  it("switches stage detail without execution", () => {
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /03 EXECUTE/ }));
    expect(
      screen.getByText(/target: controlled loopback interface/),
    ).toBeInTheDocument();
  });
  it("finishes immediately with reduced motion", () => {
    vi.stubGlobal("matchMedia", () => ({
      matches: true,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Run verification/ }));
    expect(screen.getByRole("status")).toHaveTextContent("Playback complete");
  });
  it("keeps task, implementation and agent success ordered before the handoff", () => {
    render(<App />);
    const story = screen.getByLabelText("Controlled coding-agent story");
    expect(
      within(story).getByText("Add subscription cancellation."),
    ).toBeInTheDocument();
    expect(
      within(story).getByText(/subscription\["status"\]/),
    ).toBeInTheDocument();
    expect(
      within(story).getByText(/test_returns_same_subscription_object/),
    ).toBeInTheDocument();
    expect(within(story).getByText(/TASK\s*COMPLETE\./)).toBeInTheDocument();
    expect(story.textContent!.indexOf("THE TASK")).toBeLessThan(
      story.textContent!.indexOf("CONTROLLED IMPLEMENTATION"),
    );
    expect(story.textContent!.indexOf("COMPLETION CLAIM")).toBeLessThan(
      story.textContent!.indexOf("THE INDEPENDENT QUESTION"),
    );
    expect(
      within(story).queryByText("premium_access = true"),
    ).not.toBeInTheDocument();
  });
  it("scroll reveals never start verification and navigation points to the demo", () => {
    const callbacks: IntersectionObserverCallback[] = [];
    vi.stubGlobal(
      "IntersectionObserver",
      class {
        constructor(callback: IntersectionObserverCallback) {
          callbacks.push(callback);
        }
        observe() {}
        disconnect() {}
        unobserve() {}
      },
    );
    render(<App />);
    act(() =>
      callbacks.forEach((callback) =>
        callback(
          [{ isIntersecting: true } as IntersectionObserverEntry],
          {} as IntersectionObserver,
        ),
      ),
    );
    expect(screen.getByRole("status")).toHaveTextContent("Ready");
    expect(screen.queryByTestId("story-payoff")).not.toBeInTheDocument();
    expect(
      screen.getByLabelText("Acceptance requirements"),
    ).not.toHaveTextContent("PASS");
    expect(screen.getAllByRole("link", { name: /Run the demo/ })).toHaveLength(
      4,
    );
    screen
      .getAllByRole("link", { name: /Run the demo/ })
      .forEach((link) => expect(link).toHaveAttribute("href", "#product"));
    expect(screen.queryByText("Launch AgentGuard")).not.toBeInTheDocument();
  });
  it("reveals evidence progressively and removes payoff on replay/reset", () => {
    vi.useFakeTimers();
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /Run verification/ }));
    expect(screen.queryByTestId("story-payoff")).not.toBeInTheDocument();
    for (let i = 0; i < 5; i++)
      act(() => {
        vi.advanceTimersByTime(360);
      });
    expect(
      screen.queryByText("Expected: premium_access = false"),
    ).not.toBeInTheDocument();
    act(() => {
      vi.advanceTimersByTime(240);
    });
    expect(
      screen.getByText("Expected: premium_access = false"),
    ).toBeInTheDocument();
    for (let i = 0; i < 2; i++)
      act(() => {
        vi.advanceTimersByTime(240);
      });
    expect(screen.getByTestId("story-payoff")).toBeInTheDocument();
    fireEvent.click(
      screen.getByRole("button", { name: /Replay verification/ }),
    );
    expect(screen.queryByTestId("story-payoff")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(screen.getByRole("status")).toHaveTextContent("Ready");
  });
  it("keeps narrative readable if reveal initialization fails", () => {
    vi.stubGlobal(
      "IntersectionObserver",
      class {
        constructor() {
          throw new Error("Unavailable");
        }
      },
    );
    render(<App />);
    expect(screen.getByText(/TASK\s*COMPLETE\./)).toBeVisible();
    expect(
      screen.getByRole("button", { name: /Run verification/ }),
    ).toBeEnabled();
  });
});
