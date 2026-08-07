#!/usr/bin/env python3
"""
Doubao Podcast TTS Generator
=============================
Input: plain text file → Output: MP3 podcast audio (dual-speaker AI conversation)

Protocol: Volcengine WebSocket V3 binary protocol (message_type=0b0001)
Endpoint: wss://openspeech.bytedance.com/api/v3/sami/podcasttts

Usage:
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python3 podcast-generate.py <input.txt> [output.mp3]

Env: DOUBAO_TTS_APP_ID, DOUBAO_TTS_ACCESS_TOKEN
Requires: websockets (Hermes venv). Prefer set -a; . writing/.env; set +a before run.
"""

import asyncio
import json
import os
import re
import struct
import subprocess
import sys
import uuid
import websockets

# ── Credentials ──────────────────────────────────────────────
APP_ID = os.environ["DOUBAO_TTS_APP_ID"]
ACCESS_TOKEN = os.environ["DOUBAO_TTS_ACCESS_TOKEN"]
RESOURCE_ID = "volc.service_type.10050"
APP_KEY = "aGjiRDfUWi"
ENDPOINT = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"

# ── Binary Protocol ──────────────────────────────────────────
# Podcast endpoint uses message_type=0b0001 (1), not 0b0011


def build_header(flags=0b0100):
    """4-byte header: [proto|hdr] [msg_type|flags] [ser|comp] [reserved]."""
    return bytes([
        0x11,                           # protocol v1, header=4 bytes
        (0b0001 << 4) | (flags & 0x0F), # msg_type=1 for podcast
        0x10,                           # JSON, no compression
        0x00,                           # reserved
    ])


def build_event_frame(event, session_id, payload_dict):
    """Frame with event + session_id + JSON payload."""
    header = build_header(flags=0b0100)
    ev = struct.pack(">i", event)
    sid = session_id.encode("utf-8")
    body = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
    return header + ev + struct.pack(">I", len(sid)) + sid + struct.pack(">I", len(body)) + body


def build_conn_frame(event, payload_dict=None):
    """Connection-level frame (no session_id)."""
    if payload_dict is None:
        payload_dict = {}
    header = build_header(flags=0b0100)
    ev = struct.pack(">i", event)
    body = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
    return header + ev + struct.pack(">I", len(body)) + body


def extract_payload(raw):
    """Extract JSON or binary payload from a server response frame.

    Server frames have: header(4) + event(4) + session_id_len(4) + session_id
                         + payload_len(4) + payload
    """
    if len(raw) < 12:
        return b"", None
    rest = raw[8:]  # skip header + event
    if len(rest) < 4:
        return b"", None
    sid_len = struct.unpack(">I", rest[:4])[0]
    if sid_len > 0 and sid_len < 256:
        offset = 4 + sid_len
        if len(rest) >= offset + 4:
            pl_len = struct.unpack(">I", rest[offset:offset + 4])[0]
            payload = rest[offset + 4:offset + 4 + pl_len]
            sid = rest[4:4 + sid_len].decode("utf-8", errors="replace")
            return payload, sid
    # Fallback: try as raw payload (no session_id in response)
    pl_len = struct.unpack(">I", rest[:4])[0]
    return rest[4:4 + pl_len], None


# ── Markdown Cleaning ────────────────────────────────────────

def clean_for_podcast(text):
    """Strip markdown syntax — keep plain spoken text."""
    text = re.sub(r"\*{3,}\s*", "\n\n", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"!\[.*?\]\([^)]+\)", "", text)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.replace("\xa0", " ").replace("\u00a0", " ")
    return text.strip()


# ── Main ─────────────────────────────────────────────────────

