#!/usr/bin/env python3
"""Check everything talkcut needs and print exact fix commands. Never prints secret values.
Usage: python3 doctor.py [--work work/]   (exit 0 = ready, 1 = something missing)
"""
import argparse, os, platform, shutil, subprocess, sys
from pathlib import Path

FIX = {
    "arch":   {"ffmpeg": "sudo pacman -S --needed ffmpeg", "pillow": "sudo pacman -S --needed python-pillow",
               "font": "sudo pacman -S --needed noto-fonts-cjk", "all": "sudo pacman -S --needed ffmpeg python-pillow noto-fonts-cjk"},
    "debian": {"ffmpeg": "sudo apt install -y ffmpeg", "pillow": "sudo apt install -y python3-pil",
               "font": "sudo apt install -y fonts-noto-cjk", "all": "sudo apt install -y ffmpeg python3-pil fonts-noto-cjk"},
    "macos":  {"ffmpeg": "brew install ffmpeg", "pillow": "python3 -m pip install --user pillow",
               "font": "(PingFang is built in; or: brew install --cask font-noto-sans-cjk-sc)",
               "all": "brew install ffmpeg && python3 -m pip install --user pillow"},
}


def distro():
    if sys.platform == "darwin":
        return "macos"
    try:
        txt = Path("/etc/os-release").read_text().lower()
    except OSError:
        txt = ""
    if any(k in txt for k in ("arch", "omarchy", "manjaro", "endeavouros")):
        return "arch"
    return "debian"


def run(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--work", default="."); a = ap.parse_args()
    d = distro(); fix = FIX[d]; bad = []
    ok = lambda m: print(f"  ✓ {m}")

    def no(m, f=None):
        print(f"  ✗ {m}" + (f"\n      fix: {f}" if f else "")); bad.append(m)

    print(f"talkcut doctor · {platform.system()} ({d})")
    v = sys.version_info
    ok(f"python {v.major}.{v.minor}") if v >= (3, 9) else no(f"python {v.major}.{v.minor} < 3.9", "install a newer python3")

    ff, fp = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not (ff and fp):
        no("ffmpeg / ffprobe not found", fix["ffmpeg"])
    else:
        ver = run(ff, "-version").splitlines()[0] if run(ff, "-version") else "?"
        ok(ver[:60])
        filters, enc = run(ff, "-hide_banner", "-filters"), run(ff, "-hide_banner", "-encoders")
        for f in ("subtitles", "ass", "drawbox", "drawtext", "trim", "atrim", "concat", "afade"):
            # drawtext is optional (navbar uses Pillow); the rest are required
            if f" {f} " in filters:
                ok(f"filter {f}")
            elif f == "drawtext":
                print("  · filter drawtext missing (optional; navbar uses Pillow)")
            else:
                no(f"ffmpeg filter '{f}' missing (needs libass for subtitles/ass)", fix["ffmpeg"])
        ok("encoder libx264") if " libx264 " in enc else no("encoder libx264 missing", fix["ffmpeg"])
        ok("encoder aac") if " aac " in enc else no("encoder aac missing", fix["ffmpeg"])

    try:
        import PIL
        ok(f"Pillow {PIL.__version__}")
    except ImportError:
        no("Pillow missing (needed for the navigation bar)", fix["pillow"])

    if shutil.which("fc-list"):
        fonts = [l for l in run("fc-list", ":lang=zh", "file").splitlines() if l.strip()]
        ok(f"CJK fonts: {len(fonts)} (e.g. {fonts[0].strip().rstrip(':')})") if fonts else no("no CJK font", fix["font"])
    elif d == "macos":
        ok("CJK font: system PingFang")
    else:
        no("fc-list (fontconfig) not found", fix["font"])

    envf = [p for p in (Path.home() / ".agents/env/doubao-tts.env", Path.home() / ".agents/secrets/doubao-tts.env") if p.is_file()]
    keys = [k for k in ("DOUBAO_API_KEY", "VOLC_API_KEY") if os.environ.get(k)]
    legacy = os.environ.get("VOLC_APP_ID") and os.environ.get("VOLC_ACCESS_TOKEN")
    infile = any("DOUBAO_API_KEY" in p.read_text(errors="ignore") or "VOLC_ACCESS_TOKEN" in p.read_text(errors="ignore") for p in envf)
    if keys or legacy:
        ok(f"Doubao credentials in environment ({', '.join(keys) or 'VOLC_APP_ID + VOLC_ACCESS_TOKEN'}; value hidden)")
    elif infile:
        ok(f"Doubao credentials in {envf[0]} (value hidden)")
    else:
        no("no Doubao Speech credentials",
           "enable 录音文件识别大模型 (big-model file ASR) at https://console.volcengine.com/speech/new/overview, "
           "create an API key, then: mkdir -p ~/.agents/env && echo 'DOUBAO_API_KEY=<key>' >> ~/.agents/env/doubao-tts.env "
           "&& chmod 600 ~/.agents/env/doubao-tts.env")

    free = shutil.disk_usage(Path(a.work).resolve() if Path(a.work).exists() else Path.cwd()).free / 1e9
    ok(f"free disk {free:.1f} GB") if free > 5 else no(f"only {free:.1f} GB free (renders need ~3x source size)", "free some space")

    if bad:
        print(f"\n{len(bad)} problem(s).")
        if any(not b.startswith(("no Doubao", "only")) for b in bad):
            print(f"One-shot package fix for {d}:\n  {fix['all']}")
        return 1
    print("\nReady. Next: python3 scripts/talkcut.py run clip1.mp4 [clip2.mp4 ...]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
