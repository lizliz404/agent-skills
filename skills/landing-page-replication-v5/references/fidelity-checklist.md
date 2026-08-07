# When to load: Every loop exit; gap triage in Loop 5–6
# Precondition: Active loop known
# Output: Checked gates; P0–P3 gap list

# Fidelity checklist

Work top to bottom. Do not pixel-chase before density / IMR / **behavior** pass.

## Loop gates

### After Capture
- [ ] Risk posture chosen; Two-Reference Rule filled (anti-ref + 3 sharp edges)
- [ ] `recon/index.html` + `headers.txt` exist (or manual DevTools note)
- [ ] CSS chunks fetched **or** computed.json for opaque CSS (Framer) **or** N/A documented
- [ ] Screenshots: full page, hero, densest product, nav top + scrolled (≥5); scroll-00…N for long pages
- [ ] `extract-tokens.py` shows fonts (file **or** Google Fonts/Typekit) and ranked hex — not only `--idx`
- [ ] `runtime.json` captured **or** static-no-theater N/A in SIGNAL
- [ ] If `canvasCount > 0`: `WEBGL_THEATER` tagged

### After Signal Sheet
- [ ] Section list matches heading order
- [ ] Type roles + ink/paper/accent with evidence tags
- [ ] Product-theater inventory has surface/canvas counts + scroll budget
- [ ] Micro-pattern backlog ≥3 (≥1 scroll-linked + ≥1 pointer-linked when flagged)
- [ ] **Interaction Contract table** filled (not prose) for every P0 runtime signal
- [ ] Proprietary fonts have substitutes (+ metric-align plan)

### After Skeleton
- [ ] Thumbnail section rhythm matches target
- [ ] Tokens in CSS; shared window/surface primitive exists
- [ ] Copy in data module
- [ ] Wireframe mocks accepted as temporary
- [ ] Scroll budget reserved (spacers/tunnel height from maxScroll)
- [ ] TSS sampled (`audit.py --typescale`) or flagged

### After Density
- [ ] Hero surface count / overlap / theater mass matches reference
- [ ] Tabs/platform show distinct per-tab UI (when present)
- [ ] ≥1 idle/reveal in product mocks (when target has idle)
- [ ] Blur-sniff OR `audit.py --imr` Δ ≤8% on P0 bands
- [ ] ED within ±20% of target when measurable
- [ ] `audit.py --scroll-length … --min-ratio 0.85` PASS **or** GAPS waiver
- [ ] Generic-SaaS sniff vs anti-reference

### After Micro-parity
- [ ] Named backlog done or explicitly deferred
- [ ] Sharp edges 1–3 visible
- [ ] Editorial type role applied where target uses it
- [ ] Active tabs match selected-state convention (when present)
- [ ] No hotlinked target fonts; metrics aligned or N/A
- [ ] No replica-only motion unless intentional sharp edge

### After Behavior (Loop 5)
- [ ] `audit.py --behavior-offline` (default) → `blockers: []` **or** each blocker in GAPS with pass criterion
- [ ] Static Snapshot check: assets/runtime canvas vs replica + **continuous** theater pointer delta
- [ ] Scroll-length ratio ≥ 0.85 or documented
- [ ] Scroll-state count ≥ 2 on long pages (broad-spectrum transform/opacity/filter)
- [ ] Pointer-linked theater proven when capture flagged it (not ordinary `:hover`)
- [ ] `prefers-reduced-motion` kills infinite CSS/WebGL loops
- [ ] Smooth nav when target smooth-scrolls
- [ ] No undeclared `replica-only-motion`

### After Polish (Loop 6)
- [ ] Keyboard focus visible on nav/CTAs
- [ ] Decorative theater `aria-hidden`; real CTAs/headlines semantic outside mocks
- [ ] LCP element identified; density animations do not block it (ship)
- [ ] Lighthouse Performance within ~15 of target mobile (ship)
- [ ] P0 gaps closed; P2/P3 listed not blocking

## Gap priority

| Priority | Criteria | Examples |
|----------|----------|----------|
| **P0 runtime** | Capture flagged WebGL/canvas/scroll-theater; replica absent or inert | `canvasCount` 0 with no stand-in proof; scroll ratio ≪ 0.85; zero scroll states |
| P0 | Breaks identity or core UX | Wrong story order; empty hero (IMR fail); broken nav; wrong ink/paper |
| P1 | First-visit quality | Wireframe mocks; missing dark band; dead tabs; copy uncanny; Lenis→native feel |
| P2 | Close inspection | Serif missing; chart geometry off; shadow soft; font metric drift; signature path-draw |
| P3 | Nice-to-have | Micro-easing, secondary hover, OG meta, live weather API |

## Pixel audit (Loop 6 only, P0 sections)

- Spacing ±2px on hero padding / CTA group
- Type: size, weight, tracking on H1 and primary button
- Color: ink/paper/accent eyedropper
- Shadow: window chrome roughly matching

Do not apply ±2px globally before P0/P1 **and behavior blockers** are green.
