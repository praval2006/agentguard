import { useState } from "react";
import type { AccountReport } from "./accountDemoData";

export const correctionInstruction = "Correct this accepted behaviour while preserving already-passing accepted behaviours. Do not modify the acceptance contract. Return the implementation for independent re-verification.";
export function correctionText(report: AccountReport) {
  const items = report.results.filter(r => r.verdict === "FAIL");
  return ["AGENTGUARD CORRECTION BRIEF", "Controlled fixture handoff — no agent invoked.",
    ...items.map((r, i) => [`CORRECTION ${i + 1}`, `Accepted behaviour: ${r.behavior}`, `Source: ${r.source} · accepted by you`, `Expected: ${r.expected}`, `Observed: ${r.response} · ${r.observed}`, "Evidence:", ...r.chain.map(e => `${e.label}: ${e.value}`), correctionInstruction].join("\n")),
    "NOT SENT FOR CORRECTION", ...report.results.filter(r => r.verdict !== "FAIL").map(r => `${r.title}: ${r.verdict}. ${r.verdict === "UNVERIFIED" ? r.reason : "Already-passing accepted behaviour; preserve it."}`),
    "Pending, dismissed and clarification items, and ambiguities, are not correction instructions.",
    "NEXT ACTION ONLY: coding agent → targeted change → AgentGuard → re-verify the same acceptance contract. No second result is claimed."
  ].join("\n\n");
}
export function CorrectionBrief({ report }: { report: AccountReport }) {
  const [message, setMessage] = useState("");
  const text = correctionText(report);
  async function copy() {
    try { await navigator.clipboard.writeText(text); setMessage("Correction brief copied. No agent was invoked."); }
    catch { setMessage("Clipboard unavailable. Select and copy the handoff text below."); }
  }
  return <section className="correction-brief" aria-label="Correction brief">
    <p className="eyebrow">AGENTGUARD CORRECTION BRIEF · CONTROLLED HANDOFF</p>
    <h2>{report.fail} evidence-backed corrections</h2>
    <p>Ready for coding-agent handoff. Evidence is context, not a diagnosis or authority to change the contract.</p>
    {report.results.filter(r => r.verdict === "FAIL").map((r, i) => <article className="correction-item product-surface" key={r.id}>
      <span className="eyebrow">CORRECTION 0{i + 1} · {r.source.toUpperCase()} · ACCEPTED BY YOU</span>
      <h3>{r.behavior}</h3>
      <dl><dt>Expected</dt><dd>{r.expected}</dd><dt>Observed</dt><dd>{r.response} · {r.observed}</dd><dt>Evidence</dt><dd>{r.chain.map(e => <p key={e.label}><strong>{e.label}</strong> · {e.value}</p>)}</dd></dl>
      <p>{correctionInstruction}</p>
    </article>)}
    <aside className="ambiguity-note" aria-label="Not sent for correction"><h3>Not sent for correction</h3>
      {report.results.filter(r => r.verdict !== "FAIL").map(r => <p key={r.id}>{r.title} · <strong>{r.verdict}</strong><br />{r.verdict === "UNVERIFIED" ? r.reason : "Preserve this already-passing accepted behaviour."}</p>)}
      <p>Pending, dismissed, needs-clarification suggestions and ambiguities receive no correction instruction.</p>
    </aside>
    <button className="button" onClick={copy}>Copy for coding agent</button>
    <p role="status">{message}</p>
    <details><summary>Inspect handoff text</summary><pre className="handoff-text">{text}</pre></details>
    <div className="loop-next"><p className="eyebrow">NEXT ACTION · NOT EXECUTED</p><h3>Re-verify the same acceptance contract.</h3>
      <p>Correction brief → coding agent → targeted change → AgentGuard → independent re-verification.</p>
      <p>The coding agent can act on the evidence. It still doesn’t grade itself.</p>
      <small>No agent integration, code change or second verification run occurs in this demo.</small>
    </div>
  </section>;
}
