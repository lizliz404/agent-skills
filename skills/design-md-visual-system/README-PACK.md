# DESIGN.md Visual System — skill pack

Implementation-grade **Genre A** DESIGN.md authoring for coding agents, grounded in Google DESIGN.md and shadcn/ui practice. Incremental product work updates affected decisions; complete systems retain token roles, rationale, Defaults, Signatures, CJK, Iteration and Gaps. Reuse foundations and shared variants; verify scope-relevant UI. Neither document length nor brevity is a quality metric.

## Contents

```
design-md-visual-system/
├── SKILL.md
├── README-PACK.md          ← this file
└── references/
    ├── anatomy-and-patterns.md
    ├── quality-rubric.md
    ├── skeleton.md        ← short default contract
    ├── shadcn-design-system.md ← upstream method + existing-product boundaries
    ├── current-practice.md ← dated primary evidence + maintenance/evaluation route
    └── gold-corpus/        ← 34 example design.md files + README
```

## Install

Unpack into your agent skills directory as `design-md-visual-system/` (Hermes / Claude Code / Cursor skills folder — match your runtime).

## Gold corpus (bundled)

All 34 reference `design.md` files ship in this pack under
`references/gold-corpus/<template>/` (one per beautiful-html-templates template,
463–714 lines each). Their historical length is not a minimum or acceptance gate;
load one matching example only when portable/template mode needs it. Mirrored 2026-08-05
from the local tool / public repo
**`github.com/zarazhangrui/beautiful-html-templates`** (repo HEAD `e5e204f`).

- **Start with** `references/gold-corpus/soft-editorial/design.md` — the canonical example.
- **Lint canaries** (0 errors with `npx @google/design.md lint`): creative-mode,
  editorial-forest, editorial-tri-tone, emerald-editorial, neo-grid-bold,
  peoples-platform, pin-and-paper, pink-script, soft-editorial, stencil-tablet.
- **Refresh + lint profile**: see `references/gold-corpus/README.md`.

## CLI (optional portable mode)

Use only when claiming Google format conformance or an export consumer exists;
short prose/CSS-backed contracts do not need this schema gate.

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

Skill pack `1.2.0` (see SKILL.md frontmatter). Google DESIGN.md file `version:` fields typically remain `alpha` in portable mode; short project contracts need no artificial version/frontmatter.
