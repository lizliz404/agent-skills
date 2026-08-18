# Ecosystem survey — feedback wheels (Exa, 2026-08-18)

## Query themes (Exa)

- Cloudflare Pages/Workers feedback form → GitHub Issues
- In-app feedback widget → GitHub Issues / Telegram
- npm/CDN feedback button + GitHub token patterns
- Static-site contact form spam protection (Turnstile, honeypot, rate limit)
- Adjacent: multi-tenant TG relays, AI feedback analyzers, blog comment systems

## Result buckets → decision

| Bucket | Decision | Why |
|---|---|---|
| Client-side GitHub PAT widgets | **Ignore hard** | Token leakage |
| SaaS feedback (Triagly, BugDrop, …) | **Ignore** | Lock-in, FAB defaults, extra account |
| Next/D1/admin self-host apps | **Ignore** | Overweight for one-line feedback |
| Multi-tenant CF Worker relays | **Ignore default** | Extra deploy; not same-origin per site |
| Fat capture SDKs (shot/record/console) | **Ignore default** | Wrong UX moment for Liz products |
| giscus/utterances | **Ignore** | Wrong problem (comments) |
| CF Turnstile-first guides | **Partial** | Keep honeypot/length only; no Turnstile until abuse |
| Tiny GH App + form tutorials | **Read-only** | Not fleet baseline |

## Outcome

No package replaced `github-telegram-feedback-pipeline`. Positioning and auto-ignore rules live in `SKILL.md` (Positioning + Ecosystem survey sections).

## What we did not do

- Did not add dependencies to product repos
- Did not vendor any third-party widget
- Did not expand scope to screenshots or AI triage
