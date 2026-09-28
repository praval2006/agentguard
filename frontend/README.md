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

`src/data.ts` is the central **illustrative-controlled-playback** data model. The
subscription-specific implementation side shows two tests; this is not the total
sample-app suite. The presentation separates three requirements for inspection;
it does not imply three separate historical HTTP calls. No server or model is
called, and displayed verdicts are fixed demo records, not frontend verification.
The label on the page makes this explicit. Playback lasts about 2.5 seconds and can
be reset or replayed. Missing supported evidence is shown as UNVERIFIED, not failure.

Future API integration should supply actual evidence records to the existing
`EvidenceInspector` and demo result views, replacing the local playback state in
`ControlledDemo`. Keep backend-returned verdicts authoritative; do not calculate them
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
