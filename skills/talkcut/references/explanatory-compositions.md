# Lightweight explanatory compositions

Use only when a small picture explains a relationship more clearly than the existing
footage and captions. A card repeating a visible screenshot, JD excerpt or spoken
sentence is not a useful composition. Inspect the existing frames first.

## Route to design expertise, not a new video stack

1. Load the installed **Design Templates** entry and its canonical router. Portable
   sources: [Design Templates](https://github.com/lizliz404/design-templates),
   [visual economy](https://github.com/lizliz404/design-templates/blob/main/templates/decks/visual-economy.md),
   [diagram routing](https://github.com/lizliz404/design-templates/blob/main/templates/decks/diagram-skills.md).
2. For a real relationship diagram, load **[Diagram Design](https://github.com/cathrynlavery/diagram-design/tree/main/skills/diagram-design)**
   and only its matching type and motion references. Use its relation-first layout,
   deletion test and explicit reveal order; retain the current video's approved
   colors, typography and navigation instead of importing a new default skin.
3. Choose the lightest output. A two-row role table needs no framework. A few nodes
   and arrows can be rendered with SVG, Pillow or ASS; choose HyperFrames/live-panel
   only for a concrete animation gap. A reference is not a requirement to build an
   interactive web app or full deck inside a video.

## What earns space on screen

Write a private one-line viewer question before drawing. Examples:

| Viewer question | Useful picture | Skip |
|---|---|---|
| How does this round become reusable next time? | Current images/prompt → stored version → next iteration | Another bullet list saying “save everything” |
| What else changes when the customer changes a color or price? | Change → linked image/specification or price/proposal | A decorative tool-logo wall |
| Who organizes and who confirms? | Two semantic rows, revealed with the corresponding words | A dense architecture diagram |
| What does this job posting require? | The existing actual JD screenshot, if already present | A second card re-explaining the same JD |

Use few short moments, spaced apart. A sourced GIF's original duration is not its
allowed screen time: select only informative frames, exclude loading/spinner/blank
sections, and respect the user's cap. Ten seconds is a ceiling when specified, not
a target. Leave the strong real footage alone between useful inserts. Sparse does
not mean minimal at all costs: if a whole topic has no useful visual aid, add a
well-spaced one rather than treating emptiness as a quality metric. For a true
visualization, use recognizable objects, multiplicity, paths, branches or a handoff;
a title with two lines of prose is still just a text card.

## Reveal one thought at a time

- Establish the border/background and title first, with a short opacity fade.
- Reveal the first row/node, then the next row/node when that part is being said.
  Do not drop the whole finished block on screen at once.
- Keep positions stable. Fade/very small translation is sufficient; no bouncing,
  zooming, decorative particles or endless semantic loops.
- Keep the completed thought visible long enough to read, then fade it out.
- Match actual phone-scale legibility. A hairline that looks delicate at 1080px may
  vanish at 270–360px; use a visible border, not a barely perceptible outline.
  One approved portrait treatment uses a 9px border on a 948px-wide card.
- Keep the approved progress/navigation exactly as it is. Place inserts around the
  subject, manual captions and existing PIP, not on top of them accidentally.

## Copy and provenance

Only put words on screen that help the viewer understand the content. Do not add
agent self-defense such as “non-product footage”, “not implemented”, or explanatory
source banners by default; do not label obvious UI fields a second time. Keep source
URLs, retrieval dates, rights uncertainty and selection receipts in sidecar metadata,
not as an extra speech layer. Preserve original source watermarks and any genuinely
required attribution; removing an added banner does not authorize erasing a watermark
or inventing functionality, outcomes or endorsements.

## Rendering and checks

Use a single deterministic composition timeline. ASS vector events with `\fad` can
reveal a small title/table/flow over existing footage without a browser render pass.
Repeated, independently delayed looping PNG inputs can cause ffmpeg framesync queues
and large memory use; use one synchronized overlay or vector layer instead of raising
memory limits or hiding the issue.

Before the full render, inspect the **actual production renderer** at title-only,
first-row, next-row and complete states, then expose a short local moving preview.
A static final image does not verify reveal order. Check label fit, border weight,
existing captions/PIP, no loading frames, and the gap between inserts. Reuse the same
localhost review page; no new ASR, source recut, speed change or subtitle replacement
is needed for a packaging revision.
