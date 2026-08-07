# When to load: Loop 1 — after Capture + extract-tokens + capture-runtime
# Precondition: recon/ artifacts exist (incl. runtime.json when theater-class)
# Output: docs/SIGNAL.md ≤2 pages (+ Interaction Contract table)

# Signal Sheet template

Fill after Loop 0 + `extract-tokens.py` + `capture-runtime.py`. Cap at ~2 pages.
Enough to start Skeleton. Do **not** expand into a brand bible unless shipping a
distinct product (`brand-distinction-v1`).

## Risk posture

- [ ] Study / internal-only
- [ ] Ship as product (composite 3–5 refs; Distinctiveness required later)

## Two-Reference Rule

| | URL / name | Notes |
|--|------------|-------|
| Positive | | Target to match |
| Anti-reference | | Same category; look you refuse |
| Sharp edge 1 | | Loop 4 goal |
| Sharp edge 2 | | |
| Sharp edge 3 | | |

## Target

- URL:
- Capture date:
- Stack fingerprint (headers/HTML):
- Dump quality: ☐ SSR content / ☐ shell-only (Playwright) / ☐ bot-blocked (manual DevTools)
- Capture artifacts: ☐ headers ☐ html ☐ css/ ☐ screenshots ≥5 ☐ computed.json ☐ **runtime.json** ☐ assets.json ☐ offsets.json
- Runtime tags: ☐ WEBGL_THEATER ☐ INNER_SCROLLER ☐ LENIS ☐ none (static)

## Story arc (from headings + screenshots)

| # | Section type | Heading / label | BG (ink/paper/dark/other) | Notes |
|---|--------------|-----------------|---------------------------|-------|
| 1 | Nav | | | morph? sticky? |
| 2 | Hero | | | window/surface/canvas count: |
| 3 | Logo cloud | | | marquee? |
| … | | | | |

Narrative in one line:

## Type roles

| Role | Target face (evidence) | Replica face | Weights |
|------|------------------------|--------------|---------|
| Display | | | |
| Body | | | |
| Editorial / pull | | | |
| Mono | | | |

Evidence: ☐ font filenames ☐ Google Fonts/Typekit ☐ CSS `@font-face` ☐ vision ☐ computed.json

Metric-align plan: ☐ N/A ☐ `metric-align-fonts.py` run

## Color roles (not every hex)

| Role | Hex | Evidence |
|------|-----|----------|
| Ink | | |
| Paper | | |
| Line / border | | |
| Mute text | | |
| Accent | | |
| Success / warn / danger | | |
| Signature (rebrand only) | | |

Ignore one-off illustration colors.

## Radius / shadow / container

- Button / card / window radius:
- Window shadow:
- Container max-width:
- Section vertical padding (approx):
- **Scroll budget:** target `maxScroll` from offsets/runtime: _____ px

## Product theater inventory

- Hero surfaces (count + titles) / canvas dims:
- Platform / tabs (labels + mock type):
- Dark band contents:
- Charts / SVG / WebGL patterns:
- Chips / badges / avatars density:
- Scroll tunnel / sticky field (length px):

## Named micro-patterns (Loop 4 backlog ≥3)

When `runtime.json` flags scroll or pointer theater, backlog **must** include
**≥1 scroll-linked** and **≥1 pointer-linked** pattern.

1.
2.
3.

## Interaction Contract (required — machine-checkable)

Do **not** leave interactions as prose bullets. One row per P0 runtime signal.

| Interaction | Evidence (DOM / runtime.json / video / trace) | Replica strategy | Pass criterion |
|-------------|-----------------------------------------------|------------------|----------------|
| Scroll container | e.g. `.lenis` / `scrollContainers[0]` | native / Lenis / CSS lerp | height ratio ≥ 0.85 |
| Hero theater | e.g. canvas 2160×1350 | WebGL / CSS+pointer / defer+GAPS | pointer move changes scene |
| Scroll tunnel | e.g. maxScroll 12319 | match / compress | ratio ≥ 0.85 **or** GAPS % |
| Sticky / invert | e.g. stickyCount, HUD color @ 72% | IO / scroll progress vars | ≥2 distinct scroll states |
| Nav smooth scroll | | rAF / Lenis / CSS | ≥3 frames over 600ms |
| Reduced-motion | | kill loops | no infinite CSS/WebGL |
| (add rows) | | | |

## Font / asset substitutes

| Target | Replica | Metric-align? | Reason |
|--------|---------|---------------|--------|
| | | | proprietary / legal |

## Open risks

- Missing CSS chunks? ☐
- SPA empty dump? ☐
- Bot management? ☐
- Trade-dress if shipping? ☐
- Scroll compress without GAPS? ☐
- Static snapshot (canvas flagged, no strategy)? ☐
