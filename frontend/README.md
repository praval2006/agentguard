# AgentGuard product frontend

Independent React + TypeScript + Vite app, with plain CSS and no backend coupling.
Node 20.19+ or 22.12+ is recommended. From the repository root:

```sh
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. The server uses loopback by default.

```sh
npm run typecheck
npm test
npm run build
```

The landing page includes a keyboard-operable evidence graph and inspector, controlled
verification playback, a stage explorer and explicit trust/verdict explanations.
Reduced motion skips playback delays and removes animations. A mobile layout turns
the branching graph into vertically connected buttons. The site uses system fonts
and has no font CDN, analytics, authentication or external image requests.

`src/data.ts` preserves the historical three-requirement evidence graph. In that
original task premium revocation was explicit. The graph is labelled independent
of review choices. `src/reviewData.ts` supplies a **separate illustrative shorter-task
variant** for the reviewed experience; it is not a historical planner output.
No original task artifact or frozen result was relabelled.

The reviewed contract always includes subscription status. Premium access is an
inferred suggestion, initially PENDING. Add to verification or Dismiss is required
before Run verification; selection alone never starts playback. Accepted suggestions
keep their inferred origin. Decisions can be changed before running or through Change
decision after completion, which clears old evidence. Reset returns to PENDING.
Reloading also resets local state; there is no production persistence.

The accepted fixture contains status PASS and premium-access FAIL (expected false,
observed true), overall FAIL. The dismissed fixture contains status PASS only,
overall PASS for that narrower selected sample. No frontend aggregation occurs.
Repeated cancellation is not part of the shorter contract and receives no result
there. No ambiguity output is invented. The historical graph retains its independent
UNVERIFIED explanation. The report explicitly limits claims to represented samples.
The rationale is labelled illustrative model rationale, not verified repository evidence.

Future API integration should supply actual evidence records to the existing
`EvidenceInspector` and demo result views, replacing the local playback state in
`ReviewDemo`. Keep backend-returned verdicts authoritative; do not calculate them
in the browser. No API adapter is implemented in this checkpoint. Run the demo
links intentionally navigate to the controlled product section. GitHub links point
to the existing project repository. This is not a fresh evaluation or a claim of
universal correctness.

Interaction tests use Vitest/Testing Library with local records only. Backend tests
and frozen evaluations remain separate. `dist/`, dependencies and TypeScript build
metadata are ignored. The lockfile freezes frontend dependencies.


## Cinematic scroll narrative

`CinematicStory.tsx` replaces the main reveal-once story with a 560svh native-scroll
section and a sticky viewport stage. `scrollTimeline.ts` defines overlapping scene
windows. A passive scroll listener samples normalized progress once per animation
frame and updates only stage transforms, opacity and visibility. Scrolling backward
reverses the composition; there is no scroll interception or snapping.

Large responsive serif title cards contrast with compact technical evidence. Mobile
uses vertical layering and shorter travel. Reduced motion presents the same content
as a readable stacked sequence, with immediate explicit verification playback.
Inactive layers are inert and hidden from assistive technology; DOM reading order,
a story overview and a skip-to-verification link provide context and navigation.

The existing controlled records, explicit Run verification button, phases, progressive
evidence, reset/replay, graph and stage explorer are reused. Scrolling never starts
verification. The final payoff exists only after playback completes. Reveal.tsx
remains for ordinary sections outside the cinematic stage. No animation dependency,
backend integration or verdict calculation was added.

## Review accessibility and validation

Review state types are separate from verdict types. Excluded review records do not
carry verdicts. Native buttons expose pressed/disabled states, visible focus and a
polite status announcement. A disabled verification button explains the pending
review through aria-describedby. Changing/resetting a completed view restores focus
to the review heading without moving the scroll position. Reduced motion removes
playback delays. Short viewports use document flow to prevent clipped controls;
390×844 and 1440×1000 retain the cinematic stage.

Run `npm test`, `npm run typecheck`, and `npm run build`. The tests cover both
review branches, initial exclusion, preserved origin, explicit-only inclusion,
reset/replay, fixed result selection, semantic control access, existing story,
graph/stage navigation and timeline behaviour. Browser checks supplement unit tests.
No new dependencies or backend requests are introduced.
