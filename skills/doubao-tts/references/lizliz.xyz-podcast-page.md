# Publishing a podcast page on lizliz.xyz

When a Doubao podcast MP3 has been generated, publish it on the Next.js site as a standalone
page under `/podcast/<slug>`.

## Architecture

The site is Next.js 16 (App Router), Tailwind CSS v4, `react-markdown` with `gray-matter` for
content. Articles live under `src/app/articles/[slug]/` with content in `content/articles/`.
Podcast pages follow the same split: server `page.tsx` for metadata/JSON-LD, client
`PodcastContent.tsx` for the audio player and interactive features.

## Step-by-step

### 1. Copy audio to public/

```bash
mkdir -p public/audio/podcast
cp /tmp/<slug>-podcast.mp3 public/audio/podcast/<slug>.mp3
```

### 2. Create content markdown

`content/podcast/<slug>.md` with YAML frontmatter:

```yaml
---
title: "中文标题"
slug: <slug>
date: "YYYY-MM-DD"
published_date: "YYYY-MM-DD"
description: "简短描述"
duration: "XX分XX秒"
hosts:
  - name: dayi
    role: "🧑"
    gender: male
  - name: mizai
    role: "👩"
    gender: female
tags: [podcast, ...]
keywords: [播客, ...]
audioFile: /audio/podcast/<slug>.mp3
---
```

Body is show notes / episode description in Markdown. Renders via `react-markdown` in
the page component.

### 3. Create page component

`src/app/podcast/[slug]/page.tsx` — server component:
- `generateStaticParams()`: scan `content/podcast/` for `.md` files
- `generateMetadata()`: title, description, keywords, OpenGraph, Twitter
- JSON-LD: `AudioObject` (contentUrl, duration, encodingFormat) + `BreadcrumbList`
- Renders `PodcastContent` client component + markdown children

Key import: `absoluteUrl()` from `@/lib/articles` for canonical URLs.

### 4. PodcastContent client component

`src/app/podcast/[slug]/PodcastContent.tsx` — "use client":
- `<audio>` element as source of truth for playback
- Custom progress bar (clickable), play/pause, ±15s skip buttons
- Keyboard: Space (play/pause), ←→ (skip)
- `timeupdate` → `findIndex` over subtitle array to highlight active line
- Click subtitle → `audio.currentTime = sub.start`
- Auto-scroll active subtitle into view (only when playing)

### 5. Subtitle data (preferred: ASR transcription)

After generating the podcast MP3, use Flash ASR to transcribe it — this is on a **separate quota line** and produces accurate time-aligned subtitles matching the actual audio:

```bash
python3 scripts/asr-transcribe.py /tmp/<slug>.mp3 /tmp/<slug>-subtitles.json
```

The script handles base64 encoding, speaker diarization (`enable_speaker_info: true`), and utterance-level timestamps. Output is a JSON array ready for the frontend component.

**Speaker mapping:** ASR assigns numeric IDs ("1", "2"). Map "1" → "🧑 dayi", "2" → "👩 mizai" (the default podcast speaker order). The `asr-transcribe.py` script handles this automatically.

Without subtitles, the page still works as audio-only with a notice. The subtitle sync code is fully wired — populate the array and it activates.

### 6. Deployment gotchas

- **`lib/podcast.ts` must be tracked.** If adding a new helper module (e.g., `getPodcasts()` for the homepage), ensure `git add src/lib/podcast.ts` before commit. Subagents frequently create files but forget to stage them.
- **CF Pages deploys take 1-3 minutes.** The asset URL (audio, subtitles JSON) may return 404 for up to 3 minutes after push. Wait and retry.
- **Homepage discovery.** When creating a new podcast page, also update `HomeContent.tsx` and `page.tsx` to surface the episode on the homepage. Otherwise it exists but is invisible — only reachable via direct URL.
