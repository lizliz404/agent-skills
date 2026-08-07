# Worked example 2026-07-31 — hermes-agent-one-month-review → video script

## Context

Source: `<写作目录>/2026-05-23/hermes-agent-one-month-review/` (raw-human.md / draft-zh.md / notes.md). Published article is canonical at `lizliz.xyz/content/articles/hermes-agent-one-month-review.md` — body diff vs writing draft showed only 3 small edits (extra sentence in §0, inline footnote markers moved, footnotes 12/13 shortened). Verdict: site version is the published truth; writing-folder draft lags.

The article was a `0/ 1/ 2/ …` numbered-list review (21 items). As spoken script it fails: author perspective, no hook, no user payoff.

## Liz's stated anchor theme

"如何打造你的 AI 数字员工" — 7-question chain:

1. 买什么服务器？选什么？
2. 为什么不选命令行，要选聊天框？
3. 为什么要用语音输入？
4. 怎么跟 GitHub 连起来？
5. 大概适合怎样的人？
6. 想象空间究竟有多大？
7. 为什么用它，不用 Codex、Claude Code 或那些客户端？

Killer insight: the agent is a "太监秘书" — everything usable in Cursor (Codex, Claude Code, browser tools) are its 小弟. She explicitly deprecated 宪法 as a theme ("强依赖模型能力…Bitter Lesson 式的问题") and wants ~3-min videos with the rest split into follow-ups.

## Verdicts on two AI-generated candidate scripts

| Dimension | Script A (no timestamps) | Script B (timed) |
|---|---|---|
| Hook | ✅ counterintuitive but abstract ("电脑控制权交出去") | ✅✅ best of all versions: "真正可怕的不是它失控——是它太听话了…彩虹屁" |
| User thinking | ❌ "省下决策疲劳" = empty abstraction | ✅✅ "三条可抄结论" for non-builders = strongest device |
| Structure | ❌ 5 parallel sections, no spine, 5-6 min | ✅ good rhythm, but 70s spent on 宪法 |
| Theme fit | ❌ missing 太监秘书 insight | ❌ core = 宪法 (Liz-deprecated theme) |
| Price anchor | ❌ absent | Partial (60 块 inside, not in hook) |

Common misses: no 数字员工/太监秘书 spine; no voice-input step; no "适合怎样的人"; both too long. Rule that emerged: check every candidate against (a) her stated theme, (b) price anchor, (c) 关我屁事/对我有屁用, (d) 3-min target — and put verdicts in a table.

## Accepted v3 skeleton

- 标题主推: 我给 AI 配了个秘书，Codex 和 Claude Code 全是它的小弟
- 开场 5s: "一个月 60 块钱，我给自己雇了个数字员工…全是它手下的小弟"
- 15s: 点破疑问 ("又是 AI 安利？关我什么事？") → 不需要会编程，只需要会聊天
- 一 聊天框 (Telegram 比 VS Code 轻, 不是段子是结论)
- 二 语音输入 (豆包输入法语音转文字)
- 三 服务器 (二核 4G 腾讯云 60 块, "我比过价")
- 四 GitHub 是身体的 (Obsidian/Notion 卸了)
- 五 太监秘书 (不是又一个工具，是所有 AI 工具的总管; Cursor 能用的都是小弟)
- 六 适合谁 + 丑话一句 (上下文超载; 连复制粘贴都懒得做就先别上车)
- 结尾: 想象空间 (电脑 = 住在云端随叫随到的执行者; 协作/雇佣/亲密关系被重新定价) + CTA (别买课别站队，花一个周末派一件本来就要干的事)
- 可裁剪: 2min 删二+四; 60s 只留开场+五+结尾

## 拆条 topics (follow-up 3-min videos)

1. 椅子论/先看屁股 (三种人框架)
2. 给 AI 立宪法 (反迎合 + 恍惚感 + /goal 照妖镜)
3. Harness Engineering — 把 Token 做成菜 (生啃食材 vs 加工)
4. 我把 Obsidian 扔了 (GitHub 文本底座)

## Compliance softening (domestic platforms)

- "不存在墙" → "墙的问题直接消失" (or softer)
- 中转站 / 5SIM 接码 / OAuth 绕过细节: never in 口播, keep in article/置顶评论 — judged as 引流/资质 risk.
- 竞品负面 (Kimi 不推荐): cut from video, separate topic or article only.

## DBS registration facts (environment)

- dbs-* family: `dontbesilent2025/dbskill`, installed via skills.sh CLI to `~/.agents/skills`, symlinked into writing profile skills (13 skills). Update: `npx skills update -g -y` (24 updated; ~20 seo-geo pack failures are a known separate issue).
- New symlinked skills appear in the Skill List only from the NEXT session; `skill_view` works immediately.
