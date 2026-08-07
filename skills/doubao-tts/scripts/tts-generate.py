#!/usr/bin/env python3
"""Generate TTS audio from cleaned plain text using Doubao V1 API.
Chunks at ~1800 chars (safe under 60s RPC timeout), concatenates into 2 parts
to stay under CF Pages 25 MiB per-file limit.

Usage: python3 tts-generate.py <cleaned.txt> [output_dir] [slug]

  slug: used in part filenames (default: derived from output_dir basename).
        E.g. slug="dont-die" → part files named "dont-die-part1.mp3".

Requires env: DOUBAO_TTS_APP_ID, DOUBAO_TTS_ACCESS_TOKEN
Optional env: DOUBAO_TTS_CLUSTER (default: volcano_tts),
              DOUBAO_TTS_VOICE_TYPE (default: zh_female_vv_uranus_bigtts)
"""
import os, re, sys, json, uuid, time, subprocess, base64, urllib.request
from pathlib import Path

APP_ID = os.environ["DOUBAO_TTS_APP_ID"]
TOKEN = os.environ["DOUBAO_TTS_ACCESS_TOKEN"]
CLUSTER = os.environ.get("DOUBAO_TTS_CLUSTER", "volcano_tts")
VOICE_TYPE = os.environ.get("DOUBAO_TTS_VOICE_TYPE", "zh_female_vv_uranus_bigtts")
ENDPOINT = "https://openspeech.bytedance.com/api/v1/tts"
CHUNK_SIZE = 1800

OUTPUT_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/tmp/tts-out")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SLUG = sys.argv[3] if len(sys.argv) > 3 else OUTPUT_DIR.name

with open(sys.argv[1]) as f:
    text = f.read()

# Split on paragraph boundaries
paragraphs = text.split('\n\n')
chunks = []
current = ""
for p in paragraphs:
    p = p.strip()
    if not p:
        continue
    if len(current) + len(p) + 2 > CHUNK_SIZE and current:
        chunks.append(current.strip())
        current = p
    else:
        current = current + '\n\n' + p if current else p
if current.strip():
    chunks.append(current.strip())

print(f"Total chars: {len(text)}, Chunks: {len(chunks)}")

# Generate each chunk
chunk_files = []
for i, chunk_text in enumerate(chunks):
    out_file = OUTPUT_DIR / f"chunk_{i+1:03d}.mp3"
    if out_file.exists():
        print(f"  chunk {i+1}: exists, skip")
        chunk_files.append(str(out_file))
        continue

    payload = {
        "app": {"appid": APP_ID, "token": TOKEN, "cluster": CLUSTER},
        "user": {"uid": "liz-tts-session"},
        "audio": {
            "voice_type": VOICE_TYPE, "encoding": "mp3",
            "speed_ratio": 1.0, "volume_ratio": 1.0, "pitch_ratio": 1.0
        },
        "request": {
            "reqid": str(uuid.uuid4()), "text": chunk_text,
            "text_type": "plain", "operation": "query", "with_frontend": 1
        }
    }

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Bearer; {TOKEN}",
            "Content-Type": "application/json"
        }
    )

    print(f"  chunk {i+1}/{len(chunks)}: {len(chunk_text)} chars...", end=' ', flush=True)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)

    if result.get("code") != 3000:
        print(f"API error: {result}")
        sys.exit(1)

    audio_bytes = base64.b64decode(result["data"])
    with open(out_file, 'wb') as f:
        f.write(audio_bytes)
    print(f"OK ({len(audio_bytes)/1024:.0f} KB)")
    chunk_files.append(str(out_file))
    time.sleep(0.3)

# Concatenate into 2 parts
mid = len(chunk_files) // 2
parts = [chunk_files[:mid], chunk_files[mid:]]

for part_idx, part_chunks in enumerate(parts, 1):
    part_file = OUTPUT_DIR / f"{SLUG}-part{part_idx}.mp3"
    list_file = OUTPUT_DIR / f"list-part{part_idx}.txt"
    with open(list_file, 'w') as f:
        for cf in part_chunks:
            f.write(f"file '{cf}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", str(part_file)
    ], capture_output=True, check=True)

    size_mb = part_file.stat().st_size / (1024 * 1024)
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        str(part_file)
    ], capture_output=True, text=True)
    duration = float(probe.stdout.strip())
    print(f"Part {part_idx}: {part_file} ({size_mb:.1f} MB, {duration:.0f}s)")
    if size_mb > 25:
        print(f"  WARNING: >25 MB, needs re-encoding!")
