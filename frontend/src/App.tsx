import { useEffect, useRef, useState } from "react";
import { PresentationPage } from "./PresentationPage";
import { ReviewDemo } from "./ReviewDemo";
export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const previousPath = useRef(path);
  useEffect(() => {
    const update = () => setPath(window.location.pathname);
    window.addEventListener("popstate", update);
    return () => window.removeEventListener("popstate", update);
  }, []);
  useEffect(() => {
    const target = document.getElementById(
      window.location.hash.slice(1) || "main",
    );
    const changed = previousPath.current !== path;
    previousPath.current = path;
    if (target && (changed || window.location.hash)) {
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      if (window.location.hash)
        target.scrollIntoView?.({ behavior: "instant" });
    }
    document.title =
      path === "/demo"
        ? "AgentGuard — Acceptance Review"
        : "AgentGuard — Build with AI. Verify with evidence.";
  }, [path]);
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      {path === "/demo" ? <ReviewDemo /> : <PresentationPage />}
    </>
  );
}
