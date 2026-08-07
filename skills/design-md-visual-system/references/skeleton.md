# Minimal Genre-A skeleton (expand to full bar)

Use as a starting scaffold. Expand every `TODO` until Signature Treatments, Defaults, CJK, Iteration, and Known Gaps are real. Target length after fill: **≥400 lines** for a real system; stubs under ~150 lines are not shippable.

```markdown
---
version: alpha
name: TODO System Name
description: >
  TODO one long thesis paragraph: cultural references, typeface roles,
  surface model, accent policy, depth model, density register,
  closer to X than Y.
colors:
  paper: "#F5F0E8"
  ink: "#1A1814"
  ink-soft: "#5C564C"
  accent: "#C45C26"
  border: "rgba(26,24,20,0.16)"
color-aliases:
  background: paper
  text-primary: ink
  text-secondary: ink-soft
typography:
  display:
    fontFamily: "TODO Display, Georgia, serif"
    fontSize: 4.5rem
    fontWeight: 500
    lineHeight: 0.95
    letterSpacing: "-0.02em"
  h1:
    fontFamily: "TODO Display, Georgia, serif"
    fontSize: 2.75rem
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: "-0.015em"
  h2:
    fontFamily: "TODO Display, Georgia, serif"
    fontSize: 1.75rem
    fontWeight: 500
    lineHeight: 1.15
  body:
    fontFamily: "TODO Sans, system-ui, sans-serif"
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "TODO Mono, ui-monospace, monospace"
    fontSize: 0.7rem
    fontWeight: 500
    letterSpacing: "0.14em"
    textTransform: uppercase
spacing:
  pad-x: 7.5vw
  pad-y: 5.5vh
  gap-lg: 4vh
  gap-md: 2.5vh
  gap-sm: 1.2vh
canvas:
  width: 100vw
  height: 100vh
components:
  rule-short:
    width: 36px
    height: 1px
    background: "{colors.accent}"
    description: "TODO when this mark appears."
  kicker:
    color: "{colors.accent}"
    typography: "{typography.label}"
    description: "TODO mono uppercase eyebrow above headlines."
---

## Overview

TODO thesis expanded. Name the **density philosophy** and what a broken layout looks like.

**Key Characteristics:**
- TODO
- TODO

## Colors

### Palette
- **Paper** (`{colors.paper}`): TODO job
- **Ink** (`{colors.ink}`): TODO job
- **Accent** (`{colors.accent}`): TODO only these contexts: …

### Defaults
- Default surface: …
- Default primary text: …
- Default accent application: …

## Typography

### Font Family
TODO role separation (display / body / chrome). Crossing rails is forbidden.

### Type Scale
| Token | Size | Family | Weight | Use |
|---|---|---|---|---|
| display | … | … | … | … |
| body | … | … | … | … |
| label | … | … | … | … |

### Defaults
- Primary section headline: `{typography.h2}` …
- Body: `{typography.body}` …

### Signature Treatments
These treatments are **non-optional** whenever the corresponding element type is used:
- TODO if X appears → must Y
- TODO

### Typography Principles
TODO italic/bold/underline policy; tracking rules.

## Layout

### Canvas System
TODO

### Padding and Gap Scale
| Token | Value | Use |
|---|---|---|
| pad-x | … | … |

### Chrome Frame
TODO what is persistent vs chromeless.

## Depth and Elevation
TODO single depth model (hairlines / soft cards / hard offsets). No freestyle shadows.

## Shapes and Treatment

### Border Radius
| Value | Use |
|---|---|

### Border Weights
TODO

### Decorative Element Types
TODO name each atom from `components:`.

## Do's and Don'ts

### Do
- TODO

### Don't
- TODO

## Responsive Behavior
TODO fluid vs fixed-stage. If frontend-slides: fixed 1920×1080 stage policy wins.

## CJK & International Content

### Recommended Chinese Pairing
| Role | Latin | Chinese | Weight notes |
|---|---|---|---|

### Mixed-Content Strategy
TODO

### Loading
TODO font link snippet

### Universal CJK Adjustments
- Line-height open; letter-spacing 0; no forced uppercase; Pangu spacing

### Aesthetic Notes for This System
TODO how the signature move translates (or becomes color-only)

### Known CJK Gap
TODO honest break

## Iteration Guide
1. Any new surface uses …
2. Any new headline uses …
3. Any new divider uses …
4. Any new label uses …
5. Any new accent moment is limited to …

## Known Gaps
- TODO debts, disabled experiments, browser limits, missing print CSS
```

## Local corpus pointers

| Mood | Start from |
|---|---|
| Warm magazine / pastel cards | `soft-editorial` |
| Intelligence briefing / dual surface | `signal` |
| Black ink on cream mono | `monochrome` |
| Loud poster / one red | `bold-poster` |
| Agency type-as-mass | `studio` |
| Neobrutal borders | `raw-grid` |
| Quiet green monograph | `grove` |
| Candy pills | `capsule` |

Path (operator-local tool): `beautiful-html-templates/templates/<name>/design.md`

Liz project templates (often thinner — do not treat as gold): project `_templates/design/` when present.

Optional after fill: `npx -y @google/design.md lint DESIGN.md` then export only if a Tailwind/DTCG consumer needs it.
