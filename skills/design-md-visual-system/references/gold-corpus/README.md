# Gold corpus (bundled mirror)

34 implementation-grade `design.md` files, one per template in the
**beautiful-html-templates** deck library. These are the reference examples the
skill's "Bar" and anatomy are measured against.

## Source & refresh

- Public mirror: `github.com/zarazhangrui/beautiful-html-templates` → `templates/*/design.md`
- Mirrored: 2026-08-05 (repo HEAD `e5e204f`). Refresh: clone/pull the public
  mirror, then copy `templates/*/design.md` back over `gold-corpus/*/design.md`.

## Structure standard (verified across all 34)

Every file carries: YAML frontmatter with `description:` + `colors` +
`color-aliases` + role `typography` + `spacing` (+ `canvas` where a fixed stage)
+ `components` (each with `description:`), and all 8 body sections: Overview,
Colors, Typography, Layout, Do's and Don'ts, CJK & International, Iteration
Guide, Known Gaps. Lines 463–714. Component keys 43–80.

## Lint status (npx @google/design.md, 2026-08-05)

- **0 errors (10)**: creative-mode, editorial-forest, editorial-tri-tone,
  emerald-editorial, neo-grid-bold, peoples-platform, pin-and-paper,
  pink-script, soft-editorial, stencil-tablet — use these as the lint-clean canaries.
- **Errors elsewhere are one category**: `clamp()` / `vw` responsive font sizes
  (CLI schema accepts fixed dimensions only). Intentional for responsive
  templates (cobalt-grid, long-table, sakura-chroma, biennale-yellow, coral,
  bold-poster …) — agent-readable, but lost on `export`.
- **Warnings everywhere (44–145/file)**: schema-extension vocabulary
  (`description`, `background`, `borderRadius`, `position`, `fontStyle`,
  `textTransform` …), orphaned colors, missing `primary` — same profile as
  soft-editorial. Do not present any corpus file as a lint-clean example except
  the 10 canaries above.

## Verification level (honest)

All 34 passed structural verification (frontmatter description, 8/8 sections,
component counts, lint profile). Deep-read: soft-editorial (full), signal,
monochrome, mat, bold-poster (substantial reads). Treat unread ones as
structure-verified, not prose-audited.
