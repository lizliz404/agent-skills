# DESIGN.md practice: portability, implementation and maintenance

Last reviewed: 2026-10-10. Discovery used Exa across format/implementation,
production trade-offs and recent shadcn practices, then primary-source reading.
This is a scoped synthesis, not a universal industry ranking. Do not treat
community formats or vendor claims as standards or measured results here.

## Primary evidence worth following

| Source / date | Concrete practice | Where to apply |
|---|---|---|
| [Google full spec](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md), latest file change observed `961439fc0643`, 2026-07-27 | Optional frontmatter, precise typed tokens/refs, ordered relevant prose sections, `omitted` with optional reasons | Portable visual-system contract and schema-aware exchange; not a minimum-line requirement |
| [Shadcn official DESIGN.md workflow](https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/design-system.md), introduced `2d3f1cd436b1`, 2026-10-09 | Preset geometry → theme role mapping → component variant recipes → showcase → browser verification | New full-system delivery; adapt to existing components for incremental product work |
| [Atlassian DESIGN.md testing](https://www.atlassian.com/blog/how-we-build/atlassians-design-md-is-here-what-we-learned-testing-portable-design-context-in-practice), 2026-06-15 | Portable DESIGN.md works for isolated prototypes; implementation-aware skills/MCP better fit established production components | Separate visual intent from instructions for importing/using existing APIs |
| [Atlassian CLI follow-up](https://www.atlassian.com/blog/ai-at-work/giving-ai-agents-design-system-context-from-the-terminal-what-we-learned-building-a-cli), 2026-09-16 | One structured source feeds skill, MCP and CLI; reuse handlers; batch lookups; benchmark whole tasks and inspect transcripts | Reuse current lookup/tooling routes and shared content rather than duplicating knowledge/control planes |
| [Shadcnblocks theme practice](https://www.shadcnblocks.com/blog/shadcn-theme-design-md), 2026-07-25 | Theme CSS controls values; accompanying DESIGN.md explains hierarchy, density, type roles, spacing/pacing, dark pairs and taste boundaries | Preset/theme plus explicit composition rules; this is a vendor practice, not the shadcn upstream standard |
| [Atlassian AI entry points](https://atlassian.design/get-started/develop/with-ai), read 2026-10-10 | Task-specific skills, regular updates, public CLI/MCP; internal ADS skills are private | Adopt the task routing/update model, not claims that their internal skill is publicly installable |

Dates above distinguish article publication from observed file-change dates;
Exa crawl/index dates are not release dates. GitHub file hashes were checked via
its commits API. No upstream CLI/theme install or migration was executed here.

## The important distinction: not short versus long

**Portable DESIGN.md:** give an unfamiliar agent/tool enough visual identity to
produce an on-brand system without access to your production library. Precise
values, roles, states and rationale matter; YAML is useful for interchange. Full
coverage can legitimately require a substantial file.

**Production implementation guidance:** teach the agent which existing component
to import, what variant/API to use, and where tokens live. It should not rebuild
a Button from its appearance specification when a shared Button already exists.
Read relevant implementation docs/source on demand, rather than load the entire
catalog for every screen.

**Runtime truth:** CSS/token data, shared variants and existing generated outputs
remain the executable system. Declare ownership and propagation direction. A
portable snapshot is not a second independently edited numeric authority.

This split complements, rather than replaces, the corpus's Defaults, conditional
Signatures, CJK, Iteration and real Gaps. Keep those useful decisions; do not
wholesale shrink or enlarge a working project contract based on file length.

## What the measured reports do and do not prove

Atlassian's June example reports DESIGN.md-only at 7.21M average tokens versus
3.75M for ADS MCP, approximately 92% higher. It also reports roughly 2.7× token
variance. The authors explicitly call this an internal example, not a conclusive
research paper; model, task, context and library conditions differ. It does not
prove DESIGN.md is bad or promise these savings in another project.

Their September CLI experiment reports mean task time 352s → 325s and tokens
218k → 201k, around 8% improvements, after benchmarking and trace-driven changes.
The lesson is to measure startup/query overhead, retries and actual component
reuse. CLI is not universally better than MCP, and none of these gains were
measured for our skill. No new CLI/MCP service is justified by these articles alone.

## Apply to the existing skill

1. Route by the real task: incremental product change, portable/new system, or
   explicitly requested full showcase. Preserve complete coverage where needed.
2. For existing apps, inspect shared component imports/variants before appearance
   recipes. Use installed source or current authoritative docs; avoid re-init.
3. Keep DESIGN.md visual direction/constraints and token ownership; implementation
   workflow/API guidance lives in skill references or existing component docs.
4. Reuse available native/CLI/MCP queries based on the environment. Prefer bounded
   or batched lookups when supported; do not run repeated `npx` startup loops or
   build an internal content platform for a small repository.
5. Update affected code and documentation in the same reviewed diff. Preserve token
   references; run relevant existing checks and view the rendered result.
6. Evaluate representative work, not document size: one color change, one existing
   component composition and one full-system task. Compare output quality, component
   reuse, relevant regressions, elapsed time/tool calls and user interventions.
   Inspect transcripts for unwanted reimplementation and repeated research. These
   are proposed evaluation tasks, not completed benchmark evidence.

## Keep following upstream without research churn

- On a meaningful skill update, recheck primary Google/shadcn files and one relevant
  firsthand production report. Exa discovers changes; official source adjudicates.
- Refresh sooner after schema/API changes, lint mismatch, repeated agent failures,
  or a new artifact type. Routine component edits do not require broad research.
- For a continuously used skill, propose a monthly review as a human-owned
  checkpoint; agree the cadence before adding automation. No scheduler is installed.
- Record last-reviewed date, source/version, concrete change and applicability in
  this reference or its adapter. Git preserves previous conclusions.
- Follow evidence chains from later reports: Atlassian's June portability test to
  September CLI experiment illustrates why an old summary needs revisiting.
- Change only rules affected by new evidence; check with representative tasks
  before claiming improvement. Upstream adoption is guidance, not immunity from
  evaluating the result in this project's environment.

## Secondary sources / not adopted wholesale

[Agentic Design School's maintenance case](https://agenticdesign.school/articles/design-systems-that-maintain-themselves)
(last reviewed 2026-06-14) describes token propagation, standing checks, human
review and periodic drift audits on a working copy. It is a useful practitioner
case, not a major-vendor benchmark or authorization to install an audit daemon.

Search also surfaced third-party preset exporters, catalogs and extended
“DESIGN.md v2” schemas. They may offer reference material, but are not Google's
format or proof of production quality. No new schema, importer, dependency or
parallel design authority was adopted from them.
