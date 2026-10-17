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
  version: "0.3.0"
  evidence-basis: "Real Linux footage: live Doubao ASR, manually reviewed cuts, semantic captions, full decode and sampled browser playback in an extended workspace; semantic validator/burn gates integrated here, richer workspace UI/rendering not yet fully bundled"
---

# talkcut

ffmpeg and the ASR service do the heavy lifting. The agent does only what it is actually good at: **reading the transcript** (which lines are retakes, how to chapter it) and **gluing the pieces together**.
All scripts live in `scripts/` and need only Python 3 stdlib + ffmpeg/ffprobe; the navigation bar additionally needs Pillow.

**Read [production lessons](references/production-lessons.md) before real-footage rendering or review-UI work.** It captures semantic-caption hard gates, human-edit ownership, low-cost production-frame preflight, default localhost delivery, bounded rendering and conservative speed. These are mandatory workflow requirements; it also identifies capabilities not yet fully integrated into the bundled CLI.

## Quick start (Linux / Arch / Omarchy, also macOS)

```bash
python3 scripts/doctor.py                          # checks ffmpeg+libass+x264, Pillow, CJK font, Doubao key, disk; prints fix commands
python3 scripts/talkcut.py run clip1.mp4 clip2.mp4 # prep -> ASR (cached by audio hash) -> rule cuts -> review server
#   agent: read work/transcript.json, write work/plan.json (contract below), rerun the same `run` command
python3 scripts/talkcut.py render --no-burn        # clean cut + DRAFT subtitle export; agent then writes reviewed work/caption-plan.json
python3 scripts/talkcut.py render                  # reviewed semantic subtitles + navbar (if work/chapters.json exists)
python3 scripts/talkcut.py status
```
On Arch/Omarchy the one-time setup is `sudo pacman -S --needed ffmpeg python-pillow noto-fonts-cjk`.
Every stage is cached in `work/state.json`; reruns skip finished steps, and the raw ASR result is cached in
`~/.cache/talkcut/asr/<sha256>.json`, so completed cached results are reused. This is not an exactly-once billing guarantee after an ambiguous request/network failure; inspect receipts before resubmitting. The steps below are what the driver runs.

## Workflow

All artifacts go into one working directory (`work/` below); scripts hand off only through JSON.

1. **Concat + extract audio**
   `python3 scripts/prep.py clip1.mp4 clip2.mp4 … -o work/` → `work/source.mp4`, `work/audio.mp3` (16 kHz mono).
   Multiple clips are re-encoded uniformly then joined; a single clip is copied. Join in the order the user gave; never reorder.

2. **Transcribe (Volcengine Doubao Speech big-model file ASR)**
   `python3 scripts/asr_volc.py work/audio.mp3 -o work/transcript.json` uses Flash (synchronous) and switches automatically to Standard (async submit/query) when the audio exceeds Flash limits (> 2 h or > 100 MB). `--standard` forces Standard.
   Credentials come only from env vars: `DOUBAO_API_KEY` (new console) or `VOLC_APP_ID` + `VOLC_ACCESS_TOKEN` (old console).
   Enable only punctuation + ITN + utterances (with per-character words). **Keep disfluency smoothing `enable_ddc` off** (we need fillers and repeats to decide cuts). No diarization or other paid extras.
   API details and setup: [references/volcengine-asr.md](references/volcengine-asr.md). If credentials are missing, stop and tell the user where to enable them; do not switch to another cloud provider.

3. **Transcript** `work/transcript.json` (see "Data format"). The raw response is also saved as `transcript.raw.json`.

