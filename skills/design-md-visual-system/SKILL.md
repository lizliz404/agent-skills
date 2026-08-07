---
name: design-md-visual-system
description: >-
  Use when writing or auditing Genre-A UI DESIGN.md visual systems for coding
  agents: YAML tokens + prose (Signature Treatments, Defaults, Do/Don't, CJK,
  Iteration, Known Gaps). Extract from real CSS/HTML or a gold template; lint
  and optionally export via npx @google/design.md. Not for brand/OG/image briefs
  (Genre B — use design-brief skills instead).
version: 1.1.0
author: Liz (lizliz.xyz)
license: MIT
metadata:
  hermes:
    tags:
      - design-md
      - visual-system
      - design-tokens
      - yaml
      - ui
      - coding-agents
      - stitch
    related_skills:
      - design-md
      - design-brief-authoring
      - design-brief-for-image-gen
      - creative-artifact-production
---

# DESIGN.md Visual System (implementation-grade)

Persistent design contract for coding agents — the design-side peer of `AGENTS.md`:
machine tokens plus the judgment tokens alone cannot carry.

## Genre gate (read first)

Liz has **two different documents** both sometimes called DESIGN.md:

| Genre | Job | Skill |
|---|---|---|
| **A — Visual system** | Machine tokens + prose so a coding agent can *implement* UI/slides/landings without inventing taste | **This skill** |
| **B — Brand / distribution brief** | Product identity, audience, motion/OG/favicon briefs for *image* AI | `design-brief-authoring` / `design-brief-for-image-gen` |

If Liz says 「写 DESIGN.md」without context: ask which job, or infer from target (slide template / landing system → A; favicon·OG·生图 → B). **Do not** ship a thin vibe paragraph and call it done. **Do not** replace a good B-doc with A or vice versa — split into two files if both jobs exist.

**Gold corpus (bundled):** `references/gold-corpus/<template>/design.md` — all 34 templates, structure-verified (lint profile + refresh in `references/gold-corpus/README.md`).  External sources: the `beautiful-html-templates` tool (`templates/*/design.md`); public mirror `github.com/zarazhangrui/beautiful-html-templates`.  
Primary reference: `references/gold-corpus/soft-editorial/design.md` (+ `signal`, `monochrome`, `bold-poster`, `grove` for contrast).  
Google format + CLI: `npx -y @google/design.md` (`lint` / `export` / `spec`) — upstream spec lives at `google-labs-code/design.md` (not `google/design.md`).

## Bar (what "not garbage" means)

Thin tokens + 6 vibe bullets = fail. Gold files are ~500–700 lines and always carry:

1. **YAML frontmatter** — normative tokens agents can copy
2. **Overview** with *density philosophy* + **Key Characteristics** bullets
3. **Signature Treatments** — *non-optional* when that element type appears
4. **Defaults** subsections (when unsure, reach for X)
5. **Do / Don't** paired and specific
6. **CJK & International** + **Iteration Guide** + **Known Gaps**

Full anatomy → `references/anatomy-and-patterns.md`  
Rubric + audit blockquote → `references/quality-rubric.md`  
Mini skeleton → `references/skeleton.md`

## Authoring workflow

1. **Confirm genre A.** If B, switch skills.
2. **Extract, don't invent.** Pull colors/type/radius/shadows from real CSS/HTML (or from a chosen gold template). Ground truth > vibe.
3. **Name the system in one paragraph** (cultural refs + what it is *not*). Put that in `description:` and expand in Overview.
4. **Lock 1–3 signature moves** (e.g. Signal = gold italic mid-sentence; Soft Editorial = roman/italic weight drop + pastel cards; Raw Grid = 3px black borders + hard offset shadow). These become Signature Treatments.
5. **Write YAML** first: `version` (Google format still uses `alpha`), `name`, `description`, `colors`, `typography` (role tokens), `spacing`, `canvas` (if slide/deck), `components` (each needs a `description:`). Optional: `color-aliases`, `borders`, `shadows`, `rounded`/`radii`, `motion`. Note: `canvas` is a local extension — the official CLI schema ignores it on export (kept for agent prose context only).
   - Prefer a light **token ladder**: primitive hex in `colors` → semantic roles in `color-aliases` → component props via `{colors.x}` / `{typography.y}` refs. Do not paste DTCG `$value` / `$type` JSON into the YAML — that is an export target, not the authoring format.
