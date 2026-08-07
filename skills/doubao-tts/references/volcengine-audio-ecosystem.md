# Volcengine Audio Ecosystem — Beyond 豆包语音

Last updated: 2026-07-30 (audit + prior melody-seed discovery 2026-07-11)

## Product line boundaries

Volcengine audio services are split across separate product lines, each with its own auth:

| Product Line | Console | Auth | Services |
|---|---|---|---|
| 豆包语音 (Doubao Voice) | 豆包语音控制台 | App ID + Access Token (Bearer or X-Api-*) **or** new-console `X-Api-Key` | TTS (V1/V3), Podcast TTS, ASR (Flash + Standard + streaming), 声音复刻, 异步长文本 TTS, 端到端实时语音, 语音同传, 语音妙记 |
| 音频技术 (SAMI) | 音频技术控制台 | SAMI token + appkey (query params) | MusicTagging, 音源分离 |
| 智能K歌 | 音频技术控制台 | SDK-level auth | MIDI transcription, beat detection, scoring |
| 豆包音乐模型 | 豆包大模型 | API key (separate) | Music generation (text→music) |

**Key takeaway:** TTS credentials (`DOUBAO_TTS_APP_ID` / `DOUBAO_TTS_ACCESS_TOKEN`) are scoped to 豆包语音. They return `40200002 DeniedAccess:IllegalToken` on SAMI endpoints. Do not assume credential reuse across product lines.

### 豆包语音 products covered vs adjacent

| In `doubao-tts` skill (scripts) | Adjacent (docs only / not scripted) |
|---|---|
| V1 HTTP TTS, Podcast WS, Flash ASR | V3 streaming TTS, async long-text TTS (`/api/v3/tts/submit\|query`) |
| Standard ASR notes | 声音复刻 ICL, 端到端实时语音大模型, 语音同传 2.0, 语音妙记 |
| | Console OpenAPI: `QuotaMonitoring`, `UsageMonitoring`, `ResourcePacksStatus`, `ListSpeakers` |

---

## MusicTagging API (音频技术 / SAMI)

Official docs: `https://www.volcengine.com/docs/6489/72006`

### Endpoint

```
POST https://sami.bytedance.com/api/v1/invoke?version=v4&token=<SAMI_TOKEN>&appkey=<SAMI_APPKEY>&namespace=MusicTagging
```

### Auth

Two ways to get a SAMI token:

**A. Quick test (console, manual):** 音频技术控制台 → 应用管理 → 接入详情 → 查看API密钥 → copy temp token (valid 1 day).

**B. Programmatic (IAM):** Use volcengine IAM `ACCESS_KEY` + `SECRET_KEY` to call OpenAPI `GetToken` action (service=`sami`, region=`cn-north-1`), then use returned token + the 音频技术 appkey.

### Request body

```json
{
  "data": "<base64-encoded-audio>",
  "payload": "{\"task_flow\":{\"type\":\"merge\",\"task\":[{\"task_type\":\"MusicTaggingVocal\"},{\"task_type\":\"MusicTaggingMood10\"},{\"task_type\":\"MusicTaggingGenre34\"},{\"task_type\":\"MusicTaggingTheme24\"},{\"task_type\":\"MusicTaggingLang30\"}]},\"extra\":{\"enable_tag\":true}}"
}
```

Payload config (inside the JSON-string `payload` field):
- `audio_info.format` — optional, `wav`/`mp3`/`aac`
- `audio_info.sample_rate` — optional, recommended ≥16kHz
- `extra.enable_tag` — return tag names (default true)
- `extra.enable_embed` — return embeddings (default false)
- `extra.top_num` — max tags per group (default all)

### Limits

- Audio ≤ 10 minutes, ≤ 100 MB
- Supported formats: wav, pcm, mp3, aac, m4a
- Sample rate ≥ 16 kHz recommended
- Music only — non-music audio rejected

### Response

```json
{
  "status_code": 0,
  "status_text": "success",
  "task_id": "uuid",
  "namespace": "MusicTagging",
  "payload": "{\"pred\":[0.09,0.05,...],\"task_flow\":{\"result\":[{\"task_type\":\"MusicTaggingMood10\",\"pred_dim\":10,\"task_output\":{\"tags\":[\"cute\",\"dynamic\",...]}},...]}}"
}
```

