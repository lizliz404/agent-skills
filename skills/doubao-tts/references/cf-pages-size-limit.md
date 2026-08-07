# CF Pages 25 MiB file size limit

## The constraint

Cloudflare Pages enforces a **25 MiB per-file limit** during asset validation. This limit applies to all static assets in the output directory — including MP3 audio files.

## Failure signature

```
✘ [ERROR] Error: Pages only supports files up to 25 MiB in size
  audio/articles/<slug>.mp3 is 27.3 MiB in size
Failed to validate assets in the output directory
```

**Key trap**: Next.js `npx next build` succeeds (article route is generated, TypeScript passes, static pages are built), but the subsequent CF Pages `wrangler pages deploy` asset validation step rejects the oversized file. The deployment shows `build/failure` in the CF Pages dashboard, and the site silently stays on the previous successful deployment. GitHub Actions CI (which only runs typecheck/lint/build) shows green.

## Re-encoding recipe

For speech/voice MP3 files, quality loss at 96 kbps is imperceptible:

```bash
ffmpeg -i input.mp3 -codec:a libmp3lame -b:a 96k -ac 1 output.mp3
```

Expected sizes for a ~30-minute voice track:

| Bitrate | Size |
|---------|------|
| 128 kbps | ~27 MiB ❌ |
| 112 kbps | ~24 MiB ⚠️ borderline |
| 96 kbps | ~21 MiB ✅ |
| 80 kbps | ~17 MiB ✅ |

Always re-encode the source MP3 rather than transcoding a lossy-to-lossy chain if the original WAV or FLAC is available.

## Diagnostic flow when live article returns 404 after push

1. **Confirm the push reached GitHub**: `curl -sI https://raw.githubusercontent.com/lizliz404/lizliz.xyz/main/content/articles/<slug>.md | head -1` — should return 200.
2. **Check CF Pages deployment status** (do not assume push = deployed):

```python
import json, urllib.request

cf_token = '<from /home/ubuntu/.bashrc: CLOUDFLARE_API_TOKEN>'
acct_id = 'afc4504f0abd4f4ac721eb73a6f04650'  # Liz's CF account
proj = 'lizliz-xyz'

def cf_req(path):
    url = 'https://api.cloudflare.com/client/v4/' + path
    headers = {'Authorization': 'Bearer ' + cf_token, 'Content-Type': 'application/json'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

# Get latest deployments
deps = cf_req('accounts/' + acct_id + '/pages/projects/' + proj + '/deployments?per_page=3')
for d in deps['result']:
    stage = d['latest_stage']
    commit = d['deployment_trigger']['metadata']['commit_hash'][:10]
    print(f"{stage['name']}/{stage['status']} | commit:{commit} | {d['created_on'][:19]}")
```

3. If the latest deployment is `build/failure`, get the build log:

```python
deploy_id = '<full UUID>'
logs = cf_req('accounts/' + acct_id + '/pages/projects/' + proj + '/deployments/' + deploy_id + '/history/logs')
for line in logs['result']['data']:
    if 'ERROR' in str(line) or 'error' in str(line).lower() or 'failed' in str(line).lower():
        print(line)
```

4. Common causes beyond file size:
   - Missing Wrangler config
   - Build script errors
   - Environment variable mismatches

## Prevention in TTS workflow

- After generating audio, always run `ls -lh <audio-file>` and check against 25 MiB.
- If borderline (>22 MiB), preemptively re-encode rather than waiting for CF Pages to reject.
- For the article Markdown, the audio link path should be `/audio/articles/<slug>/<slug>.mp3` — this maps to `public/audio/articles/<slug>/<slug>.mp3` in the Next.js project.
