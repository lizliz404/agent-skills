# Talking-head editing: real-use lessons

These requirements came from a real Linux talking-head review/render session (2026-10). They are operating requirements, not claims that every bundled CLI already implements the whole review/render workspace.

## 1. Deliver a simple complete experience

- By default expose originals/review, independent clips, final episodes, progress, previews and downloads on the same loopback website. Give clickable URLs without waiting for the user to ask. Files on disk alone are not a usable delivery. If an incumbent localhost UI exists, extend it rather than start a second control plane.
- Use plain labels such as 第一段 / 前半段 rather than requiring users to understand Clip/Episode IDs. Keep original source identity separate from editorial position and publish position.
- Offer obvious 编辑 / 完成编辑 controls, sentence delete/restore, word selection, subtitle text correction, undo and autosave. Preserve timestamps on text corrections; changing displayed text does not change the audio.
- Preserve all human sentence/word decisions across AI reruns. Use revision checks and frozen render snapshots. Audit findings stay advisory until approved; don't turn an independent audit into a silent reset.
- Make rendering progress visible without blocking editing or sending the user to terminal logs. Ready means finalized and verified styled output, not a clean cut or partially encoded file. Keep previous complete outputs accessible while a revision processes; generation-tag media URLs and disable stale caching.
- Do not add animations, music, transitions, B-roll, a new framework or an extra approval ceremony unless it serves the requested video. Once a style is approved, preserve it and fix the defect locally.

## 2. Semantic captions are mandatory, not an optional polish

**Never burn mechanically character-count-split subtitles as if they were finished semantic subtitles. Fail the render preflight if an explicit reviewed semantic cue plan is missing.**

- Read the entire retained transcript in editorial order, including neighboring ASR sentences. ASR sentence IDs are timing/storage units, not guaranteed complete grammatical sentences.
- Draft exact cue strings at clause, phrase, list-item and real pause boundaries. For Chinese, 6–14 characters is a flexible readability target, not an enforced minimum/maximum. Complete short cues are legitimate; an inseparable longer expression can stay together if it fits. Do not split names, number+unit, technical terms or glue the next sentence's opening onto the previous ending to fill a quota.
- Keep the speaker's wording, order and manually approved corrections exact. Do not silently clean up remaining misspeaks or hallucinated ASR words as part of segmentation. Flag uncertain wording separately; subtitle correction and footage deletion have their own authorization.
- Store `caption-plan.json` (agent-selected exact strings) and validated `captions.json` (cue text, times, source references), then derive SRT and ASS. Use `scripts/caption_plan.py cut.json caption-plan.json -o captions.json`. It proves exact character coverage and timing validity, **not** linguistic quality.
- Map original token boundaries where available. Only boundaries inside a multi-character ASR token require proportional estimated timing; record that fact. Never imply invented sub-token timing is measured.
- Review all consecutive cues in a compact text view. Look especially for hanging conjunctions/modals, abrupt restarts, tiny tail fragments, list items and ASR cross-sentence breaks. Check very short cue durations and long display gaps instead of optimizing length statistics.
- Preflight several real consecutive cues with the production renderer: one low-cost frame for size/placement plus a short moving excerpt for changes/rhythm. A good screenshot and a max-character test cannot establish fluent reading. Give the user this preview on localhost proactively; when authorization is clear and the user is away, verify yourself and continue.

## 3. Rendering should be cheap and reversible

- Keep untouched sources, raw ASR, reviewed edit JSON, clean cuts and editable caption files. Caption/style revisions reuse clean cuts: no new ASR, no repeating semantic footage cuts, no overlaying new captions over burned captions.
- Don't treat local CPU work as money spent on a paid cloud render. If the user authorizes quality work, do the straightforward local re-encode; don't substitute saving compute for solving a known comprehension defect. Explain real disk/time constraints if any, not theoretical cost anxiety.
- Preserve original resolution/aspect ratio unless asked. Select cut order by meaning, not filenames (real case: source 1→3→2).
- **Quality floor (2026-11-08):** deliverable must not look worse than the source — use the highest-quality encode path for finals (HQ preset), reserve fast drafts for samples only; keep the audio track that matches the transcript timeline unless a better source is separately verified for sync.
- Use bounded-memory range encoding for large cut maps. Accurate frame-rounded trims, lossless temporary audio and one final AAC encode avoid memory blowups and per-range AAC priming accumulation. Reuse ranges only when their media/edit signature matches.
- **Audio/video asymmetry at cuts (2026-11-08):** prevent audio clicks with ~10 ms fades, but never apply a sub-frame *video* fade at joins — it quantizes to a black frame per cut and the whole piece strobes. Hard cuts only; spot-check luminance on both sides of a few joins before delivery.
- ASS font size may not match drawtext/ImageMagick point size. Measure actual rendered glyphs before sizing a tight rounded background. In the observed Noto CJK setup fs62 rendered about43px glyphs; don't copy that ratio blindly to another font/runtime. Keep approved boldness, padding, position and top navigation while making a small requested size adjustment.
- Long-running Python retains loaded code. Changing a script does not change an active render. Safely stop and resume from validated clean intermediates when needed.
- Use native async jobs with a known log, status, stop command and resource limits. Run full media decoding and inspect actual final frames; ffmpeg exit0/file existence/HTTP206 are not interchangeable with usable playback or good edits.

## 4. Navigation, episode boundaries and speed

