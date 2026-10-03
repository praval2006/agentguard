import { useEffect, useRef } from "react";

let entrancePlayed = false;
/** Open trust boundary and an independent evidence check; original vector mark. */
export function BrandMark({ entrance = false }: { entrance?: boolean }) {
  const mark = useRef<SVGSVGElement>(null);
  useEffect(() => {
    if (entrance && !entrancePlayed) {
      entrancePlayed = true;
      mark.current?.setAttribute("data-entrance", "true");
    }
  }, [entrance]);
  return (
    <svg
      ref={mark}
      className="brand-mark"
      viewBox="0 0 32 36"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      <path
        pathLength="1"
        d="M25 7.5 16 3 5 8.5v10c0 6.2 4.7 10.4 11 14 6.3-3.6 11-7.8 11-14V15"
        stroke="#aba0ed"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        pathLength="1"
        d="m11 17 4 4L27 8"
        stroke="#91bfff"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        pathLength="1"
        d="M11 26h5"
        stroke="#dcd5ff"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}
