#!/usr/bin/env python3
"""One-command driver with stage caching.

  python3 talkcut.py run clip1.mp4 [clip2.mp4 ...] [-w work] [--port 8765] [--no-serve]
      prep -> ASR (cached by audio hash: never pay twice) -> autocut (+ work/plan.json if present) -> review server
  python3 talkcut.py render [-w work] [--style simple|karaoke] [--no-burn]
      cut -> subtitles -> navbar (navbar only if work/chapters.json exists)
  python3 talkcut.py status [-w work]

Each stage stores a hash of its inputs in work/state.json; a rerun skips stages whose inputs did not change.
Review edits (manual keep/cut) are never overwritten: autocut skips sentences marked by="manual".
ASR cache: ~/.cache/talkcut/asr/<sha256-of-audio>.json (override with TALKCUT_CACHE).
"""
import argparse, hashlib, json, os, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = Path(os.environ.get("TALKCUT_CACHE", Path.home() / ".cache/talkcut")) / "asr"


def sha(*paths_or_text):
    h = hashlib.sha256()
    for x in paths_or_text:
        p = Path(x) if isinstance(x, (str, Path)) and Path(x).is_file() else None
        if p:
            with open(p, "rb") as f:
                for b in iter(lambda: f.read(1 << 20), b""):
                    h.update(b)
        else:
            h.update(str(x).encode())
    return h.hexdigest()


class State:
    def __init__(self, work):
        self.work, self.path = work, work / "state.json"
        self.d = json.loads(self.path.read_text()) if self.path.exists() else {}

    def fresh(self, stage, key, *outputs):
        return self.d.get(stage) == key and all((self.work / o).exists() for o in outputs)

    def done(self, stage, key):
        self.d[stage] = key
        self.path.write_text(json.dumps(self.d, indent=2))


def step(name, skipped):
    print(f"{'·' if skipped else '▶'} {name}{' (cached)' if skipped else ''}", flush=True)


def py(script, *args):
    sys.stdout.flush()
    subprocess.run([sys.executable, str(HERE / script), *map(str, args)], check=True)


def cmd_run(a):
    w = Path(a.work).resolve(); w.mkdir(parents=True, exist_ok=True); st = State(w)
    clips = [Path(c).resolve() for c in a.clips]
    for c in clips:
        if not c.is_file():
            sys.exit(f"not found: {c}")
    key = sha(*[f"{c}:{c.stat().st_size}:{c.stat().st_mtime_ns}" for c in clips])
    skip = st.fresh("prep", key, "source.mp4", "audio.mp3"); step("prep (concat + audio)", skip)
    if not skip:
        py("prep.py", *clips, "-o", w); st.done("prep", key)

    akey = sha(w / "audio.mp3")
    skip = st.fresh("asr", akey, "transcript.json"); step("ASR (Doubao Speech)", skip)
    if not skip:
        CACHE.mkdir(parents=True, exist_ok=True)
        raw = CACHE / f"{akey}.json"
        if raw.exists():
            print(f"  ASR cache hit: {raw} (no charge)")
        else:
            py("asr_volc.py", w / "audio.mp3", "-o", w / "transcript.json", *(["--standard"] if a.standard else []))
            shutil.copyfile(w / "transcript.raw.json", raw)
        py("asr_volc.py", "--normalize", raw, "-o", w / "transcript.json", "--media", "source.mp4")
        st.done("asr", akey); st.d.pop("autocut", None)

    plan = w / "plan.json"
    ckey = sha(akey, plan if plan.exists() else "-", a.pause)
    skip = st.fresh("autocut", ckey, "transcript.json"); step("autocut (rules + plan.json)", skip)
    if not skip:
        py("autocut.py", w / "transcript.json", "--pause", a.pause, *(["--plan", plan] if plan.exists() else []))
        st.done("autocut", ckey)
    if not plan.exists():
        print(f"  next for the agent: read {w/'transcript.json'}, write {plan} (contract in SKILL.md), rerun `run`")
    if not a.no_serve:
        print("▶ review server (Ctrl+C when done, then: talkcut.py render)")
        py("review_server.py", w / "transcript.json", "--port", a.port)


def cmd_render(a):
    w = Path(a.work).resolve(); st = State(w)
    if not (w / "transcript.json").exists():
        sys.exit("no transcript.json; run `talkcut.py run` first")
    k = sha(w / "transcript.json", a.pad)
    skip = st.fresh("render", k, "cut.mp4", "cut.json"); step("cut", skip)
    if not skip:
        py("render.py", w / "transcript.json", "-o", w / "cut.mp4", "--pad", a.pad); st.done("render", k)
    k2 = sha(w / "cut.json", a.style, a.no_burn)
    outs = ["cut.srt"] + ([] if a.no_burn else [f"cut_{a.style}.mp4"])
    skip = st.fresh("subs", k2, *outs); step(f"subtitles ({a.style})", skip)
    if not skip:
        py("subs.py", w / "cut.json", "--style", a.style, *([] if a.no_burn else ["--burn"])); st.done("subs", k2)
    ch = w / "chapters.json"
    if ch.exists():
        k3 = sha(w / "cut.json", ch)
        skip = st.fresh("navbar", k3, "navbar.mp4"); step("navbar", skip)
        if not skip:
            py("navbar.py", w / "cut.json", ch, "-o", w / "navbar.mp4"); st.done("navbar", k3)
    else:
        print(f"· navbar skipped: agent writes {ch} from cut.json (see SKILL.md step 8), then rerun render")
    cmd_status(a)


def cmd_status(a):
    w = Path(a.work).resolve(); st = State(w)
    print(f"\nwork dir: {w}")
    for s in ("prep", "asr", "autocut", "render", "subs", "navbar"):
        print(f"  {'✓' if s in st.d else '·'} {s}")
    t = w / "transcript.json"
    if t.exists():
        S = json.loads(t.read_text())["sentences"]
        by = {}
        for s in S:
            if not s["keep"]:
                by[s.get("by", "?")] = by.get(s.get("by", "?"), 0) + 1
        print(f"  transcript: {len(S)} sentences, cut {sum(by.values())} {by}")
    for f in ("cut.mp4", "cut.srt", "cut_simple.mp4", "cut_karaoke.mp4", "navbar.mp4"):
        if (w / f).exists():
            print(f"  → {w / f}")


ap = argparse.ArgumentParser(description="talkcut driver")
sub = ap.add_subparsers(dest="cmd", required=True)
r = sub.add_parser("run"); r.add_argument("clips", nargs="+")
r.add_argument("--pause", type=float, default=0.5); r.add_argument("--port", type=int, default=8765)
r.add_argument("--standard", action="store_true"); r.add_argument("--no-serve", action="store_true")
r.set_defaults(fn=cmd_run)
d = sub.add_parser("render"); d.add_argument("--style", choices=["simple", "karaoke"], default="karaoke")
d.add_argument("--no-burn", action="store_true"); d.add_argument("--pad", type=float, default=0.05)
d.set_defaults(fn=cmd_render)
s = sub.add_parser("status"); s.set_defaults(fn=cmd_status)
for p in (r, d, s):
    p.add_argument("-w", "--work", default="work")
args = ap.parse_args()
try:
    args.fn(args)
except subprocess.CalledProcessError as e:
    sys.exit(f"\n✗ step failed: {Path(e.cmd[1]).name} (exit {e.returncode}). Fix the error above and rerun; finished steps are cached.")
except KeyboardInterrupt:
    print("\nstopped. Next: python3 talkcut.py render")
