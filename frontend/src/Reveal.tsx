import { useEffect, useRef, type ReactNode } from "react";
/** Visible fallback. Reversible entry, no scroll interception or one-way state. */
export function Reveal({
  children,
  variant = "fade-rise",
  className = "",
}: {
  children: ReactNode;
  variant?:
    "fade-rise" | "slide-left" | "slide-right" | "stagger-children" | "line";
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const media = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    let observer: IntersectionObserver | undefined;
    function setup() {
      observer?.disconnect();
      node!.classList.remove("reveal-ready", "reveal-entered");
      if (media?.matches || !("IntersectionObserver" in window)) return;
      try {
        observer = new IntersectionObserver(
          (entries) => {
            for (const entry of entries) {
              // Exit only below the viewport; scrolling back down replays naturally.
              // Above-view content stays visible for backwards navigation and focus.
              node!.classList.toggle(
                "reveal-entered",
                entry.isIntersecting || entry.boundingClientRect.top < 0,
              );
            }
          },
          { threshold: 0, rootMargin: "0px 0px -30px 0px" },
        );
        observer.observe(node!);
        node!.classList.add("reveal-ready");
      } catch {
        node!.classList.remove("reveal-ready");
      }
    }
    setup();
    media?.addEventListener("change", setup);
    return () => {
      observer?.disconnect();
      media?.removeEventListener("change", setup);
    };
  }, []);
  return (
    <div ref={ref} className={`reveal ${className}`} data-reveal={variant}>
      {children}
    </div>
  );
}
