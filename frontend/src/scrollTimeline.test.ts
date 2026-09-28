import { describe, it, expect } from "vitest";
import { pose, timeline } from "./scrollTimeline";
describe("native scroll choreography", () => {
  it("keeps a visible scene throughout the scroll distance", () => {
    for (let i = 0; i <= 1000; i++)
      expect(
        Math.max(
          ...Object.keys(timeline).map(
            (s) => pose(s as keyof typeof timeline, i / 1000).opacity,
          ),
        ),
      ).toBeGreaterThan(0);
  });
  it("interpolates and returns the same pose when scrolling backward", () => {
    const before = pose("complete", 0.42);
    expect(pose("complete", 0.44).scale).toBeLessThan(before.scale);
    expect(pose("complete", 0.56).opacity).toBe(0);
    expect(pose("complete", 0.42)).toEqual(before);
  });
});
