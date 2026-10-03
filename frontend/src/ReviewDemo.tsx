import { useEffect, useRef, useState } from "react";
import { PageLink } from "./navigation";
import {
  accountTask,
  ambiguity,
  suggestions,
  selectedFixture,
  type Decision,
  type SuggestionId,
  type AccountReport,
} from "./accountDemoData";
import type { Verdict } from "./data";

type Stage =
  | "INTRO"
  | "ANALYZING"
  | "REVIEW"
  | "CONTRACT"
  | "VERIFYING"
  | "RESULTS"
  | "REPORT";
const stages: Stage[] = [
  "INTRO",
  "ANALYZING",
  "REVIEW",
  "CONTRACT",
  "VERIFYING",
  "RESULTS",
  "REPORT",
];
function Badge({ value }: { value: Verdict }) {
  return (
    <span className={`badge ${value.toLowerCase()}`}>
      {value === "PASS" ? "✓" : value === "FAIL" ? "×" : "—"} {value}
    </span>
  );
}
function Ambiguity() {
  return (
    <aside className="ambiguity-note" aria-label="Unresolved ambiguity">
      <span className="eyebrow">? / AMBIGUITY · REQUIRES CLARIFICATION</span>
      <p>{ambiguity}</p>
      <small>No verdict. This remains a product decision.</small>
    </aside>
  );
}
function Evidence({
  report,
  tick,
  complete,
}: {
  report: AccountReport;
  tick: number;
  complete: boolean;
}) {
  return (
    <div className="evidence-flow" aria-label="Selected verification results">
      <div className="action-origin">
        <span className="signal-dot" /> DELETE ACCOUNT{" "}
        <span>→ controlled observation</span>
      </div>
      {report.results.map((result, i) => {
        const observed = complete || tick >= i * 2 + 1;
        const graded = complete || tick >= i * 2 + 2;
        return (
          <article
            key={result.id}
            className={`evidence-row ${observed ? "observed" : ""}`}
            aria-label={result.title}
          >
            <span className="evidence-number">0{i + 1}</span>
            <div>
              <div className="eyebrow">{result.operation}</div>
              <h3>{result.title}</h3>
              <small>
                {result.source === "explicit"
                  ? "YOUR REQUEST · EXPLICIT"
                  : "AGENTGUARD SUGGESTION · ACCEPTED BY YOU"}
              </small>
              {observed ? (
                <div className="evidence-values">
                  <p>
                    <span>EXPECTED</span>
                    {result.expected}
                  </p>
                  <p>
                    <span>OBSERVED / {result.response}</span>
                    {result.observed}
                  </p>
                </div>
              ) : (
                <p className="waiting">Awaiting controlled evidence…</p>
              )}
            </div>
            <div className="verdict-slot">
              {graded ? (
                <Badge value={result.verdict} />
              ) : (
                <span className="waiting">
                  {observed ? "Evidence recorded" : "—"}
                </span>
              )}
            </div>
          </article>
        );
      })}
    </div>
  );
}
export function ReviewDemo({
  onComplete,
}: {
  onComplete?: (value: boolean) => void;
}) {
  const [stage, setStage] = useState<Stage>("INTRO");
  const [decisions, setDecisions] = useState<Record<SuggestionId, Decision>>({
    session: "PENDING",
    profile: "PENDING",
  });
  const [tick, setTick] = useState(0);
  const [reduced, setReduced] = useState(
    () =>
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false,
  );
  const heading = useRef<HTMLHeadingElement>(null);
  const report = selectedFixture(decisions);
  const complete = stage === "RESULTS" || stage === "REPORT";
  useEffect(() => {
    const media = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!media) return;
    const update = () => setReduced(media.matches);
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    onComplete?.(complete);
  }, [complete, onComplete]);
  useEffect(() => {
    if (stage !== "ANALYZING") return;
    const timer = setTimeout(() => setStage("REVIEW"), reduced ? 0 : 1600);
    return () => clearTimeout(timer);
  }, [stage, reduced]);
  useEffect(() => {
    if (stage !== "VERIFYING" || !report) return;
    const timer = setTimeout(
      () => {
        if (reduced || tick >= report.results.length * 2) setStage("RESULTS");
        else setTick((t) => t + 1);
      },
      reduced ? 0 : 800,
    );
    return () => clearTimeout(timer);
  }, [stage, tick, reduced, report]);
  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
    if (stage !== "INTRO")
      heading.current?.scrollIntoView?.({
        block: "start",
        behavior: "instant",
      });
    else window.scrollTo?.({ top: 0, behavior: "instant" });
  }, [stage]);
  function analyze() {
    setStage(reduced ? "REVIEW" : "ANALYZING");
  }
  function run() {
    if (!report) return;
    setTick(0);
    setStage(reduced ? "RESULTS" : "VERIFYING");
  }
  function change() {
    setTick(0);
    setStage("REVIEW");
  }
  function reset() {
    setDecisions({ session: "PENDING", profile: "PENDING" });
    setTick(0);
    setStage("INTRO");
  }
  const title = {
    INTRO: "What does “done” mean?",
    ANALYZING: "Looking beyond the prompt.",
    REVIEW: "You decide what matters.",
    CONTRACT: "This is the acceptance contract.",
    VERIFYING: "Observe first. Then verify.",
    RESULTS: "The evidence changes the story.",
    REPORT: "Acceptance Verification Report",
  }[stage];
  const status =
    stage === "REVIEW"
      ? report
        ? "Decisions recorded. Your contract is ready."
        : "Review incomplete. Add or dismiss both suggestions to continue."
      : stage === "VERIFYING"
        ? tick === 0
          ? "Playing controlled deletion observation."
          : tick % 2
            ? "Observed evidence revealed. Verdict follows."
            : "Fixture verdict revealed after evidence."
        : stage === "RESULTS"
          ? "Playback complete. Only selected behaviors have results."
          : stage === "ANALYZING"
            ? "Reviewing controlled task and context."
            : `${stage.toLowerCase()} stage`;
  return (
    <div className="demo-page">
      <header className="demo-header">
        <PageLink to="/" className="back-link">
          ← Back to presentation
        </PageLink>
        <span className="wordmark">AGENTGUARD</span>
        <span className="demo-label">CONTROLLED DEMONSTRATION</span>
      </header>
      <main id="main" className="demo-main">
        <div className="demo-topline">
          <span>ACCEPTANCE WORKSPACE / ACCOUNT DELETION</span>
          <button className="quiet-button" onClick={reset}>
            Reset demo ↺
          </button>
        </div>
        <ol className="demo-progress" aria-label="Demo progression">
          {["Review", "Contract", "Observe", "Report"].map((label, i) => (
            <li
              key={label}
              className={
                stages.indexOf(stage) >= [2, 3, 4, 6][i] ? "active" : ""
              }
            >
              {String(i + 1).padStart(2, "0")} <span>{label}</span>
            </li>
          ))}
        </ol>
        <div className="demo-heading">
          <span className="eyebrow">
            {stage === "INTRO" ? "AGENTGUARD / ACCEPTANCE REVIEW" : stage}
          </span>
          <h1 ref={heading} tabIndex={-1}>
            {title}
          </h1>
        </div>
        {stage === "INTRO" && (
          <div className="intro-composition">
            <div className="task-sheet">
              <span className="eyebrow">THE ORIGINAL REQUEST</span>
              <blockquote>“{accountTask}”</blockquote>
              <div className="agent-stamp">
                <span>CODING AGENT</span>
                <p>✓ Implementation complete</p>
                <p>✓ Tests passing</p>
                <p>✓ Task complete</p>
              </div>
            </div>
            <div className="intro-action">
              <p>
                The implementation is done.
                <br />
                <strong>Is the acceptance complete?</strong>
              </p>
              <button className="button" onClick={analyze}>
                Analyze acceptance →
              </button>
            </div>
          </div>
        )}
        {stage === "ANALYZING" && (
          <div className="analysis-composition">
            <div className="analysis-orbit" aria-hidden="true">
              <span className="brand-mark">A</span>
            </div>
            <div className="analysis-inputs">
              <span>TASK</span>
              <span>REPOSITORY CONTEXT</span>
              <span>FINISHED CHANGE</span>
            </div>
            <p>
              A controlled review of acceptance intent.
              <br />
              No live model or repository is being queried.
            </p>
          </div>
        )}
        {stage === "REVIEW" && (
          <>
            <div className="review-request">
              Original request <q>{accountTask}</q>
            </div>
            <div className="review-layout">
              <article
                className="explicit-review"
                aria-label="Explicit requirement"
              >
                <div className="review-meta">
                  YOUR REQUIREMENT <span>EXPLICIT · INCLUDED</span>
                </div>
                <h2>Account is permanently deleted.</h2>
                <p>Automatically included. No approval needed.</p>
              </article>
              {suggestions.map((item) => (
                <article
                  key={item.id}
                  className={`suggestion-review ${decisions[item.id].toLowerCase()}`}
                  aria-label={item.title}
                >
                  <div className="review-meta">
                    AGENTGUARD SUGGESTION{" "}
                    <span>
                      {decisions[item.id] === "ACCEPTED"
                        ? "ACCEPTED BY YOU"
                        : decisions[item.id]}
                    </span>
                  </div>
                  <h2>{item.behavior}</h2>
                  <p className="rationale">Context · {item.rationale}</p>
                  <div className="review-bottom">
                    <small>
                      INFERRED · illustrative context, not verified provenance
                    </small>
                    <div className="choice-actions">
                      <button
                        className="quiet-button"
                        aria-pressed={decisions[item.id] === "DISMISSED"}
                        onClick={() =>
                          setDecisions((d) => ({
                            ...d,
                            [item.id]: "DISMISSED",
                          }))
                        }
                      >
                        Dismiss
                      </button>
                      <button
                        className="choice-button"
                        aria-pressed={decisions[item.id] === "ACCEPTED"}
                        onClick={() =>
                          setDecisions((d) => ({ ...d, [item.id]: "ACCEPTED" }))
                        }
                      >
                        {decisions[item.id] === "ACCEPTED"
                          ? "✓ Added to contract"
                          : "+ Add to verification"}
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
            <Ambiguity />
            <div className="demo-actions">
              <span>Suggestions stay inferred, even after approval.</span>
              <button
                className="button"
                disabled={!report}
                aria-describedby="demo-status"
                onClick={() => setStage("CONTRACT")}
              >
                Review acceptance contract →
              </button>
            </div>
          </>
        )}
        {stage === "CONTRACT" && report && (
          <>
            <div
              className="contract-surface product-surface"
              aria-label="Acceptance contract"
            >
              <div className="surface-bar">
                <span>ACCEPTANCE CONTRACT / FROZEN FOR THIS PLAYBACK</span>
                <span>{report.selected} SELECTED</span>
              </div>
              {report.results.map((item, i) => (
                <article className="contract-entry" key={item.id}>
                  <span>0{i + 1}</span>
                  <div>
                    <h2>{item.title}</h2>
                    <p>
                      {item.source === "explicit"
                        ? "YOUR REQUEST · EXPLICIT · AUTOMATICALLY INCLUDED"
                        : "AGENTGUARD SUGGESTION · INFERRED · ACCEPTED BY YOU"}
                    </p>
                  </div>
                  <span aria-hidden="true">↳</span>
                </article>
              ))}
            </div>
            <div className="review-history" aria-label="Review history">
              {suggestions.map((s) => (
                <p key={s.id}>
                  {s.title}: <strong>{decisions[s.id]}</strong>
                  {decisions[s.id] === "DISMISSED" &&
                    " · not included · no verdict"}
                </p>
              ))}
            </div>
            <div className="demo-actions">
              <button className="quiet-button" onClick={change}>
                Change decision
              </button>
              <button className="button" onClick={run}>
                Run independent verification →
              </button>
            </div>
          </>
        )}
        {(stage === "VERIFYING" || stage === "RESULTS") && report && (
          <>
            <Evidence report={report} tick={tick} complete={complete} />
            {stage === "RESULTS" && (
              <>
                <div className="demo-payoff" data-testid="story-payoff">
                  <p>The coding agent completed the prompt.</p>
                  <h2>
                    AgentGuard helped
                    <br />
                    <em>complete the requirement.</em>
                  </h2>
                  <small>
                    For the behaviors you selected. A narrower contract supports
                    a narrower conclusion.
                  </small>
                </div>
                <div className="demo-actions">
                  <button className="quiet-button" onClick={change}>
                    Change decision
                  </button>
                  <button className="quiet-button" onClick={run}>
                    Replay verification ↺
                  </button>
                  <button className="button" onClick={() => setStage("REPORT")}>
                    Assemble verification report →
                  </button>
                </div>
              </>
            )}
          </>
        )}
        {stage === "REPORT" && report && (
          <>
            <div className="final-report product-surface">
              <div className="surface-bar">
                <span>ACCOUNT DELETION</span>
                <span>CONTROLLED REPORT FIXTURE</span>
              </div>
              <div className="report-summary" aria-label="Verification summary">
                <div>
                  <span>OVERALL</span>
                  <Badge value={report.overall} />
                </div>
                <div>
                  <strong>{report.selected}</strong>
                  <span>SELECTED</span>
                </div>
                <div>
                  <strong>{report.pass}</strong>
                  <span>PASS</span>
                </div>
                <div>
                  <strong>{report.fail}</strong>
                  <span>FAIL</span>
                </div>
                <div>
                  <strong>{report.unverified}</strong>
                  <span>UNVERIFIED</span>
                </div>
              </div>
              <Evidence report={report} tick={tick} complete />
              <div className="report-review-history">
                <h3>Human decisions</h3>
                {suggestions.map((s) => (
                  <p key={s.id}>
                    {s.title} <strong>{decisions[s.id]}</strong>
                    {decisions[s.id] === "DISMISSED"
                      ? " · not verified"
                      : " · origin remains inferred"}
                  </p>
                ))}
              </div>
              <Ambiguity />
              <p className="report-limit">
                These fixed presentation records mirror backend report concepts.
                They are not a dynamically generated backend report. No
                complete-correctness claim.
              </p>
            </div>
            <div className="demo-actions">
              <button className="quiet-button" onClick={change}>
                Change decision
              </button>
              <button className="quiet-button" onClick={run}>
                Replay verification ↺
              </button>
              <PageLink to="/#trust" className="button">
                Explore the trust architecture →
              </PageLink>
            </div>
          </>
        )}
        <p
          id="demo-status"
          className="demo-status"
          role="status"
          aria-live="polite"
        >
          {status}
        </p>
        <p className="demo-disclosure">
          Controlled AgentGuard demonstration · local fixture playback · no live
          requests
        </p>
      </main>
    </div>
  );
}
