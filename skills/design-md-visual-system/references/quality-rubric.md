# Quality rubric & audit blockquote

Score Genre **A** (visual system) 0–10. Brand briefs use a separate B score — do not fail a good B-doc for missing slide chrome.

## Genre A dimensions (each 0–2, sum → /10)

| Dim | 0 | 1 | 2 |
|---|---|---|---|
| **Tokens** | No/broken YAML | Colors+fonts only | Full roles: colors, type scale, spacing, components w/ descriptions, refs `{colors.x}`; aliases when roles ≠ primitives |
| **Thesis** | Generic "modern clean" | Some mood words | Cultural refs + surface model + depth model + anti-reference |
| **Signature** | None | A few "prefer" tips | Named non-optional treatments when element type appears |
| **Defaults + Do/Don't** | Missing | Vague pairs | Concrete reach-for-X + specific bans |
| **Completeness** | <3 body sections | Core Google sections only | + Responsive, CJK, Iteration, Known Gaps (or explicit N/A) |

**Pass bar:** ≥7/10 and Signature ≥1. Below that = garbage-or-stub relative to soft-editorial.

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

## Prepend audit blockquote (active repos)

Insert **immediately after** YAML frontmatter closing `---` (before H1 / existing diagnosis). Do not destroy existing Chinese diagnosis — stack audits.

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

- [ ] `description` is a full thesis paragraph, not a tagline
- [ ] ≥1 Signature Treatment marked non-optional
- [ ] Type roles do not overlap (display vs body vs chrome)
- [ ] Accent policy stated (one accent / multi-pastel non-semantic / mono ink-only)
- [ ] Density philosophy names broken states
- [ ] Components have `description:`
- [ ] Token ladder clear: primitives → aliases/roles → component refs (no invented hex)
- [ ] Iteration Guide has ≥5 additive rules
- [ ] Known Gaps lists real debts
- [ ] Hex quoted; negative letter-spacing quoted
- [ ] If bilingual product: CJK pairing + known gap for the signature move
- [ ] Lint clean when claiming Google-shaped structure (`npx -y @google/design.md lint`)
- [ ] Not mistaken for Genre B / not DTCG-only JSON posing as DESIGN.md