async def generate(input_text, output_path):
    session_id = str(uuid.uuid4())
    round_count = 0

    podcast_params = {
        "input_id": session_id,
        "input_text": input_text,
        "action": 0,
        "use_head_music": True,
        "use_tail_music": True,
        "audio_config": {
            "format": "mp3",
            "sample_rate": 24000,
            "speech_rate": 0,
        },
        "speaker_info": {
            "random_order": False,
            "speakers": [
                "zh_male_dayixiansheng_v2_saturn_bigtts",
                "zh_female_mizaitongxue_v2_saturn_bigtts",
            ],
        },
        "aigc_watermark": False,
    }

    start_frame = build_event_frame(100, session_id, podcast_params)
    finish_frame = build_conn_frame(2)

    audio_chunks = []
    total_usage = None

    async with websockets.connect(
        ENDPOINT,
        additional_headers={
            "X-Api-App-Id": APP_ID,
            "X-Api-Access-Key": ACCESS_TOKEN,
            "X-Api-Resource-Id": RESOURCE_ID,
            "X-Api-App-Key": APP_KEY,
            "X-Api-Request-Id": str(uuid.uuid4()),
        },
        max_size=100 * 1024 * 1024,
        ping_interval=30,
        ping_timeout=30,
        open_timeout=15,
    ) as ws:
        print(f"✓ Connected — session: {session_id[:8]}…")
        await ws.send(start_frame)
        print(f"→ StartSession sent ({len(start_text_b64:=str(len(start_frame)))} B)\n")
        del start_text_b64  # suppress lint

        # Timeout per recv: 300s for long processing
        RECV_TIMEOUT = 300

        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=RECV_TIMEOUT)
            except asyncio.TimeoutError:
                print(f"\n⚠ Timeout ({RECV_TIMEOUT}s) — server may still be processing")
                break

            if isinstance(raw, str):
                print(f"⚠ Text: {raw[:200]}")
                continue

            # Parse header
            if len(raw) < 8:
                print(f"⚠ Short frame: {len(raw)} B")
                continue

            msg_type = (raw[1] >> 4) & 0x0F
            event = struct.unpack(">i", raw[4:8])[0]
            payload, sid = extract_payload(raw)

            # ── Event dispatch ──

            if msg_type == 0x0F:  # Error frame
                try:
                    err = json.loads(payload.decode("utf-8"))
                    print(f"❌ ERROR: {err.get('error', str(err))}")
                except Exception:
                    print(f"❌ ERROR frame: {payload[:200]}")
                break

            if event == 150:  # Session started
                print(f"  ✓ session started")

            elif event == 360:  # Round text (before audio)
                try:
                    info = json.loads(payload.decode("utf-8"))
                    speaker = info.get("speaker", "?")
                    text = info.get("text", "")
                    speaker_short = "🧑" if "male" in speaker else "👩"
                    print(f"  {speaker_short} [{info.get('round_id', '?')}] {text[:80]}…")
                except Exception:
                    pass

            elif event == 361:  # Audio data
                if len(payload) > 0:
                    audio_chunks.append(payload)

            elif event == 362:  # Round end
                round_count += 1
                total_kb = sum(len(c) for c in audio_chunks) / 1024
                try:
                    info = json.loads(payload.decode("utf-8"))
                    dur = info.get("audio_duration", 0)
                    if info.get("is_error"):
                        print(f"  ⚠ round {round_count} ERROR: {info.get('error_msg', '')}")
                    else:
                        print(f"  ✓ round {round_count} done ({dur:.0f}s) — audio so far: {total_kb:.0f} KB")
                except Exception:
                    print(f"  ✓ round {round_count} done — audio: {total_kb:.0f} KB")

            elif event == 363:  # Podcast end
                print(f"  🏁 podcast end")
                try:
                    info = json.loads(payload.decode("utf-8"))
                    audio_url = info.get("meta_info", {}).get("audio_url", "")
                    if audio_url:
                        print(f"  🔗 audio_url: {audio_url}")
                except Exception:
                    pass

            elif event == 154:  # Usage info
                try:
                    total_usage = json.loads(payload.decode("utf-8"))
                    usage = total_usage.get("usage", total_usage)
                    print(f"  📊 tokens: {usage.get('total_tokens', '?')}")
                except Exception:
                    pass

            elif event == 152:  # Session finished
                print(f"  ✓ session finished — sending FinishConnection")
                await ws.send(finish_frame)
                break

            elif event == 153:  # Session error
                try:
                    err = json.loads(payload.decode("utf-8"))
                    print(f"  ❌ session error: {json.dumps(err, ensure_ascii=False)[:300]}")
                except Exception:
                    print(f"  ❌ session error (raw): {payload[:200]}")
                break

            elif event == 50:
                pass  # connection ack — silent

            else:
                preview = ""
                if 0 < len(payload) < 2000:
                    try:
                        preview = payload.decode("utf-8", errors="replace")[:120]
                    except Exception:
                        preview = f"<{len(payload)}B>"
                elif len(payload) > 0:
                    preview = f"<{len(payload)}B binary>"
                print(f"  ? event={event} {preview}")

    # ── Save ──
    if not audio_chunks:
        print("\n❌ No audio received")
        return None

    total_audio = b"".join(audio_chunks)
    with open(output_path, "wb") as f:
        f.write(total_audio)

    size_mb = len(total_audio) / (1024 * 1024)
    print(f"\n✅ Saved: {output_path}")
    print(f"   Size: {size_mb:.1f} MB  |  Rounds: {round_count}  |  Chunks: {len(audio_chunks)}")

    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", output_path],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"   Duration: {duration:.0f}s ({duration/60:.1f} min)")
    except Exception:
        pass

    return output_path


# ── CLI ──────────────────────────────────────────────────────

async def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.txt> [output.mp3]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "/tmp/podcast-output.mp3"

    with open(input_file) as f:
        raw = f.read()

    cleaned = clean_for_podcast(raw)
    print(f"Input:  {len(raw):,} chars raw  →  {len(cleaned):,} chars cleaned\n")

    cleaned_path = "/tmp/podcast-input-cleaned.txt"
    with open(cleaned_path, "w") as f:
        f.write(cleaned)

    await generate(cleaned, output_file)


if __name__ == "__main__":
    asyncio.run(main())