The `payload` field is a JSON string containing:
- `pred` — probability array matching the tag order in `task_output.tags`
- `task_flow.result[].task_type` — which model
- `task_flow.result[].task_output.tags` — ordered tag labels
- `task_flow.result[].pred_dim` — dimension count

### Available models

**MusicTaggingVocal** (2 tags): `vocal`, `non_vocal`

**MusicTaggingMood10** (10 tags): `cute`, `dynamic`, `tense`, `weird`, `sorrow`, `chill`, `excited`, `happy`, `angry`, `romantic`

**MusicTaggingGenre34** (34 tags): `pop`, `rock`, `electronic`, `hiphop_rap`, `reggae`, `mb_soul`, `Metal`, `Jazz`, `Blues`, `Country`, `Folk`, `Indie`, `K_pop`, `Indie_Pop`, `Muslim`, `Indo_Christian`, `Bollywood`, `Bollywood_Retro`, `Urban_Punjabi_Pop`, `Tamil_Film_Music`, `Kannada_Film_Music`, `Telugu_Film_Music`, `Indian_Independent`, `Malayalam_Film_Music`, `Sertanejo`, `Baile_Funk`, `Gospel`, `Samba`, `Pagode`, `MPB`, `Forro` (+4 more)

**MusicTaggingTheme24** (24 tags): `kadian`, `DIY`, `family`, `sound_effect`, `campus`, `ACG`, `game`, `pet`, `Beauty_fashion`, `travel`, `Chinese_Style`, `cool`, `disco_dance`, `vlog`, `dance`, `dj`, `food`, `love`, `rainy`, `sport`, `spring`, `summer`, `sunny`, `funny`

**MusicTaggingLang30** (30 tags): `en`, `zh`, `ja`, `ko`, `fr`, `de`, `es`, `pt`, `it`, `ru`, `ar`, `hi`, `th`, `vi`, `id`, `ms`, `tl`, `my`, `km`, `lo`, `bo`, `ug`, `kk`, `uz`, `tk`, `az`, `tr`, `fa`, `he`, `ur`

---

## ASR emotion detection

**Where it works (verified 2026-07-30):**
- Standard file ASR submit/query (`volc.bigasr.auc` / `volc.seedasr.auc`)
- Streaming ASR: nostream interface and bidirectional-optimized variants

**Where it does NOT work:**
- Flash ASR (`.../recognize/flash`) — official docs explicitly remove customer-service fields including `enable_emotion_detection`, `enable_gender_detection`, `enable_lid`, `show_volume`, `show_speech_rate`.

Set `enable_emotion_detection: true` on Standard/streaming requests. Labels land on utterance `additions.emotion`: `angry` / `happy` / `neutral` / `sad` / `surprise`. Related: `enable_gender_detection` → `male`/`female`.

Not yet wired into `scripts/asr-transcribe.py` (Flash-only). Features table: https://www.volcengine.com/docs/6561/1354871 — Standard submit fields: https://www.volcengine.com/docs/6561/1354868

### SAMI token via IAM (programmatic)

1. Use volcengine IAM `ACCESS_KEY` + `SECRET_KEY`.
2. Call OpenAPI `GetToken` with `service=sami`, `region=cn-north-1`.
3. Use returned token + 音频技术 appkey as query params on `https://sami.bytedance.com/api/v1/invoke?...`.

Console temp tokens (音频技术控制台 → 应用管理 → 接入详情) are ~1 day — fine for smoke tests, not automation.

---

## Other related services (not explored yet)

- **音源分离 (Source Separation):** SAMI API — separate vocals from accompaniment
- **音乐转谱 (Music→MIDI):** 智能K歌 SDK — audio to MIDI transcription
- **节拍检测 (Beat Detection):** 智能K歌 SDK
- **副歌检测 (Chorus Detection):** 智能K歌 SDK
- **豆包音乐模型:** Text→music generation (1 min, 10+ styles), separate product
