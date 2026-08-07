# Worked example: 做题家 vs 出题家口播（2026-08-04）

用途：失败 AI 初稿当反例、金字塔交付、Hermes+Composer 双轨开场分叉、工具点名拍板。项目目录：`writing/2026-08-04/videoscript-tizaojia-vs-chutijia/`。

## 素材形态

- Liz 口语碎念（做题家/出题家、How vs What·Why、铲子与矿、RaaS vs feeling of progress、飞书 Voice Agent / N8N / 360 类比）
- 王川长引（框架支撑，口播只取 1–2 刀，不展开 22 条）
- raw 后半附 **两篇 AI 候选口播** + Liz：「无论 raw 还是两篇初稿效果都不算太好」→ 候选 = 失败对照，不是润色底稿

## 失败初稿病（诊断表，可复用）

| 型 | 病征 | 本条实例 |
|---|---|---|
| 摘要腔 / clear-soup | 正确、顺、钩子弱，像说明书 | 金字塔「简版」把金句磨平 |
| Sheeran mean | 舞台指示、emoji 章节、工业包装 | 「怼脸加长版」`〔开场·直视镜头〕` 过多 |
| 超时长 | 4–5 分钟硬塞 | 加长版未给可裁剪纪律 |
| 发明事实 | 课价、精确年龄人设 | 「999 课」「五十多岁」类（raw 无） |

**动作**：notes 里写诊断 → 模式①从原话重建 → 禁止「在初稿上改顺」。

## Anchor（钉死）

做题家囤工具 = Feeling of Progress 消费，不是 Result as a Service；先有矿的假设再选铲子。  
禁止主菜：认知内卷 / 知道≠做到 / 纯励志元认知鸡汤。

## 双轨结果（实测字数）

| 轨 | 文件 | 汉字 | 含标点总字符 | 开场策略 |
|---|---|---|---|---|
| Hermes v0.1 | `SCRIPT-v0.1.md` | ~793 | ~1048 | **命题先入**：「为焦虑付费」 |
| Cursor composer-2.5 v0.2 | `cursor-audit/SCRIPT-v0.2.md` | ~851 | ~1121 | **症状先入**：Mac/Windows → 停一下你在买进步感 |

英文专名（How / Result as a Service / FOMO / N8N…）抬高总字符——以汉字估时长；勿为压总字符砍锚点金句。

## 有增量的差分（合并时比这些，不和稀泥）

1. **开场**：症状先入通常「关我屁事」更强；命题先入标题钉子感更强 → 可缝合（封面用命题，口播开场用症状）。
2. **金句回补**：螺蛳壳里做道场 / 局部最优 — v0.1 易弱化，Cursor 常回补。
3. **工具点名**：OpenClaw/Hermes raw 有 → 泛化须标拍板，禁止静默砍；点名更对号、更时效。
4. **合规**：Telegram →「聊天软件」；压字时勿把合规半句当填充词误删。
5. **金字塔**：一句话版 + 一段话版 + 完整口播 — Liz 本条明确要求，交付格式默认带上。

## Cursor workspace 最小包（本条验证）

`handoff.md`（用户原话逐字）+ `assets/{raw,SCRIPT-v0.1,notes}` + `skill-refs/{SKILL,koupi,anti-slop,user-thinking,count_spoken_chars.py}` → 只写 `cursor-audit/`。  
角色标注：raw 最高优先；失败初稿 = 反例；v0.1 = 对照非唯一正确答案。

## 与 SKILL 的关系

可执行规则以 SKILL.md 为准（Pitfalls：失败初稿 / 点名拍板 / 开场二选一；§2 交付金字塔；Step 8 格式）。本文是证据/工作例。
