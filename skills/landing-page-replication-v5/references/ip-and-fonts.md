# When to load: Font substitutes, trade-dress questions, or vertical-rhythm drift after font swap
# Precondition: Target face identified (filename / Google Fonts / Typekit / computed)
# Output: Substitute table + optional @font-face metric overrides

# IP boundaries and font metric alignment

Not legal advice. Tool-design defaults that keep replicas out of the dumbest failure modes.

## What you may replicate

- Layout grammar: section order *as genre convention*, density, color **roles**, radius/shadow language, component shapes
- Motion *ideas*: sticky morph, tab swap, idle highlight — reimplemented, not copied as proprietary animation IP dumps when avoidable

## What you must not copy

| Asset | Why |
|-------|-----|
| Logos, custom illustrations, proprietary brand imagery | Copyright |
| Target `/_next/static/media/*.woff2` (or any hotlinked font) | License + ToS |
| Hero / marketing **copy** verbatim ("Welcome to agentic revenue.") | Copyright |
| Signature visual metaphors of a **named single competitor** when shipping a commercial rival | Trade dress / passing-off grey zone — use composite reference (risk posture **Ship**) |

Genre conventions (hero + logo cloud + tabs + CTA) are generally unprotected. One-to-one cloning of a competitor's *signature* product-theater metaphors (e.g. a radar that has become that product's visual ID) is the risky zone — especially same market, same buyers.

## Font substitution table (starting points)

| Proprietary / common target | Libre substitute | Notes |
|----------------------------|------------------|-------|
| Inter Display | Inter Tight / Inter | Adjust weight + tracking |
| Inter | Inter | Self-host via fontsource |
| Tiempos Text | Source Serif 4 / Crimson Pro | Always metric-align |
| Geist | Inter / Geist if licensed | Check license |
| Satoshi / Cabinet Grotesk | Plus Jakarta Sans / Manrope | Check metrics |
| GT America / similar | Inter Tight | Vision-check weight |
| Georgia / system serif editorial | Source Serif 4 | |

## Why metric alignment matters

Swapping names without metrics shifts vertical rhythm **3–7%**. That alone can fail blur-sniff / IMR rhythm even when layout is correct.

```bash
python3 scripts/metric-align-fonts.py \
  --target "Tiempos Text" \
  --substitute "Source Serif 4"
```

Typical output shape:

```css
@font-face {
  font-family: "Tiempos Sub";
  src: url("...") format("woff2");
  size-adjust: 96.3%;
  ascent-override: 89%;
  descent-override: 24%;
  line-gap-override: 0%;
}
```

Sources: Fontsource metric tables when available; otherwise measure both faces in Chromium and solve for `size-adjust` so x-height / body line box matches.

## Copy layer (see also prompts/hero-copy-rewrite.md)

Even with perfect pixels, verbatim target headlines or AI-SaaS placeholder names destroy credibility and raise IP risk. Rewrite; do not paste.

## Fake data / logo cloud (product theater)

Synthetic customers in `data.ts` (logo cloud, testimonial company names, favicon tiles) can unintentionally collide with real brands — especially in cross-border e-commerce. Prefer obviously fictional marks, or verify non-collision against the target market.

In SIGNAL.md / GAPS.md, label synthetic logo clouds explicitly, e.g.:

```text
logo_cloud: synthetic, verified non-colliding with real brands
```

Do not paste a competitor's customer list or recognizable wordmarks into the replica.
