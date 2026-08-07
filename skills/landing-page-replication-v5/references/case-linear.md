# When to load: Issue-tracker / eng-tool / Linear-class density targets
# Precondition: Second sample to force abstraction away from CRM theater
# Output: Contrasts vs Attio-case — what generalizes, what does not

# Case study: Linear-class density (second sample)

> Evidence tier: Templated (synthesized, not build-tested)

n=1 (Attio) overfits. This case forces the pipeline to stay domain-agnostic. Values below are **method templates**, not a claim that a full Linear replica was shipped in-repo. Use when the target is an eng tool, issue tracker, or high-craft monochrome SaaS.

## How Linear-class differs from Attio-class

| Dimension | Attio-class | Linear-class |
|-----------|-------------|--------------|
| Hero density | Multi-window CRM collage | Often single focused product surface + precise type |
| Product theater | Tables, pipelines, retain bars, chat | Issue list, cycle/board, command palette, keyboard cues |
| Color | Paper + one authorship accent | Near-black UI chrome, violet/indigo accent common in genre — **match target, don't invent** |
| Motion | Idle bob / reveal / tab swap | Scroll-linked subtlety, command-menu fade, checklist |
| Type | Display sans + editorial serif | Tight geometric sans; serif rarer |
| Risk | Signature radar metaphors | Trade dress around command palette + issue row chrome |

## Two-Reference example

- Positive: target eng-tool homepage
- Anti-reference: generic "AI project management" template with purple glow + 3 equal feature cards
- Sharp edges (examples): keyboard-first cues, dense issue rows, restrained accent, no rainbow sections

## Capture notes

Linear-class sites often sit behind strong bot management. Expect Capture Router → manual DevTools path more often than Attio's clean Next SSR curl.

Fonts may be self-hosted with opaque hashes **or** Google Fonts — run `extract-tokens.py` and trust Google/Typekit parse when file hints are empty.

## Density inventory checklist (adapt)

- [ ] Primary product surface row count / density
- [ ] Command palette or search affordance present?
- [ ] Status/priority chips grammar
- [ ] Dark vs light band rhythm (IMR series)
- [ ] Accent usage: links only vs chrome highlights

## Micro-parity backlog examples (do not cargo-cult)

1. Issue row hover + status pill
2. Shortcut hint typography (`⌘K` style — reimplement, don't copy trademarked glyphs if restricted)
3. Board column density
4. Changelog / ship log strip

## What generalizes from Attio evidence

- Product theater > screenshots
- Blur / IMR gates before pixel chase
- Primitives before sections
- Observer-based sticky nav when morph depends on hero exit
- Libre fonts + metric align

## What does **not** generalize

- Pipeline radar rings
- Retain `clipPath` bars
- Cyan "agent authored" chip grammar
- Traffic-light chrome in every mock (Linear UIs often use custom title bars or none)

If you catch yourself pasting Attio radar into a Linear-class page, you are failing abstraction — re-read `taste-rubric.md` and rebuild the theater inventory from screenshots.
