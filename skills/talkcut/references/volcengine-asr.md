# 火山引擎豆包语音 · 大模型录音文件识别（talkcut 用法）

官方文档：大模型录音文件识别标准版 <https://www.volcengine.com/docs/6561/1354868> ，极速版在同一目录（「录音文件识别大模型极速版」）。新版控制台：<https://console.volcengine.com/speech/new/overview>

## 开通（需要用户本人操作）

1. 登录新版豆包语音控制台 → 开通「录音文件识别大模型」（极速版 `volc.bigasr.auc_turbo`；长音频再开标准版 `volc.bigasr.auc`）。
2. 「API Key 管理」创建 Key → 本机 `export DOUBAO_API_KEY=...`，或写进 `~/.agents/env/doubao-tts.env`（与本仓库 doubao-tts 技能共用）。
3. 旧版控制台用户：`VOLC_APP_ID`（APP ID）+ `VOLC_ACCESS_TOKEN`（Access Token），对应请求头 `X-Api-App-Key` / `X-Api-Access-Key`。

## 接口

| 版本 | 地址 | Resource-Id | 方式 |
|---|---|---|---|
| 极速版 | `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash` | `volc.bigasr.auc_turbo` | 同步，base64 直传 |
| 标准版 | `…/api/v3/auc/bigmodel/submit` + `…/query` | `volc.bigasr.auc` | 异步，query 需带回 submit 的 `X-Tt-Logid` |

公共请求头：`X-Api-Key`（或 App-Key/Access-Key）、`X-Api-Resource-Id`、`X-Api-Request-Id`（UUID）、`X-Api-Sequence: -1`。
状态在**响应头** `X-Api-Status-Code`：`20000000` 成功，`20000001` 处理中，`20000002` 排队，`20000003` 静音。处理中时 body 为空结果，不是失败。

请求体（talkcut 只开这些）：
```json
{"user": {"uid": "talkcut"},
 "audio": {"data": "<base64>", "format": "mp3"},
 "request": {"model_name": "bigmodel", "enable_itn": true, "enable_punc": true,
             "enable_ddc": false, "show_utterances": true}}
```
`show_utterances: true` 时 `result.utterances[]` 每句带 `start_time/end_time`（毫秒）和 `words[]`（每个字的 `text/start_time/end_time`）。这就是剪辑需要的全部时间信息。

## 省钱原则

- 先 16 kHz 单声道 mp3（`prep.py` 已处理），体积小、识别效果不变。
- 不开 `enable_speaker_info`（单人口播用不到）、情绪/性别/语速等附加识别。
- `enable_ddc`（顺滑）必须关：它会把「嗯」和重复删掉，我们恰恰要靠这些判断剪哪里。
- 同一素材不要重复识别；`transcript.raw.json` 已缓存原始结果，可用 `asr_volc.py --normalize` 重新生成。

参考实现：本仓库 `skills/doubao-tts/scripts/asr-transcribe.py`；[lcbuaaliu/ai-jian-koubo](https://github.com/lcbuaaliu/ai-jian-koubo) 的 `volcengine_v3_transcribe.sh`。
