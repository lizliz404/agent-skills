# 豆包语音播客大模型 API 参考

> 独立于 TTS 的产品，需单独开通：https://console.volcengine.com/speech/service/10028
> 官方文档：https://www.volcengine.com/docs/6561/1668014
> Last verified against official docs: 2026-07-30

## 端点

```
wss://openspeech.bytedance.com/api/v3/sami/podcasttts
```

## 鉴权 (WebSocket Headers)

凭证与 TTS 共享（DOUBAO_TTS_APP_ID / DOUBAO_TTS_ACCESS_TOKEN），Header 名不同：

```
X-Api-App-Id:       <APP_ID>
X-Api-Access-Key:   <ACCESS_TOKEN>
X-Api-Resource-Id:  volc.service_type.10050
X-Api-App-Key:      aGjiRDfUWi  (固定值)
X-Api-Request-Id:   <uuid>      (可选，建议传)
```

响应头建议记录 `X-Tt-Logid` 以便排障。

## 二进制协议帧

V3 二进制 WebSocket 协议。**关键：播客端点 message_type=0b0001 (1)，不是 TTS 双向流的 0b0011 (3)。**

每帧结构：

| Byte | Left 4-bit | Right 4-bit |
|------|-----------|-------------|
| 0 | Protocol version (0b0001) | Header size (0b0001 = 4 bytes) |
| 1 | **Message type (0b0001)** | Flags (0b0100 = has event + session) |
| 2 | Serialization (0b0000=raw, 0b0001=JSON) | Compression (0b0000=none, 0b0001=gzip) |
| 3 | Reserved (0x00) |

Header byte 1 = `0x14`：`(0b0001 << 4) | 0b0100`

然后：event number (4 bytes int32 BE) + session_id length (4 bytes uint32 BE) + session_id + payload size (4 bytes uint32 BE) + payload

## 事件流（完整）

```
Client → StartSession (event=100, 含播客参数)
Server → event=150 (会话已启动, session started)
Server → event=360 (本轮对话文本, 含 speaker + text + round_id)
Server → event=361 (音频分片, binary, 持续流式)
Server → event=362 (本轮结束, 含 start_time + end_time + audio_duration)
Server → event=154 (用量信息, usage tokens)
... (多轮循环) ...
Server → event=363 (播客结束, 含 audio_url)
Server → event=152 (会话完成) / event=153 (会话错误)
Client → FinishConnection (event=2)
```

## 请求参数

### action 模式

| action | 模式 | 说明 |
|--------|------|------|
| 0 | 长文本总结 | 给文本/URL → AI 提炼 + 生成双人对话 → 合成 |
| 3 | 直接对话 | 给 nlp_texts 数组（每轮 speaker + text）→ 直接合成 |
| 4 | 联网搜索 | 给 prompt → AI 联网搜索 + 总结 → 合成 |

### 核心参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| action | int | 0 | 生成模式 |
| input_text | string | - | action=0 输入文本，最长 32k；与 `input_info.input_url` 二选一，都有则优先 text |
| prompt_text | string | - | action=4 必填；简单话题提示，无指令能力 |
| nlp_texts | []object | - | action=3 必填；每轮 `{speaker, text}`，单轮 ≤300 字，总 ≤10000 |
| input_info.input_url | string | - | 网页或可下载 pdf/doc/txt → 自动转长文播客 |
| input_info.only_nlp_text | bool | - | 只输出轮次文本，不生成音频 |
| input_info.return_audio_url | bool | - | 结束时 event 363 返回 `meta_info.audio_url`（约 1h 有效） |
| input_info.input_text_max_length | int | - | action=0 模型处理最大字符数，建议 ≤12000 |
| input_info.max_char_length_per_round | int | - | 每轮最大合成字符（优先句完整） |
| input_info.strict_audit | bool | false | 安全审核等级；true=严格（2026-05-12 新增；作用于 action 0/4 文本） |
| audio_config.format | string | pcm | mp3 / ogg_opus / pcm / aac |
| audio_config.sample_rate | int | 24000 | 16000 / 24000 / 48000 |
| audio_config.speech_rate | int | 0 | -50~+100, 0=正常 |
| speaker_info.speakers | []string | - | 恰好 2 个发音人 ID |
| speaker_info.random_order | bool | true | 谁先开口 |
| speaker_info.speaker_additions | map | - | TTS/ICL 音色额外参数（JSON string per speaker）；ICL 2.0 可用 `{"model":"seed-tts-2.0-standard"}` |
| use_head_music | bool | true | 片头音乐 |
| use_tail_music | bool | false | 片尾音乐 |
| aigc_watermark | bool | false | 结尾节奏水印（可听） |
| aigc_metadata | object | - | 隐式 meta 水印（mp3/wav/ogg_opus）；`enable` + producer/propagator ids |
| retry_info.retry_task_id | string | - | 断点续传：前一个 session_id（即 task_id） |
| retry_info.last_finished_round_id | number | - | 已完成的最后一轮 id |

## 发音人对

同系列配对效果更好。默认推荐（dayi + mizai，一男一女）：

- `zh_male_dayixiansheng_v2_saturn_bigtts` (dayi)
- `zh_female_mizaitongxue_v2_saturn_bigtts` (mizai)

备选（liufei + xiaolei，双男）：

- `zh_male_liufei_v2_saturn_bigtts`
- `zh_male_xiaolei_v2_saturn_bigtts`

官方 2026-03-20：除播客专属音色外，支持 TTS 与 ICL 复刻音色（复刻购买的 APPID 须与播客开通为同一 App；1.0/2.0 均可；不含 mix / 多情感音色）。TTS 音色列表：https://www.volcengine.com/docs/6561/1257544

## 响应事件

| event | 含义 | 处理 |
|-------|------|------|
| 50 | 连接已建立 | 内部状态，静默 |
| 150 | 会话已启动 | 确认 StartSession 被接受 |
| 153 | 会话错误 | 停止，解析 error 信息 |
| 360 | 本轮对话文本 | 含 speaker + text + round_id，可用于字幕 |
| 361 | 音频数据 | 二进制 payload，拼接成 MP3 |
| 362 | 本轮结束 | start_time + end_time + audio_duration，字幕对齐关键 |
| 363 | 播客结束 | audio_url 可用（1h 有效） |
| 154 | 用量信息 | usage token 统计 |
| 152 | 会话完成 | 发送 FinishConnection → event=2 |

## 字幕提取：播客 → 字幕 JSON

### 方案 A：从播客生成事件中提取（推荐，零额外成本）

播客生成过程中 event=360 返回每轮完整文本+speaker，event=362 返回 start_time/end_time。
脚本见 `scripts/podcast-generate.py`。**务必保存 event=360 的完整 payload**，不要只截前 80 字符。

### 方案 B：Flash ASR 转录已生成音频（独立 quota）

播客生成后，用 Flash ASR 转录音频获取字幕。**ASR 和播客是独立产品线，不共享 quota。**
端点：`POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash`
脚本见 `scripts/asr-transcribe.py`。
参数：`enable_speaker_info=true`（speaker diarization）+ `show_utterances=true`（时间戳）。
输出：`[{start, end, speaker, text}, ...]` JSON，可直接灌入前端字幕组件。

## Liz 默认偏好 (2026-07)

- action=0，用 TXT 原文
- format=mp3, sample_rate=24000, speech_rate=0
- speakers: dayi + mizai, random_order=false (男先开口)
- head_music=true, tail_music=true
- 所有 AIGC 水印关
- 输入前 strip MD 语法，保留纯文本
