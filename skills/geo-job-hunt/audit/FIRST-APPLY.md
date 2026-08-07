# 首投操作指引(解锁 OK_UNVERIFIED)

> **前置**: 猎聘限流已恢复(`probe_limit.py` 有 stdout「✅ 猎聘限流已恢复」)。  
> **目的**: 用 **1 次**真实 `user-apply-job` 拿到原始响应,把 `OK_UNVERIFIED` 变成可文档化的契约。  
> **来源**: feedback-1 复核结论;非代码优化,是数据解锁。

---

## 0. 选岗原则

- 真实在招、你愿意投、结果不敏感(拒了也无所谓)
- hunt JSON 里必须有 **`jobId` + `jobKind`**(缺 kind 的岗先不要用)
- 优先从近期 `geo_job_hunt forward` 输出里选,避免手填 id

---

## 1. 确认限流已恢复

```bash
cd ~/.agents/skills/geo-job-hunt
python3 scripts/probe_limit.py
# 有「✅ 猎聘限流已恢复」再继续;无输出 = 仍限流,停止
```

---

## 2. 准备 hunt JSON(若还没有)

```bash
python3 scripts/geo_job_hunt.py forward \
  --address "你的圆心" --radius 3000 --city 杭州 \
  --job "实习" --max-companies 5 \
  --format json --out /tmp/first-hunt.json
```

检查 `/tmp/first-hunt.json` 目标岗含 `jobId`、`jobKind`。

---

## 3. 先 dry-run

```bash
python3 scripts/apply_batch.py \
  --hunt /tmp/first-hunt.json --max 1 --dry-run \
  --out /tmp/first-apply-dry.json
cat /tmp/first-apply-dry.json
```

---

## 4. 真实投递(仅 1 个)

```bash
python3 scripts/apply_batch.py \
  --hunt /tmp/first-hunt.json --max 1 \
  --out /tmp/first-apply-report.json \
  --tracker-file ~/.geo-job-hunt/apply-list.json
```

**立即保存**:
- `/tmp/first-apply-report.json` 全文(含 `raw` 字段)
- 终端 stderr/stdout

---

## 5. 投递后人工闭环

1. 24h 内看猎聘 App 消息 + 短信
2. `python3 scripts/apply_tracker.py due`
3. App 内核对后 `set --id <id> --status interviewing|rejected` 或 `--checked`

---

## 6. 用响应更新 skill(下一轮,非本次 agent)

根据 `raw` 响应判断:

| 观察 | 建议动作 |
|---|---|
| 明确成功字段(如 code=0 / success=true) | 收紧 `classify_business_payload`;更新 SKILL「apply 成功形态」 |
| 明确失败字段 | 补充 FAIL 规则 |
| 仍模糊 | 保持 OK_UNVERIFIED,再投 1 个不同 jobKind 交叉验证 |
| `jobKind` 与 hunt 字段对应关系清晰 | 文档化枚举或映射表 |

可选:把脱敏后的 `raw` 存 `logs/apply-samples/YYYY-MM-DD.json`(gitignore 已排除 logs)。

---

## 7. 禁止事项

- 限流中「试一把」(`probe` 无输出仍 apply)
- 一次 `--max` > 3(共用配额,且无成功样本前无意义)
- 把 token 或完整响应贴进 git commit

---

*patch-round2 · 限流恢复后由人执行*
