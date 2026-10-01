import { useEffect, useRef, useState } from "react";
import { demo, type Verdict } from "./data";
import {
  reviewExample,
  reviewedReports,
  type ReviewItem,
  type ReviewState,
} from "./reviewData";

const phases = [
  "Reading accepted contract",
  "Grounding selected behaviours",
  "Playing controlled observations",
];
function Badge({ value }: { value: Verdict }) {
  return <span className={`badge ${value.toLowerCase()}`}>{value}</span>;
}
export function ReviewDemo({
  onComplete,
}: {
  onComplete: (value: boolean) => void;
}) {
  const [decision, setDecision] = useState<ReviewState>("PENDING");
  const [step, setStep] = useState(-1);
  const [reduced, setReduced] = useState(
    () =>
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false,
  );
  const reviewHeading = useRef<HTMLHeadingElement>(null);
  const item: ReviewItem =
    decision === "ACCEPTED"
      ? { origin: "inferred", state: decision, included: true }
      : { origin: "inferred", state: decision, included: false };
  const report = decision === "PENDING" ? null : reviewedReports[decision];
  const complete =
    report !== null && step >= phases.length + report.results.length;
  const running = step >= 0 && !complete;
  useEffect(() => {
    const media = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!media) return;
    const update = () => setReduced(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => onComplete(complete), [complete, onComplete]);
  useEffect(() => {
    if (!running) return;
    const timer = setTimeout(() => setStep((s) => s + 1), reduced ? 0 : 320);
    return () => clearTimeout(timer);
  }, [step, running, reduced]);
  function run() {
    if (!report || running) return;
    setStep(reduced ? phases.length + report.results.length : 0);
  }
  function reset() {
    setStep(-1);
    setDecision("PENDING");
    requestAnimationFrame(() =>
      reviewHeading.current?.focus({ preventScroll: true }),
    );
  }
  function change() {
    setStep(-1);
    requestAnimationFrame(() =>
      reviewHeading.current?.focus({ preventScroll: true }),
    );
  }
  const notice =
    decision === "PENDING"
      ? "Review incomplete. Add or dismiss the suggestion before verification."
      : decision === "ACCEPTED"
        ? "Added to acceptance contract. Ready for verification."
        : "Dismissed — not included in verification. Ready for verification.";
  return (
    <section className="review-demo" aria-label="Reviewed acceptance demo">
      <p className="review-disclosure">
        ILLUSTRATIVE LOCAL DEMO · NO LIVE MODEL OR BACKEND
        <br />
        Shorter task variant; not a new run of the historical subscription
        evaluation.
      </p>
      {step < 0 ? (
        <>
          <header className="review-heading">
            <span className="eyebrow">HUMAN / ACCEPTANCE REVIEW</span>
            <h2 ref={reviewHeading} tabIndex={-1}>
              You decide what matters.
            </h2>
          </header>
          <div className="review-cards">
            <article className="review-card" aria-label="Explicit requirement">
              <div className="review-meta">
                EXPLICIT REQUIREMENT <span>INCLUDED</span>
              </div>
              <h3>{reviewExample.explicit.title}</h3>
              <small>ORIGIN · YOUR REQUEST</small>
              <p>{reviewExample.explicit.behavior}</p>
              <span className="review-note">
                Included automatically. No approval needed.
              </span>
            </article>
            <article
              className="review-card suggestion"
              aria-label="AgentGuard suggestion"
            >
              <div className="review-meta">
                AGENTGUARD SUGGESTION <span>{item.state}</span>
              </div>
              <h3>{reviewExample.suggestion.title}</h3>
              <small>ORIGIN · AGENTGUARD SUGGESTION</small>
              <p>{reviewExample.suggestion.behavior}</p>
              <strong className="review-note">
                This was not explicitly requested.
              </strong>
              <p className="review-rationale">
                <b>Why suggested</b> · {reviewExample.suggestion.rationale}
                <br />
                <small>
                  Illustrative model rationale, not verified repository
                  evidence.
                </small>
              </p>
              <div className="review-actions">
                <button
                  className="review-choice"
                  aria-pressed={decision === "ACCEPTED"}
                  onClick={() => setDecision("ACCEPTED")}
                >
                  Add to verification
                </button>
                <button
                  className="review-choice"
                  aria-pressed={decision === "DISMISSED"}
                  onClick={() => setDecision("DISMISSED")}
                >
                  Dismiss
                </button>
              </div>
            </article>
          </div>
        </>
      ) : (
        <header className="review-heading">
          <span className="eyebrow">AGENTGUARD</span>
          <h2>Acceptance Verification</h2>
        </header>
      )}
      <aside className="review-contract" aria-label="Acceptance contract">
        <div className="eyebrow">
          ACCEPTANCE CONTRACT · {item.included ? "2 behaviours" : "1 behaviour"}{" "}
          selected for verification
        </div>
        <p>
          ✓ {reviewExample.explicit.title} <small>— Your request</small>
        </p>
        {item.included ? (
          <p>
            ✓ {reviewExample.suggestion.title}{" "}
            <small>— AgentGuard suggestion · Accepted by you</small>
          </p>
        ) : (
          <p className="excluded">
            {reviewExample.suggestion.title}{" "}
            <small>
              — {decision === "PENDING" ? "Pending" : "Dismissed"} · not
              included
            </small>
          </p>
        )}
      </aside>
      <div className="review-controls">
        <button
          className="button cyan"
          onClick={run}
          disabled={decision === "PENDING" || running}
          aria-describedby="review-progress"
        >
          {complete ? "Replay verification" : "Run verification"} ↗
        </button>
        {step >= 0 && (
          <button className="review-choice" disabled={running} onClick={change}>
            Change decision
          </button>
        )}
        {step >= 0 && (
          <button className="review-choice" onClick={reset}>
            Reset
          </button>
        )}
      </div>
      <p
        id="review-progress"
        className="review-progress"
        role="status"
        aria-live="polite"
      >
        {step < 0
          ? notice
          : complete
            ? "Playback complete — selected evidence shown."
            : (phases[step] ?? "Revealing selected evidence…")}
      </p>
      {step >= 0 && report && (
        <div
          className="review-report"
          aria-label="Selected verification results"
        >
          {complete && (
            <div className="review-overall">
              Overall result <Badge value={report.overall} />
              <small>{report.counts}</small>
            </div>
          )}
          {report.results
            .slice(0, Math.max(0, step - phases.length + 1))
            .map((result) => (
              <article className="review-result" key={result.id}>
                <div>
                  <h3>{result.title}</h3>
                  <Badge value={result.verdict} />
                </div>
                <small>
                  ORIGIN ·{" "}
                  {result.origin === "explicit"
                    ? "YOUR REQUEST"
                    : "AGENTGUARD SUGGESTION · ACCEPTED BY YOU"}
                </small>
                <p>{result.behavior}</p>
                <div className="review-values">
                  <code>Expected: {result.expected}</code>
                  <code>Observed: {result.observed}</code>
                </div>
                <small>
                  Controlled evidence: {demo.endpoint} · {result.observation}
                </small>
              </article>
            ))}
          {complete && (
            <p className="review-boundary">
              PASS: observed evidence matched the accepted behaviour. FAIL:
              observed evidence contradicted it. UNVERIFIED: supported
              observations could not establish it.
              <br />
              These fixed samples do not establish complete correctness or
              verify excluded behaviours.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
