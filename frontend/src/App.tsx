import { Reveal } from "./Reveal";
import { ReviewDemo } from "./ReviewDemo";
import { CinematicStory } from "./CinematicStory";
import { useState } from "react";
import {
  demo,
  stages,
  meanings,
  github,
  type Evidence,
  type Verdict,
} from "./data";

function Badge({ value }: { value: Verdict }) {
  return (
    <span className={`badge ${value.toLowerCase()}`}>
      <span aria-hidden="true">
        {value === "PASS" ? "✓" : value === "FAIL" ? "×" : "—"}
      </span>{" "}
      {value}
    </span>
  );
}
function MarketingHeader() {
  return (
    <header className="header">
      <a className="wordmark" href="#" aria-label="AgentGuard home">
        <span className="brand-icon" aria-hidden="true">
          ⊢
        </span>{" "}
        AGENTGUARD
      </a>
      <nav aria-label="Main navigation">
        <a href="#product">Product</a>
        <a href="#how">How it works</a>
        <a href="#trust">Trust</a>
      </nav>
      <div className="header-actions">
        <a className="github" href={github}>
          GitHub ↗
        </a>
        <a className="button small" href="#product">
          Run the demo <span>↗</span>
        </a>
      </div>
    </header>
  );
}
function EvidenceInspector({ item }: { item: Evidence }) {
  return (
    <div className="inspector" aria-live="polite">
      <div className="panel-label">
        <span>OBSERVATION / {item.id.toUpperCase()}</span>
        <Badge value={item.verdict} />
      </div>
      <h3>{item.title}</h3>
      {item.expected && (
        <div className="diff">
          <div>
            <span>EXPECTED</span>
            <code>{item.expected}</code>
          </div>
          <div className={item.verdict === "FAIL" ? "contradiction" : ""}>
            <span>OBSERVED</span>
            <code>{item.observed}</code>
          </div>
        </div>
      )}
      <p>{item.reason}</p>
      <div className="inspector-foot">
        {item.verdict === "UNVERIFIED"
          ? "NO SUPPORTED OBSERVATION"
          : demo.endpoint + " · HTTP 200"}
      </div>
    </div>
  );
}
function EvidenceGraph() {
  const [selected, setSelected] = useState(1);
  return (
    <div className="graph-shell">
      <div className="panel-label">
        <span>FIG. 01 / THE EVIDENCE GRAPH</span>
        <span className="live-dot">CONTROLLED EXAMPLE</span>
      </div>
      <div className="graph">
        <div className="task-node">
          <span className="eyebrow">TASK / 001</span>
          <strong>{demo.task}</strong>
        </div>
        <div className="branches" aria-label="Explore acceptance evidence">
          {demo.evidence.map((item, i) => (
            <button
              key={item.id}
              aria-pressed={selected === i}
              onClick={() => setSelected(i)}
              className={`graph-node ${selected === i ? "selected" : ""}`}
            >
              <span className="node-index">0{i + 1}</span>
              <strong>{item.title}</strong>
              <span className="observation">
                {i === 2 ? "insufficient evidence" : "observation recorded"}
              </span>
              <Badge value={item.verdict} />
            </button>
          ))}
        </div>
      </div>
      <EvidenceInspector item={demo.evidence[selected]} />
      <p className="graph-caption">
        Historical full-task example: all three behaviours were explicitly
        requested. Independent of your choices in the reviewed demo below. No
        live request is made.
      </p>
    </div>
  );
}
function Hero() {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-copy">
        <div className="eyebrow">
          <span className="tiny-square" /> INDEPENDENT ACCEPTANCE VERIFICATION
        </div>
        <h1 id="hero-title">
          Your coding agent
          <br />
          says it’s done.
          <br />
          <em>
            AgentGuard checks
            <br />
            the evidence.
          </em>
        </h1>
        <p className="hero-description">
          AgentGuard proposes acceptance intent. You approve the suggestions.
          Supported checks produce PASS, FAIL, or UNVERIFIED — with evidence.
        </p>
        <div className="hero-actions">
          <a className="button" href="#product">
            Run the demo <span>↗</span>
          </a>
          <a className="text-link" href="#how">
            How it works <span>↓</span>
          </a>
        </div>
        <div className="hero-trust">
          <span className="crosshair" aria-hidden="true">
            ＋
          </span>{" "}
          AI suggests. You decide intent. Evidence decides results.
        </div>
      </div>
      <EvidenceGraph />
    </section>
  );
}
function ProblemSection() {
  return (
    <section className="problem section">
      <div className="section-number">00 / THE PROBLEM</div>
      <div>
        <h2>
          The agent that writes the code
          <br />
          shouldn’t be the only one
          <br />
          <em>grading it.</em>
        </h2>
        <div className="problem-copy">
          <p>
            AI coding agents can interpret a requirement, implement it, write
            tests around their interpretation, and report success.
          </p>
          <p>
            Passing implementation tests therefore do not necessarily establish
            that every agreed requirement was satisfied.
          </p>
        </div>
      </div>
    </section>
  );
}
function HowItWorks() {
  const [active, setActive] = useState(0);
  return (
    <section className="section how" id="how">
      <div className="section-number">06 / HOW IT WORKS</div>
      <h2>
        Plan. Review. Verify.
        <br />
        <em>Evidence decides.</em>
      </h2>
      <div className="how-grid">
        <div className="stage-list" aria-label="Verification stages">
          {stages.map((stage, i) => (
            <button
              key={stage.name}
              aria-pressed={active === i}
              aria-controls="stage-panel"
              onClick={() => setActive(i)}
            >
              <span>0{i + 1}</span>
              <div>
                <strong>{stage.name}</strong>
                <p>{stage.description}</p>
              </div>
              <span aria-hidden="true">{active === i ? "↗" : "+"}</span>
            </button>
          ))}
        </div>
        <div id="stage-panel" className="code-panel" aria-live="polite">
          <div className="panel-label">
            <span>{stages[active].label}</span>
            <span>0{active + 1} / 04</span>
          </div>
          <pre>{stages[active].code}</pre>
          <div className="code-caption">
            ILLUSTRATIVE CONTRACT · CONTROLLED DEMO
          </div>
        </div>
      </div>
    </section>
  );
}
function TrustBoundary() {
  return (
    <section className="trust section" id="trust">
      <div className="section-number">07 / THE TRUST BOUNDARY</div>
      <div className="trust-heading">
        <h2>
          AI reasons.
          <br />
          <em>Evidence decides.</em>
        </h2>
        <p>
          The model does not
          <br />
          award itself <strong>PASS.</strong>
        </p>
      </div>
      <p className="human-boundary">
        HUMAN / PRODUCT INTENT · Explicit requirements are included. Suggested
        behaviours require your acceptance; approval never grants execution or
        verdict authority.
      </p>
      <div className="boundary-grid">
        <div>
          <span className="eyebrow">LLM / REASONING SIDE</span>
          <h3>Propose the claim.</h3>
          <ul>
            <li>Extracts requirements</li>
            <li>Proposes acceptance scenarios for human review</li>
            <li>Grounds supported checks</li>
          </ul>
        </div>
        <div
          className="boundary"
          aria-label="Deterministic validation boundary"
        >
          <span>
            VALIDATION
            <br />
            BOUNDARY
          </span>
          <b aria-hidden="true">→</b>
        </div>
        <div>
          <span className="eyebrow">DETERMINISTIC / EVIDENCE SIDE</span>
          <h3>Observe the behavior.</h3>
          <ul>
            <li>Executes bounded observations</li>
            <li>Evaluates assertions</li>
            <li>Produces evidence-backed verdicts</li>
          </ul>
        </div>
      </div>
    </section>
  );
}
function VerdictExplanation() {
  return (
    <section className="verdict-section section">
      <div className="verdict-heading">
        <div className="eyebrow">THREE OUTCOMES. NO FALSE CERTAINTY.</div>
        <h2>
          No evidence.
          <br />
          <em>No green check.</em>
        </h2>
      </div>
      <div className="verdict-list">
        {(Object.keys(meanings) as Verdict[]).map((v) => (
          <div key={v}>
            <Badge value={v} />
            <p>{meanings[v]}</p>
          </div>
        ))}
        <small>
          UNVERIFIED is an honest limit, not a failure. No verdict guarantees
          complete correctness.
        </small>
      </div>
    </section>
  );
}
function FinalCTA() {
  return (
    <section className="final section">
      <div className="eyebrow">FROM “DONE” TO DEMONSTRATED.</div>
      <h2>
        Your agent made the change.
        <br />
        <em>Verify the claim.</em>
      </h2>
      <div className="hero-actions">
        <a className="button" href="#product">
          Run the demo <span>↗</span>
        </a>
        <a className="text-link" href={github}>
          View on GitHub ↗
        </a>
      </div>
    </section>
  );
}
export default function App() {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <MarketingHeader />
      <main id="main">
        <Hero />
        <div className="principle-strip">
          <span>REQUIREMENTS → OBSERVATIONS → EVIDENCE</span>
          <span>Independent by design. Bounded by evidence.</span>
        </div>
        <Reveal variant="stagger-children">
          <ProblemSection />
        </Reveal>
        <CinematicStory
          verification={(onComplete) => <ReviewDemo onComplete={onComplete} />}
        />
        <Reveal variant="stagger-children">
          <HowItWorks />
        </Reveal>
        <Reveal variant="stagger-children">
          <TrustBoundary />
        </Reveal>
        <Reveal variant="stagger-children">
          <VerdictExplanation />
        </Reveal>
        <FinalCTA />
      </main>
      <footer className="footer">
        <a className="wordmark" href="#">
          AGENTGUARD
        </a>
        <span>Independent acceptance verification.</span>
        <a href={github}>Source & documentation ↗</a>
      </footer>
    </>
  );
}
