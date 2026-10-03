import type { MouseEvent, ReactNode } from "react";
export function PageLink({
  to,
  children,
  className = "",
}: {
  to: string;
  children: ReactNode;
  className?: string;
}) {
  function navigate(event: MouseEvent<HTMLAnchorElement>) {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    event.preventDefault();
    window.history.pushState({}, "", to);
    window.dispatchEvent(new PopStateEvent("popstate"));
    window.scrollTo?.({ top: 0, behavior: "instant" });
  }
  return (
    <a href={to} className={className} onClick={navigate}>
      {children}
    </a>
  );
}
