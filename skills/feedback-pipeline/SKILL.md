---
name: github-telegram-feedback-pipeline
description: Add a GitHub Issue + Telegram dual-channel feedback pipeline to any Cloudflare Pages project (FeedbackWidget + Pages Function, graceful degradation). Defaults to Jett bot → GitHub feedback group (-5544201640). Use when adding feedback, a suggest button, issue reporting, or a feedback pipeline.
---

# Feedback Pipeline — CF Pages + GitHub + Telegram

One widget, one Pages Function, two delivery channels. Secrets stay server-side.

```
[FeedbackTrigger / Modal] ──POST──> [functions/api/feedback.ts]
                                         ├─ GitHub Issue (label: feedback)
                                         └─ Telegram message
```

**Success rule:** any one channel succeeding is enough. Telegram-only or GitHub-only both work. Do **not** fail the whole request because the second channel failed.

## Provenance (do not reverse)

| Source | What to take |
|---|---|
| **dieline-generator** | Preferred **architecture**: controlled `FeedbackModal` once at app root + `FeedbackTrigger` in chrome + tiny open store; robust Function (attempts[], one-channel-ok, length cap) |
| **BrainRush** | Preferred **UX chrome**: top utility cluster, fade/pop, Esc/outside/X, product copy voice (`Suggest a fix` / one-sentence hint). Function is **older** (all-channels-must-succeed) — do not copy for new installs |
| **pep-words** | Same older Function pattern as BrainRush — treat as fleet debt if touched |
| **This skill `references/`** | Portable baseline to copy. Prefer it over mining old product Functions |

Product owns final copy and optional product-context fields. Skill owns delivery + chrome contract.

## Positioning (why this skill exists)

**Job:** give every Liz CF Pages product a same-origin “one sentence felt wrong” path that lands in **GitHub Issues and/or Telegram**, with chrome that looks like the product — not a third-party feedback SaaS.

**Shape we optimize for:**
- Multi-site matrix (`*.lizliz.xyz` / BrainRush / dieline / pep-words…): copy two files + env, ship
- Secrets only in Pages Function env; browser never sees PAT/bot token
- Dual channel with **graceful degradation** (TG-only or GH-only both fine)
- Header utility next to lang switcher — product chrome, not a sales FAB
- Agent-operable: concrete `missing[]` / `attempts[]`, CF env+redeploy pitfalls documented

**Not the job:** screenshot/console capture SDKs, AI triage platforms, multi-tenant form relays, blog comment systems, or “install npm + publishableKey”.

## Ecosystem survey — auto-ignore hot wheels (Exa, 2026-08-18)

Exa pass covered GitHub/npm “feedback → GitHub Issues / Telegram / Cloudflare” widgets and CF form guides. **No dominant wheel matches this skill’s job.** Agents must **not** replace this pipeline with a trendy package because it has stars or a polished demo.

### What the search actually found

| Bucket | Examples (illustrative) | Pattern |
|---|---|---|
| Browser → GitHub direct | `issue-reporter`, `feedback-vos` (`NEXT_PUBLIC_GITHUB_TOKEN`) | PAT or fine-grained token in the client — **security anti-pattern** |
| SaaS / hosted control plane | Triagly, BugDrop, Sendmux, Fidbak | Account, API keys, their endpoint; often default **bottom-right FAB** |
| Heavy self-host stacks | `meathill/app-feedback` (Next+D1+admin), AI feedback analyzers | Extra DB, admin UI, deploy surface — overkill for one-line product feedback |
| Separate multi-tenant Worker | `contact-relay` (TG relay + origins admin) | Another Worker/domain to run; not per-Pages same-origin `/api/feedback` |
| Fat capture SDKs | react-visual-feedback / bugkit-class tools | Screenshot, recording, console/network traces, many sinks — wrong product moment |
| Wrong problem | giscus / utterances | Blog comments, not in-app “suggest a fix” |
| Tiny tutorials | Astro+GitHub App+Turnstile demos (~1★) | Fine as reading; not a fleet standard library |

