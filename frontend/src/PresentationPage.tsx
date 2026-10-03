import { BrandMark } from "./BrandMark";
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
          <BrandMark entrance /> AGENTGUARD
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
              An acceptance layer between human intent and AI coding agents.
            </p>
            <p className="hero-explanation">
              Uncover acceptance requirements you may have missed.
              <br className="desktop-break" /> Decide what matters. Verify the
              finished software against that contract. Turn established failures into corrective context.
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
            01 — 15 <span>SCROLL TO EXPLORE ↓</span>
          </div>
        </section>
        <Scene id="research" number="02" label="WHY THIS MATTERS">
          <h2 className="statement">Building faster.<br /><em>Verifying deliberately.</em></h2>
          <div className="research-signals">
            <article><span className="eyebrow">SONAR · 2026 STATE OF CODE DEVELOPER SURVEY</span><strong className="research-number">96%</strong><p>of surveyed professional developers did not fully trust AI-generated code to be functionally correct.</p><p>Survey of 1,149 professional developers. Sonar describes verification as a bottleneck.</p><a href="https://www.sonarsource.com/blog/state-of-code-developer-survey-report-the-current-reality-of-ai-coding/" target="_blank" rel="noopener noreferrer" aria-label="View Sonar survey source in a new tab">View source ↗</a></article>
            <article><span className="eyebrow">SWE-RPG · UNIFIED ISSUE RESOLUTION BENCHMARK</span><h3>Requirement recovery</h3><p>Repository-level coding-agent work involves recovering explicit and implicit requirements, planning and implementation. Final patch pass/fail alone does not explain where a trajectory diverged.</p><a href="https://www.alphaxiv.org/abs/2608.09072" target="_blank" rel="noopener noreferrer" aria-label="View SWE-RPG research source in a new tab">View source ↗</a></article>
          </div><p className="section-note">Research context, not an evaluation of AgentGuard.</p>
        </Scene>
        <Scene id="problem" number="03" label="THE PROBLEM">
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
              <p>External personal data?</p>
              <p>User-created content?</p>
            </div>
          </div>
          <p className="section-payoff">
            The coding agent didn’t necessarily fail.
            <br />
            <em>The acceptance boundary was incomplete.</em>
          </p>
        </Scene>
        <Scene id="gap" number="04" label="THE ACCEPTANCE GAP">
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
        <Scene id="agentguard" number="05" label="THE INDEPENDENT LAYER">
          <h2 className="statement">
            A second boundary.
            <br />
            <em>A better question.</em>
          </h2>
          <div className="guard-diagram">
            <div>
              HUMAN INTENT<small>“Add permanent account deletion.”</small>
            </div>
            <span className="connector" aria-hidden="true" />
            <div className="guard-core">
              <BrandMark />
              <strong>AGENTGUARD</strong>
              <p>“What did we agree to accept?”</p>
            </div>
            <span className="connector" aria-hidden="true" />
            <div>
              REVIEWED ACCEPTANCE CONTRACT
              <small>
                Explicit: account deleted · Suggestions: sessions, profile, external data · Ambiguity: user-created content
              </small>
            </div>
          </div>
          <p className="section-note">
            AgentGuard separates what you requested, what may be missing,
            <br className="desktop-break" /> and what needs clarification. It
            never silently turns a suggestion into a requirement.
          </p>
        </Scene>
        <Scene id="authority" number="06" label="HUMAN AUTHORITY">
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
        <Scene id="implementation" number="07" label="CODING AGAINST THE CONTRACT">
          <h2 className="statement">The coding agent implements.<br /><em>AgentGuard independently verifies.</em></h2>
          <Flow items={[["REVIEWED ACCEPTANCE CONTRACT", "Human intent and accepted suggestions define the target."], ["CODING AGENT", "Implements against that contract. Agent-agnostic; no vendor integration is invoked here."], ["AGENTGUARD", "Bounded observations, deterministic verification and evidence."]]} />
          <p className="section-note">The before-coding flow is product direction. The demo reviews an already-authored implementation and plays controlled evidence.</p>
        </Scene>
        <Scene id="launch" number="08" label="FROM EXPLANATION TO EXPERIENCE">
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
        <Scene id="trust" number="09" label="THE TRUST ARCHITECTURE">
          <h2 className="statement">
            The coding agent can act on the evidence.<br /><em>It still doesn’t grade itself.</em>
          </h2>
          <div className="trust-surface product-surface">
            <Flow
              items={[
                ["LLM → PROPOSES", "Suggests potential acceptance gaps."],
                [
                  "HUMAN → AUTHORIZES INTENT",
                  "Decides what matters. Execution policy stays separate.",
                ],
                ["CODING AGENT → IMPLEMENTS", "Works against the reviewed contract; does not assign verdicts."],
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
            <p className="section-note">Correction brief → coding-agent handoff → independent re-verification. Automatic handoff remains product direction.</p>
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
        <Scene id="generalization" number="10" label="GENERALIZATION">
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
        <Scene id="boundary" number="11" label="NO FALSE CERTAINTY">
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
        <Scene id="report" number="12" label="THE FINAL ARTIFACT">
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
        <Scene id="correction" number="13" label="EVIDENCE INTO CORRECTIVE CONTEXT">
          <h2 className="statement">Two contradictions.<br /><em>A precise next action.</em></h2>
          <div className="report-object product-surface"><p className="eyebrow">CONTROLLED ACCOUNT-DELETION EXAMPLE · ALL SUGGESTIONS ACCEPTED</p><h3>2 evidence-backed corrections</h3><p>Existing session still authorizes GET /me → HTTP 200.</p><p>Deleted profile remains retrievable → HTTP 200 with profile data.</p><p className="section-note">External personal data: UNVERIFIED. Not sent for correction.</p></div>
          <Flow items={[["CORRECTION BRIEF", "Accepted behaviour + expected + observed + evidence. No invented repair."], ["CODING AGENT", "May make a targeted change while preserving passing behaviours and the accepted contract."], ["AGENTGUARD", "Re-verify the same acceptance contract independently."]]} />
          <p className="section-note">Handoff is demonstrated. No agent is invoked and no successful second run is claimed.</p>
          <PageLink to="/demo" className="text-link">Prepare the controlled handoff →</PageLink>
        </Scene>
        <Scene id="vision" number="14" label="THE PRODUCT VISION">
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
        <Scene id="closing" number="15" label="THE QUESTION THAT MATTERS">
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
