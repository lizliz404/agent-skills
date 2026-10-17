#!/usr/bin/env python3
"""Steps 2-3: Volcengine Doubao Speech (豆包语音) big-model file ASR -> transcript.json with per-character timestamps.

Usage:
  python3 asr_volc.py work/audio.mp3 -o work/transcript.json            # auto: Flash, or Standard if over Flash limits
  python3 asr_volc.py work/audio.mp3 -o work/transcript.json --standard # force Standard (async submit/query)
  python3 asr_volc.py --normalize raw.json -o work/transcript.json      # only convert an existing raw result

Credentials (read only from env vars / local env file, never committed):
  New console: DOUBAO_API_KEY            -> X-Api-Key
  Old console: VOLC_APP_ID + VOLC_ACCESS_TOKEN -> X-Api-App-Key / X-Api-Access-Key
  Also reads ~/.agents/env/doubao-tts.env (shared with this repo's doubao-tts skill).

Flash limits (official docs, 2026-10): audio <= 2 h and <= 100 MB (inline upload ideally <= 20 MB);
anything larger goes to Standard automatically. Docs: https://www.volcengine.com/docs/6561/1631584 (Flash),
https://www.volcengine.com/docs/6561/1354868 (Standard).

Only the needed options: punctuation + ITN + utterances (with words). No diarization, emotion, speech rate, etc., to save cost.
"""
import argparse, base64, json, os, sys, time, urllib.request, uuid
from pathlib import Path

FLASH_MAX_SEC, FLASH_MAX_BYTES = 2 * 3600, 100 * 1024 * 1024
BASE = "https://openspeech.bytedance.com/api/v3/auc/bigmodel"
FLASH = (BASE + "/recognize/flash", "volc.bigasr.auc_turbo")
STANDARD = (BASE + "/submit", BASE + "/query", "volc.bigasr.auc")


def load_env_files():
    for p in (Path.home() / ".agents/env/doubao-tts.env", Path.home() / ".agents/secrets/doubao-tts.env"):
        if p.is_file():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def headers(resource, request_id):
    load_env_files()
    h = {"Content-Type": "application/json", "X-Api-Resource-Id": resource,
         "X-Api-Request-Id": request_id, "X-Api-Sequence": "-1"}
    key = os.environ.get("DOUBAO_API_KEY") or os.environ.get("VOLC_API_KEY")
    app, tok = os.environ.get("VOLC_APP_ID"), os.environ.get("VOLC_ACCESS_TOKEN")
    if key:
        h["X-Api-Key"] = key
    elif app and tok:
        h["X-Api-App-Key"], h["X-Api-Access-Key"] = app, tok
    else:
        sys.exit("Missing credentials: set DOUBAO_API_KEY, or VOLC_APP_ID + VOLC_ACCESS_TOKEN")
    return h


def payload(audio_path):
    data = base64.b64encode(Path(audio_path).read_bytes()).decode()
    return {"user": {"uid": "talkcut"},
            "audio": {"data": data, "format": Path(audio_path).suffix.lstrip(".") or "mp3"},
            "request": {"model_name": "bigmodel", "enable_itn": True, "enable_punc": True,
                        "enable_ddc": False,          # no disfluency smoothing: we need fillers/repeats to decide cuts
                        "show_utterances": True}}     # utterances carry words[] with per-character timestamps


def post(url, hdr, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=hdr)
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.headers, r.read()


def flash(audio):
    url, res = FLASH
    h, body = post(url, headers(res, str(uuid.uuid4())), payload(audio))
    code = h.get("X-Api-Status-Code")
    if code != "20000000":
        sys.exit(f"Recognition failed {code} {h.get('X-Api-Message')}: {body[:300]!r}")
    return json.loads(body)


def standard(audio):
    sub, qry, res = STANDARD
    rid = str(uuid.uuid4())
    h, body = post(sub, headers(res, rid), payload(audio))
    if h.get("X-Api-Status-Code") != "20000000":
        sys.exit(f"Submit failed {h.get('X-Api-Status-Code')} {h.get('X-Api-Message')}")
    qh = headers(res, rid)
    if h.get("X-Tt-Logid"):
        qh["X-Tt-Logid"] = h["X-Tt-Logid"]
    for _ in range(240):
        time.sleep(5)
        h, body = post(qry, qh, {})
        code = h.get("X-Api-Status-Code")
        if code == "20000003":
            sys.exit("Audio is silent (20000003)")
        if code == "20000000":
            return json.loads(body)
        if code not in ("20000001", "20000002", None):
            sys.exit(f"Recognition failed {code} {h.get('X-Api-Message')}")
        print(".", end="", flush=True)
    sys.exit("Polling timed out")


def over_flash_limits(audio):
    size = Path(audio).stat().st_size
    try:
        from common import duration
        sec = duration(audio)
    except Exception:
        sec = 0
    if size > FLASH_MAX_BYTES or sec > FLASH_MAX_SEC:
        print(f"{size/1e6:.0f} MB / {sec/60:.0f} min exceeds Flash limits -> using Standard")
        return True
    return False


def normalize(raw, media=None):
    """Raw Volcengine result -> talkcut transcript: seconds, words per sentence, everything keep=True."""
    utts = raw.get("result", raw).get("utterances") or []
    sents = []
    for i, u in enumerate(utts):
        words = [{"text": w["text"], "start": w["start_time"] / 1000, "end": w["end_time"] / 1000, "keep": True}
                 for w in u.get("words", []) if w.get("text", "").strip()]
        sents.append({"id": i, "start": u["start_time"] / 1000, "end": u["end_time"] / 1000,
                      "text": u["text"], "keep": True, "reason": "", "words": words})
    return {"version": 1, "media": media, "pause_keep": 0.5, "sentences": sents}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("audio", nargs="?")
    p.add_argument("-o", "--out", default="work/transcript.json")
    p.add_argument("--standard", action="store_true", help="use the async Standard API (long audio / large files)")
    p.add_argument("--normalize", help="existing raw Volcengine JSON")
    p.add_argument("--media", default="source.mp4", help="video path stored in the transcript (relative to its folder)")
    a = p.parse_args()
    if a.normalize:
        raw = json.loads(Path(a.normalize).read_text(encoding="utf-8"))
    else:
        if not a.audio:
            p.error("an audio file is required")
        raw = standard(a.audio) if a.standard or over_flash_limits(a.audio) else flash(a.audio)
        Path(a.out).with_suffix(".raw.json").write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    t = normalize(raw, a.media)
    Path(a.out).write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(t['sentences'])} sentences -> {a.out}")
