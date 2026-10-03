import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
beforeEach(() => {
  window.history.replaceState({}, "", "/");
  vi.stubGlobal("scrollTo", vi.fn());
});
afterEach(() => {
  vi.unstubAllGlobals();
});
describe("AgentGuard presentation navigation", () => {
  it("centers the thesis and separate demo entry", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", {
        name: "Build with AI. Verify with evidence.",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "An acceptance layer between human intent and AI coding agents.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Analyze acceptance/ }),
    ).not.toBeInTheDocument();
  });
  it("navigates to demo and back through native links", () => {
    render(<App />);
    const link = screen.getAllByRole("link", {
      name: /Launch interactive demo/,
    })[0];
    expect(link).toHaveAttribute("href", "/demo");
    link.focus();
    expect(link).toHaveFocus();
    fireEvent.click(link);
    expect(window.location.pathname).toBe("/demo");
    expect(
      screen.getByRole("button", { name: /Analyze acceptance/ }),
    ).toBeEnabled();
    fireEvent.click(screen.getByRole("link", { name: /Back to presentation/ }));
    expect(
      screen.getByRole("heading", {
        name: "Build with AI. Verify with evidence.",
      }),
    ).toBeInTheDocument();
  });
  it("supports direct demo entry and browser history events", () => {
    window.history.replaceState({}, "", "/demo");
    render(<App />);
    expect(
      screen.getByText(/Add a feature that lets users permanently delete/),
    ).toBeInTheDocument();
    act(() => {
      window.history.replaceState({}, "", "/");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    expect(
      screen.queryByRole("button", { name: /Analyze acceptance/ }),
    ).toBeNull();
  });
  it("keeps explicit authority, trust and verdict limits visible", () => {
    render(<App />);
    expect(screen.getByText(/The coding agent can act on the evidence/)).toBeInTheDocument();
    expect(
      screen.getByText(/Approval changes authority, not history/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/The behavior could not be established/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Machine-readable JSON reporting exists/),
    ).toBeInTheDocument();
  });
  it("covers unrelated behaviors without starting a demo", () => {
    render(<App />);
    for (const label of [
      "STATE TRANSITION",
      "PRESERVATION",
      "DELETION",
      "REPEATED OPERATION",
    ])
      expect(screen.getByText(label)).toBeInTheDocument();
    expect(screen.queryByRole("status")).toBeNull();
  });
  it("re-enters naturally on down/up scrolling and never starts playback", () => {
    const callbacks: IntersectionObserverCallback[] = [];
    vi.stubGlobal(
      "IntersectionObserver",
      class {
        constructor(cb: IntersectionObserverCallback) {
          callbacks.push(cb);
        }
        observe() {}
        disconnect() {}
      },
    );
    const { container } = render(<App />);
    const change = (isIntersecting: boolean, top: number) =>
      act(() =>
        callbacks.forEach((cb) =>
          cb(
            [
              {
                isIntersecting,
                boundingClientRect: { top },
              } as IntersectionObserverEntry,
            ],
            {} as IntersectionObserver,
          ),
        ),
      );
    change(true, 100);
    expect(container.querySelector(".reveal")).toHaveClass("reveal-entered");
    change(false, 1000);
    expect(container.querySelector(".reveal")).not.toHaveClass(
      "reveal-entered",
    );
    change(true, 50);
    expect(container.querySelector(".reveal")).toHaveClass("reveal-entered");
    change(false, -1000);
    expect(container.querySelector(".reveal")).toHaveClass("reveal-entered");
    expect(screen.queryByRole("status")).toBeNull();
  });
  it("falls back to readable content when observer initialization fails", () => {
    vi.stubGlobal(
      "IntersectionObserver",
      class {
        constructor() {
          throw Error("Unavailable");
        }
      },
    );
    const { container } = render(<App />);
    expect(container.querySelector(".reveal")).not.toHaveClass("reveal-ready");
    expect(
      screen.getByText(/Your coding agent can perfectly implement/),
    ).toBeVisible();
  });
  it("reduced motion leaves narrative visible without reveal transforms", () => {
    vi.stubGlobal("matchMedia", () => ({
      matches: true,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    const { container } = render(<App />);
    expect(container.querySelector(".reveal")).not.toHaveClass("reveal-ready");
    expect(screen.getByText(/Who checks/)).toBeVisible();
  });
});
