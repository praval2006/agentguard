import { codingStory, demo } from "./data";
import { Reveal } from "./Reveal";

export function CodingStory() {
  return (
    <div className="coding-story" aria-label="Controlled coding-agent story">
      <div className="story-disclosure">
        CONTROLLED EXAMPLE / REPLAYED NARRATIVE · NO LIVE CODING AGENT
      </div>
      <section className="story-chapter section">
        <Reveal>
          <div className="section-number">01 / THE TASK</div>
          <h2>
            Give the agent
            <br />
            <em>the job.</em>
          </h2>
        </Reveal>
        <Reveal variant="slide-right">
          <article className="story-panel task-panel">
            <div className="panel-label">
              CODING AGENT <span>TASK INPUT</span>
            </div>
            <div className="story-panel-body">
              <span className="eyebrow">TASK</span>
              <h3>{codingStory.task}</h3>
              <p>{codingStory.introduction}</p>
              <ul className="task-requirements">
                {codingStory.requirements.map((text) => (
                  <li key={text}>
                    <span aria-hidden="true">○</span>
                    {text}
                  </li>
                ))}
              </ul>
              <small>Requirements to satisfy. Not verified outcomes.</small>
            </div>
          </article>
        </Reveal>
      </section>
      <section className="story-chapter section implementation-chapter">
        <Reveal>
          <div className="section-number">02 / THE IMPLEMENTATION</div>
          <h2>
            The agent
            <br />
            <em>gets to work.</em>
          </h2>
          <p className="story-aside">
            A small change.
            <br />A familiar development loop.
          </p>
        </Reveal>
        <Reveal variant="slide-left">
          <article className="story-panel">
            <div className="panel-label">
              CODING AGENT <span>CONTROLLED PLAYBACK</span>
            </div>
            <Reveal variant="stagger-children" className="activity-list">
              {codingStory.activity.map((text, i) => (
                <div key={text}>
                  <span>0{i + 1}</span>
                  {text}
                </div>
              ))}
            </Reveal>
            <Reveal>
              <pre className="implementation-code">{codingStory.code}</pre>
            </Reveal>
          </article>
        </Reveal>
      </section>
      <section className="story-chapter section result-chapter">
        <Reveal>
          <div className="section-number">03 / AGENT RESULT</div>
          <h2>
            All its tests.
            <br />
            <em>All green.</em>
          </h2>
          <p className="story-aside">
            The coding agent reports completion.
            <br />
            Its implementation tests agree.
          </p>
        </Reveal>
        <article className="story-panel agent-success">
          <div className="panel-label">
            CODING AGENT <span>IMPLEMENTATION TESTS</span>
          </div>
          <Reveal variant="stagger-children" className="story-panel-body">
            <div className="story-tests">
              {codingStory.tests.map((test) => (
                <div key={test}>
                  <span aria-hidden="true">✓ </span>
                  <code>{test}</code>
                </div>
              ))}
            </div>
            <div className="test-total">
              {demo.implementationTests} <span>PASSING</span>
            </div>
            <div className="story-complete">TASK COMPLETE.</div>
            <small>Subscription-specific implementation tests only.</small>
          </Reveal>
        </article>
      </section>
      <section className="handoff section">
        <Reveal>
          <div className="section-number">04 / AN INDEPENDENT QUESTION</div>
          <h2>
            But did it actually
            <br />
            <em>satisfy the task?</em>
          </h2>
        </Reveal>
        <Reveal>
          <p>
            Passing implementation tests show that the tested behavior works.
            <br />
            They do not necessarily establish that every agreed requirement was
            tested.
          </p>
        </Reveal>
        <Reveal variant="stagger-children" className="handoff-track">
          <div>
            <span>CODING AGENT</span>
            <strong>{demo.implementationTests} tests passing</strong>
          </div>
          <div className="handoff-arrow" aria-hidden="true">
            ⟶
          </div>
          <div>
            <span>AGENTGUARD</span>
            <strong>Check the claim.</strong>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
