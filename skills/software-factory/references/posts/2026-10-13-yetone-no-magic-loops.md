---
archive: yetone — no magic, three Claude Code loops, nightly UI/UX
source: https://x.com/yetone/status/2109855710444237018
conversation_id: "2109855710444237018"
api_status: "not authorized to see the post (2026-11-18 public X API)"
text_source: "Independent public mirrors agreed on the wording: TodayRss, XPut, Zhihao, Tony's Lab, Today for AI (URLs in source-index.md)."
---

author: yetone (@yetone)
source: https://x.com/yetone/status/2109855710444237018
published: 2026-10-13 11:56:15 Asia/Shanghai (UTC+8)
published_utc: 2026-10-13T03:56:15.250Z
post_id: "2109855710444237018"
quoted: "2109650264601117141" (WquGuru's article, per mirrors)
engagement: not available from the API. One mirror (Zhihao) showed "44.3K Views" at the time it captured the post; that figure was not re-verified.

很多人想让我分享一下工作流，我一直没想好怎么分享，因为其实我没有任何的魔法，甚至还特别简陋，总觉得分享出来毫无意义。其实我就是用 Claude Code，然后用官方的 Opus 5.5 模型执行 loop 就可以了。

我会并行执行图里的 3 个 loop，然后每晚抽一点时间铲铲屎（主要是 UI/UX 的问题），然后就没活儿了。

The post included three screenshots of `/loop` prompts (media not retrievable via the API). Consistent transcriptions of those prompts, in the original Chinese, from Tony's Lab (2026-10-14) and Today for AI:

LOOP-01:

> /loop 盯一下 GitHub issues，仔细分析，看看哪些是值得修复和实现的，修复或者实现后记得发版和回复，如果不值得修复或者实现也要回复，如果是中转站的广告商，就统一回复：感谢关注，日后会出相关合作方案，敬请期待。而不能一股脑地把第三方中转站直接加到我们产品里面。也要盯一下GitHub的PR，然后你要认真的去review PR的每行代码、每个逻辑，你要把代码拉下来实际跑一下，验证一下是否没有 bug。因为我怕有的人提的PR，是无脑用Coding Agent乱写的，自己都没测过。所以你要看一下他这个PR，是否有问题，确保一切都没有问题，且实际验证过之后也没有问题的话，你才能够去合并，否则你就去回复一下这个PR或者关掉 PR。
> 另外还要监控一下 Magpie Discord Server 里用户的反馈，实时的加入讨论，如果有有价值的反馈和建议，就去做修复跟添加新的功能。如果值得进一步讨论，那就继续讨论。记得查看 Magpie Discord Server 里所有的 channel，一个都不能漏掉！记得在 Discord 里要真实地 at 人，而不是只叫名字，不然对方收不到你的消息！

LOOP-02:

> /loop 盯一下推特上关于 magpie 的反馈，如果是有价值的反馈，或者是真实可复现的 bug，那么就去做实现或者修复。完毕后记得上线，上线后记得回复推特
>
> 你应该先用便宜的决策模型比如 jev 去判断推文是不是与 magpie 相关，是不是 magpie 的反馈，如果不是直接忽略不要把内容转发给你，不然太浪费 Token 了

LOOP-03:

> /loop 现在 magpie 完全是自动化更改代码和合并社区里的 PR，你要定时清理一下屎山代码和恶意代码防止项目变得难以维护以至于变废，并总结出经验教训，比如哪些是不应该合并的哪些是验证不缜密的等等放到经验中防止以后的 agent 犯同样的错误，以及要把老是提低质量代码的人拉入黑名单

Comment-thread replies attributed to yetone by Tony's Lab and Today for AI were not independently retrieved (same API restriction). They are summarized, not treated as API-verified text, in `../yetone-loops.md`.
