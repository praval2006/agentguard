import type { ReactNode } from "react";
import { Reveal } from "./Reveal";
import { PageLink } from "./navigation";
import { github } from "./data";

function Scene({
  id,
  number,
  label,
  children,
}: {
  id: string;
  number: string;
  label: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="presentation-scene" aria-label={label}>
      <Reveal>
        <div className="section-kicker">
          <span>{number}</span> / {label}
        </div>
        {children}
      </Reveal>
    </section>
  );
}
function Flow({ items }: { items: readonly (readonly [string, string])[] }) {
  return (
    <ol className="flow">
      {items.map(([title, text], index) => (
        <li key={title} style={{ "--i": index } as React.CSSProperties}>
          <span className="flow-index">0{index + 1}</span>
          <div>
            <strong>{title}</strong>
            <p>{text}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
export function PresentationPage() {
  return (
    <>
      <header className="site-header">
        <a className="wordmark" href="#main">
          <span className="brand-mark" aria-hidden="true">
            A
          </span>{" "}
          AGENTGUARD
        </a>
        <nav aria-label="Presentation navigation">
          <a href="#problem">The gap</a>
          <a href="#trust">The trust</a>
          <PageLink to="/demo" className="nav-demo">
            Open demo <span aria-hidden="true">↗</span>
          </PageLink>
        </nav>
      </header>
      <main id="main">
        <section className="hero-stage" aria-labelledby="hero-title">
          <div className="hero-grid" aria-hidden="true" />
          <div className="hero-content">
            <p className="eyebrow">INDEPENDENT ACCEPTANCE VERIFICATION</p>
            <h1 id="hero-title">
              AGENT<span>GUARD</span>
            </h1>
            <h2 className="hero-thesis">
              Build with AI.
              <br />
              <em>Verify with evidence.</em>
            </h2>
            <p className="hero-definition">
              An independent acceptance layer for AI-generated code.
            </p>
            <p className="hero-explanation">
              Uncover acceptance requirements you may have missed.
              <br className="desktop-break" /> Decide what matters. Verify the
              finished software against that contract.
            </p>
            <div className="hero-actions">
              <a className="button" href="#problem">
                See how it works <span>↓</span>
              </a>
              <PageLink to="/demo" className="text-link">
                Launch interactive demo →
              </PageLink>
            </div>
            <div className="hero-baseline">
              <span>AI PROPOSES</span>
              <b>→</b>
              <span>YOU DECIDE</span>
              <b>→</b>
              <span>EVIDENCE TELLS</span>
            </div>
          </div>
          <div className="page-cue">
            01 — 12 <span>SCROLL TO EXPLORE ↓</span>
          </div>
        </section>
        <Scene id="problem" number="02" label="THE PROBLEM">
          <h2 className="statement">
            Your coding agent can perfectly implement
            <br />
            <em>an incomplete prompt.</em>
          </h2>
          <div className="problem-object product-surface">
            <div className="surface-bar">
              <span className="window-dots" aria-hidden="true">
                ● ● ●
              </span>
              <span>A COMPLETION CLAIM IS NOT A COMPLETE CONTRACT</span>
            </div>
            <div className="problem-request">
              <span className="eyebrow">YOU ASK</span>
              <h3>
                “Add a feature that lets users permanently delete their
                account.”
              </h3>
            </div>
            <div className="agent-completion">
              <span>CODING AGENT</span>
              <strong>✓ Implementation complete</strong>
              <strong>✓ Tests passing</strong>
              <strong>✓ Task complete</strong>
            </div>
            <div className="open-questions">
              <b>BUT…</b>
              <p>Existing sessions?</p>
              <p>The profile?</p>
              <p>User-created content?</p>
            </div>
          </div>
          <p className="section-payoff">
            The coding agent didn’t necessarily fail.
            <br />
            <em>The acceptance criteria were incomplete.</em>
          </p>
        </Scene>
        <Scene id="gap" number="03" label="THE ACCEPTANCE GAP">
          <h2 className="statement">
            Requested. Expected.
            <br />
            <em>Actually observed.</em>
          </h2>
          <div className="gap-composition">
            <Flow
              items={[
                ["REQUESTED", "What you explicitly asked for."],
                [
                  "EXPECTED",
                  "Additional behavior suggested by context. Reviewed by you.",
                ],
                ["OBSERVED", "What the finished software actually does."],
              ]}
            />
            <div className="gap-notes">
              <article>
                <span className="eyebrow">01 / REQUIREMENT GAP</span>
                <p>Something important never made it into the prompt.</p>
              </article>
              <article>
                <span className="eyebrow">02 / IMPLEMENTATION GAP</span>
                <p>An accepted behavior exists. The software contradicts it.</p>
              </article>
            </div>
          </div>
        </Scene>
        <Scene id="agentguard" number="04" label="THE INDEPENDENT LAYER">
          <h2 className="statement">
            A second boundary.
            <br />
            <em>A better question.</em>
          </h2>
          <div className="guard-diagram">
            <div>
              AI CODING AGENT<small>“The implementation is complete.”</small>
            </div>
            <span className="connector" aria-hidden="true" />
            <div className="guard-core">
              <span className="brand-mark" aria-hidden="true">
                A
              </span>
              <strong>AGENTGUARD</strong>
              <p>“What did we agree to accept?”</p>
            </div>
            <span className="connector" aria-hidden="true" />
            <div>
              EVIDENCE FOR YOUR SHIP DECISION
              <small>
                Explicit intent · reviewed suggestions · open questions
              </small>
            </div>
          </div>
          <p className="section-note">
            AgentGuard separates what you requested, what may be missing,
            <br className="desktop-break" /> and what needs clarification. It
            never silently turns a suggestion into a requirement.
          </p>
        </Scene>
        <Scene id="authority" number="05" label="HUMAN AUTHORITY">
          <h2 className="statement">
            The model can suggest.
            <br />
            <em>You decide what matters.</em>
          </h2>
          <div className="authority-grid">
            <article>
              <span className="authority-symbol">01</span>
              <h3>Your requirement</h3>
              <span className="eyebrow">EXPLICIT / INCLUDED</span>
              <p>Automatically included in the acceptance contract.</p>
            </article>
            <article className="suggestion-object">
              <span className="authority-symbol">02</span>
              <h3>AgentGuard suggestion</h3>
              <span className="eyebrow">INFERRED / YOUR DECISION</span>
              <p>Pending until you accept or dismiss it.</p>
              <span className="contract-arrow">Your approval → contract</span>
            </article>
            <article>
              <span className="authority-symbol">?</span>
              <h3>Ambiguity</h3>
              <span className="eyebrow">REQUIRES CLARIFICATION</span>
              <p>An open product question. No automatic verdict.</p>
            </article>
          </div>
          <p className="section-note">
            Approval changes authority, not history. Accepted suggestions stay
            inferred.
            <br />
            Pending and dismissed suggestions are <strong>not verified</strong>
            —not UNVERIFIED.
          </p>
        </Scene>
        <Scene id="launch" number="06" label="FROM EXPLANATION TO EXPERIENCE">
          <div className="launch-stage">
            <span className="eyebrow">
              A SIMPLE REQUEST. A BIGGER ACCEPTANCE QUESTION.
            </span>
            <h2 className="statement">
              See the acceptance
              <br />
              <em>boundary in action.</em>
            </h2>
            <p>
              Give a coding agent an account-deletion task.
              <br />
              Then decide what “done” should mean.
            </p>
            <PageLink to="/demo" className="button large">
              Launch interactive demo <span>→</span>
            </PageLink>
            <small>
              Controlled demonstration · no live repository execution
            </small>
          </div>
        </Scene>
        <Scene id="trust" number="07" label="THE TRUST ARCHITECTURE">
          <h2 className="statement">
            The model doesn’t grade
            <br />
            <em>its own homework.</em>
          </h2>
          <div className="trust-surface product-surface">
            <Flow
              items={[
                ["LLM → PROPOSES", "Suggests potential acceptance gaps."],
                [
                  "HUMAN → AUTHORIZES INTENT",
                  "Decides what matters. Execution policy stays separate.",
                ],
                [
                  "EXECUTION → OBSERVES",
                  "Performs supported, bounded observations.",
                ],
                [
                  "DETERMINISTIC VERIFIER",
                  "Determines what the evidence establishes.",
                ],
              ]}
            />
            <div className="trust-outcomes">
              <span className="badge pass">✓ PASS</span>
              <span className="badge fail">× FAIL</span>
              <span className="badge unverified">— UNVERIFIED</span>
            </div>
          </div>
          <p className="section-payoff">
            The LLM never awards itself <em>PASS or FAIL.</em>
          </p>
        </Scene>
        <Scene id="generalization" number="08" label="GENERALIZATION">
          <h2 className="statement">
            One verification architecture.
            <br />
            <em>Many behaviors.</em>
          </h2>
          <div className="behavior-list">
            {[
              ["STATE TRANSITION", "active", "→", "cancelled"],
              ["PRESERVATION", "before.username", "=", "after.username"],
              ["DELETION", "DELETE → GET", "→", "404"],
              ["REPEATED OPERATION", "action → action", "→", "observe state"],
            ].map(([label, a, symbol, b]) => (
              <article key={label}>
                <span className="eyebrow">{label}</span>
                <div>
                  <code>{a}</code>
                  <span className="operator">{symbol}</span>
                  <code>{b}</code>
                </div>
              </article>
            ))}
          </div>
          <p className="capability-line">
            HTTP observations · JSON assertions · Registered checks
            <br />
            Composite checks · Stateful observation sequences
          </p>
          <p className="section-note">
            Supported observations need grounded interfaces and evidence.
            <br />
            This is not an account-deletion checker.
          </p>
        </Scene>
        <Scene id="boundary" number="09" label="NO FALSE CERTAINTY">
          <div className="outcome-list">
            <article>
              <span className="badge pass">✓ PASS</span>
              <p>Observed evidence supports the accepted behavior.</p>
            </article>
            <article>
              <span className="badge fail">× FAIL</span>
              <p>Observed evidence contradicts the accepted behavior.</p>
            </article>
            <article>
              <span className="badge unverified">— UNVERIFIED</span>
              <p>
                The behavior could not be established with supported
                observations.
              </p>
            </article>
          </div>
          <h2 className="statement boundary-punch">
            AgentGuard would rather say
            <br />
            <em>UNVERIFIED</em>
            <br />
            than guess PASS.
          </h2>
          <p className="section-note">
            Not a claim of complete software correctness.
            <br />A clear account of what was accepted, observed, contradicted,
            or not established.
          </p>
        </Scene>
        <Scene id="report" number="10" label="THE FINAL ARTIFACT">
          <h2 className="statement">
            Not just a verdict.
            <br />
            <em>A record of acceptance.</em>
          </h2>
          <div className="report-object product-surface">
            <div className="surface-bar">
              <span>AGENTGUARD / ACCEPTANCE VERIFICATION REPORT</span>
              <span>JSON</span>
            </div>
            <div className="report-chain">
              <span>Original request</span>
              <b>↓</b>
              <span>Explicit requirements + suggestions</span>
              <b>↓</b>
              <span>Human decisions → acceptance contract</span>
              <b>↓</b>
              <span>Observed evidence</span>
              <b>↓</b>
              <strong>PASS / FAIL / UNVERIFIED</strong>
            </div>
            <div className="report-footnote">
              A deterministic reporting layer. Existing verdicts, preserved.
            </div>
          </div>
          <p className="section-note">
            Machine-readable JSON reporting exists in the backend.
            <br />
            This presentation is illustrative; it does not dynamically consume
            that report.
          </p>
        </Scene>
        <Scene id="vision" number="11" label="THE PRODUCT VISION">
          <h2 className="statement">
            Automate the mechanics.
            <br />
            <em>Not acceptance authority.</em>
          </h2>
          <Flow
            items={[
              ["DESCRIBE FEATURE", "Start with your intent."],
              [
                "ESTABLISH ACCEPTANCE",
                "Discover requirements. Human approves.",
              ],
              ["AI BUILDS", "Work against the accepted contract."],
              [
                "AGENTGUARD VERIFIES",
                "Automatic supported observations → evidence-backed report.",
              ],
            ]}
          />
          <p className="section-note">
            The eventual connected workflow. Today’s demonstration is controlled
            playback.
          </p>
        </Scene>
        <Scene id="closing" number="12" label="THE QUESTION THAT MATTERS">
          <h2 className="closing-title">
            AI can build the code.
            <br />
            <em>
              Who checks
              <br />
              the acceptance?
            </em>
          </h2>
          <div className="closing-brand">AGENTGUARD</div>
          <p className="closing-tagline">
            Build with AI. Verify with evidence.
          </p>
          <p className="section-note">
            Independent acceptance verification for AI-generated software.
          </p>
          <div className="hero-actions">
            <PageLink to="/demo" className="button">
              Launch demo →
            </PageLink>
            <a href="#main" className="text-link">
              Back to top ↑
            </a>
          </div>
        </Scene>
      </main>
      <footer className="site-footer">
        <span>AGENTGUARD / BUILT FOR EVIDENCE</span>
        <a href={github}>Source & documentation ↗</a>
      </footer>
    </>
  );
}
