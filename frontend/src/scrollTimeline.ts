export const clamp = (n: number) => Math.max(0, Math.min(1, n));
export const range = (p: number, a: number, b: number) =>
  clamp((p - a) / (b - a));
export const timeline = {
  task: [0, 0.18],
  work: [0.12, 0.32],
  tests: [0.26, 0.43],
  complete: [0.37, 0.55],
  question: [0.48, 0.66],
  handoff: [0.6, 0.76],
  verification: [0.72, 0.91],
  payoff: [0.87, 1.06],
} as const;
export type Scene = keyof typeof timeline;
export function pose(scene: Scene, p: number) {
  const [start, end] = timeline[scene];
  const local = range(p, start, end);
  const enter = scene === "task" ? 1 : range(p, start, start + 0.035);
  const leave = scene === "payoff" ? 0 : range(p, end - 0.035, end);
  return {
    opacity: Math.min(enter, 1 - leave),
    y: (1 - enter) * 55 - leave * 65,
    scale:
      1 - (scene === "complete" || scene === "question" ? 0.23 : 0.08) * local,
  };
}
