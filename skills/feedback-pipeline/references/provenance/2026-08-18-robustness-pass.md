# feedback-pipeline build log — 2026-08-18

## Input
- Existing skill already liked by Liz (delivery + header UX)
- Real installs: BrainRush, dieline-generator, pep-words
- Exa: CF form spam guides (Turnstile-heavy), light honeypot/time-gate patterns, GitHub create-issue label semantics, Telegram length

## Output
- Hardened SKILL.md + references (Function, Widget, store, tokens map)
- No product repo code changes this pass

## Constraint
- Maximize robustness without heavy stack (no Turnstile / KV / D1 / email SaaS)

## Changed (priority)
1. **P0 secrets hygiene** — removed embedded `CLOUDFLARE_API_TOKEN=cfut_…` from SKILL; tokens doc is routing-only
2. **P0 provenance** — dieline = architecture SoT; BrainRush = chrome/copy SoT; BrainRush/pep Functions marked older all-must-succeed drift
3. **P0 Function** — min/max length, honeypot fake-200, repo format check, parallel channels, label 422 → retry unlabeled, telegram truncate, optional locale/route, issueUrl on success, 405 non-POST
4. **P1 UI reference** — controlled `FeedbackModal` primary; EN default copy aligned with BrainRush voice; honeypot field; double-submit guard; standalone marked prototype-only
5. **P1 scope fence** — explicit non-goals + fleet table + verify curls including honeypot

## Did NOT change
- Did not upgrade live BrainRush / pep-words / dieline product Functions
- Did not add Turnstile, KV rate limits, D1, email, multi-tenant worker
- Did not add nonce / min-fill-ms timers
- Did not force Zustand when project lacks it
- Did not rewrite product-specific BrainRush WeChat tab pattern into the portable widget

## Anti-relapse
- “Do not hardcode secrets” must not reappear as pasted tokens in examples
- “One channel enough” must not regress to BrainRush all-must-succeed when agents mine product repos
- Light honeypot ≠ license to add CAPTCHA “while we’re here”

## Verify
- Read SKILL.md: no `cfut_` / full bot tokens
- `references/feedback-function.ts` has honeypot + label fallback + Promise.all
- `references/FeedbackWidget.tsx` exports FeedbackModal + DEFAULT_COPY Suggest a fix
