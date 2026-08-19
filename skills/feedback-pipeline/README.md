# Feedback Pipeline (GitHub + Telegram)

Same-origin Cloudflare Pages feedback widget → GitHub Issues and/or Telegram, with a quiet bilingual paper/ink sheet instead of a generic “submit feedback” modal.

Drop the folder into your agent skills directory. Copy `references/feedback-function.ts` and `references/FeedbackWidget.tsx` into a CF Pages project, wire `language="zh"` or `"en"`, set env vars, redeploy.

See `SKILL.md` for the full workflow, anti-SaaS positioning, and verify curls.

MIT via the parent agent-skills repo.