4. **AI first-pass cut** (edits keep flags only; the video is untouched)
   - The driver runs the heuristic first (adjacent sentences with bigram similarity ≥ 0.72 within 20 s → retake, keep the last; fillers-only sentences → cut). Its cuts are tagged `by: "rule"`.
   - Then **the agent does the semantic pass** using the contract below, writes `work/plan.json`, and reruns `talkcut.py run …` (or `autocut.py work/transcript.json --plan work/plan.json`). Plan cuts are tagged `by: "ai"`; anything the user toggles in the review page is `by: "manual"` and is never overridden.
   - Breathing room: `pause_keep` (default 0.5 s, tune within 0.4–0.6). Pauses between kept words ≤ this value stay as-is; longer ones are shortened to it. Pauses are handled by render.py; do not cut sentences just to remove silence.

   **Semantic-pass contract (follow exactly).**
   Read every sentence of `work/transcript.json` (`id`, `text`, `start`, `end`, `words[]` with indexes from 0) in order. Then write `work/plan.json`:
   ```json
   {
     "cut":       [{"id": 1, "type": "retake", "kept": 2, "reason": "same line restated; keep the last take #2"}],
     "cut_words": [{"id": 3, "from": 0, "to": 3, "reason": "restart mid-sentence: drop the first 我们今天"}],
     "keep":      [{"id": 0, "reason": "rule flagged it but it is intentional repetition for emphasis"}],
     "notes":     "optional free text for the user"
   }
   ```
   - `type` ∈ `retake | false_start | filler | off_topic | other`. A `retake` **must** name `kept`: the id of the surviving take, which must come **after** the cut one and must not be cut itself. When a line is said 3 times, cut the first two, both with `kept` = the third.
   - Retakes count by **meaning**, not wording: "我每句话都会说好几遍" then "我每句话都会重复说好几遍" → cut the first. The last take wins unless it is clearly broken off; in that case keep the best complete one and say why.
   - Partial restart inside one sentence ("我们今天，我们今天只留最后一遍"): use `cut_words` with inclusive word indexes `from..to` covering the abandoned start. Never use `cut_words` for the whole sentence; use `cut`.
   - Fillers (嗯/啊/那个, "um", "like"): cut standalone ones or obvious stumbles; keep fillers that carry tone or meaning.
   - Use `keep` to overrule a heuristic cut that is wrong (intentional repetition, callbacks, lists).
   - Never cut for silence alone, never reorder, never rewrite text. When unsure, keep it and mention it in `notes`.
   - Validate before applying: `python3 scripts/autocut.py work/transcript.json --plan work/plan.json --check-only`. Fix every reported error; exit code 2 means invalid.

5. **Localhost review page**
   `talkcut.py run` starts it (or `python3 scripts/review_server.py work/transcript.json`) → `http://127.0.0.1:8765`.
   Cuts are struck through and colour-coded by source: amber = rule, violet = AI, red = you. Live counters show kept duration vs original.
   Keys: `space` play/pause, `j`/`k` next/previous sentence (seeks video), `x` toggle cut, `p` preview (plays the final cut, skipping cut parts and capping long pauses), `u` or ⌘/Ctrl+Z undo. Click toggles a sentence, Alt/⌥+click a word cuts just that word, double-click plays from there.
   Edits autosave to `transcript.json` (previous version kept as `transcript.bak.json`).
   Give the user the URL and **wait for confirmation** before rendering. The user may also say "keep sentence 12" in chat; the agent edits the JSON directly.

6. **Render** `python3 scripts/render.py work/transcript.json` → `work/cut.mp4` + `work/cut.json` (transcript on the new timeline).
   trim/atrim + concat with re-encode for frame accuracy; 10 ms audio fades at each cut prevent clicks.

