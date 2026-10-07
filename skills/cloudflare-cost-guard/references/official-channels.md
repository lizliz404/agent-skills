# 官方能力与核验入口

初次核对：2026-10-07，通过 EXA 检索并读取 Cloudflare 官方页面。
2026-10-08 融合审查重新核对 Budget、Custom Alerts、DO alarms、R2 analytics/pricing
与 token 权限；其他条目仍为 2026-10-07 资料快照。邮件来源见 delivery.md。
这是资料快照，不是账号开通、完整覆盖或生产送达的证据。套餐、Beta、API 与价格可能变化；
实施时只刷新影响当前任务的条目，不重新做泛化行业调研。

## 原生告警

- [Budget alerts](https://developers.cloudflare.com/billing/manage/budget-alerts/)：
  Pay-as-you-go 账号可在 Billing → Billable Usage 设置账号累计用量支出美元阈值及邮件。
  每账期触发后重置；只通知，不暂停/封顶。产品页面创建的预算也不应误写成只针对该产品。
- [Billable Usage](https://developers.cloudflare.com/billing/manage/billable-usage/)：
  日粒度、按产品的用量超额费用，需 Billing Read，与发票计费系统同源。
  不包括固定订阅，不视为秒级信号。早期发布说明与当前指南的阈值措辞不同，实施以当前配置及指南为准。
- [Custom Alerts (Beta)](https://developers.cloudflare.com/notifications/notification-available/)：
  定时 SQL 查询，支持阈值、异常检测和 SLO。多数支持的数据集最低检查间隔 1min，
  Log Explorer 最低 10min；重复通知默认 1h，与查询间隔分开。
  异常检测至少需要 30min 历史；无返回行没有信号，不能把告警安静当成数据健康。
  官方检查间隔不等于数据新鲜度或投递时延保证。
- [Webhook 配置](https://developers.cloudflare.com/notifications/get-started/configure-webhooks/)：
  2026-10-02 文档明确所有套餐可用，没有付费 zone 的账号最多 100 个目标。
  Generic webhook 仅投递到可公开解析的地址、端口 80/443，可用 cf-webhook-auth 校验秘密。
  Save and Test 是实际发送动作；配置不等于送达。原生支持不意味着 Telegram 无需适配。
- [Alerting API](https://developers.cloudflare.com/api/node/resources/alerting/)：
  查可用类型、投递资格、规则和发送历史。预算设置与普通 Notifications 不假定共用配置接口。
  现成 usage alert 的产品范围与资格要从当前账号读取，不能假设 covers-all。

## 数据覆盖与口径

- [SQL 数据集](https://developers.cloudflare.com/analytics/sql-api/datasets/)：
  用 `GET /client/v4/analytics/sql/introspection?account_tag=ACCOUNT_ID` 发现当前目录，
  需 Account Analytics Read。目录随部署和账号变化；字段存在还需真实查询授权。
  `events` 是事件，`states` 是观测快照，`logs` 是日志；存储快照不能随意求和。
  Custom Alerts 消费 SQL API 数据集，不能直接使用 GraphQL 数据集名字。
- [SQL API 限制](https://developers.cloudflare.com/analytics/sql-api/limits/)：
  单条 SELECT、一个数据集、一个账号、下界时间约束；字段、保留期、查询跨度、分页限制随数据集/套餐变化。
  429/503/507 等错误要保留并有界退避，遵守 Retry-After。
- [DO analytics](https://developers.cloudflare.com/durable-objects/observability/metrics-and-analytics/)：
  GraphQL 提供调用、周期、存储与子请求数据。长连接某些请求指标在连接结束后才出现，
  只看 invocation 请求量不足以证明没有长期占用。
- [R2 analytics](https://developers.cloudflare.com/r2/platform/metrics-analytics/)：
  GraphQL 的 operations / storage / bandwidth；存储包括 payloadSize、metadataSize、objectCount、uploadCount。
  文档列出最长 31 天查询跨度。确认所在 jurisdiction 的桶名及实际数据时间。
  带宽指标不覆盖所有小传输，不能把带宽图当成准确操作账单。
- [用量计费产品](https://developers.cloudflare.com/billing/understand/usage-based-billing/)：
  由实际绑定与账单确认适用产品；日志、图像、Stream、AI 等不因核心监控没列出而消失。

## 保护措施与边界

- [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) 与
  [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/)：
  CPU limits 约束单次 CPU，网络和存储等待不算 CPU。
  Workers Paid 无普通日请求总上限；单次限额不能当账号总预算。
- [DO alarms](https://developers.cloudflare.com/durable-objects/api/alarms/)：
  抛异常自动退避重试最多 6 次，只适用于最近一次 setAlarm。
  处理器自行重新安排 alarm 可持续运行；deleteAlarm 在运行中的 handler 内阻止重试只是 best effort。
  不能从这些机制推出应用已经具备总尝试上限或停止条件。
- [DO pricing](https://developers.cloudflare.com/durable-objects/platform/pricing/)：
  核对 compute 请求、wall-clock duration 和对应存储后端读写。
  setAlarm 本身也计写操作，未休眠的对象可能产生 duration 费用。
- [Workers Rate Limiting](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/)：
  Worker 内部检查、按地点维护、最终一致，不是严格全球预算账本。
- [R2 public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/)：
  自定义域名支持缓存/WAF/访问控制，r2.dev 不具备同等能力，且保留该入口会绕开另一域名的保护。
- [R2 lifecycles](https://developers.cloudflare.com/r2/buckets/object-lifecycles/) 与
  [R2 pricing](https://developers.cloudflare.com/r2/pricing/)：
  清理/转存规则不是即时容量上限；默认七天清理未完成 multipart，不等于已完成对象会过期。
  按 storage class、操作类别和免费额度估算；公网出站带宽免费不等于操作免费。
  Infrequent Access 还有取回与最低保留期计费，不能默认转存一定更省。
- [Queues retries](https://developers.cloudflare.com/queues/configuration/batching-retries/)：
  max_retries、退避、逐条 ack、DLQ 可控制重送；重试仍计操作费用，应用重新入队要单独追踪。

只有经当前账号证明的覆盖才能用于上线结论。原生指标缺口可由现有监控补读，
无需先新增日志全量采集、供应商或付费服务。
