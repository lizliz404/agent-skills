# Doubao TTS V3 Streaming & TTS 2.0 Reference

Last verified against Volcengine docs: 2026-07-30.

Official docs:
- Bidirectional WS: https://www.volcengine.com/docs/6561/2532486
- HTTP Chunked/SSE unidirectional: https://www.volcengine.com/docs/6561/1598757
- Voice list (TTS 2.0): https://www.volcengine.com/docs/6561/1257544
- Async long-text TTS: https://www.volcengine.com/docs/6561/1829010

**Production article audio still uses V1 HTTP** (`/api/v1/tts`). Use V3 only for real-time / streaming / migration experiments.

## Endpoint matrix

| Endpoint | Protocol | Input | Output | Best for |
|---|---|---|---|---|
| `wss://openspeech.bytedance.com/api/v3/tts/bidirection` | WebSocket bidirectional | Streaming text chunks | Streaming audio | LLM realtime / chat voice |
| `wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream` | WebSocket unidirectional | Full text once | Streaming audio | One-shot stream without chunked text |
| `https://openspeech.bytedance.com/api/v3/tts/unidirectional` | HTTP Chunked | Full text once | Streaming audio | HTTP-only clients |
| `https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse` | HTTP SSE | Full text once | Streaming audio | Browser/SSE clients |

## Auth headers

**New console (API Key):**

```text
X-Api-Key: $DOUBAO_TTS2_API_KEY
X-Api-Resource-Id: seed-tts-2.0
X-Api-Connect-Id: <uuid>          # bidirectional; recommended for tracing
X-Control-Require-Usage-Tokens-Return: *   # optional; return billed char counts
```

**Old console (App ID + Access Token):**

```text
X-Api-App-Id: $DOUBAO_TTS_APP_ID
X-Api-Access-Key: $DOUBAO_TTS_ACCESS_TOKEN
X-Api-Resource-Id: seed-tts-2.0
```

### Resource ID → model / billing

| X-Api-Resource-Id | Model / product | Billing product |
|---|---|---|
| `seed-tts-2.0` | 豆包语音合成模型 2.0 voices | 语音合成2.0字符版 |
| `seed-tts-1.0` | 豆包语音合成模型 1.0 voices | 语音合成1.0字符版 |
| `seed-tts-1.0-concurr` | TTS 1.0 concurrent | 语音合成1.0并发版 |
| `seed-icl-2.0` | 声音复刻 2.0 | 声音复刻2.0字符版 |
| `seed-icl-1.0` / `seed-icl-1.0-concurr` | 声音复刻 1.0 | 声音复刻1.0字符/并发版 |

Voice/resource mismatch → `resource ID is mismatched with speaker related resource`.

## Bidirectional session baseline

Endpoint: `wss://openspeech.bytedance.com/api/v3/tts/bidirection`

Protocol helpers (from ByteDance sample / `TTS Websocket Bidirection protocols.zip`):
`start_connection` → `start_session` → `task_request` chunks → `finish_session` → `finish_connection`.

Collect `MsgType.AudioOnlyServer` until `EventType.SessionFinished`.

Session `req_params` baseline:

```json
{
  "req_params": {
    "speaker": "zh_female_vv_uranus_bigtts",
    "audio_params": {
      "format": "mp3",
      "sample_rate": 24000
    }
  }
}
```

### audio_params (verified)

| Field | Notes |
|---|---|
| `format` | `mp3` / `pcm` / `ogg_opus` / `wav`. Streaming prefers `pcm`; avoid `wav` (repeated headers). |
| `sample_rate` | 8000, 16000, 22050, 24000, 32000, 44100, 48000 |
| `bit_rate` | bps; mp3 only; typical range 64000–160000 |
| `speech_rate` | −50…100 (−50=0.5×, 100=2.0×) |
| `loudness_rate` | −50…100 |
| `enable_subtitle` | TTS 2.0 only; zh/en word timestamps via `TTSSubtitle` events |

### Useful additions (JSON string in V3 HTTP / WS)

| Field | Default | Notes |
|---|---|---|
| `disable_markdown_filter` | false | true → strip MD markers before speak |
| `disable_emoji_filter` | false | |
| `enable_latex_tn` | false | education; raises latency |
| `explicit_language` | unset | zh-cn / en / ja / es-mx / id / pt-br / ko / … |
| `explicit_dialect` | unset | dongbei / shaanxi / sichuan (dialect-capable speaker required) |
| `aigc_watermark` | false | audible end marker |
| `cache_config.use_cache` | false | pair with `text_type: 0` |

ICL 2.0 model variants via `req_params.model`:
- `seed-tts-2.0-standard` (default; lower latency; no QA/Cot)
- `seed-tts-2.0-expressive` (higher expressiveness; QA/Cot; quality variance)

## HTTP Chunked unidirectional sketch

```http
POST https://openspeech.bytedance.com/api/v3/tts/unidirectional
X-Api-Key: <key>
X-Api-Resource-Id: seed-tts-2.0
Content-Type: application/json
```

Body uses `req_params` (speaker, text/ssml, audio_params, additions). Response is chunked audio frames.

## Async long-text TTS (not used in article pipeline)

For very long single-shot jobs (up to ~100k chars; results retained ~7 days):
- Submit: `/api/v3/tts/submit`
- Query: `/api/v3/tts/query`
- Docs: https://www.volcengine.com/docs/6561/1829010

Prefer chunked V1 + ffmpeg concat for lizliz.xyz article audio (auditability + CF Pages size control).

## Relation to V1 production path

| Concern | V1 HTTP | V3 streaming |
|---|---|---|
| Credentials | APP_ID + ACCESS_TOKEN (`Bearer;`) | API Key **or** App-Id + Access-Key headers |
| Cluster | `volcano_tts` in JSON body | `X-Api-Resource-Id` header |
| Article batch | ✅ production default | possible but heavier |
| Realtime LLM | ❌ | ✅ bidirectional |
| Scripts in this skill | `tts-generate.py` | none yet (needs protocol helper) |