7. **Subtitles** `python3 scripts/subs.py work/cut.json --caption-plan work/caption-plan.json --style simple|karaoke [--burn]`
   - `simple`: white text with black outline. `karaoke`: per-word highlight (current word recoloured and scaled to 118%).
   - Always exports `cut.srt` (importable into CapCut / 剪映) and the matching `.ass`; `--burn` also renders `cut_<style>.mp4`.
   - Tuning: `--max-chars` per line, `--font` font name, `--highlight` colour (ASS `&HAABBGGRR`).
   - **Semantic phrasing comes before character count.** For Chinese, aim for a flexible 8–12 characters per cue when suitable; this is a readability guide, not a quota or mandatory minimum. Prefer complete short phrases, clauses, real punctuation and spoken pauses. Do not split every 10 characters, split a word/name/number-unit combination, or strand a conjunction merely to meet a count. Short complete cues are fine; preserve longer inseparable expressions when layout permits. ASR sentence boundaries can also be incomplete: review adjacent sentences together.
   - **Hard render gate:** no final subtitle burn without an explicit agent-authored, reviewed semantic cue plan. Fixed-count chunking is prohibited for final delivery, even if every cue passes a length assertion. Preserve exact retained wording and order; save `caption-plan.json` as `{"reviewed_by":"agent-name", "cues":["exact phrase", "next phrase"]}`, then run `python3 scripts/caption_plan.py work/cut.json work/caption-plan.json -o work/captions.json`. Map reviewed cues into SRT/ASS. The validator proves exact text coverage and timing, not semantics. Use proportional within-token timing only when unavoidable and record that it is estimated. `subs.py --max-chars` remains a mechanical draft fallback; its direct output is not an approved final-caption path. Both `subs.py --burn` and the render driver now reject missing/unreviewed semantic plans, and the driver includes the plan in its subtitle cache key.
   - **Review before burning:** inspect several real consecutive cues and one frame from the production subtitle renderer. A good-looking still does not prove fluent segmentation. Retain a clean cut without overlays plus editable SRT/ASS, so approved caption changes do not require ASR or redoing cuts.
   - **2026-10 real-use lesson:** mechanically cutting Chinese every 10 characters produced abrupt, unnatural subtitles despite passing length checks. Do not turn a user's approximate length preference into a rigid splitter. When captions are already burned, estimate the cost of returning to the clean cut and re-encoding before rerendering; do not paint a second caption on top of old text or silently repeat expensive full renders.
   - **Packaging and speed:** choose episode boundaries at complete ideas, not equal duration alone. If the user accepts existing overlays, compatible H.264/AAC parts can be joined/split near verified video keyframes with stream copy. A small speed change may be possible by retiming copied video and using pitch-preserving audio `atempo`; verify actual output duration, playback and A/V sync, and state the changed effective frame rate. If constant source FPS, precise non-keyframe cuts or new overlays are required, re-encode once from clean cuts and combine all approved changes in that pass.

8. **Chapter navigation bar** (style credited to [dbskill / dbs-video-navigation](https://github.com/dontbesilent2025/dbskill))
   - The agent reads `cut.json`, chapters it by "what problem is being addressed", and writes `work/chapters.json`:
     ```json
     {"chapters": [{"title": "Part 1: Why cut talking heads",
                    "segments": [{"start": 0, "desc": "CapCut misses meaning"}, {"start": 12.3, "desc": "Keep only the last take"}]}]}
     ```
     `start` is final-cut time in seconds, taken from sentence starts in `cut.json`; the first segment starts at 0. Top line = which part we are in, bottom line = what this segment says; both must fit on one line. Write titles in the video's language.
   - `python3 scripts/navbar.py work/cut.json work/chapters.json` → `work/navbar.mp4`: same length as the cut, no audio, same width, black background, white text, blue progress bar with gaps between chapters. Style lives in `assets/navbar-black-blue.json`.
   - On delivery, explain: drop it into CapCut above the main track, aligned at 0 s, at the top of the frame; to make room, scale the original down and shift it.

## Delivery defaults

- Choose one durable user-approved video root on the media/data partition and use one project directory per job. Keep final MP4 and subtitle sidecars together; put new job inputs/work/cache under that project rather than scattering directories. Move approved existing deliverables instead of making duplicate copies; verify hashes and update links (or use lightweight symlink compatibility paths). Never broadly move/delete unrelated old media without authorization. Do not hard-code a user's absolute path into this portable Skill.
- Serve review, independent clips and final episodes on the same loopback site with progress, real playback, seeking and downloads. Provide clickable localhost links without waiting for a user reminder; file paths alone are not delivery. Extend an existing review service where available. The bundled CLI review page is not yet the full Clip/Episode delivery workspace: implement missing delivery routes when needed and report that integration boundary.
- Before a full burn, show a low-cost actual production frame and check a short sequence of consecutive captions. Preserve approved navigation/design; don't add effects or reset the workflow for a local correction.
- Default to natural speed. Where a mild speedup is approved, keep it at 1.05× for this style unless the user explicitly asks for and accepts more after listening. Faster encoding playback is not necessarily better comprehension; avoid a rushed, less-human delivery. Viewers can choose a faster player speed themselves.

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
