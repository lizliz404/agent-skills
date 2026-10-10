# Shadcn/ui DESIGN.md adapter

## Source and evidence

- Announcement: https://x.com/shadcn/status/2108574564586332615 (2026-10-09).
  Says the skill chooses a preset then builds colors, tokens, type scale,
  elevation, primitives and blocks from DESIGN.md.
- Primary skill: https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/SKILL.md
- Design-system workflow:
  https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/design-system.md
- Showcase patterns:
  https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/design-system-page.md
- Install/context documentation: https://ui.shadcn.com/docs/skills

Reviewed 2026-10-10. Exa could not extract the X post and a real-browser attempt
returned an empty page; the exact announcement text was retrieved through the
FxTwitter mirror. The official upstream skill/workflow documents were read
separately. The post is discovery evidence, not a guarantee of CLI/runtime
behavior. Upstream commands were **not executed** during this reference update;
check current docs and installed versions when implementing.

## Primary-practice cross-check

Latest open-search synthesis and production follow-up:
[current-practice.md](current-practice.md), including Atlassian's June DESIGN.md
trade-offs and September shared-content CLI experiment.

Reviewed 2026-10-10, with different sources serving different jobs:

| Primary source | Observed guidance | Adaptation in this skill |
|---|---|---|
| [Google spec](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) | Optional YAML plus rationale; relevant sections in canonical order; typed values/refs; sections may be omitted | Preserve precision and rationale. Compact mode is allowed; no line-count gate. Full systems retain applicable coverage |
| [Shadcn workflow](https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/design-system.md) | Preset geometry, token mapping, shared variant recipes, showcase and browser checks | Follow this implementation foundation; full showcase when requested, incremental slice for existing-product changes |
| [Carbon color tokens](https://carbondesignsystem.com/guidelines/color/tokens/) and [components](https://carbondesignsystem.com/components/overview/) | Tokens specify roles/states/layers; reusable components solve defined UI problems consistently | Semantic roles before arbitrary swatches, shared component variants before call-site restyling |
| [Atlassian tokens](https://atlassian.design/foundations/tokens/) | Tokens name/store design decisions as a single source | Explicit numeric ownership and consistent semantic consumption |
| [Anthropic Skills engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) | Progressive disclosure; start with representative evaluations; improve from observed usage | Small entry map, deeper references on demand, scope scenarios and evidence-led iteration |

These are primary practices, not a universal ranking of “industry best.”
No source above establishes that a 400-line document is bad or that shorter is
always better. The bundled corpus is valuable for complete systems; its historical
length must not substitute for decision coverage or real UI acceptance. Do not
wholesale shrink existing good contracts during an unrelated incremental edit.

Google currently makes frontmatter optional in its full spec; README introduces
YAML + prose as the normal structured format. Treat YAML as the interoperable
token layer when needed, not an obligation to maintain a second set of CSS values.
If DESIGN.md tokens are canonical, declare a generated/synchronized code direction.
If runtime tokens are canonical, document that explicitly and avoid contradictory
manually maintained snapshots.

## What belongs here, not in each project DESIGN.md

The reusable method: **foundation → roles → variants → composition → verification**.
Project DESIGN.md records the chosen foundation, token ownership, distinguishing
rules and exceptions. It need not repeat command references or component catalogs.
Link to this adapter from the owning skill; do not create a separate competing
skill or vendor the upstream source.

## Adapted workflow

1. **Detect, don't replace.** Read `components.json`, the package manager, installed
   UI files and actual CSS source. When a CLI query is useful, use the project's
   runner for `shadcn info --json`; inspect `base`, `style`, `iconLibrary`, aliases,
   resolved paths and `tailwindCssFile`. Radix `asChild` and Base UI `render` are
   not interchangeable. Existing components may predate current upstream APIs.
2. **Preset is a foundation, not final taste.** For a new project pick one style
   closest to density/radius/control geometry, then rebind brand roles. For an
   existing project keep its foundation. A style/preset switch needs explicit
   authorization; no default re-init, dependency upgrade or `apply` overwrite.
3. **Map semantic roles to the existing numeric source.** Canvas → background;
   ink → foreground; CTA/on-CTA → primary/primary-foreground; card/popover pair;
   descriptive ink → muted-foreground; hover wash → accent; border/input/focus;
   sidebar roles. Add only needed hover/pressed tokens. Preserve existing color
   representation and independent status/platform/chart/media colors.
   - Prefer current CSS-backed ownership over duplicating hex snapshots in YAML.
   - Follow the existing imported token-file structure; upstream's “edit only
     tailwindCssFile” means centralization, not deleting established modules.
   - Register needed custom roles in existing Tailwind theme wiring. Resolve aliases
     inside nested theme scopes; test first-paint cascade if colors do not propagate.
4. **Style shared variants, not every call site.** Reuse Button default/secondary/
   outline/ghost/link, Card, fields and navigation recipes. Keep variant APIs.
   Match radius/elevation roles and align button/field control heights when changed.
   Keep headline fonts distinct from small component titles where necessary.
   Use documented substitutes for unavailable fonts; don't install fonts speculatively.
5. **Prove it on one real screen first.** Show a common composition in actual copy.
   For changed primitives check applicable default/hover/focus/pressed/disabled,
   loading or invalid states. Include the relevant awkward case (long text, empty,
   error, missing image), not every state × variant × size permutation.
6. **Check and stop.** Inspect narrow overflow, console errors, accessible focus and
   measured foreground/surface contrast when affected. Motion checks include
   no-pointer autoplay, pointer takeover/resume and reduced motion. No perpetual
   polish loop: fix observed mismatches, deliver, wait for feedback.

## Optional full showcase

Upstream `design-system.md` scaffolds a new app, installs **all** components and
builds a full design-system page. That is useful **only when a library/showcase is
the requested deliverable**. It is not the default for a product color adjustment.

When that deliverable is explicitly requested, read current upstream guidance:
foundations first, surface/foreground pairs with contrast, type specimens,
variant/state matrices, real triggers for overlays, do/don't pairs and a realistic
example screen. Reuse existing preview infrastructure when available. Do not add
production routes, all components or a dark-mode switch just to satisfy a sample.

## Representative evaluation cases

Declared acceptance scenarios, **not executed agent evaluations**. Use them to
check whether this revision improves behavior before claiming measured savings:

| Task | Expected behavior | Failure to catch |
|---|---|---|
| Change one brand color in an existing app | Inspect existing token ownership, update relevant aliases/states and targeted screen | Re-init, add-all, rewrite the full contract or recolor status/media |
| Build a complete new visual system from a supplied DESIGN.md | Follow preset → precise role mapping → shared variants → requested component/state coverage → realistic screen | Vague short prose with missing type/radius/focus/state/CJK rules |
| Improve a mature 600-line contract | Keep useful coverage, resolve stale/duplicate decisions against code and primary docs | Declare it bad solely for length, or pad to hit a rubric |
| Add an interactive figure | Read native API, verify autoplay/hover/reduced motion and layout | Hand-build geometry/timers before checking existing capability |

Evaluate on representative tasks: can the agent find the source, implement the
intended states, avoid unrelated writes and stop at the agreed scope? Record
actual mismatches and improve the skill from those, not an unmeasured token claim.

## Execution boundaries

- This reference changes no app and installs no package.
- CLI `init`, `apply`, `add`, all-component installs and base migrations are writes;
  scope/authorization and diff review are required before execution.
- Upstream includes rules for current components that older projects may not have.
  Read actual docs/source before using new fields, chat primitives or overlay APIs.
- Document length is neither a pass nor a fail. Preserve full-system rigor where
  needed; incremental work updates affected decisions without rebuilding the system.
  Success is consistent UI, usable guidance and cheap future edits.
