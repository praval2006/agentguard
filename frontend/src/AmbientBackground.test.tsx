import { render } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { BrandMark } from "./BrandMark";
import { AmbientBackground } from "./AmbientBackground";
afterEach(() => vi.unstubAllGlobals());
function setup(reduced: boolean) {
  const listeners = new Map<string, () => void>();
  const media = {
    matches: reduced,
    addEventListener: vi.fn((name, cb) => listeners.set(name, cb)),
    removeEventListener: vi.fn(),
  };
  const pointer = {
    ...media,
    matches: true,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  };
  vi.stubGlobal("matchMedia", (query: string) =>
    query.includes("reduced-motion") ? media : pointer,
  );
  vi.stubGlobal("innerWidth", 1440);
  vi.stubGlobal("innerHeight", 810);
  vi.stubGlobal(
    "requestAnimationFrame",
    vi.fn(() => 7),
  );
  vi.stubGlobal("cancelAnimationFrame", vi.fn());
  const context = {
    save: vi.fn(),
    restore: vi.fn(),
    scale: vi.fn(),
    moveTo: vi.fn(),
    lineTo: vi.fn(),
    stroke: vi.fn(),
    setTransform: vi.fn(),
    clearRect: vi.fn(),
    createRadialGradient: () => ({ addColorStop: vi.fn() }),
    fillRect: vi.fn(),
    beginPath: vi.fn(),
    arc: vi.fn(),
    fill: vi.fn(),
  };
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(
    context as unknown as CanvasRenderingContext2D,
  );
  return { media, pointer, listeners, context };
}
it("is decorative and gracefully survives an unavailable canvas renderer", () => {
  const { container } = render(<AmbientBackground />);
  expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  expect(container.querySelector("canvas")).not.toHaveAttribute("tabindex");
});
it("draws a static reduced-motion background without starting a frame loop", () => {
  const { context } = setup(true);
  const { container } = render(<AmbientBackground />);
  expect(container.querySelector("canvas")).toHaveAttribute(
    "data-motion",
    "static",
  );
  expect(context.fillRect).toHaveBeenCalled();
  expect(requestAnimationFrame).not.toHaveBeenCalled();
});
it("bounds density, calms demo and cancels animation/listeners on unmount", () => {
  const { media } = setup(false);
  const { container, rerender, unmount } = render(<AmbientBackground />);
  const count = Number(container.querySelector("canvas")!.dataset.particles);
  expect(count).toBe(33);
  rerender(<AmbientBackground demo />);
  expect(Number(container.querySelector("canvas")!.dataset.particles)).toBe(16);
  expect(requestAnimationFrame).toHaveBeenCalled();
  unmount();
  expect(cancelAnimationFrame).toHaveBeenCalledWith(7);
  expect(media.removeEventListener).toHaveBeenCalled();
});

it("reduces density for coarse pointers and responds to motion preference changes", () => {
  const { media, pointer, listeners } = setup(false);
  pointer.matches = false;
  const { container } = render(<AmbientBackground />);
  expect(Number(container.querySelector("canvas")!.dataset.particles)).toBe(10);
  vi.mocked(requestAnimationFrame).mockClear();
  media.matches = true;
  listeners.get("change")!();
  expect(container.querySelector("canvas")).toHaveAttribute(
    "data-motion",
    "static",
  );
  expect(cancelAnimationFrame).toHaveBeenCalledWith(7);
  expect(requestAnimationFrame).not.toHaveBeenCalled();
});
it("renders a scalable decorative brand mark without another accessible name", () => {
  const { container } = render(<BrandMark />);
  expect(container.querySelector("svg")).toHaveAttribute(
    "viewBox",
    "0 0 32 36",
  );
  expect(container.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
  expect(container.querySelector("svg")).toHaveAttribute("focusable", "false");
});
