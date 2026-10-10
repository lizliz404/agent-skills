---
name: design-md-visual-system
description: >-
  Write, improve or audit coding-agent DESIGN.md visual systems using Google
  DESIGN.md and shadcn/ui practices. Scope incremental edits separately from
  complete design-system delivery: reuse presets, semantic tokens, component
  variants and visual verification. Preserve design rationale, CJK, iteration
  rules and real gaps; load deep references on demand. Not for brand/OG/image briefs.
version: 1.2.0
author: Liz (lizliz.xyz)
license: MIT
metadata:
  hermes:
    tags: [design-md, visual-system, design-tokens, ui, coding-agents, shadcn, stitch]
    related_skills: [design-md, design-brief-authoring, design-brief-for-image-gen]
disable-model-invocation: true
---

# DESIGN.md Visual System

A persistent implementation contract: precise tokens/roles plus the judgment that
values alone cannot convey. Follow primary expert workflows before inventing a
new one. Match coverage to the deliverable; neither length nor brevity is a quality
metric. The existing gold corpus remains valuable for complete systems.

Reusable methods live in this skill; concrete decisions live in one project
`DESIGN.md`; Git carries history. Improve incrementally from observed failures,
not by declaring previous approaches wrong merely because they are extensive.

## Choose the job and scope

- **UI visual system (Genre A):** this skill.
- **Brand / OG / image-generation brief (Genre B):** use the design-brief skill;
  preserve an existing brief rather than replacing it with UI rules.
- **Incremental product work:** read the existing contract and relevant runtime
  sources; change only affected decisions. Preserve useful full-system sections.
  A new small project can start with the compact skeleton, then grow as needed.
- **Complete visual system / portable template:** use the corpus anatomy, token
  roles, Defaults, conditional Signature Treatments, responsive/CJK, Iteration
  and Known Gaps. Google YAML + prose is a strong interoperable foundation; do
  not omit essential coverage just to be short. Read [anatomy](references/anatomy-and-patterns.md).
- **Component library / showcase:** follow upstream shadcn full workflow when
  this is the requested output. State coverage and validate its component/state
  examples; it is not the default artifact for an incremental color change.
- **Export:** only when an interchange/build consumer needs it. Google spec
  permits optional YAML and omitted irrelevant sections; no minimum line count.

Ask only if ambiguity changes the artifact or implementation. Do not create a
second competing visual-system document. If a distinct distribution brief is
needed, name its job explicitly and keep it out of the UI token contract.

## Coverage before length

For incremental/small-project scope use [skeleton](references/skeleton.md). For a
complete system use the anatomy/corpus. Both must carry applicable decisions:

1. **Source of truth:** runtime token file, component source and any intentional
   numeric ownership/export rule.
2. **Direction + density:** one short paragraph, 1–3 distinguishing treatments;
   describe what would look wrong.
3. **Roles + defaults:** surface/ink/brand, type roles, spacing/radius/depth;
   refer to code rather than recopying values.
4. **Hard boundaries:** where accents/materials may appear, what stays independent
   (status/platform/chart/media), responsive and reduced-motion behavior, relevant
   CJK handling.
5. **Change + acceptance:** where to edit, a representative screen/state to check,
   genuine gaps. No invented debts or rubric boilerplate.

Short is not vague: “warm surface” alone is insufficient; “canvas uses
`--background` from `src/theme-tokens.css`, data cards use `--card`, no blur on data”
is actionable. A precise paragraph can replace a duplicated table.

## Workflow

1. **Read current evidence first.** Existing DESIGN.md, CSS tokens, component
   variants/config, and at most one matching reference. Preserve stack/base,
   naming and working behavior. Reuse existing color research and templates.
2. **Reuse a foundation.** For a new UI choose one preset by geometry/density;
   for an existing UI retain its foundation unless a switch is authorized. Say
   the choice and reason in one line; do not compare every style.
3. **Write/update the scoped contract.** Preserve the old skill's strengths:
   explicit density, Defaults, conditional Signature Treatments, CJK when relevant,
   Iteration and Known Gaps. For incremental work update only affected decisions.
   For a full system cover these systematically; avoid vague vibe paragraphs.
4. **Reuse implementation, then map roles/variants.** Check the existing import
   and API before translating appearance recipes: a production Button should be
   used, not rebuilt from prose. Primitive → semantic alias → component.
   Centralize values and states; reuse shared Button/Card/Input variants rather
   than repeating raw colors/styles at call sites. Existing runtime token files
   remain canonical; no Markdown-to-CSS engine by default.
