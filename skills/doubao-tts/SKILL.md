---
name: doubao-tts
description: "Use when generating Doubao/Volcengine article audio (TTS), AI dual-speaker podcasts, or ASR transcripts for Liz's writing pipeline. Covers text cleaning, V1/V3 endpoints, Flash/Standard ASR, podcast binary protocol, lizliz.xyz publish paths, and ElevenLabs fallback routing."
version: 1.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tts, asr, podcast, doubao, volcengine, audio, speech, lizliz]
    related_skills: [elevenlabs-tts]
---

# Doubao TTS (TTS + Podcast + ASR)

## Overview

Doubao / Volcengine（豆包语音）is widely regarded as **top-tier Chinese speech AI** and is the quality-default provider for Liz's writing pipeline. Prefer 火山引擎豆包 over generic TTS alternatives unless blocked.

This skill covers three 豆包语音 products: **TTS** (text→speech for article audio), **Podcast** (AI dual-speaker conversation), and **ASR** (speech→text with optional diarization). On the **new console**, one API Key authenticates across these services via `X-Api-Key`. Endpoints and resource IDs still differ per product.

ElevenLabs has a cleaner HTTP API but weaker preferred voice/model quality for this workflow — last-resort fallback only (`elevenlabs-tts`). Do not choose it for convenience.

## Onboarding (new console — preferred)

Do **not** start on the old console for new setups — it is harder to navigate. Use the new 豆包语音 console:

