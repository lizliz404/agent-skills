# When to load: Attio-class CRM / multi-window product theater / Next.js SSR dumps
# Precondition: Studying a similar target OR comparing against attio-replica evidence
# Output: Case-specific patterns — do NOT copy Attio hex/keyframes into unrelated targets

# Case study: attio.com → Agent CRM (`attio-replica`)

> Evidence tier: Verified (real build)

Optional evidence appendix. Paths below are environment-specific; treat as historical proof, not required deps.

**Runtime note:** Attio-class sites are density/nav-morph heavy, not WebGL-tunnel heavy. Still run `capture-runtime.py` — expect `WEBGL_THEATER=false`. Loop 5 still applies (observer nav, reduced-motion, scroll-length usually near 1.0). For WebGL portfolios load `case-haoqi.md` instead.

- Replica: `/home/ubuntu/projects/attio-replica` (16 commits)
- Recon: `/home/ubuntu/projects/attio-recon` (`index.html` ~1.1MB, `headers.txt`)

## What the recon dump actually contained

| Signal | Present? | Notes |
|--------|----------|-------|
| Headings / story arc | Yes | Best section map — **zero** `<section id>` |
| `font-family:` decls | **No** | Faces from `/_next/static/media/inter_display_*.woff2`, `tiempos_text_*.woff2` |
| Design tokens as `--color-*` | Sparse / noisy | `--idx` ×672, `--stagger` ×344 — animation runtime |
| Ranked hex | Yes | Top: `#e6e7ea`, `#242629`, `#eeeff1`, `#101112`, `#266df0`, … |
| Inlined keyframes | Rare gold | `pipeline-radar-ring-inner/outer`, `pipeline-radar-bob` |
| SVG density | High | ~372 `<svg>`, ~18 clipPath-ish |
| Headers | Next + Vercel + CF | `x-nextjs-prerender`, Storyblok in CSP |

Replica simplified roles to `#0a0a0a` / `#fafafa` / `#e5e5e5` — **roles beat copying every gray**.

## Commit arc → loops

```text
9251632  V1 structure + tokens          → Loop 2 Skeleton
46b57ec  component split + @theme       → primitives / data
bf651ed  product theater (+1693/−542)   → Loop 3 Density (biggest leap)
539444b  reference screenshots          → Capture 0c + Density gate
d43e21d  rebrand Attio → Agent CRM      → brand-distinction (out of skill)
43eb99e  live mocks                     → Density liveness
ad968b3  Dynamic Island nav             → Loop 5 behavior
5f24ae2  DESIGN.md                      → docs after code
e4a808f  Attio-parity micro-patterns    → Loop 4
eefbb11  nav after hero, not scrollY    → Loop 5 bugfix
```

## Working token set (replica)

From `attio-replica/src/app/globals.css`:

- Ink/paper/line: `#0a0a0a` / `#fafafa` / `#e5e5e5`
- Signature (rebrand only): `--color-agent #0891b2`, `--color-agent-bright #22d3ee`
- Radii: btn `10px`, card `14px`, window `16px`
- Fonts: Inter Tight / Inter / Source Serif 4 (Tiempos stand-in)
- Section order: `Navbar → Hero → LogoCloud → PlatformTabs → DarkFeature → FeatureCards → BuildToScale → CustomerStories → Changelog → FinalCTA → Footer`

## Named micro-patterns (Attio-specific — Loop 4 backlog examples)

| Pattern | Implementation cue |
|---------|-------------------|
| Pipeline radar | Concentric SVG rings + bobbing chips; keyframes above |
| Retain stacked bars | `clipPath` + segmented rects + 2px white seams |
| Editorial serif pull | `.text-pull` italic Source Serif 4 |
| Black-fill active tab | `bg-ink text-paper` |
| Agent authorship chip | Cyan ≠ status green |
| Nav morph | Full-width while hero intersects → frosted pill after exit (`IntersectionObserver`) |

## WindowChrome (generalized primitive; values from this case)

- Light bar `#f7f7f7`, border `#ececec`, title ~12.5px
- Dark bar `#161616`, border `white/10`
- Traffic lights decorative `aria-hidden`
- See `src/components/ui.tsx`

## Anti-reference example (Two-Reference Rule)

When studying Attio-class restraint, a useful anti-ref is a busy multi-hue CRM/marketing site (HubSpot-class rainbow). Sharp edges to keep: monochrome paper/ink, overlapping window collage, editorial serif, one authorship accent — not a new color per section.

## Claims that failed (why v2→v3)

| Old claim | Reality |
|-----------|---------|
| curl dump is full tokens | Fonts = filenames; CSS in chunks |
| Map via `<section id>` | Zero IDs; use headings + `data-*` |
| DESIGN.md before build | First fidelity shipped without it |
| ±2px before density | Density leap first (`bf651ed`) |

## Distinctiveness lessons (rebrand only)

Hand SVG marks; asymmetry by construction; signature color in favicon; sniff test (cover wordmark). These live in `brand-distinction-v1`, not replication loops. See historical `docs/design-audit-v3.md` / `docs/DESIGN.md` in the replica repo.
