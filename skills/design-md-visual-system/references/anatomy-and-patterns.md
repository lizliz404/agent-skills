# Anatomy & patterns (beautiful-html-templates corpus)

Source: gold corpus bundled at `gold-corpus/` (34 templates, mirrored 2026-08-05 from `beautiful-html-templates`; structure + lint profile in `gold-corpus/README.md`). Canonical bar: `gold-corpus/soft-editorial/design.md`.  
The corpus **is** shipped in the public skill zip under `references/gold-corpus/`; the external tool remains the refresh source.

## Universal structure (34/34)

### YAML frontmatter (top-level keys)

| Key | Coverage | Notes |
|---|---|---|
| `version` | 34/34 | Usually `alpha` (Google design.md era — format still evolving) |
| `name` | 34/34 | Human system name |
| `description` | 34/34 | **Long** one-paragraph thesis: cultural refs, faces, palette logic, depth model, what it is closer to than X |
| `colors` | 34/34 | Named semantic tokens → quoted hex/rgba |
| `typography` | 34/34 | **Role tokens** not just h1/body — e.g. display, h1–h3, lead, body, caption, label, stat-value, quote-text |
| `spacing` | 34/34 | pad-x/pad-y, gap-lg/md/sm, or named pads |
| `canvas` | 34/34 | Usually `100vw × 100vh` for decks |
| `components` | 34/34 | Named atoms with properties + **`description:`** prose |
| `color-aliases` | 21/34 | Map roles → color keys (`background: paper`) |
| `borders` / `shadows` / `radii` / `motion` | rare | When the system is border/shadow-defined (raw-grid, daisy-days) |

Typography role object fields (when present): `fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`, optional `textTransform`, `fontStyle`, `color`, `transform`.

Component values may use token refs: `"{colors.gold}"`, `"{typography.label}"`, `"{spacing.gap-md}"`.

Hex and negative dimensions must be **quoted** in YAML (`"#F2EEDF"`, `"-0.02em"`).

### Token ladder (primitive → role → component)

Aligns with Carbon/shadcn practice without leaving Google DESIGN.md YAML:

1. **Primitives** — named swatches in `colors:` / type faces in `typography:` (exact CSS values from code or corpus).
2. **Roles / aliases** — `color-aliases:` (and prose Defaults) map jobs → primitives (`background: paper`, `text-primary: ink`). Prefer surface/foreground pairs in product UIs when that matches the system.
3. **Components** — atoms reference roles via `{colors.x}` / `{typography.y}`; each atom has a **when/where** `description:`.

Do **not** author DTCG `$type`/`$value` trees in the frontmatter. If a pipeline needs W3C Design Tokens or Tailwind `@theme`, use `npx @google/design.md export --format dtcg|css-tailwind|json-tailwind`. DESIGN.md stays the agent-facing contract; exports are interchange.

### Markdown body H2 order (canonical)

1. Overview *(optional prefix: Frontend Slides Fixed-Stage Policy for deck generators)*
2. Colors
3. Typography
4. Layout
5. Depth and Elevation *(alias: Elevation and Depth)*
6. Shapes and Treatment
7. Do's and Don'ts
8. Responsive Behavior
9. CJK & International Content
10. Iteration Guide
11. Known Gaps

Google design.md minimal set is Overview → Colors → Typography → Layout → Elevation → Shapes → Components → Do's/Don'ts.  
**This corpus extends** with Responsive + CJK + Iteration + Known Gaps. Prefer the extended set for Liz.

### High-frequency H3 patterns

- **Colors:** Palette · Defaults
- **Typography:** Font Family · Type Scale (table) · Defaults · **Signature Treatments** · Typography Principles
- **Layout:** Canvas System · Padding and Gap Scale · Chrome Frame / Persistent Chrome
- **Shapes:** Border Radius · Border Weights · Decorative Element Types
- **Do's and Don'ts:** Do · Don't
- **Responsive:** Scaling Behavior · Presenter Behavior · Print Behavior
- **CJK:** Recommended Chinese Pairing · Mixed-Content Strategy · Loading · Universal CJK Adjustments · Aesthetic Notes for This System · Known CJK Gap

## Pattern library (what gold prose always does)

### 1. Thesis paragraph in `description` + Overview

Not "a modern clean UI." Instead:

- **Cultural references** (literary quarterly, Italian sports poster, intelligence briefing, Saul Bass, Memphis ice-cream parlor)
- **Typeface roles** in one sentence (who leads / who supports / who is chrome)
- **Surface model** (single cream field vs dual navy/cream vs binary black/acid-yellow)
- **Accent policy** (one gold only / five interchangeable pastels / no chromatic accent)
- **Depth model** (flat+hairline / soft translucent cards / hard offset shadows)
- **Anti-reference** (closer to X than corporate deck)

