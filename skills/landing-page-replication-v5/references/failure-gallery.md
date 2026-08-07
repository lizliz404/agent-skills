# When to load: Density/polish/behavior "looks fine" but feels wrong; before declaring Loop 3/4/5 done
# Precondition: Screenshots of replica (and ideally target) + runtime.json when theater-class
# Output: Named syndrome + fix; re-run taste/runtime gates after fix

# Failure Gallery

Text diagnoses of "looks right but isn't." Pair with `taste-rubric.md`. When you have screenshots, paste them next to the matching syndrome in your project `docs/GAPS.md` or `docs/gap-analysis.md`.

---

## A — Empty Cards Syndrome

**Symptom:** Clean, spacious, "premium" — and empty. Hero IMR often **~12%** vs target **~28%**.  
**Cause:** Loop 3 skipped; icon + two lines of lorem inside large cards.  
**Fix:** Build `WindowChrome` product UI (tables/charts/chips). Re-run `audit.py --imr`. Cut a weak section before adding more empty cards.

## B — Rainbow Section Syndrome

**Symptom:** Every section invents a new palette. Reads like Zapier-era marketing collage.  
**Anti-ref cue:** Busy multi-hue SaaS 2021.  
**Fix:** Lock ink/paper/line/accent in SIGNAL.md; semantic colors only inside mocks (success/warn). Generic-SaaS sniff vs anti-reference.

## C — Glow Blur Cliché

**Symptom:** Purple/indigo radial blobs behind hero; "AI aura."  
**Anti-ref cue:** 2023–24 AI template cluster.  
**Fix:** Match target atmosphere. If target has no glow, delete yours. Atmosphere ≠ purple blur.

## D — Perfect Grid Death

**Symptom:** `grid-cols-3` equal cards, no overlap, no collage depth.  
**Cause:** Template muscle memory; target is often asymmetric collage.  
**Fix:** Overlap windows, rotate secondary cards slightly, vary sizes. One primary sharp window.

## E — Font Metric Drift

**Symptom:** Hierarchy "almost" matches but page feels taller/shorter; TSS OK but rhythm off.  
**Cause:** Libre substitute without `size-adjust` / ascent overrides.  
**Fix:** `metric-align-fonts.py` + `references/ip-and-fonts.md`.

## F — Chrome Overuse

**Symptom:** Every section gets a full `WindowChrome` traffic-light frame → chrome feels cheap.  
**Fix:** Chrome for product theater only. Feature cards / quotes / logo clouds stay frameless.

## G — Motion Everywhere

**Symptom:** Impressive with motion on; dead or seizure-inducing with `prefers-reduced-motion`. Also: **replica-only** flourishes (cursor trails, intro staggers) not on target — false progress.  
**Fix:** Cap idle loops (one per primary mock). Reduced-motion → final reveal state, no infinite bob. Log replica-only motion as intentional sharp edge or delete. **v5 machine gate:** `audit.py --replica-only` / `--behavior-offline` blocker `replica-only-motion` when undeclared.

## H — Real-Data Uncanny

**Symptom:** Fake metrics too round: `100%, 90%, 80%` or `Nexus Flow Analytics`.  
**Fix:** Slightly messy credible numbers (`87.3%, 71%, 68.9%`). Specific verbs + objects. See `prompts/hero-copy-rewrite.md`.

## I — Static Snapshot Syndrome (v4 — critical; v5 probe tightened)

**Symptom:** IMR passes on hero PNG; `recon/assets.json` or `runtime.json` shows `canvases.length > 0` / `webgl: true`; replica has `canvasCount === 0` and pointer path does not produce **continuous** theater-node delta. Page is a frozen study, not a runtime peer.  
**Cause:** Loop 3 optimized ink mass on screenshots; Loop 5 (v3 polish) was nav/tabs-centric and never gated theater runtime. v4 pointer probe could false-positive on ordinary `:hover`. Proven on haoqi.design study (stress-test 2026-07-23).  
**Fix:** Block Loop 5 exit. Declare theater strategy in Interaction Contract: implement WebGL, CSS+pointer stand-in with continuous reactivity, or explicit P0/P1 defer in `GAPS.md` with pass criterion. Re-run:

```bash
python3 scripts/audit.py --behavior-offline recon/runtime.json {replica_url} \
  --signal docs/SIGNAL.md --out recon/behavior-diff.json
```

`blockers` containing `canvas` / `webgl` / `pointer-theater` → not done.

## J — Scroll Compress Syndrome (v4 — critical)

**Symptom:** Replica feels "done" but journey to contact is ~40–60% shorter. `offsets.json maxScroll` (e.g. 12,319) vs replica ~6,400. Mid-scroll tunnel / sticky field disappears. IMR on hero/contact still passes.  
**Cause:** No scroll-length gate in v3; sticky tunnel height read from DOM (`height: 7200px`) never compared.  
**Fix:** Hard gate `replica.maxScroll / target.maxScroll ≥ 0.85` unless `docs/GAPS.md` records measured ratio + rationale.

```bash
python3 scripts/audit.py --scroll-length recon/offsets.json {replica_url} --min-ratio 0.85
```

Lengthen scroll tunnel / sticky wrappers before polish. Highest-impact haoqi V4.1 fix was 6,400 → 12,458 px — not another screenshot tolerance tweak.

## K — Inner Scroller Syndrome (v4)

**Symptom:** `document.documentElement.scrollHeight ≈ viewport` but target scrolls inside `.lenis` / inner wrapper. Replica scrolls the document; tunnel length looks OK on paper but journey is wrong. `runtime.json` flags `INNER_SCROLLER` / `scrollContainers[0].maxScroll` ≫ doc scroll.  
**Cause:** Loop 2 reserved doc-level height only; Lenis wrapper never wired. Scroll-length ratio may pass on wrong scroller.  
**Fix:** Match primary scroller from `runtime.json.scrollContainers[0]`. Interaction Contract row for scroll container must name inner selector. Re-run `--behavior` + manual scroll on inner node.

## L — Tunnel Hollow Syndrome (v4; v5 sampling broadened)

**Symptom:** Scroll length ratio passes (≥0.85) but mid-scroll feels empty. `behavior-diff.json` shows `scroll-states.distinctStates < 2` on long pages. Sticky field is spacer-only; no transform/opacity/filter drift across scroll fractions.  
**Cause:** Height copied without scroll-linked state machine (IO / CSS vars / scene morph / GSAP / Three progress). Gallery J fixed length; Gallery L fixes **content inside** the tunnel.  
**Fix:** Implement ≥2 distinct scroll states. v5 probes broad-spectrum `transform`/`opacity`/`filter` (body class/bg fallback only) — do not rely on haoqi-only `--tunnel-progress`. Block Loop 5 when `t_max ≥ 4000` and `distinctStates < 2`.

---

## Quick triage

| You notice… | Check syndrome |
|-------------|----------------|
| Blur looks empty | A |
| Too colorful | B / C |
| Too tidy / template | D / F |
| Tall/short after font swap | E |
| Dead with reduced motion / fake motion | G |
| Feels fake before you read UI | H |
| Beautiful stills, dead live / no canvas | **I** |
| Page ends too soon / no tunnel | **J** |
| Doc doesn't scroll; inner scroller only | **K** |
| Long page but one scroll "state" | **L** |
