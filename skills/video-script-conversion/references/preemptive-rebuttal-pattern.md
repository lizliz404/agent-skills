# 预反驳 worked example：真实群聊反馈 → 视频脚本（2026-07-31）

Context: Liz's video script (AI 数字员工/太监秘书, 3-min) needed real-human objections instead of imagined ones. Source: WeChat group "某 AI 工具社群" (weflow JSON export, 2715 messages, 2026-07-26~31, 4 members).

## Extraction shapes

**(a) 为什么没选 Hermes / 这套玩法** — objections cluster into four buckets:
- 界面论: "我不喜欢用telegram，好麻烦" / "memory管理呀，然后Agent tool的状态什么的。你都看不到"（成员A）
- 掌控感: "我自己要做项目的话，还是在自己电脑上面跑，Claude Code…我感觉更有掌控感一点"（成员A）
- 价格: "云服务器还蛮贵的"（成员A）
- 折腾: "gateway有时候还老出毛病" / "还得下一个tailscale来当服务器" / "但太麻烦了 这套系统"（成员B）

**(b) 他们对 Agent 的理解与实践**:
- 元代理 CEO 架构（成员B）："用一个当CEO，用来任务分配，但永远不执行具体任务…不被具体问题困住"
- "多Agent是去年trendy…现在都是harness agent在agent runtime里面跑"（成员A/成员B）
- AIPM 独立印证 IM 机器人 > 前端："做成一个接入IM的机器人的形式比做一个前端好 前端还是要填表格很麻烦"（成员C）

**(c) 差异与选择** — the gold: Liz's own live rebuttals from the SAME conversation:
- 掌控感 vs 云端爽感："后面就直接上云服务器了，爽死我了"（Liz）
- 贵 vs 便宜："我是没跑本地模型…跑的人里面大多数可能也是炮灰"（Liz）
- 看不到状态 vs GitHub 托管："先造一个类似Agent Context的GitHub Repo…GitHub就是最好的增删改查界面"（Liz）
- **隐喻诞生现场**: "卧槽…突然发现我现在已经在这样做了。相比于CEO，我称之为太监或秘书"（Liz，回应成员B的元代理架构）— the anchor metaphor's birth scene, usable as 花絮/置顶评论.

## Insertion pattern（密度合适，不要动太多）

Three insertions, each at the exact beat the objection targets, each = objection + her real response:

| 脚本位置 | 插入 | 来源对 |
|---|---|---|
| 一、聊天框 | "聊天框里看不到它干活的状态，配置也不直观。我的解法：长期配置单独放一个 GitHub 仓库…开始我也觉得别扭，后来就习惯了" | 成员A ← Liz ×2 |
| 三、服务器 | "贵不贵，看你跑什么——要跑本地大模型，几百块打不住；纯跑 Agent，几十块够用" | 成员A ← Liz |
| 六、丑话 | "第二句：把活儿交给云端的 AI，会丢掉一部分掌控感——我是主动交的…掌控感是药也是毒，值不值，自己坐一遍才知道" | 成员A ← Liz + 原文"过度追求掌控感可能是毒" |

## Traceability table (end of script file)

Each insertion documented: 反驳 → 来源引用/时间 → 回应出处. This makes every line defensible in comments and prevents drift into invented "假想观众".

## Rules extracted

- Never invent an imagined viewer's question when real voices exist.
- One objection per insertion; don't stack.
- Keep her own spoken rebuttals verbatim-ish (they're already in her voice, no rewriting needed).
- The birth-scene of the anchor metaphor is a credibility asset — record it.