- Keep major-part titles and meaningful small-section titles. Draw gaps for **all** section boundaries with actual timeline proportions, not just an equal division into source videos. Maintain full-content progress offsets across separately delivered files unless asked to restart per episode.
- Preserve approved navigation rather than embellishing it. Color claims must match the actual implementation: the approved example was fixed light blue over a dark gray track, not a programmed light-to-dark gradient.
- **Island nav (2026-11-10):** the floating chapter pill renders only itself. No blur, glow, vignette or cast shadow outside the pill — that treatment was rejected as 弄巧成拙. Inside the pill: a 1–2px top specular, a soft vertical gradient, a hairline inner stroke. Layout is fixed: chapter name left (real title, no 开场/爆点/钩子-style meta words), `03/07` right, a thin bar under the title for progress *inside this chapter*. Spec: `island-nav/DESIGN.md`.
- **Island nav (2026-11-10, Liz on G6 A/B):** the pill only. No frost, vignette, glow or diffused shadow outside the island; a same-shape drop of a few pixels is allowed. Inside: 1px top specular that follows the rim, a soft vertical gradient, a hairline inner stroke. Layout is fixed — chapter name left (real title, never 开场/爆点/钩子 and the other meta words), `03/07` right, thin bar below is progress inside this chapter, not the whole film. Presets and the renderer live in `island-nav/`. Burn path is a PNG overlay, not ASS; ASS cannot mask-blur the pill interior.
- **Island burn, verified on G6 (2026-11-10):** one transparent PNG per chapter (text + empty track baked), ASS draws only the in-chapter fill. Do not redraw the pill in ASS. Alpha bbox of every G6 overlay was exactly the pill box 60,28–1020,153; a nosub-vs-final diff at t=70s was 2.1 outside the pill and 70.8 inside, so the frost did not leak. Chapter switch = swap the PNG, not a per-frame reblur. `NAV_MIN_DUR` is 120s, not 300 — a film just under 5 min still gets the island.
- **BGM audible floor (2026-11-10, G6):** a sidechain gain of -26dB left the bed inaudible. Lock the applied gain near -15dB (±2) and check a real speech gap, not the whole-file mean. G6 gap at 25.6s measured -23.5dB with the original track kept. Cover check: frame 0 must be the title card, not a bare content frame.
- **Crop is per film, not per file (2026-11-10):** `CROP_Y` is a shared table, but the same source sits at different heights across films. G5 needed `IMG_9477.MOV` at y=390; G6's head top on that file is ~110, so y=390 clips the crown and y=200 is the fix. Override in the calling process. Do not write a one-film measurement back into the shared table.
- **Cover design and frame-0 replacement (2026-11-10, Liz ruling on G6):** 封面 = 真实帧 + 标题 overlay，严禁重裁、重拼或缩放人像。从新成片对应时刻抽出一帧真实帧（如通过精确匹配 SRT 台词对应时刻），保持原片完整几何：上下双机位布局、中间黑带及字幕原样保留（字幕留在封面完全合规），直接作为底图；仅在其上叠加纸带标题层与底部 footer。若成片已完成整烧，仅需更换帧 0 封面时，严禁整片重烧：只需重编码包含帧 0 的最小段（如首个 GOP / 到下一个 IDR 关键帧），其后长段直接以 `-c copy` 接回原片并复用原音频，确保拼接点无断、逐像素一致、零解码错误与零质量退化。
- Prefer an episode boundary after a complete idea, ideally in a real speech pause. Near-balanced five-minute episodes can be better than equal source-file divisions. Do not truncate speech or force exactly five minutes. State that a continued second half is not a newly recorded standalone intro/outro.
- **Do not assume faster output means faster audience understanding.** Liz's current spec (2026-11-08, interview two-cam) sets delivery speed at **1.05×–1.15×, never 1.0×**; this supersedes the older conservative ceiling for that format. Outside that range, ask first. Use pitch-preserving audio and verify actual A/V timing.
- Plan all timing-affecting changes together. At each speed/concat/split step verify actual A/V timing and subtitle/navigation offsets, not just nominal command arguments.
- Stream-copy packaging is useful when existing overlays are accepted. A timestamp-retimed copied video has a changed effective FPS; disclose it. Use one clean re-encode if exact cuts or mandated CFR are required. Verify actual segment boundary: a 30fps B-frame test missed a chosen keyframe with `segment_time_delta=0.001` and landed correctly at0.1. This is a case-specific observation, not a universal magic flag.

## 5. Evidence and tools

- Only necessary audio goes to the authorized existing ASR service; never upload original video by default. Cache reuse reduces repeat requests, but a local hash cache is not an exactly-once billing guarantee after an ambiguous network timeout.
- Agent semantic tasks need whole readable input, not a tool-truncated giant JSON line. Chunk by sentences, check coverage, validate output. Use bounded thinking to avoid overthinking a straightforward editing job. Keep delegated agents visible and honor the requested provider/model.
- Test save/delete/undo/conflicts on isolated fixtures, never by toggling live user decisions. Actual output playback can be checked read-only.
- Verify real paths: Linux support, authenticated access and actual render behavior matter more than README claims or a passing dependency doctor. Keep third-party licenses distinct from the parent repository license.
- Match the installed ffmpeg: an actual render failed because `-filter_complex_script` was unsupported. Passing encoder/filter discovery does not prove that the full invocation is supported.
- Final acceptance distinguishes structural tests, parent semantic review, sampled visual/playback checks and the user's own listening judgment. Do not claim a complete listening pass from decode-to-null.
