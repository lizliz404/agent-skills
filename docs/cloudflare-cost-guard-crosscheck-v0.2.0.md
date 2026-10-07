# Cloudflare Cost Guard：交叉验证与融合结果

日期：2026-10-08。成果是一个 `cloudflare-cost-guard`，版本 **0.2.0**。保留官方能力优先、现有监控复用、用量1h / 存储6h / 账单每天、正常静默。融合的是执行规程；不把规程交付当成监控上线。

## 输入和可核验范围

| 输入 | 本轮能确认什么 |
| --- | --- |
| Artemis首版，commit `c1e9b4e1feb168e7ac829493b176665f279fcba5` | 读取完整skill与官方参考；审查前冻结文件hash |
| Vesper独立首版MD和ZIP，0.1.0 | 读取5个文件；ZIP CRC通过，SHA256与MD一致；12个声明式场景 |
| Vesper运行报告 | 报告称17个隔离单元测试通过，以及SMTP/IMAP/OAuth/Telegram实践；包内没有对应监控源码、测试runner或原始投递收据，本轮未复验 |

Vesper ZIP SHA256：`f40450377aedf62c2372d787fc07b2fcb71bfb066c8399bdfd277d0dd85e923e`。
“未先阅读对方首版”是提供方对写作过程的声明；本轮验证包内容与hash，不验证写作过程。

## 融合取舍

| 项目 | 处理及原因 |
| --- | --- |
| 官方能力、完整公开入口与后台计费依赖 | 保留Artemis规则，避免只查首页或把预算邮件当硬上限 |
| 降频的耦合问题 | 吸收Vesper：窗口、水位、阈值、失败时限、watchdog、超时、防重入一起调整 |
| 补跑累计量 | 补充两版均欠明确的规则：采集覆盖窗口与阈值评估窗口分开；4h总量不直接对比1h阈值，也不以平均值排除尖峰 |
| API探针失败 | 修正Vesper SKILL.md原第59行：局部权限失败仅暂停该能力；不能停止仍可读的用量能力 |
| 空数据健康 | 修正Vesper原第80行并明确共享合同：真空、错误、过旧、缺权限、截断分别记录，成功空不等于零账单 |
| Telegram投递 | 保留待发事件跨恢复、真实sender契约检查、历史补发时间与当前状态；不把某一bridge的行为推广到所有工具 |
| Gmail周报 | 吸收可复用的发送/读取权限分离、测试外发隔离与OAuth期限；保持条件分支，不强制gws、IMAP或邮箱管理 |
| Vesper本机历史与17个测试 | 不放成公共skill的运行事实或通用默认；审查报告保留证据归属 |
| 场景文件 | 吸收12个场景，修正token、旧开关及SMTP/OAuth场景；新增局部权限、有效空、补跑窗口和只审查不部署，共16个 |
| Codex元数据 | Vesper顶层author/version未通过本机Codex quick_validate；融合版沿用metadata结构。该结果不代表所有Agent都拒绝Vesper原格式 |

正式入口保持一个名字；没有发布第二个职责相同的Vesper入口。公共文件不包含实际账号、收件人、凭据位置或运行日志。

## 官方事实复核

- 预算邮件按账期累计用量支出触发，不暂停、不封顶；两版判断一致。[Cloudflare Budget alerts](https://developers.cloudflare.com/billing/manage/budget-alerts/)
- Custom Alerts查询频率与重复提醒频率分开，数据集与账号资格影响覆盖；安静不证明采集健康。[Available alerts](https://developers.cloudflare.com/notifications/notification-available/)
- DO最多六次失败重试只对应最近一次setAlarm；应用重新安排alarm仍可能持续执行。[DO alarms](https://developers.cloudflare.com/durable-objects/api/alarms/)
- token权限按能力和资源授权；某资源读取错误不自动证明整把凭据失效。暂停局部能力是基于此权限模型的实施判断。[Create API token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- R2操作、存量与带宽是不同指标；存量快照不应加总成费用。[R2 analytics](https://developers.cloudflare.com/r2/platform/metrics-analytics/)、[R2 pricing](https://developers.cloudflare.com/r2/pricing/)
- gmail.send不授予读信能力，getProfile不接受send-only；不得为验收发送而扩成读取权限。[Gmail scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)、[getProfile](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users/getProfile)
- External Testing且包含Gmail scopes的OAuth refresh token存在七天期限；此事实限定对应OAuth渠道，不自动使独立SMTP渠道失效。[OAuth refresh expiry](https://developers.google.com/identity/protocols/oauth2#expiration)
- gws仓库说明它不是Google正式支持产品；融合版将其列为可选客户端。[googleworkspace/cli](https://github.com/googleworkspace/cli)

以上是文档复核，不是两个账号当前权限、资源、费用或告警配置的读回。其他官方条目保留2026-10-07资料日期，实施时刷新相关项。

## 验证口径

已完成：ZIP完整性与hash、相对引用、JSON与16个唯一场景、Codex skill格式、UI元数据、可见私密标识模式扫描、git diff检查。模式扫描未发现匹配，不代表证明不存在任何秘密。

两份原稿分别接受16个请求的独立指令试跑，共32条判断；验证者未获得预期答案。试跑复现了局部权限与有效空规则的歧义，以及首版补采规则不够具体的问题。另一个新上下文验证者仅拿融合版和原始场景做复核：16例均能由规程支持适当决策，未发现可复现的指令矛盾；每例都标记 runtime_verified=false。这只说明给定场景的规程审查结果，不能证明监控程序正确。逐例判断摘要如下；完整隔离推演记录在本轮审查工作目录保留。


| 场景 | 融合版指令试跑判断 |
| --- | --- |
| native-first | HTTP目录不推导DO/R2覆盖 |
| hourly-migration | 窗口、水位、阈值、watchdog联动 |
| token-denied | 过期凭据停用，局部403保留可读能力 |
| r2-growth | 增长趋势不直接定义紧急成本风险 |
| alarm-loop | 六次重试不限制应用自重排 |
| false-send | 核验sender契约，恢复不删除pending |
| stale-healthy | 进程完成不等于数据完整成功 |
| smtp-vs-oauth | SMTP收据与OAuth长期期限分别判断 |
| unit-test-production | 隔离凭据、状态、所有外发与setup副作用 |
| readonly-switch | 从fixture识别写状态，不从参数名猜只读 |
| telegram-only | 不强制邮件/gws/邮箱整理 |
| delivery-before-handoff | 新覆盖和投递验收前不退唯一有效监控 |
| scope-specific-403 | active不等于全权限；保留合法用量读取 |
| legitimate-empty | 成功空、当前不适用、未知分别记录 |
| window-catchup | 4h汇总与平均数均不证明小时尖峰 |
| review-only | 只融合规程，不安装或部署 |

未执行：生产监控、Cloudflare账号采集、真实通知、Vesper的17个单元测试、定时器迁移、OAuth发布或双机移交。这些未验证项不阻止完成skill融合，但不能据此宣布持续监控已上线。

## 可复用目录

```text
cloudflare-cost-guard/
├── SKILL.md
├── agents/openai.yaml
├── references/official-channels.md
├── references/monitoring.md
├── references/delivery.md
└── evals/scenarios.json
```

主入口仅增加关键判断与路由；运行窗口与投递细节按需读取。完整skill目录与本报告直接在仓库阅读，不另外交付ZIP。仓库继续使用原分支与Draft PR #5；并非生产部署或PR合并。


融合提交：`528a83731598b87f243b87906a0256ef8edbc629`。


[Draft PR #5](https://github.com/lizliz404/agent-skills/pull/5)继续作为审阅入口。
