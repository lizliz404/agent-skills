# Quality rubric & audit blockquote

Optional audit for Genre **A** (visual system) 0–10. Score applicable decision coverage, not document length. Short CSS-backed contracts can pass without YAML or all corpus headings. Brand briefs use a separate B score; do not fail a good B-doc for missing slide chrome.

## Genre A dimensions (each 0–2, sum → /10)

| Dim | 0 | 1 | 2 |
|---|---|---|---|
| **Tokens / ownership** | Values invented or no source | Some roles/source unclear | Runtime source + relevant roles/aliases explicit; valid YAML refs when using portable mode |
| **Direction** | Generic "modern clean" | Mood without implementation consequences | Audience/density + surface/accent/depth policy + what looks wrong |
| **Distinguishing rules** | Agent must invent treatment | Preferences lack boundaries | 1–3 conditional, actionable rules; existing variant references may suffice |
| **Defaults + boundaries** | Missing | Vague pairs | Concrete defaults + likely mistakes prevented; unrelated color domains stay independent |
| **Change + acceptance** | No edit/test path | Partial instructions | Cheap change path, representative acceptance, relevant responsive/CJK/motion/gaps |

**Optional pass bar:** ≥7/10 and distinguishing rules ≥1. A low score identifies missing decisions, not a reason to add pages. No scoring ritual for small edits; a concise actionable contract beats padded corpus imitation.

## Genre B dimensions (brand/distribution brief) — quick /10

| Dim | Weight |
|---|---|
| Product identity + one-liner + anti-refs | 2 |
| Audience + tone do/don't | 2 |
| Tokens extracted from code (not invented) | 2 |
| Distribution priority (motion/OG/favicon as relevant) | 2 |
| Executable asset briefs (or intentional placeholders) | 2 |

## Verdict vocabulary

- `keep-as-is` — fits its genre, ≥8
- `upgrade-in-place` — right genre, missing Signature/CJK/Gaps etc.
- `split-into-two-docs` — file mixes A+B poorly; keep B as DESIGN.md, add DESIGN.system.md for A
- `rewrite` — wrong genre or <5/10 with no salvageable structure
- `archive-stub` — template sketch, not production truth

## Audit report (only when requested)

Prefer a concise response, not permanent boilerplate in every project. If asked to persist the audit, place it after YAML (or after H1 in short mode), preserve meaningful diagnosis, and replace a superseded audit instead of stacking history; Git already preserves it.

```markdown
> **DESIGN.md quality audit** · YYYY-MM-DD · gold: beautiful-html-templates/soft-editorial
> - **Genre:** A visual-system | B brand/distribution brief | hybrid | unclear
> - **Grade A (UI system):** X/10 — …
> - **Grade B (brand brief):** X/10 — …
> - **Strengths:** …
> - **Gaps vs gold pattern:** …
> - **Verdict:** keep-as-is | upgrade-in-place | split-into-two-docs | rewrite | archive-stub
> - **Next action:** …
```

Keep ≤25 lines. No body rewrite in audit-only passes.

## Fast fail checklist (agent self-review before shipping A)

- [ ] Direction states density/surface/accent decisions, not just a tagline
- [ ] 1–3 distinguishing rules are actionable when the relevant element appears
- [ ] Type roles do not overlap (display vs body vs chrome)
- [ ] Accent policy stated (one accent / multi-pastel non-semantic / mono ink-only)
- [ ] Density philosophy names broken states
- [ ] Relevant component defaults point to existing variants; portable YAML components have `description:`
- [ ] Token ladder clear: primitives → aliases/roles → component refs (no invented hex)
- [ ] Change path names the actual source and a representative acceptance check
- [ ] Gaps are genuine; no invented debts or irrelevant section filler
- [ ] In YAML mode, hex and negative letter-spacing are quoted
- [ ] If bilingual product: CJK pairing + known gap for the signature move
- [ ] Lint clean when claiming Google-shaped structure; short CSS-backed mode does not claim it
- [ ] No duplicated numeric truth, minimum line count, mandatory all-component install or showcase
- [ ] Not mistaken for Genre B / not DTCG-only JSON posing as DESIGN.md
