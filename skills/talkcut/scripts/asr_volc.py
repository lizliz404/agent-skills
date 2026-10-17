#!/usr/bin/env python3
"""步骤 2–3：火山引擎豆包语音「大模型录音文件识别」→ 带字级时间戳的逐字稿 transcript.json。

用法:
  python3 asr_volc.py work/audio.mp3 -o work/transcript.json            # 极速版（同步，默认）
  python3 asr_volc.py work/audio.mp3 -o work/transcript.json --standard # 标准版（异步 submit/query）
  python3 asr_volc.py --normalize raw.json -o work/transcript.json      # 只把已有原始结果转成 talkcut 格式

凭证（只从环境变量 / 本机 env 文件读取，绝不写进仓库）：
  新版控制台: DOUBAO_API_KEY            → X-Api-Key
  旧版控制台: VOLC_APP_ID + VOLC_ACCESS_TOKEN → X-Api-App-Key / X-Api-Access-Key
  也会读取 ~/.agents/env/doubao-tts.env（与本仓库 doubao-tts 技能共用）。

只开必要参数：标点 + ITN + 分句(utterances，含 words)。不开说话人分离、情绪、语速等附加项，省钱。
"""
import argparse, base64, json, os, sys, time, urllib.request, uuid
from pathlib import Path

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
        sys.exit("缺少凭证：设置 DOUBAO_API_KEY，或 VOLC_APP_ID + VOLC_ACCESS_TOKEN")
    return h


def payload(audio_path):
    data = base64.b64encode(Path(audio_path).read_bytes()).decode()
    return {"user": {"uid": "talkcut"},
            "audio": {"data": data, "format": Path(audio_path).suffix.lstrip(".") or "mp3"},
            "request": {"model_name": "bigmodel", "enable_itn": True, "enable_punc": True,
                        "enable_ddc": False,          # 不做顺滑：语气词/重复要留给我们自己判断
                        "show_utterances": True}}     # utterances 内含 words[] 的字级时间戳


def post(url, hdr, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=hdr)
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.headers, r.read()


def flash(audio):
    url, res = FLASH
    h, body = post(url, headers(res, str(uuid.uuid4())), payload(audio))
    code = h.get("X-Api-Status-Code")
    if code != "20000000":
        sys.exit(f"识别失败 {code} {h.get('X-Api-Message')}: {body[:300]!r}")
    return json.loads(body)


def standard(audio):
    sub, qry, res = STANDARD
    rid = str(uuid.uuid4())
    h, body = post(sub, headers(res, rid), payload(audio))
    if h.get("X-Api-Status-Code") != "20000000":
        sys.exit(f"提交失败 {h.get('X-Api-Status-Code')} {h.get('X-Api-Message')}")
    qh = headers(res, rid)
    if h.get("X-Tt-Logid"):
        qh["X-Tt-Logid"] = h["X-Tt-Logid"]
    for _ in range(240):
        time.sleep(5)
        h, body = post(qry, qh, {})
        code = h.get("X-Api-Status-Code")
        if code == "20000000":
            return json.loads(body)
        if code not in ("20000001", "20000002", None):
            sys.exit(f"识别失败 {code} {h.get('X-Api-Message')}")
        print(".", end="", flush=True)
    sys.exit("轮询超时")


def normalize(raw, media=None):
    """火山原始结果 → talkcut transcript：秒为单位，每句带 words，默认全部 keep。"""
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
    p.add_argument("--standard", action="store_true", help="用标准版异步接口（长音频/大文件）")
    p.add_argument("--normalize", help="已有的火山原始 JSON")
    p.add_argument("--media", default="source.mp4", help="写入 transcript 的视频路径（相对 transcript 所在目录）")
    a = p.parse_args()
    if a.normalize:
        raw = json.loads(Path(a.normalize).read_text(encoding="utf-8"))
    else:
        if not a.audio:
            p.error("需要音频文件")
        raw = standard(a.audio) if a.standard else flash(a.audio)
        Path(a.out).with_suffix(".raw.json").write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    t = normalize(raw, a.media)
    Path(a.out).write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(t['sentences'])} 句 → {a.out}")
