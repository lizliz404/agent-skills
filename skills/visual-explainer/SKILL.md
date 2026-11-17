---
name: visual-explainer
description: Turn complex processes, SOPs, role collaboration, data flows, stage-gates, feedback loops, or system boundaries into beginner-friendly explanatory visuals. Use when the user asks to explain, visualize, map, or present a process, workflow, approval chain, system, or multi-actor collaboration as an editable SVG or self-contained HTML diagram. Do not use for decorative marketing graphics, photo illustration, data charts from datasets, or video/motion work.
---

# Visual Explainer

Content-to-explainer workflow. Rendering grammar is delegated to the
vendored upstream pack; this skill owns the explaining method.

**Canonical source:** `/home/liz/dev/agent-skills/skills/visual-explainer`
(a checkout of this repo's `skills/visual-explainer/` directory is the SOT).
**Rendering pack (third-party, MIT, read-only):**
`/home/liz/dev/repos/diagram-design/skills/diagram-design/`
(upstream: https://github.com/cathrynlavery/diagram-design).
Never modify the rendering pack; update it with `git pull` only.

**Global bridge:** `~/.agents/skills/visual-explainer/SKILL.md` (discovery only).

## 0. Non-goals (do not use)

- Decorative hero art, marketing illustration, photo/mascot work.
- Statistical charts from raw datasets (use Vega/Plot natively instead).
- Video, animation, slide decks with presenter flow (use motion-graphics /
  slideshow / hyperframes skills).
- Quick inline doc sketches (a Mermaid fence in Markdown is enough).
- Pixel-perfect print layout; output targets screen-first, print-tolerant.

## 1. Understand before drawing

Before any SVG/HTML, establish in chat (or from the brief):

1. **Audience**: who reads this, what do they already know?
2. **Question**: what single question must the figure answer?
   (If it answers nothing, do not draw — write the paragraph instead.)
3. **Core tension**: the one conflict, handoff risk, or decision the
   explanation turns on.
4. **Fact discipline**: mark every element fact / inference / unknown.
   Unknowns render as dashed, labelled "unconfirmed" — never invented.
5. **Evidence status**: source for each fact; secrets stay local
   (never upload internal material to hosted renderers).

## 2. Grammar selection

| Content shape | Grammar | Upstream reference |
|---|---|---|
| Time / sequence / stages | stage-gate flow or flowchart | `type-flowchart.md`, `type-process.md` |
| Cross-role handoffs | swimlane | `type-swimlane.md` |
| Data objects / pipeline | data-flow / ER | `type-data-flow.md`, `type-er.md` |
| Feedback / reinforcement | causal loop | `type-loop.md` |
| Decisions / branches | tree / quadrant | `type-tree.md`, `type-quadrant.md` |
| Whole system at a glance | architecture / nested | `type-architecture.md`, `type-nested.md` |
| Talk / progressive reveal | story panels (one figure per beat) | `type-timeline.md` + `animation.md` only if asked |

One figure, one grammar. Above ~9 nodes, split into two figures.
Never answer everything with a card wall + arrows.

## 3. Information architecture, then visual encoding

1. Draft the IA as a list: actors → stages → handoffs → gates →
   feedback edges → boundary (in-scope / out-of-scope).
2. Encode with more than color: shape + label + position carry meaning;
   color is redundant reinforcement only.
3. Fact / inference / unknown get distinct strokes (solid / dotted / dashed
   + "unconfirmed" tag).
4. Every figure carries: title, one-question caption, source line,
   evidence-status note.

## 4. Output contract

- **Primary**: single self-contained `.html` (inline SVG, no JS unless the
  reader must click through steps; zero CDN/network deps).
- **Or** standalone `.svg` with `<title>`/`<desc>`, `viewBox`, system font
  stack + CJK fallback
  (`-apple-system, "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei", sans-serif`).
- Responsive (`max-width:100%`), mobile-readable (min ~12px equivalent),
  print-tolerant (light theme default, ink-safe palette).
- a11y: semantic HTML, `role="img"` + `<title>`/`<desc>` on SVG,
  no color-only encoding, AA contrast.
- Follow the upstream `references/style-guide.md` + `output-spec.md`;
  for a branded project run its style-gate first.

## 5. Validation (must pass before delivery)

1. SVG/XML well-formed (`python3 -c xml.dom.minidom.parse`) or HTML opens
   with zero console errors.
2. No text overflow at 360px and 1280px widths (upstream `layout-budget.md`).
3. No hallucinated nodes: every element traces to brief §1 facts.
4. No external URLs except allow-listed sources; no secrets in output.
5. Open the file in a real browser (desktop + mobile width) and look at it.

## 6. Minimal procedure

1. §1 questions → 2. grammar table → 3. load ONLY the matching upstream
   `references/type-*.md` (+ `style-guide.md`, `output-spec.md`) →
   4. draft IA → 5. write HTML/SVG → 6. run §5 checks → 7. deliver file
   + one-paragraph reading guide.

Research log: `references/research-2026-09-30.md` (candidate long-list,
scores, rejections, links, final choice).
