# Simple frame-based series covers

Use when the user asks for standalone covers from finished episodes, or says
“朴素高效封面 / 黑字白底 / AI × / 上下集封面”. This is optional: do not add a
cover unasked, or mistake a cover image for an opening-video overlay.

## Smallest useful workflow

1. Reuse the authoritative final MP4 and approved wording. Choose a real frame;
   if requested, use the first decoded frame showing the first burned subtitle.
   Caption JSON helps locate it but mux offsets can move its actual appearance.
   Inspect nearby decoded frames; save the selected frame index/PTS and source.
   A dark-caption-box region scan can help, but its threshold is footage-specific.
2. Keep exact keywords and line breaks. A title may attract attention; the cover
   should plainly label the content. Do not invent tutorial claims, search-volume
   evidence, slogans or more metadata. Preserve the real scene; deliberate headline
   overlap of face/eyes is allowed when the user prefers it.
3. Prefer the incumbent bold local font, black type on white rounded strips and
   one existing accent. Do not import a deck framework or generate new artwork
   when image compositing does the job. The approved example is:
   `AI ×` then `外贸新品开发（上）` / `外贸新品开发（下）`.
4. Render independent PNG/JPG with `scripts/cover.py` (ImageMagick 7; no ASR,
   cloud calls, video re-encode or new Python dependencies). The layout scales
   from a 2560×1440 design canvas to 16:9 input. It does not crop. Other aspect
   ratios or substantially different layouts need deliberate adaptation, not a
   silent crop. Shorten overlong copy instead of creating unreadable small text.
5. Show native-size and thumbnail results on the existing localhost episode page,
   with PNG/JPG downloads. Save source, generator parameters and final covers
   flat in the durable video project root beside MP4/subtitle files. Use matching
   episode prefixes, not covers/stickers subfolders. Verify original MP4 hashes remain unchanged.

## Render

```bash
# Extract an already-verified decoded frame index, not an arbitrary attractive frame:
ffmpeg -i episode.mp4 -vf 'select=eq(n\,7)' -frames:v 1 frame.png
# Frame 7 is only an example; locate it for the actual footage.
python3 scripts/cover.py frame.png -o cover.png --title 外贸新品开发 --part 上
# Optional: --kicker AI --accent '#64A9E8' --outline 8 --font /path/to/cjk-bold.ttc
magick cover.png -quality 94 cover.jpg
magick cover.png -resize 640x360 thumbnail.jpg
```

`cover.design.json` records the font, copy, dimensions and visual parameters.
Fontconfig finds Noto Sans CJK SC Bold; supply `--font` when unavailable. Keep
private source locators in the project, not in published example configurations.
This helper intentionally does not start a web service or infer subtitle onset.
Reuse/extend the current review service for delivery.

## Portrait blue-serif paper strips

For a portrait talking-head cover, reuse `scripts/paper_cover.py` instead of forcing
`cover.py`'s landscape coordinates onto a tall frame. The signature is large navy
serif headlines on slightly tilted off-white paper strips, with one small series
kicker. It needs only Pillow and local CJK fonts; no image model or new framework.

```bash
python3 scripts/paper_cover.py --source frame.png --output 01-cover.jpg \
  --line 'AI 出图之后' --line '报价还得人填？' \
  --kicker '外贸新品开发  01 / 04' --top 340 --font-size 210
```

The component fits each explicit line by the **rotated strip's complete bounds**,
not merely the unrotated text width. It saves JPG + PNG, a full-canvas transparent
`*-paper-overlay.png`, `*.design.json` and a 270px-wide thumbnail. Keep the transparent
overlay and measured parameters for future covers; change copy/position/font/color
without rebuilding a template. The static source frame is not overwritten and video
input is rejected. Use `--font` and `--kicker-font` for fonts on another platform.

