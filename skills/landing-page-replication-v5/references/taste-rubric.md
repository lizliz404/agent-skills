# When to load: Before Loop 3–5 gates, or any "does it feel right" debate
# Precondition: Target + replica screenshots (or live URLs) for the bands under test; runtime.json for theater-class
# Output: Pass/fail on IMR / ED / TSS / scroll-length / behavior; soft rhythm note; Generic-SaaS sniff

# Taste Rubric (v5)

Measurable gates that replace "blur-sniff vibes." Hard gates block Loop exit; Rhythm is soft.
**Runtime hard gates** — ink-mass alone is insufficient. Probe design: `behavior-gates.md`.

## Hard gates (visual)

| Gate | Metric | Pass threshold | Fail example |
|------|--------|----------------|--------------|
| **IMR** (Ink-Mass Ratio) | Non-white / non-gray pixels per 100vh (or per section band) | Hero **20–35%**; feature **30–45%**; dark band **55–75%**. Replica vs target **Δ ≤ 8%** on matched bands | Empty cards → replica hero IMR **12%** vs target **28%** |

**Per-scroll-position IMR:** Hero-only PNGs can pass while mid-scroll bands fail (tunnel hollow).
Pin screenshots at **0 / 25 / 50 / 75 / 100%** scroll (match `capture.py` shots) and run
`audit.py --imr` per band — not only the hero frame. A passing hero IMR with SLR **0.52**
(haoqi) is a **Scroll Compress (J)** fail, not a tolerance tweak.
| **ED** (Element Density) | DOM leaf elements per vh | Modern SaaS baseline **60–120 / vh**; replica within **±20%** of target | Replica **40** vs target **95** → instant template look |
| **TSS** (Type Scale Spread) | H1 `font-size` ÷ body `font-size` | Modern SaaS **4.5–6.5** (editorial sites often **3.0–4.0**). Replica vs target **Δ ≤ 0.5** | Replica **3.2** vs target **5.8** → flat talk, no hierarchy |

## Hard gates (runtime — v5)

| Gate | Metric | Pass threshold | Fail example |
|------|--------|----------------|--------------|
| **SLR** (Scroll-Length Ratio) | `replica.maxScroll / target.maxScroll` | **≥ 0.85** unless GAPS waiver with measured % | haoqi V4 pre-fix: **0.52** (6.4k / 12.3k) — IMR still passed |
| **Canvas / theater** | `runtime.json.canvasCount` vs replica + **continuous** pointer delta on theater nodes | WebGL **or** CSS+pointer continuous reactivity **or** explicit defer | Ordinary button `:hover` must **not** clear this |
| **Scroll states** | Distinct broad-spectrum samples @ 0/25/50/75/100% | Long pages (`maxScroll≥4000`): **≥2** distinct primary fingerprints | haoqi-only field sampling false-negatives GSAP/Three tunnels |
| **Replica-only motion** | Undeclared cursor-trail / stagger-intro / `.magnetic` | Absent **or** listed as sharp edge in SIGNAL | Motion Everywhere false progress |
| **Behavior blockers** | `behavior-diff.json.blockers` | **Empty** or each listed in GAPS with pass criterion | `["canvas","scroll-length"]` after Loop 4 |

## Soft gate

| Gate | Metric | Pass threshold | Fail example |
|------|--------|----------------|--------------|
| **Rhythm** | Adjacent-section IMR delta sequence | Visual match + optional DTW distance on IMR series | Target `low-high-low-high`; replica `low-mid-mid-mid` → no pulse |

Rhythm fails rarely block ship alone, but explain why a page with "correct" average IMR still feels dead.

---

## How to measure (`audit.py`)

```bash
# Ink-mass: section bands or auto-split vs target screenshot
python3 scripts/audit.py --imr target.png replica.png --tolerance 8

# Element density: live or local replica URL
python3 scripts/audit.py --density https://replica.local

# Type scale: computed H1 / body (and optional H2 / button)
python3 scripts/audit.py --typescale https://replica.local

# Rhythm: IMR sequence + DTW vs target sequence
python3 scripts/audit.py --rhythm replica.png --bands 5 --target-imr-series path/to/target-series.json

# Scroll-length (hard gate)
python3 scripts/audit.py --scroll-length recon/offsets.json https://replica.local --min-ratio 0.85

# Behavior / theater parity (hard gate) — offline default
python3 scripts/audit.py --behavior-offline recon/runtime.json https://replica.local \
  --signal docs/SIGNAL.md --out recon/behavior-diff.json
```

Interpret:
- `--imr` prints per-band IMR + Δ heatmap; any P0 band with Δ > 8% → Loop 3 not done
- `--density` prints leaves/vh; flag if outside ±20% of target or outside 60–120 SaaS baseline
- `--typescale` prints TSS; flag if outside target band or Δ > 0.5
- `--scroll-length` FAIL if ratio < 0.85 without waiver (Failure Gallery J)
- `--behavior-offline` FAIL if `blockers` non-empty (Failure Gallery I); prefer over live `--behavior`
- `--rhythm` advisory: large DTW → reconsider section order / empty bands

Human companion (cheap): blur both screenshots to ~10px — dark/light masses should still align. If the replica looks empty after blur, IMR will fail too. **Then load the live page and move the mouse / scroll** — if nothing changes, Behavior fails even when blur passes.

---

## Generic-SaaS Sniff Test (loop-gate)

At every Loop 3+ exit:

1. Cover the wordmark / logo area on the replica.
2. Ask: could this still be confused with the **anti-reference** (Two-Reference Rule), or with a generic "AI SaaS template"?
3. If yes → fail the gate even when numbers pass. Check Failure Gallery B/C and copy bans in `prompts/hero-copy-rewrite.md`.

Sniff test outranks "looks nice." Numbers catch empty; sniff catches Sheeran-mean; **behavior gates catch dead theater**.

---

## Cut strategies (opportunity cost)

Fidelity improves faster by **removing** than by decorating:

1. **Remove a section before adding one.** Blur-match / IMR rhythm is about pulse, not section count.
2. **Two mocks at ~90% beat four at ~25%.** Finish hero + densest platform tab before spreading effort.
3. **Text hits uncanny valley before pixel drift.** Fix copy before chasing ±2px.
4. **Lengthen scroll before polishing pixels** when SLR fails — haoqi V4.1: tunnel height was the #1 gap, not another IMR band.

---

## Two-Reference Rule (inputs to this rubric)

Before Loop 1: positive target + anti-reference + **3 sharp edges** to keep. Those edges are Loop 4 goals; IMR/ED/TSS prove the body is dense enough to carry them; SLR/behavior prove the body is **alive** enough to carry them.