CF docs and indie posts push **Turnstile + rate limit + honeypot** as the default “serious” form stack. We take **honeypot + length caps** only; Turnstile/KV stay off until real abuse.

### Why we deliberately do **not** look like those hot wheels

1. **Security model** — Hot demos put GitHub tokens in `NEXT_PUBLIC_*` or CDN widgets. We refuse that. Function proxy is non-negotiable.
2. **Deploy model** — Liz ships **Git-connected CF Pages** per product. A shared multi-tenant relay Worker or SaaS dashboard is another moving part and another failure domain.
3. **Channel model** — Most wheels are GitHub-only, email-only, or TG-only. We need **GitHub issue trail + TG pager** with one-channel-ok, defaulting to Jett → feedback group.
4. **Chrome model** — Marketplace widgets optimize for drop-in FAB and generic skin. Liz products forbid bottom-right emoji pills; feedback sits in **header utilities** with the same motion/a11y contract as the rest of the app.
5. **Weight** — Screenshot/AI/D1/admin are cool demos and bad default deps for a low-traffic indie matrix. Complexity without external signal = echo chamber.
6. **Operability** — Agents need env/redeploy/label pitfalls and `attempts[]` diagnostics more than a theme picker.

### Our advantages (keep these; do not “upgrade away”)

| Advantage | Detail |
|---|---|
| Same-origin Pages Function | No CORS circus; one deploy with the site |
| Dual channel + degrade | TG works while GH label/token is broken and vice versa |
| Liz defaults wired | Jett + `-5544201640`; per-repo `GITHUB_REPO` |
| Product chrome contract | Trigger/modal split, fade/pop, Esc/outside/X, no FAB |
| Fleet-proven copy path | references/ + BrainRush voice + dieline structure |
| Agent-grade failure text | 503 `missing`, 502 channel detail — not “Something went wrong” |
| Two-file install | No npm feedback SDK, no extra Worker project |
| Explicit non-goals | Prevents the next agent from “helpfully” adding Turnstile/SaaS |

**Rule for future agents:** discovering a popular feedback SDK is **not** a reason to migrate. Only revisit if (a) sustained abuse exceeds CF WAF + honeypot, or (b) product requirements change to screenshots/session replay — and even then prefer a **narrow** addition over a full SDK swap.

## Scope / non-goals

**In scope:** same-origin POST → Pages Function → GitHub and/or Telegram; header-slot UI; concrete misconfig diagnostics; light abuse filters.

**Out of scope until real abuse (do not add by default):**
- Cloudflare Turnstile / CAPTCHA
- KV / Durable Object rate limits
- D1 / email / Airtable / multi-tenant Workers
- Nonce round-trips, min-fill timers, third-party form SaaS
- Bottom-right FAB “反馈” pills
- npm/CDN feedback widgets that need publishable keys or client-side GitHub tokens
- Replacing this pipeline with Triagly / BugDrop / Sendmux / Fidbak / contact-relay / browser-PAT issue reporters

If spam appears: first check CF WAF / Bot Fight; only then escalate.

Survey notes: [references/provenance/2026-08-18-ecosystem-survey.md](references/provenance/2026-08-18-ecosystem-survey.md)

## Quick start

1. Copy [references/feedback-function.ts](references/feedback-function.ts) → `functions/api/feedback.ts`
2. Copy UI from [references/FeedbackWidget.tsx](references/FeedbackWidget.tsx):
   - Prefer **header-slot**: export `FeedbackTrigger` + controlled `FeedbackModal` (not standalone FAB)
   - Optional glue: [references/useFeedbackStore.ts](references/useFeedbackStore.ts)
3. Mount **one** `FeedbackModal` at app root (outside routes). Put `FeedbackTrigger` next to the language switcher on **every** chrome that has utilities (landing SiteNav **and** workspace TopBar)
4. Set `APP_SLUG` in the Function (or pass `app` from client) — never leave `[app-name]`
5. Set env vars on the **CF Pages project** (Production **and** Preview)
6. Ensure GitHub label `feedback` exists **or** rely on Function label-fallback (see Robustness)
7. Verify pipeline **and** UX checklist below

