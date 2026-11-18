# Seed case — yetone's Magpie maintenance loop

This is one 2026 implementation of the method in `SKILL.md`, not the
definition. The product (a local LLM gateway) and the method (how the
repo is maintained) are easy to conflate. Keep them apart.

Confidence: **observed** / **reconstructed from consistent secondary
sources** / **claimed by others** / **unverified**. A special gap: on
2026-11-18 the public X API used for this pack returned an authorization
error for @yetone's posts and for
https://x.com/yetone/status/2109855710444237018. His words below are
therefore taken from multiple independent public mirrors, not from a
direct API read. Mirrors agreed on the text. See `posts/` and
`source-index.md`.

## Two different things named Magpie

| | Product | Method |
| --- | --- | --- |
| What | yetone/magpie: menu-bar app + local gateway at `127.0.0.1:3425` that lets coding agents use any configured model or subscription. Site: https://usemagpie.ai | How that repo (and related products) is maintained: standing agent loops, written standards, a lessons ledger, acceptance gates, a public feedback channel |
| In his bio / docs | "Every agent's model. One place." | In the 2026-10-13 post: three Claude Code `/loop`s + a nightly UI/UX window, "no magic," "quite crude" |
| In this repo family | [`fleet-orch`](../../fleet-orch/SKILL.md) already treats `magpie` as a local gateway (`http://127.0.0.1:3425/v1`) for dispatching workers | This skill is the doctrine layer |

A third Magpie — the 2024 UW / Allen AI alignment-data paper — is
unrelated. See `due-diligence.md`.

## His own words (mirrors, 2026-10-13)

Post: https://x.com/yetone/status/2109855710444237018

Snowflake time: 2026-10-13 03:56:15 UTC = **2026-10-13 11:56:15
Asia/Shanghai**. Mirrors: TodayRss (same clock), XPut, Zhihao's mark,
Tony's Lab, Today for AI.

Chinese original (mirrors agree):

> 很多人想让我分享一下工作流，我一直没想好怎么分享，因为其实我没有任何的魔法，甚至还特别简陋，总觉得分享出来毫无意义。其实我就是用 Claude Code，然后用官方的 Opus 5.5 模型执行 loop 就可以了。
>
> 我会并行执行图里的 3 个 loop，然后每晚抽一点时间铲铲屎（主要是 UI/UX 的问题），然后就没活儿了。

He quoted @wquguru's article
https://x.com/wquguru/status/2109650264601117141 (API-readable; see
`posts/2026-10-12-wquguru-yetone-magic.md`).

**Observed from this text:** he attributes the work to Claude Code +
official Opus 5.5 + three parallel loops + a nightly human window on
UI/UX. He downplays ceremony. He does not use the phrase "software
factory."

## What commentators transcribed from the three screenshots

Tony's Lab (2026-10-14, "依据 @yetone 原推 及其评论区整理"), Today for
AI, and the 2026-10-13 nuts.nvirellia.im digest transcribe the same
three `/loop` prompts from the images on that post. The prompts are
**not in the repo**. Treat the wording as a consistent transcription,
not as an API-verified media download (the post itself was unreadable
via the API).

Paraphrase of the standing orders (full Chinese text is in
`posts/2026-10-13-yetone-no-magic-loops.md`):

1. **GitHub issues, PRs, and every Discord channel.** Decide what is
   worth fixing; fix or implement, release, and reply — including when
   declining. Reseller / "中转站" advertisers get a canned "we'll have
   a partnership plan later" and are not added to the product. PRs are
   reviewed line by line, checked out, and actually run; merge only
   after that, otherwise comment or close. In Discord, really @ people.
2. **X feedback.** Valuable feedback or reproducible bugs get
   implemented or fixed, released, then replied to. A cheap decision
   model (he names "jev") should drop unrelated posts before they reach
   the expensive model, because "magpie" is also an English bird and
   keyword intake is noisy.
3. **Periodic cleanup.** Because "magpie 完全是自动化更改代码和合并社区里的 PR,"
   regularly clean unmaintainable or malicious code, write lessons
   (what should not have merged, what was verified too thinly) so later
   agents do not repeat it, and put repeat low-quality submitters on a
   block list.

Tony's Lab and Today for AI also quote comment-thread replies they
attribute to him. **These were not independently retrieved** (same API
gap). Consistent claims across those write-ups:

- A real macOS machine, a Windows machine, and a Linux VM on the
  Windows box, used to reproduce before fixing.
- Decisions lean on Claude Code's memory plus the repo's design docs,
  from early brainstorming with the model.
- Asked whether he uses `tw` CLI to watch X: "所有的操作都是 browser use."
- Asked why `/loop` instead of a scheduled task: "没有优势，目的就是监听而已，只要能达成目的，啥方式都可以."
- Asked about prompt injection in GitHub issues: "现在已经很难了."
  (thin).
- Asked whether $200/month is enough: "哈哈，完全不够。我每个月在 Magpie + Alma 上的支出至少 400 刀，然后还要注册 200 刀给工作."
  **Claimed via secondary sources; do not treat as a measured benchmark.**

