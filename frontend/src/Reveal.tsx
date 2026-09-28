import { useEffect, useRef, type ReactNode } from "react";

/** Reveal once; content is visible by default, even if observation fails. */
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
    if (!node || !("IntersectionObserver" in window)) return;
    const media = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (media?.matches) return;
    let observer: IntersectionObserver | undefined;
    try {
      observer = new IntersectionObserver(
        (entries) => {
          if (entries.some((e) => e.isIntersecting)) {
            node.classList.add("reveal-entered");
            observer?.disconnect();
          }
        },
        { threshold: 0.12 },
      );
      observer.observe(node);
    } catch {
      observer?.disconnect();
    }
    const stop = () => {
      if (media?.matches) {
        observer?.disconnect();
        node.classList.remove("reveal-entered");
      }
    };
    media?.addEventListener("change", stop);
    return () => {
      observer?.disconnect();
      media?.removeEventListener("change", stop);
    };
  }, []);
  return (
    <div ref={ref} className={`reveal ${className}`} data-reveal={variant}>
      {children}
    </div>
  );
}