Prioritize phone-scale headline size. Face/eye overlap is an editorial choice, not
a universal prohibition; enlarge deliberately when approved. Preserve existing
handmade opening-cover artwork when no change is requested. Do not rewrite approved
copy or add filler metadata to fill the frame.

Run `python3 -m unittest discover -s scripts -p 'test_paper_cover.py'`, then inspect
real-frame covers and thumbnails. These tests cover bounds, transparent recomposition,
parameter changes and invalid sources; they do not certify taste.

## Two-tone hug strips (landscape burned covers)

For a plain two-color cover over a screenshot/webpage frame, the approved shape
is **strips that hug each line of text**, never one fixed-size board holding all
lines (包着字走，不是一整块定死长宽的板子). Approved example: FDE interview
covers (cream strips "做 FDE" / "难在沟通" + small series chip).

- One cream/paper strip per explicit line; strip bounds = real ink bbox + even
  padding (≈0.4× font size). Lines of different length get strips of different
  width — do not equalize to the longest line.
- The offset accent is a second-color edge peeking bottom-right of **each**
  strip (≈10–14px), not a border around a single slab and not a full second
  card. Same for the small series/kicker chip.
- Ink is a third, contrasting color (e.g. navy serif on cream + amber offset).
  Stack strips left-aligned as a group; center the group in the frame's real
  free zone, clearing face/webcam and key page content.
- No logos, mascots or extra artwork unless the user explicitly asks; a plain
  two-tone cover means text strips only.
- Burned first-frame covers overlay frame 0 only; save the transparent overlay
  PNG + design JSON beside the render script.

## Optional local stickers

If the user asks, use a small local code/SVG/PNG library rather than regenerating
art or fetching a CDN for every cover. The approved recurring pair is an orange
Clawd crab and a purple **Codex-inspired community cloud** (not an official pet).
Prefer lively waving/hopping poses, tilt slightly in opposite directions, place
one on each free side, and do not obscure the subject, subtitle or title. Do not
add a background card or explanation text just to label the stickers.

```json
[
  {"file":"clawd-lively.png", "x":2010,"y":650,"width":330},
  {"file":"codex-cloud-lively.png", "x":185,"y":1030,"width":245}
]
```

Pass `--stickers stickers.json`. Coordinates refer to the 2560×1440 design canvas;
relative image paths are relative to the JSON file. Files must be trusted local
SVG/PNG (inspect SVG scripts/events/external refs first). This helper does not
sanitize arbitrary downloaded SVG, infer licenses, choose positions or check
semantic overlap. Keep source commit, attribution, artwork license and derivative
recipe with the local library/project, outside the portable Skill. MIT code does
not imply rights to all artwork or trademarks. Highly popular pet repos can
explicitly exclude their art from the code license.

For CSS-animated SVG, a static converter may ignore the animation. Capture a
chosen actual browser animation pose as transparent PNG once and reuse it; keep
the original SVG/HTML for motion work. An animated SVG/HTML composition can be
rendered as an overlay for video, but that is a separately requested operation;
do not install a desktop app or modify a finished MP4 just to get its mascot.

## Approved finishing details

- **Outline:** 8px at the 2560px design width (was 3px). A white-heavy screenshot
  needs this separation; check at thumbnail size rather than merely increasing
  weight until it looks heavy.
- **Blue offset edge:** directional toward bottom-right, not a hard opaque ledge.
  Layer translated rounded silhouettes with decreasing alpha. Near the card it
  is visible; across a 28px extent it fades to **zero opacity / 100% transparency**.
  Composite over the actual frame so the background remains visible through it.
  Do not fake transparency with a white gradient or fade the black outline/text.
- Keep approved typography, geometry and source frame for local refinements.
  No unrelated effects, music, video rerender or automatic publishing.

## Verification boundaries

Run `python3 -m unittest discover -s scripts -p 'test_cover.py'` for gradient alpha,
image render and invalid-input checks. Also inspect actual full-size/thumbnail
covers. Tests do not prove taste, semantic copy quality or correct frame choice.
