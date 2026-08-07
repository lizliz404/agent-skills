# 2026-06-17 Prigogine article audio session notes

## What changed in the workflow

- Skill discovery correction: when Liz asks for article TTS, load the visible TTS skill first instead of broad file search. If provider guidance is buried in another skill's reference, promote it into the class-level TTS skill.
- Class-level shape: the article-audio workflow belongs in `doubao-elevenlabs-tts`, not in one-off `doubao-tts` fragments. Keep Doubao as the default provider and ElevenLabs as an explicit fallback/provider option.
- Credential handling preference: for this workflow, Liz treats ElevenLabs-style API keys as low-sensitivity operational config. Write them to local env/secrets files efficiently; do not waste turns using placeholder values or excessive masking that prevents execution. Still avoid echoing secrets in summaries unless necessary.

## Provider defaults

### Doubao / Volcengine

- Default provider for this skill.
- Default voice: `zh_female_vv_uranus_bigtts` / Vivi2.0.
- Preferred working endpoint observed on this server: `https://openspeech.bytedance.com/api/v1/tts` with `cluster: volcano_tts`.
- Vivi guide preferences: no `emotion`/`neutral`; speed `1.0`, volume `1.0`, sample rate `24000`, mp3.
- If Liz says to use the default voice, skip multi-voice smoke comparisons and go straight to generation with Vivi.

### ElevenLabs

- Fallback when Doubao quota is exhausted or Liz explicitly chooses ElevenLabs.
- Default model: `eleven_multilingual_v2`.
- Default output format: `mp3_44100_128`.
- Default voice selected from available premade voices for Chinese article narration: `Xb7hH8MSUJpSbSDYk0k2` (`Alice - Clear, Engaging Educator`).
- Request endpoint: `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128`.
- Useful voice settings: `stability=0.55`, `similarity_boost=0.75`, `style=0.0`, `use_speaker_boost=true`.

## Env persistence pattern

Use a canonical secret file plus profile/global `.env.d` symlinks so future sessions do not require manual copy/paste:

```text
/home/ubuntu/.hermes/secrets/doubao-tts.env
/home/ubuntu/.hermes/secrets/elevenlabs.env
/home/ubuntu/.hermes/profiles/writing/.env.d/*.env -> /home/ubuntu/.hermes/secrets/*.env
/home/ubuntu/.hermes/profiles/trading/.env.d/*.env -> /home/ubuntu/.hermes/secrets/*.env
/home/ubuntu/.hermes/.env.d/*.env -> /home/ubuntu/.hermes/secrets/*.env
```

Also mirror the keys into each `.env` when convenient, because some existing scripts only source `.env` and do not load `.env.d` automatically. New scripts should load both.

## Article text cleanup rules

- Do not feed raw Markdown into TTS.
- Strip YAML frontmatter, Markdown markers, footnote markers, raw URLs, image syntax, code fences, and table syntax.
- Stop before `Footnotes`, `References`, `Sources`, `参考资料`, `脚注`, or `引用` unless Liz explicitly asks for source narration.
- Save the cleaned TTS input beside the generated audio for auditability.

## Long article generation pattern

- Chunk on paragraph/heading boundaries.
- Reuse already generated chunks on rerun.
- Concatenate chunks with `ffmpeg -f concat -safe 0 -i concat.txt -c copy`.
- Verify the final mp3 with `ffprobe` duration and file size.
- Copy audio to both the writing project and `lizliz.xyz/public/audio/articles/`.
- Insert a plain Markdown audio link near the top of both the writing `final.md` and the synced site article.

## Failure handling

- Doubao `quota exceeded for types: text_words_lifetime`: stop retrying that provider; switch quota/App or use ElevenLabs fallback.
- `speech.volcengineapi.com` DNS failure: use the observed V1 `openspeech.bytedance.com` route; do not treat it as article text failure.
- ElevenLabs `user_read` missing permission on subscription endpoint does not prove TTS failure; test the actual text-to-speech endpoint.
