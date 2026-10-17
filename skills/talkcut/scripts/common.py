"""talkcut 共用工具：读写 JSON、ffprobe、时间格式。仅标准库。"""
import json, shutil, subprocess, sys
from pathlib import Path


def need(tool):
    path = shutil.which(tool)
    if not path:
        sys.exit(f"缺少 {tool}，请先安装 ffmpeg（含 ffprobe）")
    return path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def duration(media):
    out = subprocess.run([need("ffprobe"), "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(media)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def video_info(media):
    out = subprocess.run([need("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", str(media)],
                         capture_output=True, text=True, check=True)
    s = json.loads(out.stdout)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(n) / float(d)


def ts(sec, sep=","):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"
