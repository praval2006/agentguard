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
    let atmosphere = 1,
      targetAtmosphere = 1;
    let observer: IntersectionObserver | undefined;
    let points: {
      x: number;
      y: number;
      depth: number;
      radius: number;
      ox: number;
      oy: number;
    }[] = [];
    let dust: {
      x: number;
      y: number;
      radius: number;
      vx: number;
      vy: number;
      ox: number;
      oy: number;
      color: string;
    }[] = [];
    let traces: Path2D[] = [];
    let lineGradient: CanvasGradient;
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
        pointer.matches && width > 800 ? (demo ? 130 : 300) : demo ? 24 : 55,
        Math.max(12, Math.round((width * height) / (demo ? 11200 : 4600))),
      );
      // Repeatable pseudo-random positions avoid a visible lattice; O(n), no pairs.
      let seed = 91827;
      const random = () => {
        seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
        return seed / 4294967296;
      };
      points = Array.from({ length: count }, (_, i) => {
        const depth = i % 20 === 0 ? 0.85 : i % 4 === 0 ? 0.4 : 0.12;
        return {
          x: random() * width,
          y: random() * height,
          depth,
          radius: i % 20 === 0 ? 1.45 : i % 5 === 0 ? 1 : 0.55 + depth * 0.4,
          ox: 0,
          oy: 0,
        };
      });
      const secondaryCount = Math.min(
        pointer.matches && width > 800 ? (demo ? 250 : 620) : demo ? 35 : 80,
        Math.max(18, Math.round((width * height) / (demo ? 5600 : 2350))),
      );
      dust = Array.from({ length: secondaryCount }, (_, i) => ({
        x: random() * width,
        y: random() * height,
        radius: 0.5 + random() * 0.25,
        vx: 0.8 + (i % 3) * 0.55,
        vy: -0.25 - (i % 3) * 0.3,
        ox: 0,
        oy: 0,
        color: `rgba(${colors[i % colors.length]},${(0.18 + random() * 0.12) * (demo ? 0.78 : 1)})`,
      }));
      // Stable trace geometry/gradient created only on resize, not per particle/frame.
      traces = [];
      for (let i = 0; i < 3; i++) {
        const path = new Path2D();
        path.moveTo(-80, height * 0.13 + i * 18);
        path.bezierCurveTo(
          width * 0.12,
          height * 0.28 + i * 18,
          width * 0.27,
          height * 0.02 + i * 18,
          width * 0.48,
          -30 + i * 12,
        );
        path.moveTo(width * 0.6, height + 40 + i * 16);
        path.bezierCurveTo(
          width * 0.72,
          height * 0.75 + i * 16,
          width * 0.87,
          height * 0.88 + i * 16,
          width + 60,
          height * 0.58 + i * 16,
        );
        traces.push(path);
      }
      const parallel = new Path2D();
      for (let i = 0; i < 5; i++) {
        parallel.moveTo(-20, height * 0.66 + i * 13);
        parallel.lineTo(width * 0.17 - i * 9, height * 0.58 + i * 13);
      }
      traces.push(parallel);
      lineGradient = context.createLinearGradient(0, 0, width, height);
      lineGradient.addColorStop(0, "rgba(117,142,211,0)");
      lineGradient.addColorStop(0.12, "rgba(117,142,211,.18)");
      lineGradient.addColorStop(0.42, "rgba(117,142,211,0)");
      lineGradient.addColorStop(0.68, "rgba(155,133,204,0)");
      lineGradient.addColorStop(0.88, "rgba(155,133,204,.18)");
      lineGradient.addColorStop(1, "rgba(155,133,204,0)");
      node!.dataset.particles = String(count);
      node!.dataset.secondaryParticles = String(secondaryCount);
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
      atmosphere += (targetAtmosphere - atmosphere) * 0.025;
      x += (targetX - x) * 0.14;
      y += (targetY - y) * 0.14;
      light += ((active && fine() ? 1 : 0) - light) * 0.06;
      context.clearRect(0, 0, width, height);
      const drift = Math.sin(elapsed / 28) * 38;
      const depth = moving ? Math.sin(scroll / 1500) * 65 : 0;
      glow(
        width * 0.24 + drift,
        height * 0.28 - depth,
        Math.max(width * 0.6, 460),
        "55,60,124",
        (demo ? 0.12 : 0.22) * atmosphere,
      );
      glow(
        width * 0.82 - drift,
        height * 0.77 + depth,
        Math.max(width * 0.46, 380),
        "47,77,117",
        (demo ? 0.11 : 0.2) * atmosphere,
      );
      // Elongated edge haze keeps the central reading area clear.
      context.save();
      context.scale(1, 0.32);
      glow(
        -width * 0.04 + drift,
        height * 1.35 - depth,
        Math.max(420, width * 0.5),
        "77,65,137",
        (demo ? 0.08 : 0.17) * atmosphere,
      );
      glow(
        width * 1.04 - drift,
        height * 2.2 + depth,
        Math.max(400, width * 0.48),
        "38,91,143",
        (demo ? 0.07 : 0.15) * atmosphere,
      );
      context.restore();
      // Only two faded edge fragments, never a viewport-wide grid.
      context.lineWidth = 0.6;
      const trace = (demo ? 0.04 : 0.065) * atmosphere;
      for (let j = 0; j < 2; j++) {
        const left = j === 0 ? width * 0.03 : width * 0.86;
        const top = height * (j === 0 ? 0.24 : 0.62) - depth * 0.22;
        for (let k = 0; k < 5; k++) {
          const fade = 1 - Math.abs(k - 2) / 3;
          context.strokeStyle = `rgba(125,153,205,${trace * fade})`;
          context.beginPath();
          context.moveTo(left + k * 26, top);
          context.lineTo(left + k * 26, top + 104);
          context.moveTo(left, top + k * 26);
          context.lineTo(left + 104, top + k * 26);
          context.stroke();
        }
      }
      context.strokeStyle = `rgba(131,142,204,${trace * 0.7})`;
      context.beginPath();
      context.arc(
        width * 1.12,
        height * 0.48 + depth * 0.15,
        width * 0.34,
        Math.PI * 0.8,
        Math.PI * 1.24,
      );
      context.stroke();
      context.save();
      context.translate(0, -depth * 0.12);
      context.strokeStyle = lineGradient;
      context.globalAlpha = atmosphere * (demo ? 0.4 : 0.8);
      for (let i = 0; i < traces.length; i++) context.stroke(traces[i]);
      if (fine() && light > 0.001) {
        const reveal = context.createRadialGradient(x, y, 0, x, y, 300);
        reveal.addColorStop(0, "rgba(155,165,228,.12)");
        reveal.addColorStop(1, "rgba(155,165,228,0)");
        context.strokeStyle = reveal;
        context.globalAlpha = light * (demo ? 0.35 : 0.65);
        for (let i = 0; i < traces.length; i++) context.stroke(traces[i]);
      }
      context.restore();
      const interactive = fine() && active;
      // Deep field flows coherently, with only a small cursor displacement.
      for (let i = 0; i < dust.length; i++) {
        const p = dust[i];
        if (moving) {
          p.x = (p.x + p.vx * dt + width) % width;
          p.y = (p.y + p.vy * dt + height) % height;
        }
        const py =
          (p.y - ((moving ? scroll * 0.003 : 0) % height) + height) % height;
        const dx = p.x - x,
          dy = py - y;
        const distance = interactive ? Math.hypot(dx, dy) : 270;
        const t = Math.max(0, 1 - distance / 270);
        const influence = t * t * (3 - 2 * t);
        p.ox += ((dx / Math.max(1, distance)) * influence * 4 - p.ox) * 0.06;
        p.oy += ((dy / Math.max(1, distance)) * influence * 4 - p.oy) * 0.06;
        context.globalAlpha = (0.35 + 0.65 * Math.pow(Math.abs(p.x / width - 0.5) * 2, 0.7)) * Math.min(
          1,
          p.x / 35,
          (width - p.x) / 35,
          py / 35,
          (height - py) / 35,
        );
        context.fillStyle = p.color;
        context.beginPath();
        context.arc(p.x + p.ox, py + p.oy, p.radius, 0, Math.PI * 2);
        context.fill();
      }
      context.globalAlpha = 1;
      for (let i = 0; i < points.length; i++) {
        const p = points[i];
        if (moving)
          p.y =
            (p.y - dt * (0.22 + p.depth * 1.2) + height + 12) % (height + 12);
        const px = p.x + (moving ? Math.sin(elapsed / 22 + i) * 12 : 0);
        const py =
          (p.y - ((moving ? scroll * 0.014 * p.depth : 0) % height) + height) %
          height;
        const dx = px - x,
          dy = py - y,
          distance = interactive ? Math.hypot(dx, dy) : 270;
        const t = interactive ? Math.max(0, 1 - distance / 270) : 0;
        const proximity = t * t * (3 - 2 * t);
        const force = proximity * (3 + p.depth * 44);
        p.ox += ((dx / Math.max(distance, 1)) * force - p.ox) * 0.09;
        p.oy += ((dy / Math.max(distance, 1)) * force - p.oy) * 0.09;
        const edge = Math.min(1, py / 55, (height - py) / 55) *
          (0.35 + 0.65 * Math.pow(Math.abs(px / width - 0.5) * 2, 0.7));
        context.fillStyle = `rgba(${colors[i % colors.length]},${(0.18 + p.depth * 0.26 + proximity * p.depth * 0.12) * edge * (demo ? 0.8 : 1)})`;
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
          light * (demo ? 0.07 : 0.105),
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
        dust.forEach((p) => {
          p.ox = p.oy = 0;
        });
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
    if (!demo && typeof IntersectionObserver !== "undefined") {
      const emphasis: Record<string, number> = {
        problem: 0.65,
        gap: 1.05,
        agentguard: 1.1,
        authority: 1.1,
        trust: 1.2,
        boundary: 0.6,
        report: 0.7,
        closing: 1.05,
      };
      observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries)
            if (entry.isIntersecting) {
              targetAtmosphere = emphasis[entry.target.id] ?? 1;
            }
        },
        { rootMargin: "-45% 0px -45% 0px" },
      );
      document
        .querySelectorAll(".hero-stage, .presentation-scene")
        .forEach((section) => observer!.observe(section));
    }
    window.addEventListener("resize", resize);
    window.addEventListener("pointermove", move, { passive: true });
    document.documentElement.addEventListener("pointerleave", leave);
    window.addEventListener("blur", leave);
    window.addEventListener("scroll", scrolled, { passive: true });
    document.addEventListener("visibilitychange", restart);
    motion.addEventListener("change", restart);
    pointer.addEventListener("change", resize);
    return () => {
      observer?.disconnect();
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", move);
      document.documentElement.removeEventListener("pointerleave", leave);
      window.removeEventListener("blur", leave);
      window.removeEventListener("scroll", scrolled);
      document.removeEventListener("visibilitychange", restart);
      motion.removeEventListener("change", restart);
      pointer.removeEventListener("change", resize);
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
