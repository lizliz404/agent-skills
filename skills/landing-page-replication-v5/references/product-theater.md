# When to load: Loop 3–5 — building product mocks / density leap / theater stand-ins
# Precondition: SIGNAL.md theater inventory + reference screenshots pinned + runtime.json tags
# Output: Code-built product UI inside shared primitives (not PNGs); runtime-reactive theater

# Product theater patterns (v5)

Cross-site density patterns. Case-specific geometry lives in `case-attio.md` /
`case-linear.md` / `case-haoqi.md` — do not cargo-cult.

## 1. One WindowChrome (or equivalent) primitive

Do not invent a new frame per section.

- Light + dark tones only
- Decorative traffic lights / window controls: `aria-hidden`
- Body = fake product UI (table, chart, list, chat, board) — not a screenshot PNG

If the target uses custom title bars (eng-tools often do), match that grammar instead of forcing macOS chrome. If the target is a **portfolio HUD** (haoqi-class), prefer instrument chrome over WindowChrome.

## 2. Hero = overlapping surfaces, not one hero image

- 3–5 surfaces with intentional overlap; slight rotation on secondary cards when the target does
- One primary surface sharp / highest z-index
- ≥1 live signal: pulse, typing lines, cycling status, **or pointer-linked theater**
- Avoid a single flat dashboard screenshot — density dies → Failure Gallery A

## 2b. WebGL / canvas theater (v4)

When `runtime.json.flags.WEBGL_THEATER`:

| Strategy | When | Pass criterion |
|----------|------|----------------|
| Real WebGL / Three.js | Study clone, agent can ship shaders | `canvasCount ≥ 1` + pointer/scroll linkage |
| CSS/SVG stand-in | Legal/time constraint; no proprietary meshes | Pointer move changes scene (`--rx/--ry`, refraction vars, or measurable style delta) |
| Explicit defer | P0/P1 in GAPS with date/owner | Documented; Behavior gate waived with criterion |

**Illegal escape hatch (v3 hole):** CSS gradient wash that looks good in a PNG but does not react to pointer or scroll → Failure Gallery **I**.

haoqi evidence: CSS `.glass-hello` + `--rx/--ry` is a valid stand-in **only if** pointer reactivity is proven; scroll tunnel still needs length + scroll-linked vars (`--tunnel-progress`).

## 3. Tabs = selected-state convention + per-tab mock

- Match target selected tab (often solid ink-on-paper; sometimes underline/accent)
- Pane swaps full mock variants — not text-only
- Each tab: different chart/list metaphor from the theater inventory
- Skip this section when target has no tabs (portfolios) — do not invent tabs to satisfy v3 muscle memory

## 4. Charts as SVG / DOM, not images

Techniques that survive across SaaS:

| Technique | When |
|-----------|------|
| `clipPath` + stacked segments | Cohort / retain / stacked bars |
| Seam dividers in paper color | Separates stacked segments |
| Concentric rings + opacity keyframes | Live monitoring metaphors (**only if target has them**) |
| Per-chip `animation-delay` | Organic desync |
| Rounded path tops | Softer than raw rects |

If the HTML dump inlines `@keyframes` / paths, extract geometry; don't restyle from memory.

## 5. Cheap liveness hooks

```text
useReveal        — progressive lines on interval
useCycle         — rotate N states ~3s
useIdleHighlight — pulse a row/bar index
hover lift       — translateY + stronger shadow
pointer vars     — --rx/--ry / tilt on theater nodes
scroll progress  — --tunnel-progress on sticky wrappers
```

`prefers-reduced-motion`: freeze pulses; show final reveal state; bypass scroll-jacking.

## 6. Dark feature band / scroll tunnel

When the target has one: full-bleed near-black (or brand dark), sticky headline optional, scroll-driven field. **Match scroll length** — a one-viewport dark band is not a 7k-px tunnel (Failure Gallery **J**).

Read sticky wrapper heights from `dom.html` / computed styles (`height: 7200px` patterns), not from a single innovate screenshot.

## 7. Color grammar inside mocks

- Green = live / success; amber/rose = warn/risk; blue = info/selection
- Signature accent (rebrand) = authorship only — never primary buttons
- Do not invent a rainbow (Failure Gallery B)

## 8. Data-driven copy

Headlines, tabs, quotes, changelog in `data.ts` (or equivalent). Components stay presentational. Enables Loop 4 copy passes without markup churn.

## Cut strategies (opportunity cost)

1. Remove a weak section before adding another — rhythm > count
2. Two mocks at ~90% beat four at ~25%
3. Fix uncanny copy before ±2px (Failure Gallery H)
4. Fix scroll-length before inventing more idle animations (Failure Gallery J)

## Anti-patterns

- One giant PNG as hero
- Empty cards with icon + lorem
- Different chrome styles per section
- Animating everything (prefer scroll + hover + one idle loop)
- Purple AI glow / neural nets unless the **target** uses them
- Pasting Attio radar into a Linear-class page (wrong case file)
- **Static WebGL wash** that passes IMR and fails Behavior
- **Replica-only cursor trails** not on target (false motion progress)
