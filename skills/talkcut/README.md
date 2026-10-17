# talkcut

Turn one or more raw talking-head clips into a publishable cut: **when a line is said several times, keep only the last take; keep natural breathing pauses, shorten long silences; get subtitles and a chapter navigation bar in the same pass.**

```
clips ──prep──▶ source.mp4 + audio.mp3 ──asr_volc──▶ transcript.json (per-character timestamps)
      ──autocut + agent reads──▶ retakes/fillers marked ──review_server──▶ localhost strike-through review
      ──render──▶ cut.mp4 + cut.json ──reviewed semantic cue plan + subs──▶ subtitles (simple / per-word highlight)
                                     ──navbar──▶ navbar.mp4 (black/white/blue, same length)
```

## Why another one

The existing projects are essentially **glue layers**: ffmpeg does the real work (cut, join, burn subtitles) and ASR supplies timestamps. Each is good at its part, but none is exactly "Doubao Speech ASR + meaning-aware keep-the-last-take + a light local review page + direct render + navigation bar". talkcut packs that into a few dependency-free Python scripts and one single-file HTML page, easy to bend to your own taste.

## Requirements

- Python 3.9+, ffmpeg/ffprobe; the navigation bar needs `pip install pillow` and a CJK font
- Volcengine Doubao Speech (豆包语音) big-model file ASR: `DOUBAO_API_KEY` (or `VOLC_APP_ID` + `VOLC_ACCESS_TOKEN`); see [references/volcengine-asr.md](references/volcengine-asr.md)

## Quick start (Linux / Arch / Omarchy)

```bash
cd agent-skills/skills/talkcut
sudo pacman -S --needed ffmpeg python-pillow noto-fonts-cjk   # Arch/Omarchy (doctor prints Debian/macOS equivalents)
python3 scripts/doctor.py
python3 scripts/talkcut.py run ~/videos/clip1.mp4 ~/videos/clip2.mp4   # opens the review page at http://127.0.0.1:8765
python3 scripts/talkcut.py render --no-burn                            # clean cut + draft subtitles
# Agent writes and reviews work/caption-plan.json (exact cue strings; see SKILL.md)
python3 scripts/talkcut.py render                                      # reviewed semantic captions; rejects missing/unreviewed plan
python3 scripts/talkcut.py status
```

Stages are cached in `work/state.json` and the raw ASR result in `~/.cache/talkcut/asr/`, so completed stages/results can be reused. A cache is not an exactly-once billing guarantee after an ambiguous request failure. Full workflow, semantic cue contract and data formats: [SKILL.md](SKILL.md). Read [production lessons](references/production-lessons.md) before real-footage delivery.

Chinese captions follow meaning and speech rhythm; 8–12 characters is a flexible guide, not a fixed splitter. Final burns require a reviewed cue plan, exact retained-text coverage and valid timing. Subtitle plan changes invalidate the driver cache. Run focused regressions with `python3 -m unittest discover -s scripts -p test_caption_plan.py`.

## Validation status

- ✅ End-to-end on real Chinese speech generated with espeak-ng (two clips) plus a simulated Doubao ASR result: the ASR cache hit, so nothing was billed. A retake was removed with the last take kept, a mid-sentence restart was trimmed with `cut_words`, and a fillers-only sentence was cut. A 2.0 s silence was capped (all remaining silences ≤ 0.61 s). 25.6 s → 15.7 s, with karaoke subtitles burned in and a navbar of matching length. A rerun skipped every stage.
- ✅ plan.json validator rejects wrong-direction retakes, out-of-range word indexes and empty reasons.
- ✅ Review page rendered in headless Chrome (colour-coded rule/AI cuts, live kept duration).
- ✅ Real Linux footage was processed with live Doubao Flash ASR, manually reviewed cuts, parent/independently reviewed semantic subtitles, chapter navigation and two roughly five-minute 1.05× episodes. Final episodes passed full decoding and browser playback/seek checks. Sources and manual decisions were preserved.
- Scope: the real-footage run used an extended local workspace. Its richer review UI, bounded range renderer, rounded caption styling and Clip/Episode delivery pages are **not yet all bundled into this CLI**. The reusable semantic cue validator, burn gates, manual word protection and ffmpeg invocation fix are included here; see production lessons for workflow requirements. Sampled playback/visual checks are not a complete listening-quality guarantee.