## What the repo itself says (stronger evidence)

All of the following were read from
[yetone/magpie](https://github.com/yetone/magpie) on 2026-11-18.

- `LESSONS.md` opens: "magpie's code is written, reviewed, merged and
  released by agents." Each night, the day's commits are reviewed for
  what had to be fixed again, what should not have merged, and what was
  verified too thinly. A lesson is a rule, a why, and evidence. "Seen"
  counts the days a review found it. A lesson seen on three or more
  separate days moves into `docs/code-standards.md`.
- The first review (commit `303819c`, covering 2026-10-05) records 220
  commits and about 170 releases that day, of which about 40 fixed
  something released that day or the day before, and the line
  "294 tags in 51 hours left no run to finish." A rule followed: a
  tag needs a *finished* green CI run; a cancelled run does not count.
- `AGENTS.md` is a router, not a rulebook: read the subsystem design
  page, the code standards, the contributor rules, then LESSONS, before
  changing code.
- `docs/code-standards.md` "Acceptance criteria": a change is merged or
  released only when each listed check is shown. "A check that wasn't
  run is listed as not run, never left out." The six criteria are: a
  test that fails without the change; sandboxed tests; the build and
  the whole suite (not only the packages you think you touched); GUI
  tests in both engines and every listed language (this suite is local,
  not CI); real use where possible, and if not, say so; the UI rules.
  A PR is merged only after a maintainer has pulled it, merged it onto
  current `main`, run the checks, and run
  `gh pr merge --match-head-commit <reviewed sha>`. A release also
  needs a finished green CI run, a tag on `main`, and a
  `yetone/magpie-releases` release with all 17 assets (the number of
  assets has moved since mid-October write-ups that said 16).
- `docs/contributors.md`: "magpie merges community PRs through agents."
  Harm is checked before the PR is run (`.github/`, release scripts,
  Dockerfile, `site/`, new network/telemetry/credential flows,
  dependencies, binaries, relays). "Don't run the PR's code on a
  machine with real accounts until the maintainer has cleared it."
  "An agent only proposes" a block list; the maintainer decides. As of
  the 2026-11-18 read, "Blocked: none yet," with a short "extra care"
  list. The same file now says **PRs are open to collaborators only**,
  so a reporter's fix often arrives in an issue — which matches the
  GitHub API field `pull_request_creation_policy: collaborators_only`.

WquGuru's 2026-10-12 article (API-readable, high engagement) is the
best early *external* analysis of that doctrine: AGENTS.md as a routing
table, LESSONS.md as an error ledger, the Seen-3× promotion rule, and
the admission that the nightly-review trigger and loop prompts are not
in the repo. Some of his mid-October counts are snapshots; current
counts are in `due-diligence.md`.

## What other people inferred (not his words)

- @geraldpppppp asked him, 2026-10-02, "是有自己的 software factory
  方法论嘛？" and later wrote that, inspired by magpie and by the
  authors of omp and tern, he was trying to build his own 软件工厂.
  That is a commentator applying the name. We did not find yetone
  adopting it in a primary source this pack could read.
- Tony's Lab titled the write-up "yetone 的 AI 全自动软件工厂."
- @yangyi (2026-11-12) called Magpie the real "build in public": users
  trigger fixes on X, agents judge, merge, and CI-release. He contrasted
  his own NewMax loop, which still had daily human review and no auto
  release. **Inferred / claimed by others.** "Loop 框架" is his phrase.
- @LeiCheng42 (2026-10-19) restated WquGuru's doctrine (AGENTS.md /
  LESSONS.md, humans hold direction and gates, agents close the loop)
  under "#AgentBuildInPublic." Low engagement; useful as a compact
  restatement, not as independent evidence.
- Official product account [@magpie_router](https://x.com/magpie_router)
  (display name "Magpie," created 2026-11-09; yetone announced it as
  the only official Magpie account — mirror text in
  `posts/2026-11-09-yetone-magpie-router.md`). On 2026-11-18 it was
  actively replying to user reports with version numbers (e.g. v0.1.4481
  on a window-resize performance fix). One reply duplicated the same
  fix summary twice with slightly different wording — consistent with
  an agent-drafted official voice, **inferred**.

## Gaps the comment threads already named

These were asked under the 2026-10-13 post and, in the write-ups, were
not given a complete answer:

- How three loops avoid writing the same tree at once (worktrees, merge
  queue, or directory ownership). LESSONS.md later records two sessions
  in one checkout shipping each other's files — so the risk is real.
- Deduping the same bug reported on GitHub, Discord, and X.
- A precise "must call a human" rule. Harm-first review and "don't
  reverse deliberate decisions" are the repo-side partial answer.
- Prompt-injection hardness — his quoted reply is one short sentence.

## How to use this case

Steal the **invariants** that are in the repo: lessons with a promotion
threshold, acceptance criteria that list what was not run, merge pinned
to a reviewed SHA, harm-first intake, a human window for taste, a cap
on shipping once CI cannot finish. Do not steal the mythology of "three
magic loops" or assume the current open-issue pile (see
`due-diligence.md`) means the line is keeping up with demand.
