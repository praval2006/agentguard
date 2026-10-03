import { render } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { AmbientBackground } from "./AmbientBackground";
afterEach(() => vi.unstubAllGlobals());
function setup(reduced: boolean) {
  const listeners = new Map<string, () => void>();
  const media = {
    matches: reduced,
    addEventListener: vi.fn((name, cb) => listeners.set(name, cb)),
    removeEventListener: vi.fn(),
  };
  vi.stubGlobal("matchMedia", () => media);
  vi.stubGlobal(
    "requestAnimationFrame",
    vi.fn(() => 7),
  );
  vi.stubGlobal("cancelAnimationFrame", vi.fn());
  const context = {
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
  return { media, listeners, context };
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
  expect(count).toBeLessThanOrEqual(18);
  rerender(<AmbientBackground demo />);
  expect(
    Number(container.querySelector("canvas")!.dataset.particles),
  ).toBeLessThanOrEqual(8);
  expect(requestAnimationFrame).toHaveBeenCalled();
  unmount();
  expect(cancelAnimationFrame).toHaveBeenCalledWith(7);
  expect(media.removeEventListener).toHaveBeenCalled();
});
