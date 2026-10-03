import { useEffect, useRef } from "react";

/** Decorative only: one canvas, bounded density, no per-frame React state. */
export function AmbientBackground({ demo = false }: { demo?: boolean }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const node = canvas.current;
    if (!node) return;
    let ctx: CanvasRenderingContext2D | null;
    try {
      ctx = node.getContext("2d");
    } catch {
      return;
    }
    if (!ctx) return;
    const context = ctx;
    const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const pointer = window.matchMedia("(hover: hover) and (pointer: fine)");
    let width = 0,
      height = 0,
      frame = 0,
      last = 0,
      elapsed = 0;
    let scroll = 0,
      targetScroll = window.scrollY;
    let x = 0,
      y = 0,
      targetX = 0,
      targetY = 0,
      light = 0,
      active = false;
    let points: {
      x: number;
      y: number;
      depth: number;
      radius: number;
      ox: number;
      oy: number;
    }[] = [];
    const colors = ["143,133,194", "114,148,201", "177,165,218", "196,207,224"];
    const fine = () => pointer.matches && width > 800 && !motion.matches;
    function resize() {
      width = window.innerWidth;
      height = window.innerHeight;
      const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
      node!.width = Math.round(width * ratio);
      node!.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const count = Math.min(
        pointer.matches && width > 800 ? (demo ? 8 : 18) : demo ? 4 : 6,
        Math.max(4, Math.round((width * height) / (demo ? 150000 : 75000))),
      );
      points = Array.from({ length: count }, (_, i) => ({
        x: ((i * 0.618033 + 0.13) % 1) * width,
        y: ((i * 0.414214 + 0.21) % 1) * height,
        depth: 0.3 + (i % 3) * 0.25,
        radius: 0.6 + (i % 3) * 0.22,
        ox: 0,
        oy: 0,
      }));
      node!.dataset.particles = String(count);
      x = targetX = width / 2;
      y = targetY = height / 2;
      draw(0);
      restart();
    }
    function glow(
      cx: number,
      cy: number,
      radius: number,
      color: string,
      alpha: number,
    ) {
      const gradient = context.createRadialGradient(cx, cy, 0, cx, cy, radius);
      gradient.addColorStop(0, `rgba(${color},${alpha})`);
      gradient.addColorStop(0.45, `rgba(${color},${alpha * 0.35})`);
      gradient.addColorStop(1, `rgba(${color},0)`);
      context.fillStyle = gradient;
      context.fillRect(0, 0, width, height);
    }
    function draw(dt: number) {
      const moving = !motion.matches;
      elapsed += moving ? dt : 0;
      scroll += ((moving ? targetScroll : 0) - scroll) * 0.045;
      x += (targetX - x) * 0.07;
      y += (targetY - y) * 0.07;
      light += ((active && fine() ? 1 : 0) - light) * 0.06;
      context.clearRect(0, 0, width, height);
      const drift = Math.sin(elapsed / 28) * 38;
      const depth = moving ? Math.sin(scroll / 1500) * 65 : 0;
      glow(
        width * 0.24 + drift,
        height * 0.28 - depth,
        Math.max(width * 0.6, 460),
        "55,60,124",
        demo ? 0.1 : 0.16,
      );
      glow(
        width * 0.82 - drift,
        height * 0.77 + depth,
        Math.max(width * 0.46, 380),
        "47,77,117",
        demo ? 0.09 : 0.14,
      );
      for (const [i, p] of points.entries()) {
        if (moving)
          p.y = (p.y - dt * (1 + p.depth) + height + 12) % (height + 12);
        const px = p.x + (moving ? Math.sin(elapsed / 22 + i) * 12 : 0);
        const py =
          (p.y - ((moving ? scroll * 0.014 * p.depth : 0) % height) + height) %
          height;
        const dx = px - x,
          dy = py - y,
          distance = Math.hypot(dx, dy);
        const proximity =
          fine() && active ? Math.max(0, 1 - distance / 145) : 0;
        p.ox += ((dx / Math.max(distance, 1)) * proximity * 13 - p.ox) * 0.045;
        p.oy += ((dy / Math.max(distance, 1)) * proximity * 13 - p.oy) * 0.045;
        const edge = Math.min(1, py / 55, (height - py) / 55);
        context.fillStyle = `rgba(${colors[i % colors.length]},${(0.16 + p.depth * 0.16 + proximity * 0.1) * edge})`;
        context.beginPath();
        context.arc(px + p.ox, py + p.oy, p.radius, 0, Math.PI * 2);
        context.fill();
      }
      if (light > 0.001 && fine())
        glow(
          x,
          y,
          Math.max(380, width * 0.36),
          "91,77,151",
          light * (demo ? 0.045 : 0.065),
        );
    }
    function animate(time: number) {
      if (document.hidden || motion.matches) {
        frame = 0;
        return;
      }
      if (!last || time - last >= 1000 / 30) {
        draw(last ? Math.min((time - last) / 1000, 0.06) : 0);
        last = time;
      }
      frame = requestAnimationFrame(animate);
    }
    function restart() {
      cancelAnimationFrame(frame);
      frame = 0;
      last = 0;
      node!.dataset.motion = motion.matches ? "static" : "ambient";
      if (motion.matches) {
        active = false;
        light = 0;
        scroll = 0;
        points.forEach((p) => {
          p.ox = p.oy = 0;
        });
        draw(0);
      } else if (!document.hidden) frame = requestAnimationFrame(animate);
    }
    function move(event: PointerEvent) {
      if (event.pointerType === "touch" || !fine()) return;
      targetX = event.clientX;
      targetY = event.clientY;
      active = true;
    }
    function leave() {
      active = false;
    }
    function scrolled() {
      targetScroll = window.scrollY;
    }
    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("pointermove", move, { passive: true });
    document.documentElement.addEventListener("pointerleave", leave);
    window.addEventListener("blur", leave);
    window.addEventListener("scroll", scrolled, { passive: true });
    document.addEventListener("visibilitychange", restart);
    motion.addEventListener("change", restart);
    pointer.addEventListener("change", restart);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", move);
      document.documentElement.removeEventListener("pointerleave", leave);
      window.removeEventListener("blur", leave);
      window.removeEventListener("scroll", scrolled);
      document.removeEventListener("visibilitychange", restart);
      motion.removeEventListener("change", restart);
      pointer.removeEventListener("change", restart);
    };
  }, [demo]);
  return (
    <div
      className={`ambient-environment${demo ? " ambient-demo" : ""}`}
      aria-hidden="true"
    >
      <canvas ref={canvas} />
    </div>
  );
}
