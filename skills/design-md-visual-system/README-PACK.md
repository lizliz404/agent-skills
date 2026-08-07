# DESIGN.md Visual System — skill pack

Implementation-grade **Genre A** DESIGN.md authoring for coding agents: YAML tokens + prose (Signature Treatments, Defaults, Do/Don't, CJK, Iteration, Known Gaps).

## Contents

```
design-md-visual-system/
├── SKILL.md
├── README-PACK.md          ← this file
└── references/
    ├── anatomy-and-patterns.md
    ├── quality-rubric.md
    ├── skeleton.md
    └── gold-corpus/        ← 34 example design.md files + README
```

## Install

Unpack into your agent skills directory as `design-md-visual-system/` (Hermes / Claude Code / Cursor skills folder — match your runtime).

## Gold corpus (bundled)

All 34 implementation-grade `design.md` files ship in this pack under
`references/gold-corpus/<template>/` (one per beautiful-html-templates template,
463–714 lines each, all with the 8 standard body sections). Mirrored 2026-08-05
from the local tool / public repo
**`github.com/zarazhangrui/beautiful-html-templates`** (repo HEAD `e5e204f`).

- **Start with** `references/gold-corpus/soft-editorial/design.md` — the canonical example.
- **Lint canaries** (0 errors with `npx @google/design.md lint`): creative-mode,
  editorial-forest, editorial-tri-tone, emerald-editorial, neo-grid-bold,
  peoples-platform, pin-and-paper, pink-script, soft-editorial, stencil-tablet.
- **Refresh + lint profile**: see `references/gold-corpus/README.md`.

## CLI

```bash
npx -y @google/design.md lint DESIGN.md
npx -y @google/design.md export --format dtcg DESIGN.md
npx -y @google/design.md export --format css-tailwind DESIGN.md
```

Upstream format: https://github.com/google-labs-code/design.md

## Genre boundary

- **A (this skill):** UI visual system agents can implement.
- **B:** Brand / OG / image-gen briefs — use separate design-brief skills; do not collapse into one thin file.

## Version

Skill pack `1.0.0` (see SKILL.md frontmatter). Google DESIGN.md file `version:` fields typically remain `alpha` per upstream format.