## Env vars

| Key | Default / source | Notes |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | **Jett** — see [telegram-tokens.md](references/telegram-tokens.md) | Default bot for feedback |
| `TELEGRAM_CHAT_ID` | **`-5544201640`** (GitHub 反馈群) | Default push target |
| `GITHUB_TOKEN` | GitHub PAT with **Issues: write** (fine-grained) or classic `repo`/`public_repo` | Optional if Telegram-only |
| `GITHUB_REPO` | **`owner/repo` — per project** | Never hardcode; ask which repo |

Set in: Cloudflare Dashboard → Workers & Pages → **this project** → Settings → Environment variables  
**or** CF API (below). Apply to **Production and Preview**.

**Critical:** saving env vars does **not** redeploy. Running Functions keep old bindings until a new deployment. After env changes: empty commit + `git push`, or Dashboard “Retry deployment”.

Token sourcing for agents:
- `CLOUDFLARE_API_TOKEN` already in shell env / `your shell env` (Pages/general)
- Workers Builds user token paths if needed: `your CF API token env` (and symlinks) — **not** for Pages env patches usually
- **Never** paste API tokens or bot tokens into SKILL.md, commits, or issue bodies

## Robustness (baseline, keep light)

| Guard | Behavior |
|---|---|
| Method | Only `POST`; other methods → `405` |
| JSON | Invalid body → `400` |
| Message | Required; trim; **min 3** / **max 2000** chars |
| Honeypot | Optional client field `website` (must be empty). If filled → **fake `200 {ok:true}`** (do not tip bots) |
| `GITHUB_REPO` | Must match `owner/repo` or GitHub channel is treated misconfigured |
| GitHub labels | Create with `labels: ["feedback"]`. On **422** that looks label-related → **retry once without labels** (issue still opens) |
| GitHub permissions | Fine-grained needs Issues **write**. Labels need push-equivalent access; otherwise GitHub may silently drop labels — issue still ok |
| Telegram length | Cap send text ~3500 chars (API limit 4096) |
| Channels | Run independently; return `ok:true` if `deliveredTo.length >= 1`; include `attempts[]` |
| Diagnostics | 503 lists `missing` + channel needs; 502 includes per-channel `detail` (truncated) |
| Client double-submit | Disable button while `submitting` |

Still **not** required: IP rate limit in Function. Note abuse → CF edge. dieline comment pattern is correct.

### Optional product context (keep flat)

Client may send extra **string** fields; Function should only append known keys to the issue body:

- always useful: `url`, `userAgent`, `app` / `APP_SLUG`
- optional: `locale`, `route`
- product-specific (BrainRush-style): only if that app needs them — do not invent a generic schema framework

## Pitfalls

1. **Forgot CF env vars** → `503` + `missing: [...]`. Widget must surface that, not generic “发送失败”.
2. **Env var changes don’t auto-deploy** — must redeploy after save.
3. **Vars only on Production or only Preview** → one URL works, the other 503s.
4. **CF API PATCH** requires both `deployment_configs.preview` and `.production` with matching `fail_open`, or error `8000066`.
5. **Incomplete channel pair** (e.g. token without `GITHUB_REPO`) → that channel skipped; need both keys per channel.
6. **Hardcoded `GITHUB_REPO` / app slug** — wrong; project-specific.
7. **Bot not in Telegram group** → Telegram HTTP 400/403.
8. **Label `feedback` missing** → may 422; Function retries unlabeled; still better to create the label once.
9. **Local `wrangler pages dev` without vars** → same 503; use `.dev.vars`.
10. **CF Pages project name ≠ GitHub repo name** (e.g. repo `dieline-generator` → CF `cutting-die`). Confirm with list-projects before PATCH.
11. **Copying BrainRush/pep-words Function** → old all-must-succeed semantics; use skill reference instead.
12. **Standalone fixed top-right widget** on a site that already has a header → wrong; use trigger-in-chrome + root modal.
13. **Secrets in repo / skill text** — never commit PAT/bot tokens; read from env files.

