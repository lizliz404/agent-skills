#!/usr/bin/env python3
"""
Transcribe podcast audio → time-aligned JSON subtitles via Doubao Flash ASR.

Endpoint: POST https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash
Features: speaker diarization, utterance-level timestamps, word-level timing
Note: Flash ASR does NOT support enable_emotion_detection (use Standard ASR).

Output: [{"start": 0.0, "end": 5.2, "speaker": "🧑 dayi", "text": "..."}, ...]

Usage:
  python3 asr-transcribe.py <audio.mp3> <output.json>
  # or Hermes venv if other deps needed:
  # /home/ubuntu/.hermes/hermes-agent/venv/bin/python3 asr-transcribe.py ...

Env: DOUBAO_TTS_APP_ID, DOUBAO_TTS_ACCESS_TOKEN
"""
import base64, json, os, sys, uuid, urllib.request

APP_ID = os.environ["DOUBAO_TTS_APP_ID"]
ACCESS_TOKEN = os.environ["DOUBAO_TTS_ACCESS_TOKEN"]
ENDPOINT = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/recognize/flash"
RESOURCE_ID = "volc.bigasr.auc_turbo"

# Speaker mapping: ASR assigns numeric IDs.
# For Liz's default podcast config (random_order=false, dayi first):
SPEAKER_MAP = {"1": "🧑 dayi", "2": "👩 mizai"}


def transcribe(audio_path, output_path):
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

    file_size_mb = len(audio_bytes) / (1024 * 1024)
    print(f"Audio: {audio_path} ({file_size_mb:.1f} MB)")
    print(f"Base64 payload: {len(audio_b64)/1024:.0f} KB")

    payload = {
        "user": {"uid": APP_ID},
        "audio": {"data": audio_b64},
        "request": {
            "model_name": "bigmodel",
            "enable_itn": True,
            "enable_punc": True,
            "enable_ddc": False,         # keep filler words for natural podcast feel
            "enable_speaker_info": True,  # speaker diarization
            "show_utterances": True,      # sentence-level timestamps
        },
    }

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Api-App-Key": APP_ID,
            "X-Api-Access-Key": ACCESS_TOKEN,
            "X-Api-Resource-Id": RESOURCE_ID,
            "X-Api-Request-Id": str(uuid.uuid4()),
            "X-Api-Sequence": "-1",
        },
    )

    print("Sending to Flash ASR...")
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            status_code = resp.headers.get("X-Api-Status-Code", "")
            result = json.loads(resp.read())
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    if status_code != "20000000":
        print(f"API error: status={status_code}")
        print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")
        sys.exit(1)

    audio_info = result.get("audio_info", {})
    duration_ms = audio_info.get("duration", 0)
    utterances = result.get("result", {}).get("utterances", [])
    full_text = result.get("result", {}).get("text", "")

    print(f"\nDuration: {duration_ms/1000:.0f}s ({duration_ms/60000:.1f} min)")
    print(f"Utterances: {len(utterances)}")
    print(f"Full text length: {len(full_text)} chars")

    subtitles = []
    for utt in utterances:
        speaker_id = utt.get("additions", {}).get("speaker", "1")
        speaker_label = SPEAKER_MAP.get(speaker_id, f"speaker {speaker_id}")
        subtitles.append({
            "start": round(utt["start_time"] / 1000, 2),
            "end": round(utt["end_time"] / 1000, 2),
            "speaker": speaker_label,
            "text": utt["text"],
        })

    with open(output_path, "w") as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(subtitles)} subtitles → {output_path}")
    print(f"   Time range: {subtitles[0]['start']}s – {subtitles[-1]['end']}s")

    print("\nSample:")
    for sub in subtitles[:3]:
        print(f"  [{sub['start']:.1f}s] {sub['speaker']}: {sub['text'][:60]}…")
    print(f"  ...")
    for sub in subtitles[-2:]:
        print(f"  [{sub['start']:.1f}s] {sub['speaker']}: {sub['text'][:60]}…")

    return subtitles


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <audio.mp3> [output.json]")
        sys.exit(1)
    transcribe(
        sys.argv[1],
        sys.argv[2] if len(sys.argv) > 2 else "/tmp/podcast-subtitles.json",
    )
