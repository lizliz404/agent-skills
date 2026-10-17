---
name: talkcut
description: >-
  Talking-head video cutting: concat clips → Volcengine Doubao Speech (豆包语音) ASR with per-character timestamps →
  AI marks retakes by meaning (keep only the last take of a repeated line), fillers and over-long pauses (keeping
  natural breathing room) → localhost review page with strike-through editing → frame-accurate ffmpeg cut with
  remapped timeline → subtitles (simple or per-word karaoke highlight) → black/white/blue chapter navigation bar.
  Use when the user wants to cut a talking-head video, remove retakes, add subtitles, or add chapter navigation.
license: MIT
metadata:
  version: "0.1.0"
  evidence-basis: "Scripts run end-to-end on a synthetic video and fake transcript; live Volcengine ASR and semantic cut quality on real footage not yet verified"
---

# talkcut

ffmpeg and the ASR service do the heavy lifting. The agent does only what it is actually good at: **reading the transcript** (which lines are retakes, how to chapter it) and **gluing the pieces together**.
All scripts live in `scripts/` and need only Python 3 stdlib + ffmpeg/ffprobe; the navigation bar additionally needs Pillow.

## Workflow

All artifacts go into one working directory (`work/` below); scripts hand off only through JSON.

1. **Concat + extract audio**
   `python3 scripts/prep.py clip1.mp4 clip2.mp4 … -o work/` → `work/source.mp4`, `work/audio.mp3` (16 kHz mono).
   Multiple clips are re-encoded uniformly then joined; a single clip is copied. Join in the order the user gave; never reorder.

2. **Transcribe (Volcengine Doubao Speech big-model file ASR)**
   `python3 scripts/asr_volc.py work/audio.mp3 -o work/transcript.json` (Flash, synchronous).
   If the audio exceeds Flash limits, add `--standard` (async submit/query).
   Credentials come only from env vars: `DOUBAO_API_KEY` (new console) or `VOLC_APP_ID` + `VOLC_ACCESS_TOKEN` (old console).
   Enable only punctuation + ITN + utterances (with per-character words). **Keep disfluency smoothing `enable_ddc` off** (we need fillers and repeats to decide cuts). No diarization or other paid extras.
   API details and setup: [references/volcengine-asr.md](references/volcengine-asr.md). If credentials are missing, stop and tell the user where to enable them; do not switch to another cloud provider.

3. **Transcript** `work/transcript.json` (see "Data format"). The raw response is also saved as `transcript.raw.json`.

4. **AI first-pass cut** (edits keep flags only; the video is untouched)
   - Run the heuristic first: `python3 scripts/autocut.py work/transcript.json --pause 0.5`
     Adjacent sentences with bigram similarity ≥ 0.72 within 20 s → retake: cut the earlier ones, keep the last. Sentences made only of fillers → cut.
   - Then **the agent must read the whole transcript**, catch what the rules miss, write `work/plan.json`, and run `autocut.py work/transcript.json --plan work/plan.json`:
     - Rephrased retakes (same meaning, different words) → cut the earlier ones, keep the last. **The last take is assumed best** unless it is clearly cut off.
     - Fragments and instant self-corrections ("this… no, that") → use `cut_words` to remove up to the correction.
     - Fillers (嗯/啊/那个, "um", "like"): cut only standalone ones or obvious stumbles; keep fillers that carry meaning.
     - When unsure, keep it and write a reason so the user decides on the review page. Under-cutting beats cutting meaningful content.
   - Breathing room: `pause_keep` (default 0.5 s, tune within 0.4–0.6). Pauses between words ≤ this value stay as-is; longer ones are shortened to it.

5. **Localhost review page**
   `python3 scripts/review_server.py work/transcript.json` → open `http://127.0.0.1:8765`.
   Click a sentence to toggle keep/cut (cut is shown struck through); Alt/⌥+click cuts a single word; double-click plays from there; "Preview final cut" skips cut parts during playback; drag the pause slider; ⌘/Ctrl+S saves back to the JSON (previous version kept as `transcript.bak.json`).
   Give the user the URL and **wait for confirmation** before rendering. The user may also say "keep sentence 12" in chat; the agent edits the JSON directly.

6. **Render** `python3 scripts/render.py work/transcript.json` → `work/cut.mp4` + `work/cut.json` (transcript on the new timeline).
   trim/atrim + concat with re-encode for frame accuracy; 10 ms audio fades at each cut prevent clicks.

7. **Subtitles** `python3 scripts/subs.py work/cut.json --style simple|karaoke [--burn]`
   - `simple`: white text with black outline. `karaoke`: per-word highlight (current word recoloured and scaled to 118%).
   - Always exports `cut.srt` (importable into CapCut / 剪映) and the matching `.ass`; `--burn` also renders `cut_<style>.mp4`.
   - Tuning: `--max-chars` per line, `--font` font name, `--highlight` colour (ASS `&HAABBGGRR`).

8. **Chapter navigation bar** (style credited to [dbskill / dbs-video-navigation](https://github.com/dontbesilent2025/dbskill))
   - The agent reads `cut.json`, chapters it by "what problem is being addressed", and writes `work/chapters.json`:
     ```json
     {"chapters": [{"title": "Part 1: Why cut talking heads",
                    "segments": [{"start": 0, "desc": "CapCut misses meaning"}, {"start": 12.3, "desc": "Keep only the last take"}]}]}
     ```
     `start` is final-cut time in seconds, taken from sentence starts in `cut.json`; the first segment starts at 0. Top line = which part we are in, bottom line = what this segment says; both must fit on one line. Write titles in the video's language.
   - `python3 scripts/navbar.py work/cut.json work/chapters.json` → `work/navbar.mp4`: same length as the cut, no audio, same width, black background, white text, blue progress bar with gaps between chapters. Style lives in `assets/navbar-black-blue.json`.
   - On delivery, explain: drop it into CapCut above the main track, aligned at 0 s, at the top of the frame; to make room, scale the original down and shift it.

## Acceptance checks (after every render)

- `ffprobe` the durations of cut.mp4 / navbar.mp4 (navbar.py compares them automatically).
- Grab a few frames: no clipped words at cuts, subtitles inside the frame, longest navbar title fits (the script warns), progress bar fills at the end.
- Report to the user: sentences cut, final length, path of every artifact. A clean script run ≠ a good edit; semantic quality counts only once the user has watched it.

## Data format

`transcript.json` (before render):
```json
{"version": 1, "media": "source.mp4", "pause_keep": 0.5,
 "sentences": [{"id": 0, "start": 0.3, "end": 2.4, "text": "Hello", "keep": true, "reason": "",
                "words": [{"text": "He", "start": 0.3, "end": 0.5, "keep": true}]}]}
```
`cut.json` (after render, final-cut times): `{"media": "cut.mp4", "duration": …, "segments": [[src_start, src_end], …], "sentences": [{id, start, end, text, words[]}]}`

## Boundaries

- Upload nothing to any service other than Volcengine; never commit or print credentials.
- Never overwrite the user's source footage; all output goes into `work/`.
- Out of scope: colour grading, music, B-roll, covers. For animated captions, hand `cut.json` to a tool like HyperFrames.
