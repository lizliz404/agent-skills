# references 维护约定

> 规则权威在 `SKILL.md`。本文档只约定 references 的维护方式，不改各 reference 的 raw 存档与提取表正文（合入时只动文末「与 SKILL 的关系」段和落点指针）。

## 权威分层

| 层 | 文件 | 角色 |
|---|---|---|
| 规则 | `SKILL.md` | 唯一操作权威：硬原则、模式、步骤、门禁 |
| 证据 | `references/*.md` | raw 原文、提取表、工作例、对比表、元 prompt 存档 |

## 文末段统一格式

```text
## 与 SKILL 的关系
本文是证据/存档。可执行规则以仓库内 SKILL.md 为准。
若提取表与 SKILL 表述冲突，以 SKILL + Liz 当场裁决为准，再回头改本文。
```

## 各文件职责（保持现状，不合并）

| 文件 | 留它的理由 |
|---|---|
| dbs-five-dimension-audit | 审计模板；外部包的本地缩略 |
| worked-example-2026-07-31 | 转换会话 + 裁决表 + 拆条（过程证据） |
| worked-example-digital-employee-2026-08 | 口播 raw + 12 devices（产物证据） |
| preemptive-rebuttal-pattern | 真人反馈→插入的工作例 |
| user-thinking-blogger-2026-08 | 外源范本；明确「学 devices 不抄文风」 |
| anti-slop-mantra-2026-08 | 录制复盘原文 + 开场对比 |
| ip-content-meta-prompt-2026-08 | 元 prompt 逐字存档；§5 的源 |
| worked-example-ai-psychosis-2026-08 | 反平庸选题重锚工作例 |
| worked-example-tizaojia-2026-08 | 失败初稿反例 + 金字塔 + 双轨开场分叉 + 工具点名拍板 |
| patch-list-refine-geo-job-2026-08 | 模式④补丁装配工作例 |
| koupi-voice-profile-2026-08 | 口癖细则（操作型 vs 排泄型） |
| koupi-raw-discussion-2026-08 | 口癖讨论原始全档 |

07-31 与 digital-employee-2026-08 同主题、不同职责，**不要合并**。

## 落点指针维护

SKILL 重排（Step 编号/beats 改名）后，必须同步检查各 reference 里的「落点」表述（如「Step 4.6」→「Step 6」、「beat 5a」→「落地 beats」）。遇 SKILL 结构变更，先 grep references 里的 Step/beat 引用再合入。

## 不建议做的事

- 把 raw 范本再贴进 SKILL
- 不为「对称」硬凑新 reference（现在的文件数已远超初版，新增只看真实边际价值）
- 删减元 prompt 存档（Liz 要逐字可回指）
