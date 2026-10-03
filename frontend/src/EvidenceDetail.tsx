import { implementationExcerpt, type AccountEvidence } from "./accountDemoData";

/** Presentation of fixed external evidence, never a verdict calculator. */
export function EvidenceDetail({ result }: { result: AccountEvidence }) {
  return (
    <section
      className={`evidence-detail verdict-${result.verdict.toLowerCase()}`}
      aria-label={`${result.title} evidence explanation`}
    >
      <div className="detail-heading">
        <span className="eyebrow">
          {result.codeNote
            ? "WHY THIS FAILED"
            : result.verdict === "UNVERIFIED"
              ? "WHAT COULD NOT BE ESTABLISHED"
              : "WHAT THE EVIDENCE ESTABLISHES"}
        </span>
        <h4>{result.behavior}</h4>
        <small>
          Accepted behavior ·{" "}
          {result.source === "inferred"
            ? "inferred, added by you"
            : "explicit request"}
        </small>
      </div>
      <div className={result.codeNote ? "code-evidence-grid" : "evidence-only"}>
        {result.codeNote && (
          <figure className="implementation-view">
            <figcaption>CONTROLLED IMPLEMENTATION EXCERPT</figcaption>
            <pre>
              <code>
                {implementationExcerpt.map((line, i) => (
                  <span
                    className={`code-line ${i === 1 ? "code-focus" : ""}`}
                    key={i}
                  >
                    <span className="line-number" aria-hidden="true">
                      {i + 1}
                    </span>
                    {line.tokens.map((token, j) => (
                      <span className={`syntax-${token.kind}`} key={j}>
                        {token.text}
                      </span>
                    ))}
                    {"\n"}
                  </span>
                ))}
              </code>
            </pre>
            <p>{result.codeNote}</p>
            <small>
              Illustrative demo code · not extracted or executed during
              playback.
            </small>
          </figure>
        )}
        <ol className="evidence-chain" aria-label="Controlled evidence chain">
          {result.chain.map((step) => (
            <li key={step.label}>
              <span>{step.label}</span>
              <p>{step.value}</p>
            </li>
          ))}
        </ol>
      </div>
      <div className="evidence-reason">
        <span className="eyebrow">WHY · {result.verdict}</span>
        <p>{result.reason}</p>
      </div>
      {result.verdict === "UNVERIFIED" && (
        <p className="evidence-boundary">
          AgentGuard would rather say UNVERIFIED than guess PASS.
          <small>No evidence is not evidence of success—or failure.</small>
        </p>
      )}
    </section>
  );
}
