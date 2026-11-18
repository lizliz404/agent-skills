---
archive: WquGuru — yetone 的魔法：magpie 是怎么让 AI 自己维护项目的
source: https://x.com/wquguru/status/2109650264601117141
conversation_id: "2109650264601117141"
---

author: WquGuru (@wquguru)
source: https://x.com/wquguru/status/2109650264601117141
published: 2026-10-12 22:19:53 Asia/Shanghai (UTC+8)
published_utc: 2026-10-12T14:19:53.000Z
post_id: "2109650264601117141"
article_title: "yetone 的魔法：magpie 是怎么让 AI 自己维护项目的"
engagement (API, 2026-11-18): bookmarks 2226, impressions 323055, likes 1158, quotes 28, replies 51, reposts 132

The post body is a link to an X Article. Full article text was returned by the API (`article.plain_text`). Chinese original, lightly wrapped:

关于全 AI 自动化构建软件该不该存在的问题，最近终于爆发了。起因是 @yetone 维护的 magpie，被同行喷“快餐式服务”、“不太敢用”。
相信大部分朋友已经有共识，AI 自动化构建软件是大势所趋，那么 magpie 是怎么实践的呢？我把 magpie 拉下来，分析了过去十来天的 2,862 个 commit，顺手拿 OpenClaw 做个对照。

19 天 1204 个版本
magpie 是个本地 LLM 网关，能把 Claude Code、Codex、Gemini CLI 这些编程 agent 接到任意模型和订阅上。9 月 22 日第一个 commit，到今天 19 天，9,474 星。2,862 个 commit 里 yetone 账号占 85%，合并了 383 个社区 PR。
tag 数（等同版本） 19 天高达 1,204 个，一天平均 60 多个版本，人手可发不出这个频率。对比之下，OpenClaw 头 19 天是 1,423 个 commit，99% 是 Peter Steinberger 自己提的，tag 大概 10 个。
magpie 的 commit 多了一倍，版本多了一百多倍。
我想搞清楚的就一件事：AI 在这个项目里到底是怎么闭环的。

一张路由表，一本错题本
magpie 的 CLAUDE.md 只引用了两个文件，AGENTS.md 和 LESSONS.md。
AGENTS.md 是张路由表，自己不写规则，只告诉 agent 干什么活之前翻哪份文档：改子系统先看 docs/subsystems/，写代码、审代码照 docs/code-standards.md，审社区 PR 看 docs/contributors.md。
LESSONS.md 第一句就回答了最开始的问题：
magpie's code is written, reviewed, merged and released by agents.
（magpie 的代码由 agent 编写、审查、合并和发布）

写、审、合、发，全是 agent。那没人盯着，它凭什么不翻车？答案就在这个文件里。479 行，说白了是一本错题本，而且是 agent 自己每晚写的。
每天夜里，agent 把当天的 commit 全过一遍，关注三个场景：
哪些修完又返工了
哪些压根不该合
哪些验证做得太糙
每揪出一个就记一条，一句规则，一段原因，后面挂上 commit 和 issue 号当证据。

关键是最后那行 Seen 1×。同一条教训，如果在 3 个不同日子的复盘里都出现了，就从 LESSONS.md 挪进 code-standards.md，从经验变成硬规则。之后每个 PR 审查都要逐条对。

错题本是 10 月 6 日凌晨才引入（commit 303819c5，10 月 6 日凌晨 3:10）。再往前一天，10 月 5 日，magpie 发了 168 个版本。LESSONS.md 第一版里就记着这天。220 个 commit，大约 170 次发版，其中 40 来个是在修当天或前一天刚发出去的版本。CI 几乎每一轮都被下一次 push 取消……于是第一版里就多了一条：打 tag 前，这个 commit 的 CI 必须跑完、全绿，被下一次 push 取消的不算。
168，第二天 42，第三天 15，之后一直在 15 到 26 之间。中间没人开会，也没人发通知。夜审翻出问题，往错题本里加了一条，后面干活的 agent 读到了，发版就慢下来了。

PR 验收标准、回退测试、真实使用、没跑的要写出来、`gh pr merge --match-head-commit`，以及 Human in the Loop（不要推翻已拍板的产品决定；安全闸门；社区建议进 commit 标题），见 the article and the first-party docs cited in `../yetone-loops.md`.

WquGuru also notes what is *not* in the repo: the nightly-review trigger, the review prompt, which agent, how many sessions. LESSONS.md update timestamps he listed (03:10, 03:49, 00:23, 23:46, 03:48, 14:24, 05:26) did not look like a cron to him.

These mid-October counts are his snapshots. Current repo counts are in `../due-diligence.md`. The peroration ("未来已来") is advocacy, not evidence.

---

author: WquGuru (@wquguru)
source: https://x.com/wquguru/status/2109458639501271530
published: 2026-10-12 09:38:26 Asia/Shanghai (UTC+8)
published_utc: 2026-10-12T01:38:26.000Z
post_id: "2109458639501271530"
engagement (API, 2026-11-18): bookmarks 121, impressions 61368, likes 234, quotes 14, replies 81, reposts 7

关于全 AI 自动化构建软件该不该存在的问题，最近终于爆发了。

这次事件的主角是 @yetone 的 magpie：
从 9 月 23 日建仓开始算，短短 19 天积累了 9200 星
版本号已经到 v0.1.1203，过去 24 小时发了 25 版

有人说：讲真不太敢用，有人说它是快餐式服务，作者则直接怒怼，自己掏钱订最贵的模型、7×24 小时在满足用户需求。

我梳理了一下整个过程，其实问题核心已经不是该不该了。全自动AI构建软件已经成为了现实，离广泛采用只是临门一脚， @yetone 作为时代的弄潮儿，被当成榜样学习还来不及呢 😄
