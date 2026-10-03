# AgentGuard presentation frontend

React + TypeScript + Vite, with plain CSS and no runtime dependencies beyond React.

```sh
cd frontend
npm ci
npm run dev
```

Open the local URL printed by Vite (normally http://127.0.0.1:5173).

- `/`: twelve-section presentation, from the acceptance gap to an evidence-backed report.
- `/demo`: interactive account-deletion acceptance review and controlled playback.

```sh
npm test
npm run typecheck
npm run build
```

## Presentation and navigation

`App.tsx` selects the two views using the History API and `popstate`; native links
retain modifier-click/new-tab behavior. `navigation.tsx` handles in-app navigation.
A static production host must serve `index.html` for `/demo` (SPA fallback).
Direct entry, back navigation and returning to `/#trust` are supported. No router,
animation, image, font, analytics or API dependency was added.

`PresentationPage.tsx` contains the centered narrative: hero, problem, acceptance
gap, independent boundary, human authority, demo launch, trust architecture,
generalization, verdict boundary, report, future vision and closing. Shared Scene
and Flow compositions keep the small presentation component tree understandable.
The references inform the midnight/navy surfaces and restrained violet illumination;
no reference assets, branding or product layouts are copied.

`Reveal.tsx` reuses the existing IntersectionObserver approach but supports repeated
entry. Below-view elements rise gently into place; elements above the viewport stay
visible when returning upward. No sticky stacking, scroll capture or one-way hidden
state. Flow connections and staggered steps communicate progression. Observer failure
leaves content visible. Reduced motion disables transitions and playback delays.

## Controlled demo and trust boundary

`ReviewDemo.tsx` extends the previous local human-review/timer pattern into:
INTRO → ANALYZING → REVIEW → CONTRACT → VERIFYING → RESULTS → REPORT.
The earlier subscription narrative and data files remain historical source material;
they are no longer mounted by the presentation. The old timeline unit tests remain.

`accountDemoData.ts` supplies a separate, explicitly authored account-deletion
presentation fixture. It is not a frozen evaluation, real repository analysis or
backend report. No browser HTTP request, planner, grounder or verifier is invoked.
The analyzing display contains only input categories, not fabricated reasoning.

The explicit deletion requirement is always included. Both session/profile
suggestions begin PENDING. Each must be accepted or dismissed before the contract
can proceed. Accepted suggestions retain inferred origin. Dismissed suggestions
remain in review history and have no result. User-created content is an ambiguity,
not a suggestion to approve or a verification verdict.

All four completed decision combinations select explicitly authored fixtures:

| Session   | Profile   | Selected | PASS | FAIL | UNVERIFIED | Overall |
| --------- | --------- | -------: | ---: | ---: | ---------: | ------- |
| Accepted  | Accepted  |        3 |    1 |    2 |          0 | FAIL    |
| Accepted  | Dismissed |        2 |    1 |    1 |          0 | FAIL    |
| Dismissed | Accepted  |        2 |    1 |    1 |          0 | FAIL    |
| Dismissed | Dismissed |        1 |    1 |    0 |          0 | PASS    |

React selects a fixture; it does not compare responses or aggregate verdicts.
Normal playback reveals observed evidence before each fixture verdict. Reduced
motion exposes the same evidence immediately on explicit run. Completion reveals
the payoff; a separate action assembles the report view from the same fixed fixture.
Ambiguity stays outside counts. Narrower selection means a narrower conclusion.
Changing decisions clears playback/results before review; reset cancels timers,
restores pending decisions and returns to intro. Replay does not change decisions.
Reloading or leaving the demo resets local state. There is no persistence.

The report mirrors Phase 5 concepts (origin, decisions, contract, evidence, result,
ambiguity and limits). It does not dynamically consume backend JSON or calculate
backend results. A future adapter must preserve backend verdict authority.

## Accessibility and presentation use

Native links/buttons, pressed and disabled states, visible keyboard focus, a skip
link, heading focus on stage changes and polite status announcements are retained.
Verdicts have symbols and text as well as color. Controls never trigger execution
from scrolling. Stage changes bring the next heading into view; long review/report
views use normal document scrolling rather than clipping a fixed-height viewport.

Large clamp-based headings and central compositions target 16:9 projection; tablet
and mobile stack technical panels. Headless Chrome checks at 1440×810 and 390×844
cover the narrative, reverse scrolling, review, contract, evidence, results and report.
Unit tests cover navigation, reveal fallback/reentry, reduced motion, all review
branches, pending gates, fixture identity, evidence-before-verdict, reset/replay,
stale-result clearing and ambiguity separation. Backend and frozen evaluations are
not run by frontend tests. No paid API calls occur.

## Ambient environment and hosting

`AmbientBackground.tsx` renders one decorative, pointer-transparent canvas behind
both views. Muted navy/violet illumination and tiny drifting points respond gently
to scroll depth. Desktop fine pointers add slight particle repulsion and a broad,
faint light with a 270px smoothstep influence radius; touch and narrow screens omit pointer effects. Density is capped at
40 points on the presentation and 20 in the demo (33/16 at 1440×810), reduced to 10/6 on coarse or narrow
screens. Reduced motion draws a static composition. Canvas drawing is capped at
30 fps and device pixel ratio at 1.5; hidden tabs pause and unmount removes listeners
and animation frames. No animation dependency or per-frame React state is used.
Static procedural SVG grain, elongated edge haze and two very faint localized grid
fragments add texture. A sparse edge arc and gently interpolated section emphasis
keep technical depth out of the central reading area. Demo texture is weaker.
`BrandMark.tsx` supplies the original scalable open-shield/evidence-check SVG; its
internals are decorative while surrounding wordmarks retain accessible text.

With Vercel Root Directory set to `frontend`, `vercel.json` supplies the
[recommended Vite SPA fallback](https://vercel.com/docs/frameworks/frontend/vite)
so direct `/demo` navigation and refresh resolve to `index.html`. Redeploy to apply
this hosting configuration; verify `/demo` refresh and static assets on that deployment.
The local browser checks do not establish the deployed Vercel configuration.
