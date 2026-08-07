#!/usr/bin/env python3
"""
Extract podcast transcript with timestamps from Doubao Podcast API.

Connects with only_nlp_text=true, captures all event=360 (text) + event=362 (timing).
Output: JSON array of {start, end, speaker, text}

Usage:
  python3 extract-transcript.py <input.txt> <output.json>

Requires: DOUBAO_TTS_APP_ID, DOUBAO_TTS_ACCESS_TOKEN
"""
import asyncio, json, os, struct, sys, uuid
import websockets

APP_ID = os.environ["DOUBAO_TTS_APP_ID"]
ACCESS_TOKEN = os.environ["DOUBAO_TTS_ACCESS_TOKEN"]
ENDPOINT = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"
RESOURCE_ID = "volc.service_type.10050"
APP_KEY = "aGjiRDfUWi"

def build_header(flags=0b0100):
    return bytes([0x11, (0b0001 << 4) | (flags & 0x0F), 0x10, 0x00])

def build_event_frame(event, session_id, payload_dict):
    header = build_header(0b0100)
    ev = struct.pack(">i", event)
    sid = session_id.encode("utf-8")
    body = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
    return header + ev + struct.pack(">I", len(sid)) + sid + struct.pack(">I", len(body)) + body

def build_conn_frame(event, payload_dict=None):
    if payload_dict is None:
        payload_dict = {}
    header = build_header(0b0100)
    ev = struct.pack(">i", event)
    body = json.dumps(payload_dict, ensure_ascii=False).encode("utf-8")
    return header + ev + struct.pack(">I", len(body)) + body

def extract_payload(raw):
    if len(raw) < 12:
        return b"", None
    rest = raw[8:]
    if len(rest) < 4:
        return b"", None
    sid_len = struct.unpack(">I", rest[:4])[0]
    if 0 < sid_len < 256:
        offset = 4 + sid_len
        if len(rest) >= offset + 4:
            pl_len = struct.unpack(">I", rest[offset:offset + 4])[0]
            payload = rest[offset + 4:offset + 4 + pl_len]
            sid = rest[4:4 + sid_len].decode("utf-8", errors="replace")
            return payload, sid
    pl_len = struct.unpack(">I", rest[:4])[0]
    return rest[4:4 + pl_len], None

SPEAKER_EMOJI = {
    "zh_male_dayixiansheng_v2_saturn_bigtts": "🧑 dayi",
    "zh_female_mizaitongxue_v2_saturn_bigtts": "👩 mizai",
}

async def extract(input_text, output_path):
    session_id = str(uuid.uuid4())

    params = {
        "input_id": session_id,
        "input_text": input_text,
        "action": 0,
        "use_head_music": False,
        "use_tail_music": False,
        "audio_config": {"format": "mp3", "sample_rate": 24000, "speech_rate": 0},
        "speaker_info": {
            "random_order": False,
            "speakers": [
                "zh_male_dayixiansheng_v2_saturn_bigtts",
                "zh_female_mizaitongxue_v2_saturn_bigtts",
            ],
        },
        "aigc_watermark": False,
        "input_info": {
            "only_nlp_text": True,  # Skip audio generation, get text only
        },
    }

    start_frame = build_event_frame(100, session_id, params)
    finish_frame = build_conn_frame(2)

    entries = []
    current_speaker = None
    current_text = None
    current_round = None

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
    ) as ws:
        print(f"Connected. Session: {session_id[:8]}…")
        await ws.send(start_frame)
        print("StartSession sent\n")

        while True:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=300)
            except asyncio.TimeoutError:
                print("Timeout")
                break

            if len(raw) < 8:
                continue

            event = struct.unpack(">i", raw[4:8])[0]
            msg_type = (raw[1] >> 4) & 0x0F
            payload, _ = extract_payload(raw)

            if msg_type == 0x0F:
                try:
                    err = json.loads(payload.decode("utf-8"))
                    print(f"ERROR: {err.get('error', str(err))}")
                except:
                    print(f"ERROR frame")
                break

            if event == 360:  # Text
                try:
                    info = json.loads(payload.decode("utf-8"))
                    current_speaker = info.get("speaker", "")
                    current_text = info.get("text", "")
                    current_round = info.get("round_id", -1)
                    if current_round == -1 and current_speaker == "":
                        print(f"  [intro] {current_text[:60]}…")
                        current_text = None
                        continue
                    speaker_label = SPEAKER_EMOJI.get(current_speaker, current_speaker)
                    print(f"  [{current_round}] {speaker_label}: {current_text[:80]}…")
                except Exception as e:
                    print(f"  parse error: {e}")

            elif event == 362:  # Round end with timing
                try:
                    info = json.loads(payload.decode("utf-8"))
                    if info.get("is_error"):
                        print(f"  ⚠ round error: {info.get('error_msg', '')}")
                        continue
                    start_t = info.get("start_time", 0)
                    end_t = info.get("end_time", 0)
                    if current_text and current_speaker:
                        speaker_label = SPEAKER_EMOJI.get(current_speaker, current_speaker)
                        entries.append({
                            "start": round(start_t, 2),
                            "end": round(end_t, 2),
                            "speaker": speaker_label,
                            "text": current_text,
                        })
                        print(f"  ✓ [{current_round}] saved: {start_t:.1f}s–{end_t:.1f}s ({len(current_text)} chars)")
                    current_text = None
                    current_speaker = None
                except Exception as e:
                    print(f"  timing parse error: {e}")

            elif event == 152:
                print("\nSession finished")
                await ws.send(finish_frame)
                break

            elif event == 153:
                try:
                    err = json.loads(payload.decode("utf-8"))
                    print(f"Session error: {err}")
                except:
                    print(f"Session error")
                break

    with open(output_path, "w") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    total_dur = entries[-1]["end"] if entries else 0
    print(f"\n✅ Saved {len(entries)} entries → {output_path}")
    print(f"   Duration: {total_dur:.0f}s ({total_dur/60:.1f} min)")
    return entries


async def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.txt> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "/tmp/podcast-transcript.json"

    with open(input_file) as f:
        text = f.read()

    await extract(text, output_file)


if __name__ == "__main__":
    asyncio.run(main())