6. **Write body in canonical order** (see anatomy). Every color/type role gets prose *why* + Defaults.
7. **Lint** when structure is Google-shaped: `npx -y @google/design.md lint DESIGN.md`. Fix broken refs.
8. **Optional export** when a build pipeline needs it:
   - `npx -y @google/design.md export --format css-tailwind DESIGN.md` (Tailwind v4 `@theme`)
   - `npx -y @google/design.md export --format json-tailwind DESIGN.md` (v3 `theme.extend`)
   - `npx -y @google/design.md export --format dtcg DESIGN.md` (W3C Design Tokens Format)
   Genre A DESIGN.md stays the **agent-facing** source; DTCG/Tailwind outputs are interchange, not a reason to delete prose.
9. **Self-score** with rubric. Below 7/10 on Structure or Signature → keep writing.

## Interoperability (keep boundaries clear)

| Artifact | Job |
|---|---|
| **Genre A DESIGN.md** | Coding-agent contract: tokens + rationale + signatures |
| **DTCG `tokens.json`** | Cross-tool / multi-platform token exchange |
| **Tailwind theme / CSS vars** | Runtime styling in the app |
| **Genre B brief** | Image/motion/OG identity — separate file |

Do not collapse these into one thin file. If a mature design-ops pipeline already treats DTCG as canonical for mobile+web codegen, keep DESIGN.md as the AI-facing mirror of a *subset* plus the judgment layer — still extract, don't invent.

## Placement

- Slide/template pack: beside the template (`design.md` lowercase OK — match corpus).
- Product UI system: `docs/DESIGN.system.md` or `docs/visual-system.md` if `docs/DESIGN.md` is already genre B.
- Prefer not to overwrite a strong brand brief; **split**.

## Evolution

- Google DESIGN.md format remains `version: alpha` in file frontmatter — expect schema drift; re-lint after CLI upgrades.
- **Iteration Guide** = rules for additive change without drift.
- **Known Gaps** = intentional absences + debts (also serves as a lightweight changelog of what not to "fix").
- Skill pack version (this file's `version:`) is independent of the Google format `alpha` tag.
- Bundled corpus lint profile: 10/34 files are 0-error canaries (list in `references/gold-corpus/README.md`); the rest warn/error only on `clamp()`/`vw` responsive sizes + schema-extension keys — intentional, not defects. Never cite a non-canary corpus file as a lint-clean example.

## Anti-patterns

- ❌ Genre confusion (OG brief pretending to be UI system, or vice versa)
- ❌ Invented hex/fonts not in code or chosen reference
- ❌ YAML without component `description:` / body without Signature Treatments
- ❌ Inter/Roboto default stack with no role separation (display / body / mono chrome)
- ❌ "Use generous whitespace" with no pad tokens or density philosophy
- ❌ Semantic rainbow (success green / warn yellow) forced onto a monochrome or single-accent system
- ❌ Replacing DESIGN.md prose with DTCG-only JSON and hoping agents infer taste
- ❌ Deleting existing DESIGN.md wholesale — enhance or split

## References

**Google DESIGN.md 规范/CLI(外部权威源,URL 逐个 curl 验证)**
- Spec 仓库 — `https://github.com/google-labs-code/design.md` — 证据 高(200)— 用途:格式规范/字段定义/上游变更;旧路径 `google/design.md` 已 404
- Stitch spec 可读版 — `https://stitch.withgoogle.com/docs/design-md/specification` — 证据 高(200)— 用途:人读规范,比 repo 好读
- Stitch overview — `https://stitch.withgoogle.com/docs/design-md/overview` — 证据 高(200)— 用途:DESIGN.md 是什么/何时用
- npm 包 — `https://registry.npmjs.org/@google/design.md` — 证据 高(200,latest 0.4.0)— 用途:CLI 版本/lint/export 行为变化
- 官方博客公告 — `https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/` — 证据 高(200)— 用途:设计动机与边界

**令牌标准(DTCG)**
- Format 2025.10 — `https://www.designtokens.org/tr/2025.10/format/` — 证据 高(200)— 用途:`export --format dtcg` 的目标格式;跨工具互通讨论

**本地兜底/工具**
- CLI 权威 schema — `npx -y @google/design.md spec` — 证据 高(本机实测)— 用途:字段合法性裁决(lint 报错时先查它,别猜)
- Gold corpus 真源(刷新镜像用)— 本地 `beautiful-html-templates` 工具 `templates/*/design.md` 或公开镜像 `github.com/zarazhangrui/beautiful-html-templates` — 用途:更新 `references/gold-corpus/`(见其 README)
- Hermes bundled `design-md` — 用途:CLI 封装入口

## Related

- Spec/CLI lint-export: Hermes bundled `design-md` / `npx @google/design.md`
- Brand/OG briefs: `design-brief-authoring`, `design-brief-for-image-gen`
- Steal motion/structure from live sites: `creative-artifact-production` → design-template-extraction
- Frontend slides fixed 1920×1080 stage policy: see bold-poster / grove templates' "Frontend Slides Fixed-Stage Policy" section when generating decks
