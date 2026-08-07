# CHANGES v0.3.3 — video-script-conversion

相对真源 `assets/video-script-conversion/`（v0.3.2）。草稿在 `out/`，**尚未合入 assets**。

## 变更表

| 改了什么 | 为什么 | 风险 |
|---|---|---|
| frontmatter `version: 0.3.2` → `0.3.3`；标题下增加 `> v0.3.3: …` 一行摘要 | 版本纪律：行为/契约兑现的微补丁走 patch | 低；无历史版本行可保留（原文件无 `> vX.Y.Z` 行） |
| Step 8 交付前自检：「重建 / 修整 / 实录修整」→ 追加「/ 补丁装配」 | 与 §3 模式④对齐，避免模式④任务漏勾 | 极低 |
| Support files 中脚本说明改为「双口径：汉字数 + 含标点总字符」 | 与 Step 10 文案一致，避免读者以为脚本只报一口径 | 极低 |
| `count_spoken_chars.py`：新增 `count_hanzi`；打印汉字数 + 含标点总字符两行；docstring 注明 CHECK_WORDS 为 geo-job 遗留 | 兑现 Step 10 已写明的双口径契约（独立复验：旧脚本无「汉字」字样） | 低；下游若解析单行输出需适配第二行。汉字正则覆盖基本区+扩展 A，罕见扩展汉字可能漏计 |

合入路径建议：用 `out/SKILL-v0.3.3.md` 覆盖 `SKILL.md`；用 `out/count_spoken_chars-v0.3.3.py` 覆盖 `scripts/count_spoken_chars.py`（文件名仍为 `count_spoken_chars.py`）。

## 未做（有意）

| 未做项 | 理由 |
|---|---|
| 不改 §2 硬原则措辞（含「口播字」含糊点） | 硬原则禁区；Step 10 已是操作澄清 |
| 不反向「优化」已知张力（语气词/口癖/真人先讲/故事感） | 已裁决禁区 |
| 不新增原则、不风格重写、不重排 Step/beats | 结构已收敛；边际收益为负 |
| 不改名/移动/删除 references | 契约；且非本轮必要 |
| 不自行脱敏/改写群聊摘录与绝对路径 | 公开发布约束：只报告位置与建议（见 AUDIT-REPORT §④） |
| 不内联 `cursor-agent` §3.9 全文 | 属扩展依赖说明，可后续加一句指针，不值得本轮膨胀 SKILL |
| 不改 `references/README.md`「第八个」过时句 | 属维护文案；建议合入时顺手改，可不单独占版本叙事 |
| 不为 references 批量补「与 SKILL 的关系」footer | 结构维护债，非内容/原则缺陷；README 已约定合入时再动 |
| 不改 CHECK_WORDS 默认列表内容 | SKILL 已明示 geo-job 遗留与跨题材自建；改默认易误伤既有工作流 |

## 验证

```bash
diff -u assets/video-script-conversion/SKILL.md out/SKILL-v0.3.3.md
python3 out/count_spoken_chars-v0.3.3.py <某 SCRIPT.md>   # 应见「汉字数」与「总字数(含标点)」两行
```
