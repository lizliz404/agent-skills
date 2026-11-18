# Due diligence — identities, claims vs evidence, risks

Survey date: **2026-11-18**, times below in **Asia/Shanghai (UTC+8)**
unless a source timestamp is quoted. GitHub numbers are from the
public API at about 23:33 that day (2026-11-18 15:33 UTC).

Confidence: **observed** / **inferred** / **claimed by others** /
**unverified**.

## Identity (only what primary sources show)

| Claim | Status | Source |
| --- | --- | --- |
| X account [@yetone](https://x.com/yetone), user id `147786784`, display name "yetone", verified (blue) | **observed** | `get_users_by_username`, 2026-11-18. Created 2010-05-25T01:52:30.000Z. Followers 106,187; posts 22,564. Bio lists built avante.nvim and "Building" usemagpie.ai, alma.now, cumora.ai, yansu.app, confirmo.love, swordgame.ai. URL: https://github.com/yetone. Location field: "无". |
| GitHub [yetone](https://github.com/yetone), id 1206493 | **observed** | `GET /users/yetone`. Created 2011-11-19T14:26:08Z. Name "yetone", bio "ohh", `twitter_username: yetone`, location "China", 11,260 followers, 642 public repos. No company field. |
| Legal name, employer, incorporation | **unverified** / not stated in these primary sources. Nicknames used by others on X ("叶天帝", "老叶") are not legal facts and are not repeated as such. |
| Official Magpie X account is [@magpie_router](https://x.com/magpie_router) | **observed** (account) + **mirrored** (his announcement) | Account: user id `2119790402245148673`, display name **Magpie** (not "Magpie Router"), verified blue, created 2026-11-09T13:57:30.000Z, bio "Magpie Official Account" + usemagpie.ai. As of the lookup: 7,441 followers, 2,200 posts, following 1. The handle Liz recalled as "Magpie Router" is this account. `MagpieRouter` (no underscore) does not exist. Announcement text from public mirrors (his own posts were not API-readable): he applied for this as the only official Magpie X account so feedback need not @ him. See `posts/2026-11-09-yetone-magpie-router.md`. |

**X API gap (observed):** `get_users_posts` and `get_posts_by_id` on
yetone's user and on status `2109855710444237018` returned "not
authorized to see the user/post." `from:yetone` search returned zero
rows. Commentators' posts, @magpie_router, and @wquguru were readable.
This pack therefore does not pretend to have a complete archive of his
own timeline.

## The product (yetone/magpie)

| Fact | Status | Notes |
| --- | --- | --- |
| Repo [yetone/magpie](https://github.com/yetone/magpie), homepage [usemagpie.ai](https://usemagpie.ai) | **observed** | Both HTTP 200. Description: "Every agent's model. One place. Codex on DeepSeek, Claude Code on Kimi, from the menu bar." Language Go. Default branch `main`. Created 2026-09-23T16:22:35Z. |
| License MIT | **observed** | `license.spdx_id: MIT`. |
| Companion [yetone/magpie-releases](https://github.com/yetone/magpie-releases) | **observed** | "Signed builds of magpie." Latest published release at the snapshot: **v0.1.4482**, 2026-11-18 15:19:11 UTC = **23:19:11 Asia/Shanghai**. v0.1.4481 and v0.1.4480 went out the same hour. |
| Local gateway `127.0.0.1:3425`, OpenAI / Anthropic / Gemini dialects, token `magpie` on loopback | **observed** | Official docs and README. |
| Stars 38,560; forks 3,493; commits on `main` 8,725; tags 4,479 | **observed** (snapshot) | Stars are popularity, not quality or safety. |
| Issues: 4,552 open, 1,974 closed | **observed** | Open exceeds closed. Cause **unverified** (duplicates, agent-opened tickets, genuine backlog, or intake outrunning closure). It is enough to refuse the slogan that the factory "keeps up with all feedback." |
| PRs: 16 open, 397 merged, 154 closed unmerged | **observed** | `pull_request_creation_policy: collaborators_only`, confirmed by `docs/contributors.md` ("PRs are open to collaborators only"). Early October commentary about hundreds of community PRs describes a phase that has since been tightened. WquGuru (2026-10-12) counted 383 merged community PRs in the first 19 days; the lifetime merged count by 2026-11-18 is 397, which implies the merge rate slowed sharply after that burst **inferred** from the two snapshots. |
| Signed, notarised Mac builds; GitHub Actions attestations on magpie-releases | **claimed in official docs**, not re-verified build-by-build here. |

Related products listed in his X bio were not all audited. Repos
observed as his and recently active include
[yetone/cumora](https://github.com/yetone/cumora) (MIT, "Where agent
teams gather," https://cumora.ai, 4,204 stars), alma-relay / alma-releases
(https://alma.now), plus older work such as avante.nvim (the bio says
"Built"). yansu.app, confirmo.love, and swordgame.ai were listed in the
bio and not opened for this pack.

## Name collision — not this Magpie

**Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned
LLMs with Nothing**, Zhangchen Xu, Fengqing Jiang, Luyao Niu, Yuntian
Deng, Radha Poovendran, Yejin Choi, Bill Yuchen Lin (University of
Washington and Allen Institute for AI), arXiv:2406.08464,
https://arxiv.org/abs/2406.08464 (HTTP 200), project
https://magpie-align.github.io/ and
https://github.com/magpie-align/magpie (HTTP 200).

It is a 2024 method for synthesizing alignment data by prompting an
already-aligned model with only its pre-query template. **It has
nothing to do with yetone, usemagpie.ai, or software factories.** Do
not mix citations.

Other "Magpie" software exists. If a source does not point at
`yetone/magpie` or `usemagpie.ai`, assume it may be a different
project until proven otherwise.

## Claims vs evidenced output

| Claim | Status |
| --- | --- |
| "magpie's code is written, reviewed, merged and released by agents" | **observed** as a first-party repo statement (`LESSONS.md`). Reviews and merges appear under the `yetone` GitHub account, so "agent-authored" vs "human-authored under the same login" is **not independently separable** from the outside. |
| Three Claude Code `/loop`s on official Opus 5.5, nightly UI/UX | **his words, via mirrors** (see `yetone-loops.md`). The harness is **not in the repo** (no scheduled workflow for the nightly review; WquGuru listed LESSONS.md update times that did not look like cron). |
| He has a "software factory methodology" | **claimed by others** (e.g. @geraldpppppp asking; Tony's Lab's title). **Not found in his own words** in sources this pack could read. |
| First 19 days: 2,862 commits, 1,204 tags, ~9,474 stars, 383 merged community PRs (WquGuru, 2026-10-12) | **claimed by others**, from a repo analysis he describes. Plausible next to today's 8,725 commits / 4,479 tags, but not re-run for that exact window here. |
| "25 versions in 24 hours" (WquGuru prelude, 2026-10-12) | **claimed by others** at that date. |
| Same-day rework and cancelled CI in early October | **observed** in `LESSONS.md` itself (220 commits / ~170 releases on 2026-10-05; ~40 fixing that day or the day before; "294 tags in 51 hours left no run to finish"). This is evidence *against* treating tag velocity as success. |
| Auto-fix from X, then a versioned reply | **observed** in mid-to-late November @magpie_router threads (e.g. v0.1.4481 window-resize reply on 2026-11-18). Mechanism (which agent, which machine) **unverified**. |
| Monthly model spend ≥ $400 on Magpie + Alma, plus $200 "for work" | **claimed via secondary write-ups** of a reply. Not API-verified. |
| "Build in public will keep bringing exposure" (@yangyi) | **claimed by others.** Stars and follower counts are **observed**; causality is not. |
| Factory.ai customer list and outcome percentages | **vendor claims, unverified** (`landscape.md`). |

## Cost, including the non-token kind

- Tokens / subscriptions: only the secondary $400+$200 figure above;
  no ledger.
- Human time: even in the "then I have no work left" framing, the
  nightly UI/UX window, maintainer-only harm review, block-list
  decisions, and "don't reverse deliberate decisions" are standing
  human costs **inferred** from first-party docs plus his mirrored
  post.
- Rework and entropy removal: first-party (`LESSONS.md`, loop 3).
- Coordination: first-party evidence of two sessions in one checkout
  shipping each other's files.
- Disk / session residue: a later commenter under the loop post
  reported multi-gigabyte `~/.codex` and cache growth after an
  overnight loop (**claimed by others**, one anecdote).
- Review load vs intake: 4,552 open issues at the snapshot is a cost,
  whatever the cause.

## Security, IP, ToS, operational risk

**Observed in first-party docs or official posts:**

- Community PRs are harm-checked before they are run; listed stop
  conditions include CI/release/Docker/site changes, new network or
  credential flows, dependencies, binaries, and relays. Agents propose
  blocks; the maintainer decides.
- `LESSONS.md` records real security defects that reached the work
  stream and were later fixed, including a privacy exemption keyed on a
  field name that let tool arguments go out unmasked, a documented
  DNS-rebinding hole, and pages with `Origin: null` or `*.localhost`
  that could spend a subscription without a key.
- Built-in Antigravity (and then the official Antigravity plugin) was
  withdrawn because the approach simulated a client talking to Google
  and "账号容易被封." The official account told users to switch to a
  community ACP plugin that drives a locally logged-in official client,
  with residual risk, and not to run many accounts at high frequency.
  `AGENTS.md` records a broader retirement of built-in subscriptions
  that "can break their vendors' terms," moved to community plugins.
- @magpie_router publicly documented a social-engineering attempt
  (someone asking that the dev machine enable sshd / frp and send IP
  and passwords) and said they would not comply.
- `contributors.md` "extra care" and "watched" lists include community
  plugin work that attempted cookie-jar harvesting, TLS-fingerprint
  impersonation, bot-detection evasion, and prompt canaries. Those PRs
  are described as closed unrun or held. This is evidence that a
  factory which auto-considers community patches needs the harm-first
  stop, and that the stop is being exercised — not that it is complete.

**Inferred / product-level residual risk:**

- The headline feature — "your Claude / ChatGPT / Copilot plan, in
  another agent" — may conflict with vendor terms. This pack did not
  litigate those ToS. Do not tell a user it is "safe" or "allowed."
- A loop that reads GitHub issues, Discord, and X and then writes code
  is an untrusted-input system. His mirrored reply on prompt injection
  ("现在已经很难了") is not a threat model.
- `curl | sh` install from usemagpie.ai is convenient and is an
  integrity bet on that domain plus release attestations.
- Sharing the gateway beyond loopback requires user-issued gateway
  keys; official docs warn that anyone with a key can call command
  servers with the host's rights.

**Reproducibility:** another operator cannot reproduce the loop from
the repo alone. Prompts and scheduler are missing. CI is documented;
the standing agent processes are not.

**License:** MIT for the main repo (**observed**). Downstream use of
vendor plans is a separate question from the copyright license.

## Hype and conflicts

- WquGuru's article (2026-10-12 22:19 Asia/Shanghai) is the main
  amplifier: 323,055 impressions, 1,158 likes, 2,226 bookmarks at the
  API read. It is a serious repo reading, and it is also advocacy
  ("未来已来"). Use the artefact analysis; do not inherit the peroration.
- "快餐式服务 / 不太敢用" is how that article describes *other
  people's* criticism. We did not independently archive those critical
  posts.
- Official @magpie_router is both a feedback intake and a marketing
  surface. Agent-drafted replies that sometimes duplicate a paragraph
  are a quality tell, not proof of unreliability of the product.
- This pack's author is not affiliated with yetone or Factory.ai /
  Warp. The seed was Liz's request to study the *method*.

## What was not observable

- yetone's full X timeline and comment-thread replies, via the API.
- The actual loop process, machines, and prompts as they run today
  (October screenshots may be stale).
- A breakdown of which commits are human vs agent, except for the
  repo's own claim.
- A complete cost ledger; ToS rulings; whether open issues are
  mostly noise.
- Legal identity beyond the handles above.
- Discord internals (the loop is said to watch every channel).
