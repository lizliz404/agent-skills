# Volcengine Doubao Speech (豆包语音) · Big-model file ASR (how talkcut uses it)

Official docs: Standard file ASR <https://www.volcengine.com/docs/6561/1354868>; Flash is in the same section ("录音文件识别大模型极速版", big-model file ASR Flash). New console: <https://console.volcengine.com/speech/new/overview>

## Setup (the user must do this)

1. Sign in to the new Doubao Speech console → enable "录音文件识别大模型" (big-model file ASR): Flash `volc.bigasr.auc_turbo`; also Standard `volc.bigasr.auc` for long audio.
2. Create a key under API Key management → `export DOUBAO_API_KEY=...` locally, or put it in `~/.agents/env/doubao-tts.env` (shared with this repo's doubao-tts skill).
3. Old-console users: `VOLC_APP_ID` (APP ID) + `VOLC_ACCESS_TOKEN` (Access Token), sent as `X-Api-App-Key` / `X-Api-Access-Key`.

## Limits (checked against the official docs, 2026-10-17)

- Flash: audio ≤ 2 h and ≤ 100 MB, WAV/MP3/OGG Opus; inline binary upload ideally ≤ 20 MB (depends on upload bandwidth). Longer files must use Standard; `asr_volc.py` switches automatically.
- Flash accepts the same request fields as Standard minus callback and the call-centre extras (language ID, emotion, gender, volume, speech rate). talkcut uses none of those anyway.
- 16 kHz mono 48 kbps mp3 ≈ 21 MB per hour, so a typical talking-head recording stays well inside Flash.
- `enable_ddc` defaults to false upstream; talkcut sets it to false explicitly.

## Endpoints

| Tier | URL | Resource-Id | Mode |
|---|---|---|---|
| Flash | `POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash` | `volc.bigasr.auc_turbo` | sync, base64 upload |
| Standard | `…/api/v3/auc/bigmodel/submit` + `…/query` | `volc.bigasr.auc` | async; query must echo the submit's `X-Tt-Logid` |

Common headers: `X-Api-Key` (or App-Key/Access-Key), `X-Api-Resource-Id`, `X-Api-Request-Id` (UUID), `X-Api-Sequence: -1`.
Status is in the **response header** `X-Api-Status-Code`: `20000000` done, `20000001` processing, `20000002` queued, `20000003` silent audio. While processing the body is an empty result; that is not a failure.

Request body (the only options talkcut enables):
```json
{"user": {"uid": "talkcut"},
 "audio": {"data": "<base64>", "format": "mp3"},
 "request": {"model_name": "bigmodel", "enable_itn": true, "enable_punc": true,
             "enable_ddc": false, "show_utterances": true}}
```
With `show_utterances: true`, each `result.utterances[]` entry has `start_time/end_time` (ms) and `words[]` (each character's `text/start_time/end_time`). That is all the timing the cut needs.

## Keeping cost down

- Send 16 kHz mono mp3 (`prep.py` does this): smaller upload, same accuracy.
- Leave off `enable_speaker_info` (single speaker) and emotion/gender/speech-rate extras.
- `enable_ddc` (smoothing) must stay off: it deletes fillers and repeats, which are exactly what we use to decide cuts.
- Never transcribe the same footage twice; `transcript.raw.json` caches the raw result and `asr_volc.py --normalize` regenerates the transcript from it.

Reference implementations: this repo's `skills/doubao-tts/scripts/asr-transcribe.py`; `volcengine_v3_transcribe.sh` in [lcbuaaliu/ai-jian-koubo](https://github.com/lcbuaaliu/ai-jian-koubo).