## Ideas

- [Browser-only Screen Studio-style recorder](references/ideas/2026-10-18-browser-screen-studio.md) (Liz, 2026-10-18, verbatim). Planned as a separate repo.

## References

Local snapshots, with commit SHAs and licenses, are listed in [references/vendor/README.md](references/vendor/README.md). Vendored code keeps its own upstream license, not this repo's MIT.


- [dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill) ([local snapshot](references/vendor/dbskill/)) — dontbesilent's content-creation skill toolbox. Its `dbs-video-navigation` has the agent chapter the subtitles, draws text PNGs with Swift/Pillow, and draws the progress bar with ffmpeg `drawbox`/`sendcmd` into a standalone navigation MP4. **Our navigation bar style (black background, white text, segmented blue progress bar) is a direct tribute**, simplified to Pillow + a time-driven drawbox and wired straight to the post-cut `cut.json`.
- [Agentchengfeng/chengfeng-videocut-skills](https://github.com/Agentchengfeng/chengfeng-videocut-skills) ([local snapshot](references/vendor/chengfeng-videocut-skills/)) — Chengfeng talking-head cutter: Codex plugin + separate Runtime/browser Studio, Volcengine ASR, "delete earlier, keep later" rule, HyperFrames captions. Complete but heavy (plugin/runtime/version pinning); we borrow the keep-later rule and drop the runtime.
- [lcbuaaliu/ai-jian-koubo](https://github.com/lcbuaaliu/ai-jian-koubo) ([local snapshot](references/vendor/ai-jian-koubo/)) — Volcengine Flash/Standard ASR, AI pre-marks mistakes, local review page with waveform, exports FCPXML to CapCut (剪映) / Final Cut Pro. We followed its Volcengine API details and review interaction; unlike it, we render with ffmpeg directly instead of exporting a project.
- [fxl1209739475-fxl/ai-xunjian](https://github.com/fxl1209739475-fxl/ai-xunjian) ([local snapshot](references/vendor/ai-xunjian/)) — faster-whisper word timestamps, silence trimming, keeps the later of adjacent repeated sentences, React visual editor + HyperFrames effects. We borrow "trim pauses but cap them", using Doubao ASR instead.
- [modelscope/FunClip](https://github.com/modelscope/FunClip) ([local snapshot](references/vendor/FunClip/)) — Alibaba Tongyi Lab: FunASR Paraformer recognition, select text in a Gradio page to clip it, LLM-assisted clipping and SRT. The classic "edit video by editing text" pattern; we keep the pattern without binding to FunASR.
- [xixihhhh/hotclip](https://github.com/xixihhhh/hotclip) ([local snapshot](references/vendor/hotclip/)) — `src/core/retakes.ts`: adjacent sentences with bigram Dice ≥ 0.72, within 20 s, up to 2 sentences apart are retakes; keep the last. **`autocut.py`'s heuristic adopts these conservative parameters**, with the agent adding semantic judgment on top.
- [Gitruck/cli](https://github.com/Gitruck/cli) ([local snapshot](references/vendor/cli/)) — `gtrk oralcut`: paid cloud rough cut for talking heads, script alignment, exports to CapCut/Premiere/FCPXML/OTIO. A commercial reference point; talkcut is fully local and pays only for ASR.
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) ([local snapshot](references/vendor/hyperframes/)) — write video in HTML/CSS/GSAP and render to MP4, with embedded captions. Not a cutter; when you want fancier per-word animation than ASS, feed it `cut.json`.

## License

MIT
