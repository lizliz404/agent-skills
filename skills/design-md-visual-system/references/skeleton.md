# Compact contract (incremental / small-project scope)

Not a replacement for a good complete system. For incremental work preserve the
existing contract and update only affected decisions. For a new small project,
fill applicable decisions from code and expand when scope requires it. No minimum
length. Link runtime values instead of duplicating them.
This is a prose/CSS-backed contract, **not** a claim of Google YAML conformance.

```markdown
# DESIGN.md — <system name>

## Source of truth
- Palette/semantic tokens: `<actual path>`.
- Typography/materials/layout: `<actual path>`.
- Shared component variants: `<actual path>`.
- This file owns decisions; code owns runtime numbers. Git owns history.

## Direction and defaults
<One paragraph: audience, density, surface/ink/accent policy and what looks wrong.>
- Surfaces use `<semantic roles>`; data/chrome material boundary: `<rule>`.
- Typography uses `<body/display/metadata roles>`; CJK pairing if relevant.
- Radius/depth/control density follow `<existing tokens/variants>`.

## Distinguishing rules
1. When `<element>` appears, use `<specific treatment>`.
2. `<Another necessary rule, if any>`.

## Boundaries
- Brand color changes do not recolor `<status/platform/data/media roles>`.
- Responsive layout: `<layout rule, not arbitrary font inflation>`.
- Motion: `<native behavior and reduced-motion rule, if applicable>`.
- Do not `<the few mistakes this project is likely to make>`.

## Change and acceptance
- Change `<source>` → semantic aliases → shared variants → consumers.
- Check `<representative screen/state>` at `<relevant viewport>`.
- Known gaps: `<real limitations only; omit if none>`.
```

## Portable YAML/export mode (opt-in)

Only when a template consumer, design interchange or explicit format requirement
needs it. Use a relevant `gold-corpus/<name>/design.md` plus
[anatomy-and-patterns.md](anatomy-and-patterns.md), trimming deck-only and irrelevant
sections. Include needed tokens, descriptions and defaults. Do not pad to corpus
length or invent a second numeric source.

- If Markdown/YAML is canonical, declare generated CSS/DTCG direction explicitly.
- If runtime CSS is canonical, exported snapshots must say so and are not manually
  maintained as a second truth.
- Lint Google-shaped files with `npx -y @google/design.md lint DESIGN.md`; export
  only when a consumer exists. Do not run that schema gate on deliberate short mode.
- Shadcn implementation: [shadcn-design-system.md](shadcn-design-system.md).
