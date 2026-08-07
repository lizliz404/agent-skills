# When to load: CJK independent sites / 独立站 / bilingual brand pages
# Precondition: Target primarily CJK or mixed CJK+Latin
# Output: Type + layout adjustments; OG/WeChat notes

# Domain fork: CJK independent site

> Evidence tier: Templated (synthesized, not build-tested)

## Type

- Latin TSS bands (4.5–6.5) **do not** transfer cleanly to CJK — CJK display sizes are often closer to body; judge hierarchy by weight/color/tracking more than size ratio
- Prefer fonts with real CJK coverage (Noto Sans/Serif SC/JP/KR, Source Han). Do not pair Latin Inter with a system CJK fallback and call it done without checking wrap rhythm
- Metric-align Latin substitutes; for CJK, verify line-height visually (IMR still useful)

## Capture

- Webflow / Shopify / Framer common — assume Capture Router non-curl paths
- WeChat / Open Graph cards: square or 2.35:1 crops differ; screenshot share cards if the target invests there

## Copy

- Do not trust diffusion models for final CJK marketing copy (precision fails)
- Ban Engrish SaaS calques; rewrite in natural CJK or hire edit
- `prompts/hero-copy-rewrite.md` ban-list is English-centric — add local cliché bans per market

## Density

- Product theater still beats empty cards
- Avoid US SaaS chrome cargo-cult on tea/craft/DTC brands — match category anti-reference carefully

## Ship posture

Composite references from the **same market language**, not only US SaaS leaders.