### 2. Density philosophy (31/34)

Explicit sentence: sparse / medium-low / medium-high / high-populist.  
State what a *broken* slide looks like (too full vs too empty).

### 3. Key Characteristics (34/34)

6–10 bullets that an implementer can check against a screenshot.

### 4. Signature Treatments (31/34) — the load-bearing section

Header usually: *"These treatments are **non-optional** whenever the corresponding element type is used."*

Each bullet: **If element type X appears → must look like Y.** Examples from corpus:

| System | Signature move |
|---|---|
| Signal | `<em>` inside serif headline → italic Source Serif + gold |
| Soft Editorial | Headline roman 500 + mid-sentence italic 400 same family |
| Bold Poster | Hero Shrikhand stack: ≥1 rotated line + ≥1 red line |
| Monochrome | Jost display weight 200 only; Lora only on quote/insight title |
| Grove | Playfair italic in terracotta for accent emphasis |
| Raw Grid | 3px solid black borders + hard black offset shadow |
| Studio | Barlow 900 uppercase as graphic mass; only dark↔acid-yellow inversion |

Without this section, agents freestyle and the system dies. Market parallel: named **variants** / non-optional treatments in Radix-style systems — same job, prose form.

### 5. Defaults subsections (31/34)

Answer "when unsure, use ___." Default surface, default headline size token, default body, default accent application, default border weight.

### 6. Role-separated type ladder

Almost every strong system uses **2–4 faces with non-overlapping jobs**:

- Display / voice (serif or heavy display)
- Body / substance (sans or literary serif)
- Chrome / metadata (mono or tracked grotesque)
- Optional: quote-only face

Crossing rails is listed under Don't.

### 7. Accent scarcity

Single accent used in 2–4 named contexts only — or multi-pastel with **no semantic lock** (lemon ≠ warning). Explicit "never fill body with accent / never second accent."

### 8. Depth is a system decision

One of:

- Flat + 1px hairlines (Signal, Monochrome, Grove)
- Translucent soft cards, no shadow (Soft Editorial)
- Hard offset shadows only (Raw Grid, Daisy Days)
- One stacked text-shadow exception (Bold Poster red panels)

Never "add some shadow for polish" without a rule. Carbon's *layering model* is the same idea at product scale: pick one stacking law and stick to it.

### 9. Components as named atoms with jobs

Each component entry: visual props + **description of when/where it appears**. Prefer atoms (rule-short, kicker, stat-cell, chrome-bar) over page templates.

### 10. CJK translation honesty (34/34)

- Pairing table Latin ↔ 思源/Noto
- What breaks (no italic axis, weight 200 unusable on SC, uppercase+tracking mono kickers)
- **Known CJK Gap** — name the signature move that cannot fully translate and the deliberate workaround (color-only emphasis, weight remapping)

### 11. Iteration Guide (34/34)

Numbered rules for *adding* a new slide/component without drifting. Copy this tone: "Any new divider is a 1px hairline in border-dark. Never thicker."  
Also the lightweight **evolution** surface: how the system grows without a separate VERSIONING.md.

### 12. Known Gaps (34/34)

Honest debts: disabled sidebar, browser support (`color-mix`), animation engine wiring, name aliases, missing print CSS. Prevents agents "fixing" intentional absences — the gotchas layer agents need (same role as failure notes in design-system Claude skills).

## Genre A vs Google minimal CLI

Bundled Hermes `design-md` / `npx @google/design.md` teaches Google's schema + lint/export.  
This skill demands the **corpus-complete** prose layer (Signature, Density, CJK, Iteration, Gaps). Lint still useful for broken refs and contrast; export useful when Tailwind/DTCG consumers appear. Do not shrink to Stitch's short "Visual Theme + Palette" stub.

## How to steal a template into a product UI

1. Pick closest template by mood (not by name).
2. Keep Signature Treatments + density + type ladder.
3. Rebind colors/copy to product tokens from real CSS.
4. Drop deck-only chrome (slide counter, progress bar) or remap to app chrome.
5. Add product components (forms, tables, nav) under same depth/border/radius laws.
6. Keep CJK section if Liz ships bilingual.

## Anti-patterns observed in thin local DESIGN.md files

- YAML colors/type present, body is product essay only (no Signature, no scale table)
- Overview is brand stance without density or characteristics checklist
- Components list button variants only — no decorative/structural atoms
- Missing CJK entirely on bilingual products
- No Known Gaps → agents invent "fixes" for intentional constraints
- Tokens-only export mistaken for a finished Genre A doc