1. Open the [火山引擎豆包语音新版控制台](https://console.volcengine.com/speech/new/overview?projectName=default).
2. Top up / activate the speech products you need (TTS, ASR, Podcast, etc.).
3. Create or copy a single **API Key** from the new console's API Key management.
4. Store it as `DOUBAO_API_KEY` (canonical) in the writing-profile secrets path below. Alias `DOUBAO_SPEECH_API_KEY` / legacy `DOUBAO_TTS2_API_KEY` are accepted.
5. Hand the key to the agent. If auth or product routing is unclear, also hand the [豆包语音产品简介 / 能力总览文档](https://docs.volcengine.com/docs/6561/163032) (or the relevant API page from [References / 参考文献](#references--参考文献)).

**One key, many services:** After topping up on the new console, that API Key is the credential for TTS, ASR (speech→text), Podcast generation, and related 豆包语音 calls that accept `X-Api-Key`. You no longer need a separate App ID + Access Token pair **for new-console workflows**.

Existing bundled scripts (`tts-generate.py`, `podcast-generate.py`, `asr-transcribe.py`) still read the **legacy** App ID / Access Token env vars and old-console header shapes. Keep those vars populated until scripts are migrated; for new agent code prefer `DOUBAO_API_KEY` + `X-Api-Key`.

## When to Use

- **TTS:** Liz asks to turn a writing project, `final.md`, essay, or lizliz.xyz post into spoken audio (豆包 / 火山引擎 / ByteDance TTS).
- **Podcast:** Liz asks to turn an article, TXT, URL, or topic into a dual-speaker AI podcast (豆包语音播客大模型). Separate product — activate via the [new console](https://console.volcengine.com/speech/new/overview?projectName=default) (legacy activation deep-link also listed in References).
- **ASR:** Liz asks to transcribe MP3 / WAV / OGG / voice memo / video audio to verbatim text (prefer Flash ASR).
- Debugging Doubao voices, payloads, article-audio placement, lizliz.xyz audio links, or ASR quality.

**Don't use for:**
- ElevenLabs-first generation → `elevenlabs-tts`
- Music tagging / source separation / MIDI / beat detection → separate SAMI / 智能K歌 product lines (see `references/volcengine-audio-ecosystem.md`)
- Real-time S2S voice agents → 端到端实时语音大模型 (out of scope; see References)

## Core rules

1. **Do not read Markdown aloud.** Strip YAML, heading markers, emphasis, footnotes, table pipes, HRs, raw URLs, images, code fences unless the content itself must be spoken.
2. **Do not narrate References / Footnotes by default.** Stop before `References` / `参考资料` / `Footnotes` / `脚注` / `Sources` / `引用`. Source appendix audio only if Liz asks.
3. **Keep the article voice.** Preserve Chinese punctuation rhythm, paragraph breaks, quotes, and English technical terms.
4. **Skip multi-voice smoke tests** when Liz already chose the default.
5. **Default voice:** `zh_female_vv_uranus_bigtts` (Vivi2.0) unless Liz picks another or quota blocks.
6. **Production TTS route:** verified V1 `https://openspeech.bytedance.com/api/v1/tts` with `cluster: volcano_tts`. V3 streaming is the migration/realtime path, not the article default.
7. **Prefer new-console `DOUBAO_API_KEY`** for new work; keep legacy App ID / Access Token only for existing scripts or V1 Bearer payloads until migrated.
8. **ElevenLabs last resort only** — quota/auth/platform failure, or explicit request. Keep provider visible in filenames/manifests.
9. **Start from this skill** when Liz mentions Doubao TTS / article audio (`skill_view` / registry) — do not broad-search buried notes first.

## Environment contract

Secrets stay out of this file. Record variable names and paths only.

Canonical secrets + symlinks:

```text
/home/ubuntu/.hermes/secrets/doubao-tts.env
/home/ubuntu/.hermes/secrets/elevenlabs.env
/home/ubuntu/.hermes/profiles/writing/.env.d/*.env -> /home/ubuntu/.hermes/secrets/*.env
/home/ubuntu/.hermes/profiles/trading/.env.d/*.env -> /home/ubuntu/.hermes/secrets/*.env
/home/ubuntu/.hermes/.env.d/*.env -> /home/ubuntu/.hermes/secrets/*.env
```

Also mirror into profile `.env` when convenient (older scripts only source `.env`). New scripts should load `.env` and `.env.d/*.env`.

Writing-profile home: `/home/ubuntu/.hermes/profiles/writing/.env`

### Preferred: single API Key (new console)

```bash
DOUBAO_API_KEY=...                 # canonical — X-Api-Key for TTS / ASR / Podcast (new console)
# accepted aliases (same value):
DOUBAO_SPEECH_API_KEY=...
DOUBAO_TTS2_API_KEY=...            # historical name from TTS 2.0 samples; keep as alias
```

Resolution order for new code: `DOUBAO_API_KEY` → `DOUBAO_SPEECH_API_KEY` → `DOUBAO_TTS2_API_KEY`.

Optional (shared): `DOUBAO_TTS_CLUSTER=volcano_tts`, `DOUBAO_TTS_VOICE_TYPE=zh_female_vv_uranus_bigtts`.

### Legacy auth (old console) — existing scripts / V1 HTTP

**Deprecated for new setups.** Keep populated while `tts-generate.py`, `podcast-generate.py`, and `asr-transcribe.py` still expect them.

```bash
DOUBAO_TTS_APP_ID=...              # old console App ID → X-Api-App-Key / X-Api-App-Id / V1 app.appid
DOUBAO_TTS_ACCESS_TOKEN=...        # old Access Token → X-Api-Access-Key / V1 Authorization: Bearer; …
DOUBAO_TTS_SECRET_KEY=...          # optional; some SDK variants
```

Aliases (compat): `VOLCENGINE_TTS_*`, `VOLC_TTS_*`.

| Path | Auth shape |
|---|---|
| **New console** | `X-Api-Key: $DOUBAO_API_KEY` alone (ASR Flash, TTS V3, and related new-console APIs) |
| **Old console / current scripts** | `X-Api-App-Key`/`X-Api-App-Id` + `X-Api-Access-Key`, or V1 `Authorization: Bearer; <token>` + JSON `app.appid`/`app.token` |

Do **not** put the API Key into the V1 `Bearer;` header or the Access Token into `X-Api-Key` interchangeably — formats differ.

Shell export gotcha — plain `source .env` may not export to child Python:

```bash
set -a; . /home/ubuntu/.hermes/profiles/writing/.env; set +a
```

Presence check (no secret dump):

```bash
python3 - <<'PY'
import os, re
for name in sorted(k for k in os.environ if re.search(r'(DOUBAO|VOLC|TTS)', k)):
    print(f"{name}=<set>")
PY
```

If neither `DOUBAO_API_KEY` (or aliases) nor legacy App ID / Access Token is set: stop. Do not fall back to Edge/OpenAI or claim Doubao audio was generated.

---

## TTS (文字→语音)

### V1 HTTP — production default

Verified working for article audio. Official docs now list this under historical/小模型 docs, but the endpoint remains active and is Liz's reliable route from this server. Full parameter notes: [V1 HTTP API](https://www.volcengine.com/docs/6561/79820).

This path still uses **legacy** App ID + Access Token in the JSON body and `Authorization: Bearer; <AccessToken>` — not `DOUBAO_API_KEY` / `X-Api-Key`. Bundled `tts-generate.py` matches this shape.

```text
POST https://openspeech.bytedance.com/api/v1/tts
Authorization: Bearer; <AccessToken>
Content-Type: application/json
```

(`Bearer;` with semicolon is intentional — official format.)

```json
{
  "app": {"appid": "APPID", "token": "TOKEN", "cluster": "volcano_tts"},
  "user": {"uid": "unique_user_identifier"},
  "audio": {
    "voice_type": "zh_female_vv_uranus_bigtts",
    "encoding": "mp3",
    "speed_ratio": 1.0,
    "volume_ratio": 1.0,
    "pitch_ratio": 1.0
  },
  "request": {
    "reqid": "uuid",
    "text": "plain text",
    "text_type": "plain",
    "operation": "query",
    "with_frontend": 1
  }
}
```

Success: `code == 3000`; audio in base64 `data`. Unique `reqid` per call (UUID).

**Limits:** Official small-model docs cite ~1024 UTF-8 bytes per request; HTTP also has a ~60s RPC timeout. For Liz's bigtts App, practical safe chunk size is **~1800–2000 characters**. Chunks of 5000+ often fail with `code:3031 / RPC timeout`.

### V3 / TTS 2.0 streaming — migration & realtime

Prefer for realtime / streaming text; keep V1 for batch article audio until a protocol helper is wired into scripts.

| Endpoint | Role |
|---|---|
| `wss://openspeech.bytedance.com/api/v3/tts/bidirection` | Bidirectional stream (LLM token → audio) |
| `wss://openspeech.bytedance.com/api/v3/tts/unidirectional/stream` | Full text in, audio stream out (WS) |
| `https://openspeech.bytedance.com/api/v3/tts/unidirectional` | HTTP Chunked unidirectional |
| `https://openspeech.bytedance.com/api/v3/tts/unidirectional/sse` | HTTP SSE unidirectional |

Bidirectional headers (new console):

```text
X-Api-Key: $DOUBAO_API_KEY
X-Api-Resource-Id: seed-tts-2.0
X-Api-Connect-Id: <uuid>
X-Control-Require-Usage-Tokens-Return: *
```

(`DOUBAO_SPEECH_API_KEY` / `DOUBAO_TTS2_API_KEY` aliases resolve to the same header value.)

Resource IDs: `seed-tts-2.0` / `seed-tts-1.0` / `seed-tts-1.0-concurr` / `seed-icl-2.0` / `seed-icl-1.0` (+ concurr). Full payload, additions (`disable_markdown_filter`, subtitles, dialects), and async long-text (`/api/v3/tts/submit|query`) → `references/tts-streaming-v3.md`. Official pages: [双向流式 TTS 2.0](https://www.volcengine.com/docs/6561/2532486), [V3 HTTP Chunked/SSE](https://www.volcengine.com/docs/6561/1598757).

### Known voices

Smoke-test voices on the current App rather than trusting a guide blindly. Common comparison set:

| voice_type | Notes |
|---|---|
| `zh_female_vv_uranus_bigtts` | **Default** Vivi2.0 — model `doubao-seed-tts-2.0`; do **not** send `emotion`/`neutral` (ignored) |
| `zh_female_xueayi_saturn_bigtts` | 薛艾依 / 绘本艾依 — observed working on V1 |
| `zh_female_wanwanxiaohe_moon_bigtts` | Prior auth/resource mismatch — retest after package change |
| `zh_female_shuangkuaisisi_moon_bigtts` | Prior auth/resource mismatch — retest after package change |

Vivi defaults: speed `1.0`, volume `1.0`, sample rate `24000`, format `mp3`. If too lively, try speed `0.98` after a baseline at `1.0`.

Discover voices via console or OpenAPI `ListSpeakers` / `ListBigModelTTSTimbres`.

### Text cleaning checklist

MP3 is baked — clean before synthesize. Work in memory or `/tmp`; **never modify the source manuscript for TTS**.

1. Strip YAML frontmatter (`---\n...\n---`).
2. Cut from `## References` / `参考资料` / `Footnotes` / `脚注` / `Sources` / `引用` / Claim Check onward.
3. Strip **all** HTML (`<a id>`, `<span>`, etc.). Leakage was read as "IA Intro".
4. Strip citation links entirely: `[N](#ref-N)` → remove (not bare `N`).
5. Strip MD: `#`, `**`, `*`, `[text](url)`→text, images, `---`, backticks, `>`, `[^N]`.
6. Strip top audio links (`[收听音频版...](...)`).
7. Save cleaned text under `/tmp` for audit.

Automated: `scripts/strip-for-tts.py`.

### Article audio workflow

**Skill dir:**

```bash
SKILL_DIR="$HOME/.hermes/profiles/writing/skills/media/doubao-tts"
VENV_PY="/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"
```

1. Clean: `python3 "$SKILL_DIR/scripts/strip-for-tts.py" <final.md> /tmp/<slug>-tts.txt`
2. Generate (chunk → 2 parts under CF 25 MiB):  
   `python3 "$SKILL_DIR/scripts/tts-generate.py" /tmp/<slug>-tts.txt /tmp/<slug>-tts/ <slug>`  
   → `<slug>-part1.mp3`, `<slug>-part2.mp3`. Merge if total &lt; 25 MiB:  
   `ffmpeg -y -i "concat:...-part1.mp3|...-part2.mp3" -c copy /tmp/<slug>-tts/<slug>.mp3`
3. Place site audio: `public/audio/articles/<slug>/<slug>.mp3` (or project convention).
4. Link near top: `[收听音频版](/audio/articles/<slug>/<slug>.mp3)`.
5. Verify size, duration, link; push writing + site repos (writing Action syncs Markdown, not arbitrary local audio).

**Audio-first stub** (正文 not ready): minimal `final.md` with frontmatter + placeholder + audio link; copy MP3 into site `public/audio/articles/`; light sync checks only — not a full publish audit.

**Multi-part source narration:** boundary files `tts-part-N.txt`; `text_type: plain`; one MP3 + manifest per segment; `ffprobe` every file.

### Chunking & quality

- Max ~2000 chars / request; split on `\n\n`.
- Concat: `ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp3`.
- Group into 2+ parts for CF Pages **25 MiB/file** limit.
- Prefer native Doubao bitrate (~160 kbps). Floor for publish: **96 kbps**. Re-encode only if over limit: `ffmpeg -i in.mp3 -codec:a libmp3lame -b:a 96k -ac 1 out.mp3`. See `references/cf-pages-size-limit.md`.

---

## Podcast (AI 播客)

Separate product from TTS. Full protocol: `references/podcast-api.md`. Session traps: `references/podcast-session-learnings.md`. Publish: `references/lizliz.xyz-podcast-page.md`. Official WS protocol: [播客 API websocket-v3](https://www.volcengine.com/docs/6561/1668014).

```text
wss://openspeech.bytedance.com/api/v3/sami/podcasttts
```

**New console (preferred for new clients):**

```text
X-Api-Key: $DOUBAO_API_KEY
X-Api-Resource-Id: volc.service_type.10050
X-Api-App-Key: aGjiRDfUWi   # fixed product key (still required by protocol docs)
X-Api-Request-Id: <uuid>
```

**Legacy / current `podcast-generate.py` headers:**

```text
X-Api-App-Id / X-Api-Access-Key / X-Api-Resource-Id: volc.service_type.10050
X-Api-App-Key: aGjiRDfUWi   # fixed
```

Binary frame **message_type = 0b0001** (header byte1 `0x14`). Do **not** use TTS bidirectional `0b0011` → `"unsupported message type (3)"`.

| action | Mode |
|---|---|
| 0 | Long-text / URL summarize → dual dialogue (default) |
| 3 | Direct `nlp_texts` dialogue synthesize |
| 4 | `prompt_text` web-search summarize |

**Liz defaults (2026-07):** action=0, mp3/24000/speech_rate=0, speakers dayi+mizai, `random_order=false` (male first), head+tail music on, AIGC watermarks off, strip MD first.

Default speakers: `zh_male_dayixiansheng_v2_saturn_bigtts` + `zh_female_mizaitongxue_v2_saturn_bigtts`. Alt pair: liufei + xiaolei. Official update (2026-03): TTS/ICL voices also allowed (same App as podcast); use `speaker_info.speaker_additions` for ICL model switches. New (2026-05): `input_info.strict_audit`.

Generate: `$VENV_PY "$SKILL_DIR/scripts/podcast-generate.py" input.txt out.mp3`  
NLP-only transcript: `scripts/extract-transcript.py` (`only_nlp_text`). Prefer Flash ASR on the finished MP3 for subtitles (separate quota, matches actual audio).

---

## ASR (语音→文字)

**New console:** same `DOUBAO_API_KEY` as TTS/Podcast (`X-Api-Key`). **Legacy scripts:** still use `DOUBAO_TTS_APP_ID` / `DOUBAO_TTS_ACCESS_TOKEN` with old header names.

### Flash ASR — preferred ≤2h

One-shot; no submit/poll. Docs: [录音文件识别极速版 HTTP](https://www.volcengine.com/docs/6561/1631584).

```text
POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash
```

**New console headers:**

```text
X-Api-Key: $DOUBAO_API_KEY
X-Api-Resource-Id: volc.bigasr.auc_turbo
X-Api-Request-Id: <uuid>
X-Api-Sequence: -1
```

**Legacy / current `asr-transcribe.py` headers:**

```text
X-Api-App-Key / X-Api-Access-Key / X-Api-Resource-Id: volc.bigasr.auc_turbo
X-Api-Request-Id: <uuid> / X-Api-Sequence: -1
```

```json
{
  "user": {"uid": "<APP_ID>"},
  "audio": {"data": "<base64>"},
  "request": {
    "model_name": "bigmodel",
    "enable_itn": true,
    "enable_punc": true,
    "enable_ddc": false,
    "enable_speaker_info": true,
    "show_utterances": true
  }
}
```

URL mode: `"audio": {"url": "https://..."}` instead of `data`.

| Param | Verbatim 逐字稿 | Clean reading |
|---|---|---|
| `enable_ddc` | **false** (keep 嗯/啊/是吧) | true |
| `enable_punc` | true | true |
| `enable_itn` | true | true |
| `enable_speaker_info` | true for podcasts | as needed |

Limits: ≤2h, ≤100 MB; WAV/MP3/OGG OPUS. Base64 inflates ~33% — prefer URL if raw &gt; ~50 MB. Binary upload recommendation: keep under ~20 MB when possible.

Success header: `X-Api-Status-Code: 20000000`. Speaker in `utterances[].additions.speaker`.

| Code | Meaning |
|---|---|
| 20000000 | Success |
| 20000003 | Silent audio |
| 45000001 | Invalid params |
| 45000002 | Empty audio |
| 45000151 | Unsupported format |
| 55000031 | Server busy |
| 550xxxx | Internal error |

Script: `scripts/asr-transcribe.py` (maps ASR `"1"`/`"2"` → dayi/mizai for default podcast order).

**Flash does not support** customer-service extras: `enable_emotion_detection`, `enable_gender_detection`, `enable_lid`, `show_volume`, `show_speech_rate` (removed from Flash; use Standard).

### Standard ASR — &gt;2h or emotion / gender / LID

```text
POST .../api/v3/auc/bigmodel/submit
POST .../api/v3/auc/bigmodel/query
```

Resource IDs: `volc.seedasr.auc` (model 2.0) or `volc.bigasr.auc` (model 1.0). URL required (no base64). Docs: [录音文件识别标准版 HTTP](https://www.volcengine.com/docs/6561/1354868). Feature matrix (emotion, diarization, ITN, etc.): [大模型录音文件识别能力表](https://www.volcengine.com/docs/6561/1354871).

**Emotion detection** (`enable_emotion_detection: true`): Standard / streaming nostream / bidirectional-optimized ASR only. Labels: `angry` / `happy` / `neutral` / `sad` / `surprise` on utterance `additions.emotion`. Also: `enable_gender_detection`, `enable_lid`, `show_volume`, `show_speech_rate`.

---

## Failure signatures

| Signature | Meaning / action |
|---|---|
| `requested resource not granted` | App lacks voice/resource — change package or voice |
| `resource ID is mismatched with speaker related resource` | V3 resource/voice mismatch — use granted pair or V1 |
| DNS fail `speech.volcengineapi.com` | Wrong host from this server — use `openspeech.bytedance.com` |
| `quota exceeded for types: text_words_lifetime` | Lifetime words gone — stop retries; refresh package or ElevenLabs |
| Podcast: event 150 then silence | Quota exhaustion (no error frame) — do not retry |
| `code:3031` / RPC timeout | Chunk too large — shrink under ~2000 chars |
| `40200002 DeniedAccess:IllegalToken` on SAMI | Wrong product line — need SAMI token, not TTS token |
| websockets `extra_headers` TypeError | Use `additional_headers` (websockets ≥14) |

Quota APIs exist in console OpenAPI (`QuotaMonitoring`, `UsageMonitoring`, `ResourcePacksStatus`) — not wired in scripts; treat runtime quota errors as authoritative.

---

## Beyond this skill

豆包语音 products here: TTS, Podcast, ASR. Adjacent (separate auth / out of default scripts):

- **声音复刻** ICL 1.0/2.0 (`seed-icl-*`)
- **异步长文本 TTS** (`/api/v3/tts/submit|query`)
- **端到端实时语音大模型**, **语音同传**, **语音妙记**
- **SAMI MusicTagging / 音源分离**, **智能K歌**, **豆包音乐模型**

Details: `references/volcengine-audio-ecosystem.md`. Search Volcengine docs before assuming credential reuse.

---

## Common Pitfalls

### Text & cleaning
1. Feeding raw `final.md` → reads MD/HTML/refs aloud.
2. HTML `<a id>` leakage (#1 artifact) — strip all tags.
3. Citation `[N](#ref-N)` left as bare numbers (#2) — remove entirely.
4. Partial-TTS requests still fed full article — trim first, then strip.

### Auth & protocol
5. Swapping `DOUBAO_API_KEY` with V1 Access Token (or putting Access Token in `X-Api-Key`) — formats are not interchangeable.
6. Starting new setups on the **old** console when the [new console](https://console.volcengine.com/speech/new/overview?projectName=default) is available.
7. Podcast `message_type=0b0011` copied from TTS bidirectional samples.
8. ASR headers ≠ TTS V1 `Authorization: Bearer;` — use `X-Api-*` (new: Key alone; legacy: App-Key + Access-Key).
9. Wrong ASR resource ID (`volc.bigasr.auc_turbo` vs `volc.seedasr.auc` vs `volc.bigasr.auc`).
10. Assuming Flash ASR supports emotion detection — it does not.
11. SAMI/MusicTagging with TTS credentials → `40200002`.

### Runtime & publish
12. Scripts path: use `$SKILL_DIR/scripts/`, not writing-repo `scripts/`.
13. Podcast/ASR need Hermes venv Python (`websockets`).
14. Regenerating good audio only for provenance without being asked.
15. Claiming deploy before site has both MP3 + Markdown link and CF Pages actually succeeded (CI green ≠ Pages deployed; 25 MiB trap).
16. Expecting bundled scripts to read `DOUBAO_API_KEY` already — they still use legacy App ID / Access Token until migrated.

---

## Verification Checklist

- [ ] Correct product chosen (TTS vs Podcast vs ASR)
- [ ] Env present: prefer `DOUBAO_API_KEY` (or alias); legacy App ID / Access Token if using bundled scripts (`<set>` check)
- [ ] Cleaned `/tmp` text audited — no YAML/HTML/citations/References
- [ ] Voice / resource ID matches granted package
- [ ] Every MP3: non-trivial size, `ffprobe` duration plausible, each file **&lt; 25 MiB**
- [ ] Article Markdown has intended audio link only
- [ ] Podcast: correct `message_type`, event 150 not followed by silent hang
- [ ] ASR: status `20000000`; verbatim uses `enable_ddc: false`
- [ ] Provider name visible if ElevenLabs fallback used
- [ ] After push: live URL or CF Pages deployment status checked if 404

---

## Scripts & local references

```bash
SKILL_DIR="$HOME/.hermes/profiles/writing/skills/media/doubao-tts"
VENV_PY="/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"
```

| Path | Role |
|---|---|
| `scripts/strip-for-tts.py` | MD → speakable plain text |
| `scripts/tts-generate.py` | V1 chunked TTS → 2-part MP3 (legacy App ID / token) |
| `scripts/podcast-generate.py` | Dual-speaker podcast WS (legacy headers) |
| `scripts/extract-transcript.py` | Podcast NLP-only transcript JSON |
| `scripts/asr-transcribe.py` | Flash ASR → subtitle JSON (legacy headers) |
| `references/podcast-api.md` | Podcast API + Liz defaults |
| `references/podcast-session-learnings.md` | Protocol/quota/venv traps |
| `references/tts-streaming-v3.md` | V3/TTS 2.0 streaming matrix |
| `references/volcengine-audio-ecosystem.md` | SAMI / emotion / product boundaries |
| `references/cf-pages-size-limit.md` | 25 MiB diagnostic |
| `references/lizliz.xyz-podcast-page.md` | Site podcast publish |
| `references/2026-06-17-prigogine-audio.md` | Historical session notes |

Split from `doubao-elevenlabs-tts`. Fallback skill: `elevenlabs-tts`.

---

## References / 参考文献

### Console & onboarding

- [火山引擎豆包语音新版控制台总览](https://console.volcengine.com/speech/new/overview?projectName=default) — 推荐入口：充值/开通服务、创建并复制单一 API Key；新账号不要走旧控制台。
- [豆包语音产品简介与能力总览](https://docs.volcengine.com/docs/6561/163032) — 产品体系与场景说明；拿不准该开哪个服务时把这篇甩给 AI。
- [播客服务旧版开通深链（service/10028）](https://console.volcengine.com/speech/service/10028) — 历史开通入口；新设置优先用新版控制台总览代替。

### TTS

- [豆包语音合成 V1 HTTP（小模型/历史非流式）](https://www.volcengine.com/docs/6561/79820) — Liz 当前文章音频生产路径：`/api/v1/tts`、`Authorization: Bearer;`、base64 音频、`reqid` 唯一性。
- [双向流式语音合成 WebSocket（TTS 2.0）](https://www.volcengine.com/docs/6561/2532486) — `wss://.../api/v3/tts/bidirection`；`X-Api-Key` + `seed-tts-2.0`；会话事件与 `audio_params`。
- [HTTP Chunked / SSE 单向流式 V3](https://www.volcengine.com/docs/6561/1598757) — 一次性送全文、流式出音频；资源 ID 与计费（`seed-tts-*` / `seed-icl-*`）对照表。
- [豆包大模型音色列表（含 2.0）](https://www.volcengine.com/docs/6561/1257544) — 查 `voice_type` / speaker；播客也可选用同表 TTS 音色（需同 App 授权）。

### ASR

- [录音文件识别极速版 HTTP（Flash）](https://www.volcengine.com/docs/6561/1631584) — 一次请求返回结果；`volc.bigasr.auc_turbo`；新控制台仅需 `X-Api-Key`；明确不含情绪/性别等客服字段。
- [录音文件识别标准版 HTTP（submit/query）](https://www.volcengine.com/docs/6561/1354868) — &gt;2h 或需 emotion/gender/LID；`volc.seedasr.auc` / `volc.bigasr.auc`。
- [大模型语音识别能力对照表](https://www.volcengine.com/docs/6561/1354871) — 流式 vs 文件、情绪检测、说话人分离、ITN/顺滑等功能矩阵。

### Podcast

- [语音播客大模型 API（websocket-v3）](https://www.volcengine.com/docs/6561/1668014) — `podcasttts` 端点、二进制帧、action 0/3/4、`strict_audit`、event 150–363、发音人对。

---

## Change log

### 2026-07-30 nuance → v1.2.0

- Added **Onboarding** for new console: top up → single API Key → one key for TTS/ASR/Podcast; prefer new console over old.
- Promoted canonical `DOUBAO_API_KEY` (`DOUBAO_SPEECH_API_KEY` / `DOUBAO_TTS2_API_KEY` aliases); moved App ID / Access Token under **Legacy auth**.
- Overview: 豆包语音 framed as top-tier Chinese speech AI.
- Replaced bare doc bookmarks with annotated **References / 参考文献**; linked console + product overview + API pages inline where cited.
- Documented new-console header shapes alongside legacy script headers; noted scripts not yet migrated off legacy env vars.
- Pitfalls/checklist updated for single-key vs legacy mismatch.

### 2026-07-30 audit → v1.1.0

- Restructured to Hermes best-practice shape: Overview, When to Use (+ don'ts), product sections, organized Pitfalls, Verification Checklist.
- Completed frontmatter: `version`, `author`, `license`, `tags`, `related_skills`; description now starts with `Use when`.
- Verified V1/Flash/Standard/Podcast endpoints against official docs; confirmed `Bearer;` and Flash resource `volc.bigasr.auc_turbo`.
- Added V3 streaming matrix (bidirectional / unidirectional WS / HTTP Chunked / SSE) + `references/tts-streaming-v3.md`.
- Corrected emotion detection: Standard/streaming only — **not** Flash ASR.
- Documented new vs old console auth (`X-Api-Key` alone vs App-Key + Access-Key).
- Podcast: noted `strict_audit`, `aigc_metadata`, TTS/ICL speakers + `speaker_additions` (official 2026-03/05 updates).
- Noted V1 listed under historical docs but remains production path; official 1024-byte small-model limit vs observed ~2k-char chunk practice.
- Flagged QuotaMonitoring/UsageMonitoring OpenAPI existence; adjacent products (async long-text, S2S, 同传, 妙记, ICL).
- Script paths confirmed under `media/doubao-tts`; venv path documented; strip script aligned to multi-name References cut.