5. **If implementing, prove composition.** Incremental work uses a representative
   real page/state or existing preview. Complete library/showcase work follows
   the upstream foundations → component states → recipes → example-screen
   coverage. No unsolicited theme switcher or framework migration.
6. **Verify proportionately.** Inspect the changed state, narrow layout and actual
   visual output; contrast/focus when their colors change; autoplay + hover +
   reduced motion when adding motion. Use targeted checks, not a ritual full
   suite for documentation or every tiny visual adjustment.
7. **Stop at the agreed acceptance, then improve from evidence.** Deliver when
   the requested scope works, relevant visual intent is shown and observed
   regressions are resolved. Iteration is valuable when driven by a mismatch,
   real feedback or a representative evaluation, not documentation length or
   perpetual polish. Report evidence and unverified gaps without claiming deployment.

## Current practice and upstream follow-up

Read [current practice](references/current-practice.md) when updating this skill,
changing artifact scope or investigating repeated agent drift. Google supplies
the portable format; shadcn supplies implementation mapping; Atlassian's June and
September reports distinguish portable prototypes from implementation-aware
production guidance and show how to evaluate the whole usage chain.

Follow primary sources and actual task traces, not a permanent snapshot of old
research. Refresh after relevant schema/API changes or recurring failures, and
propose a monthly human-owned review for sustained use; no automatic scheduler
or broad search on every small component edit. Do not claim vendor benchmark
savings as our own.

## Shadcn/ui route (optional implementation capability)

For shadcn projects, read [Shadcn DESIGN.md adapter](references/shadcn-design-system.md).
It links to the upstream skill and explains the adapted preset → tokens → variants
→ real-screen path. **Do not copy its full new-app showcase procedure into an
existing product.** Use installed APIs/base and the project's package manager.
No automatic `init`, `apply`, `add --all` or dependency upgrades.

## Portable YAML / export (only when a consumer needs it)

- Start from one relevant bundled [gold corpus](references/gold-corpus/README.md)
  example. Its extensive coverage is useful for full systems; 500–700 lines
  describe examples, not an upstream format requirement.
- Include the token roles and component descriptions the consumer actually uses.
  Preserve useful Defaults, conditional Signatures, CJK, Iteration and Gaps without
  expanding irrelevant sections. Schema requirements may differ from short mode.
- `npx -y @google/design.md lint DESIGN.md` checks Google-shaped documents; it is
  not the gate for a deliberate prose/CSS-backed project contract.
- Export (`css-tailwind`, `json-tailwind`, `dtcg`) only if a build/interchange
  consumer exists. Declare the canonical source and generated direction; never
  create two manually maintained numeric truths.
- [Quality rubric](references/quality-rubric.md) scores decision coverage, not length.

## Pitfalls

- More writing/research/agents is not better design. Do not rerun palette due
  diligence, read all 34 references or keep tuning without a concrete signal.
- CSS primitives and aliases must resolve in the correct theme scope; inherited
  root aliases do not recompute from a descendant primitive override.
- Unlayered first-paint CSS can outrank layered theme rules. Inspect the actual
  cascade before adding another override.
- Official interactive components may already have autoplay/intensity/reduced
  motion. Read their API before inventing timers, geometry or synthetic pointers.
- Width is not zoom. Make layout space wider without inflating unrelated type,
  icons or demos; inspect lower sections, not only a hero screenshot.
- A passed build is not visual acceptance; an offline screenshot is not deployment.
- No CSS palette proves medical eye health.

## Sources / boundaries

- Shadcn primary sources + announcement: [adapter](references/shadcn-design-system.md).
- Cross-checked primary practices and scope decisions: [adapter](references/shadcn-design-system.md#primary-practice-cross-check).
- Google spec: https://github.com/google-labs-code/design.md and
  https://stitch.withgoogle.com/docs/design-md/specification.
- DTCG exchange: https://www.designtokens.org/tr/2025.10/format/.
- Gold corpus: `zarazhangrui/beautiful-html-templates`; use its README for refresh
  and lint-canary limits. Never present a non-canary as lint-clean.
- Assets/research: `lizliz404/design-templates` and `lizliz404/design`; link rather
  than mirror them here. This skill owns the method, projects own the decisions.
