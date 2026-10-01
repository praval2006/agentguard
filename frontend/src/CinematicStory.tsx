import { useEffect, useRef, useState, type ReactNode } from "react";
import { codingStory } from "./data";
import { reviewExample } from "./reviewData";
import { clamp, range, pose, type Scene } from "./scrollTimeline";

/** Native scroll sampled once per frame; only this stage's DOM styles update. */
function useScrollStage(ref: React.RefObject<HTMLElement | null>) {
  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    const media = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    let frame = 0;
    const nodes = Array.from(
      root.querySelectorAll<HTMLElement>("[data-scene]"),
    );
    const reset = () => {
      root.classList.remove("scrubbing");
      nodes.forEach((n) => {
        n.removeAttribute("style");
        n.removeAttribute("aria-hidden");
        n.inert = false;
      });
      const entry = root.querySelector<HTMLElement>(".cinema-entry");
      const target = root.querySelector<HTMLElement>(".scene-verification");
      if (entry && target) entry.style.top = `${target.offsetTop}px`;
    };
    const update = () => {
      frame = 0;
      if (
        media?.matches ||
        window.innerHeight <= 740 ||
        (window.innerWidth <= 800 && window.innerHeight <= 820)
      ) {
        reset();
        return;
      }
      root.classList.add("scrubbing");
      root
        .querySelector<HTMLElement>(".cinema-entry")
        ?.style.removeProperty("top");
      const rect = root.getBoundingClientRect();
      const height = window.innerHeight;
      if (rect.height <= height) {
        reset();
        return;
      }
      const p = clamp(-rect.top / Math.max(1, rect.height - height));
      root.classList.add("scrubbing");
      root.style.setProperty("--progress", String(p));
      nodes.forEach((node) => {
        const name = node.dataset.scene as Scene;
        const state = pose(name, p);
        node.style.opacity = String(state.opacity);
        node.style.transform = `translateY(${state.y}px) scale(${state.scale})`;
        node.style.visibility = state.opacity === 0 ? "hidden" : "visible";
        const inactive = state.opacity < 0.5;
        node.inert = inactive;
        node.setAttribute("aria-hidden", String(inactive));
      });
      root.style.setProperty("--handoff", String(range(p, 0.6, 0.74)));
      root.style.setProperty("--payoff", String(range(p, 0.9, 1)));
      root.style.setProperty("--task-settle", String(range(p, 0, 0.16)));
    };
    const schedule = () => {
      if (!frame) frame = requestAnimationFrame(update);
    };
    try {
      update();
      window.addEventListener("scroll", schedule, { passive: true });
      window.addEventListener("resize", schedule);
      media?.addEventListener("change", schedule);
    } catch {
      reset();
    }
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", schedule);
      media?.removeEventListener("change", schedule);
      reset();
    };
  }, [ref]);
}
export function CinematicStory({
  verification,
}: {
  verification: (complete: (value: boolean) => void) => ReactNode;
}) {
  const ref = useRef<HTMLElement>(null);
  const [complete, setComplete] = useState(false);
  useScrollStage(ref);
  return (
    <section
      ref={ref}
      className="cinema"
      aria-label="Controlled coding-agent story"
    >
      <p className="sr-only">
        Story overview: a coding agent receives a subscription cancellation
        task, implements it and reports two passing implementation tests.
        AgentGuard independently checks the acceptance claim. Use Run the demo
        to review the suggestion before the explicit verification control.
        Results appear only after local playback.
      </p>
      <div className="cinema-entry" id="product" />
      <a className="cinema-skip" href="#product">
        Skip story to verification ↓
      </a>
      <div className="cinema-stage">
        <div className="cinema-label">
          CONTROLLED / REPLAYED DEMONSTRATION · NO LIVE AGENT OR BACKEND
        </div>
        <div className="cinema-scene scene-task" data-scene="task">
          <div className="eyebrow">01 / THE TASK · CODING AGENT</div>
          <h2>{reviewExample.task}</h2>
          <div className="cinema-task-requirements">
            <p>{codingStory.introduction}</p>
            <ul>
              <li>○ {reviewExample.explicit.behavior}</li>
            </ul>
            <small>
              Illustrative shorter task. Additional behaviours need your review.
            </small>
          </div>
        </div>
        <div className="cinema-scene scene-work" data-scene="work">
          <div className="eyebrow">02 / CONTROLLED IMPLEMENTATION</div>
          <h2>
            The agent
            <br />
            <em>gets to work.</em>
          </h2>
          <div className="cinema-code">
            <div className="activity-list">
              {codingStory.activity.map((a) => (
                <div key={a}>{a}</div>
              ))}
            </div>
            <pre>{codingStory.code}</pre>
          </div>
        </div>
        <div className="cinema-scene scene-tests" data-scene="tests">
          <div className="eyebrow">03 / IMPLEMENTATION TESTS</div>
          <h2>
            2 / 2<br />
            <em>PASSING.</em>
          </h2>
          <div className="cinema-test-names">
            {codingStory.tests.map((t) => (
              <p key={t}>✓ {t}</p>
            ))}
          </div>
          <small>
            Subscription-specific tests. Not independent acceptance evidence.
          </small>
        </div>
        <div className="cinema-scene scene-complete" data-scene="complete">
          <div className="eyebrow">CODING AGENT / COMPLETION CLAIM</div>
          <h2>
            TASK
            <br />
            COMPLETE.
          </h2>
        </div>
        <div className="cinema-scene scene-question" data-scene="question">
          <div className="eyebrow">04 / THE INDEPENDENT QUESTION</div>
          <h2>
            But did it actually
            <br />
            <em>satisfy the task?</em>
          </h2>
          <p>
            Passing tests establish tested behavior.
            <br />
            They do not establish that every requirement was tested.
          </p>
        </div>
        <div className="cinema-scene scene-handoff" data-scene="handoff">
          <div className="handoff-agent">
            <span className="eyebrow">CODING AGENT</span>
            <strong>2 / 2</strong>
            <p>
              Tests passing.
              <br />
              Task complete.
            </p>
          </div>
          <div className="handoff-guard">
            <span className="eyebrow">CHECK THE CLAIM</span>
            <h2>AGENTGUARD</h2>
            <p>
              INDEPENDENT
              <br />
              ACCEPTANCE
              <br />
              VERIFICATION
            </p>
            <div className="handoff-claims">
              <div>○ Your request → included</div>
              <div>○ AgentGuard suggestion → your decision</div>
            </div>
          </div>
        </div>
        <div
          className="cinema-scene scene-verification"
          data-scene="verification"
        >
          {verification(setComplete)}
        </div>
        <div
          data-testid={complete ? "story-payoff" : undefined}
          className="cinema-scene scene-payoff"
          data-scene="payoff"
        >
          {complete ? (
            <>
              <div className="eyebrow">
                HUMAN INTENT · CONTROLLED EVIDENCE · SELECTED BEHAVIOURS ONLY
              </div>
              <h2 className="payoff-tests">
                PROMPT
                <br />
                DONE.
              </h2>
              <h2 className="payoff-requirement">
                REQUIREMENTS
                <br />
                <em>REVIEWED.</em>
              </h2>
              <p>
                Your coding agent completed the prompt.
                <br />
                AgentGuard helped you complete the requirement.
                <br />
                Only selected behaviours participated in this illustrative
                playback.
              </p>
            </>
          ) : (
            <div className="payoff-await">
              <h2>
                Verify
                <br />
                <em>the claim.</em>
              </h2>
              <p>No verification playback has completed.</p>
              <a className="button" href="#product">
                Run the demo ↗
              </a>
            </div>
          )}
        </div>
        <div className="cinema-timeline" aria-hidden="true">
          <span />
        </div>
      </div>
    </section>
  );
}
