# Podcast Session Learnings — 2026-07-10

## websockets 15.x API change

`websockets>=14` changed the header parameter name:

```python
# OLD (pre-14):
websockets.connect(url, extra_headers={...})

# NEW (14+):
websockets.connect(url, additional_headers={...})
```

Error: `TypeError: BaseEventLoop.create_connection() got an unexpected keyword argument 'extra_headers'`

## Podcast quota exhaustion signature

When TTS/podcast quota is exhausted, the server does NOT return an error frame or close the connection. Instead:

1. WebSocket connection succeeds (HTTP 101)
2. `event=150` (session started) arrives normally
3. Then silence — no further events, no errors, no close frame
4. Eventually hits the recv timeout

**Do NOT retry** with the same credentials after this pattern — you are out of quota.
Wait for quota reset (daily/monthly depending on plan) or switch to another App ID.

## Binary protocol message_type fix

Critical: the podcast endpoint (`wss://.../sami/podcasttts`) uses **message_type=0b0001** (1),
NOT 0b0011 (3) which is the TTS bidirectional endpoint's value.

```python
# CORRECT (podcast endpoint):
header[1] = (0b0001 << 4) | 0b0100  # = 0x14

# WRONG (TTS bidirectional — copied from momei TS code):
header[1] = (0b0011 << 4) | 0b0100  # = 0x34 → "unsupported message type (3)"
```

## Python version mismatch with venv

`python3` on the system may point to a different Python than the one with `websockets` installed.
Always use the full venv path when running podcast/ASR scripts:

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 script.py
```

The `websockets` package is installed in the Hermes venv (Python 3.11.15).

## ASR as transcript extraction (preferred over re-running podcast API)

To get time-aligned subtitles for a generated podcast, use **Flash ASR** to transcribe the audio
directly — do NOT re-run the podcast API. Rationale:

1. Re-running the podcast API consumes quota (same as generation)
2. Flash ASR is a separate product line with its own quota
3. ASR returns speaker diarization + word-level timestamps out of the box
4. The transcript from ASR matches the **actual audio**, not a re-generated conversation

Script: `scripts/asr-transcribe.py` — takes an MP3 file, returns JSON with `{start, end, speaker, text}`.

ASR speaker IDs ("1", "2") map to podcast roles: dayi starts first (random_order=false), so "1" → 🧑 dayi, "2" → 👩 mizai.

## Running background scripts with proper env

Always source `.env` before running:

```bash
set -a; . /home/ubuntu/.hermes/profiles/writing/.env; set +a && \
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python3 script.py
```

The `set -a; ...; set +a` wrapper is essential — plain `source .env` does not export
variables for child processes.