## Setting env vars via CF API (no Dashboard click-ops)

Account ID: `afc4504f0abd4f4ac721eb73a6f04650`. Use existing `$CLOUDFLARE_API_TOKEN` from the environment — do not embed token values in docs.

```bash
# 1. List projects (confirm CF project name)
curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/afc4504f0abd4f4ac721eb73a6f04650/pages/projects" \
  | python3 -c "import sys,json; [print(p['name']) for p in json.load(sys.stdin)['result']]"

# 2. PATCH env (both preview + production). Fill secrets from shell env, not from this file.
#    Example shape only — merge with any existing deployment_configs the project already has.
curl -sS -X PATCH \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.cloudflare.com/client/v4/accounts/afc4504f0abd4f4ac721eb73a6f04650/pages/projects/{PROJECT_NAME}" \
  -d @- <<EOF
{
  "deployment_configs": {
    "production": {
      "env_vars": {
        "TELEGRAM_BOT_TOKEN": {"type": "secret_text", "value": "$TELEGRAM_BOT_TOKEN"},
        "TELEGRAM_CHAT_ID": {"type": "plain_text", "value": "-5544201640"},
        "GITHUB_TOKEN": {"type": "secret_text", "value": "$GITHUB_TOKEN"},
        "GITHUB_REPO": {"type": "plain_text", "value": "owner/repo"}
      },
      "fail_open": true
    },
    "preview": {
      "env_vars": {
        "TELEGRAM_BOT_TOKEN": {"type": "secret_text", "value": "$TELEGRAM_BOT_TOKEN"},
        "TELEGRAM_CHAT_ID": {"type": "plain_text", "value": "-5544201640"},
        "GITHUB_TOKEN": {"type": "secret_text", "value": "$GITHUB_TOKEN"},
        "GITHUB_REPO": {"type": "plain_text", "value": "owner/repo"}
      },
      "fail_open": true
    }
  }
}
EOF

# 3. CRITICAL: redeploy so bindings refresh
cd /path/to/project && git commit --allow-empty -m "chore: trigger redeploy for feedback env vars" && git push
```

If PATCH wipes unrelated bindings, **GET project first**, merge `env_vars` into existing `deployment_configs`, then PATCH. Prefer smallest merge.

## Verify after deploy

```bash
# 1) Happy path
curl -sS -X POST "https://<your-pages-domain>/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{"message":"pipeline smoke test","url":"https://example.com"}'
# Expect: {"ok":true,"deliveredTo":["telegram"]}  (and/or "github") + attempts

# 2) Honeypot should look successful but not deliver
curl -sS -X POST "https://<your-pages-domain>/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{"message":"bot spam","website":"http://spam.test"}'
# Expect: {"ok":true,...} and NO new Telegram/GitHub item

# 3) Empty message → 400
# 4) Telegram group -5544201640 gets the smoke message
# 5) If GitHub configured: Issues label feedback (or unlabeled after fallback)
# 6) UI: open widget → send → success; misconfig surfaces missing keys
```

## Design notes

- Browser must not hold GitHub/Telegram secrets → Pages Function is the proxy.
- Return concrete diagnostics (`missing`, `attempts`, `detail`) so the widget can show what failed.
- Bot/chat table: [telegram-tokens.md](references/telegram-tokens.md)
- Copy is product-owned. Skill reference defaults are plain EN; BrainRush EN lines are a **product voice** example, not a global string pack.

## UI/UX contract (absorb BrainRush chrome + dieline structure)

Canonical chrome: `BrainRush (product reference)/App.tsx` + `src/index.css` animations.  
Canonical structure: `dieline-generator (product reference)/src/components/FeedbackWidget.tsx` + `useFeedbackStore`.

### Placement — do NOT use bottom-right floating CTA

| Bad | Good |
|---|---|
| Fixed bottom-right pill “💬 反馈” | Top chrome, next to language switcher |
| Always-visible sales FAB | Icon-only + `aria-label` / title |
| Ignores product chrome | Same size/border/hover as other header utilities |

Default placement:

1. Landing / menu: top-right utility cluster — feedback **next to** lang switcher
2. App shell TopBar: right utilities after exports / near lang switcher
3. Iconify Lucide: `lucide:message-square` or `lucide:message-circle`. No emoji trigger

### Modal interaction (all required)

1. **Fade enter + leave** — `open` + leave animation; `TRANSITION_MS` 220–300
2. **Click outside closes** — backdrop `onClick={close}`; panel `stopPropagation`
3. **Escape closes**
4. **Explicit X** — not the only dismiss path
5. **Backdrop** — `bg-black/50–60 backdrop-blur-md`, centered / top-centered panel
6. **a11y** — `role="dialog"`, `aria-modal="true"`, labelled title
7. **Success** — short received state; auto-close ~1.5–2s; reset on next open
8. **Honeypot** — visually hidden `website` input, `tabIndex={-1}`, `autoComplete="off"`; never show in UI copy

### CSS primitives

```css
.animate-fade-in { animation: fade-in 220ms ease-out both; }
.animate-fade-out { animation: fade-out 220ms ease-out both; }
.animate-pop-in { animation: pop-in 220ms ease-out both; }
.animate-pop-out { animation: pop-out 220ms ease-out both; }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes fade-out { from { opacity: 1; } to { opacity: 0; } }
@keyframes pop-in {
  from { opacity: 0; transform: translateY(10px) scale(0.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes pop-out {
  from { opacity: 1; transform: translateY(0) scale(1); }
  to { opacity: 0; transform: translateY(8px) scale(0.985); }
}
```

### Multi-header glue

```ts
// useFeedbackStore.ts — keep tiny (Zustand only if project already has it;
// else lift React state in App)
export const useFeedbackStore = create<{ open: boolean; setOpen: (v: boolean) => void }>((set) => ({
  open: false,
  setOpen: (open) => set({ open }),
}))
```

Headers: `<FeedbackTrigger onClick={() => setOpen(true)} surface="landing|shell" />`  
Root: `<FeedbackModal open={open} onOpenChange={setOpen} appName="my-app" />`

If the project has **no** Zustand: parent state in `App` is enough — do not add a store dependency only for feedback.

### Pipeline vs chrome

- Delivery is already the hard part when misconfigured — fix env/redeploy before redesigning channels.
- When improving an existing repo: rewrite trigger + modal shell first; keep `fetch('/api/feedback')` contract; upgrade Function if still all-must-succeed.

### Anti-slop checklist before ship

- [ ] Not bottom-right floating sales pill
- [ ] Near language switcher / utility chrome
- [ ] Iconify icon, no emoji trigger
- [ ] Fade in **and** fade out
- [ ] Outside click + Escape + X
- [ ] Diagnostics for server misconfig surfaced
- [ ] Works on landing + app shell when both exist
- [ ] One-channel success; attempts on failure
- [ ] `APP_SLUG` / `app` set; no `[app-name]` left
- [ ] Label `feedback` created **or** unlabeled fallback verified
- [ ] Honeypot present (hidden)
- [ ] No secrets in client bundle or git

## Fleet snapshot (known installs)

| Project | UI pattern | Function maturity |
|---|---|---|
| dieline-generator | Trigger + root modal + store | Robust (one-channel-ok, max length) — closest to skill |
| BrainRush | In-App.tsx modal + WeChat tab; strong copy | Older all-must-succeed |
| pep-words | Product-specific | Older all-must-succeed |

New work: **copy skill references**, then paint with product tokens/copy. When touching BrainRush/pep Functions, upgrade toward skill baseline (one-channel-ok + diagnostics) without forcing UI rewrites.

## Related skills

- Product chrome audits: `product-and-portfolio-quality-audits` (feedback placement kill-list)
- Issue → PR after feedback lands: `github-issue-to-pr`
- Not this skill: plan→tickets (`to-issues`), inbox triage (`triage`)
