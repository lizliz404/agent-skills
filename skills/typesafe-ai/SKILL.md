---
name: typesafe-ai
description: Use TypeSafe AI System One (Jev) for typed semantic judgments—Noul yes/no probabilities, closed-set Choice, and ordered Score—through TypeSafe's own API and TYPESAFE_API_KEY. Use when integrating, operating, or troubleshooting TypeSafe/Jev, especially in Shelf Radar and chuhai-cloud; do not use for text generation.
---

# TypeSafe System One / Jev

Jev is TypeSafe's System One model: state in, typed judgments with probabilities out.
It is not a text-generating LLM. Code owns execution and validation; Jev supplies narrow semantic decisions.

## Route and credentials — direct only

Owner decision, 2026-10-22: use TypeSafe's own API only. Vercel Gateway is disabled (no credits). Do not select it, load its archived key, or fall back to it. A Gateway billing failure is not a TypeSafe failure.

- HTTP: `POST https://api.typesafe.ai/v1/systemone`.
- Model: `jev-latest`; record the actual model version returned.
- Credential: `TYPESAFE_API_KEY`.
- SDK base: `https://api.typesafe.ai` (SDK appends `/v1/systemone`).
- Local verified key file: `~/.agents/secrets/typesafe.env`, mode 0600.
- SG verified key file: `~/.agents/secrets/jev.env`, mode 0600; Shelf lab symlink `~/.config/shelf-radar/semantic-lab/jev.env`.
- These absolute home directories differ by host; verify existence and names without printing values. Do not assume SG lacks a key or upload another copy before checking.
- Prefer explicit per-project loading. Never print keys, provider exception bodies, Authorization headers, or secret ENV file contents.
- Do not assume price/free quota from old Gateway documentation. Usage tokens are not actual billing. Keep bounded call budgets and existing cumulative ledgers; no reset to manufacture budget.

## Request / response

```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFE_API_KEY
Content-Type: application/json

{"model":"jev-latest","state":{"query":"德国的收纳"},"questions":{"market":{"type":"choice","instructions":"Which source market is explicitly requested?","criteria":{"DE":"Germany","FR":"France","none":"Not specified","other":"Another market"}}}}
```

- Question IDs are code identifiers, not model-visible instructions.
- **Choice**: `criteria` is a map of option → description, not an `options` array. Returns `choice`, `probabilities`, `confidence`. Include unspecified/unsupported choices where needed.
- **Noul**: a yes/no question, returns `noul` in 0..1; no separate confidence.
- **Score**: ordered 2–10 levels, returns score and probability distribution.
- Response includes actual `model` and `usage.input_tokens/output_tokens`.
- Batch independent questions in one request; each question receives the state. Record actual token usage rather than assuming batching is free.
- 401: authentication; 422: request contract; 429/529: rate limit/overload. Use explicit bounded retry policy; do not silently switch providers.

## Official SDK

Python: `typesafe-sdk`, `TypeSafeClient(api_key=..., base_url="https://api.typesafe.ai", model="jev-latest")`; `system_one(state=..., questions={...})`. Use SDK `Choice(instructions=..., criteria={...})`, `Noul`, `Score`, and explicit timeout/retry limits. Reuse existing installed SDK before adding dependencies.

JS: `@typesafe-ai/sdk`. Verify installed version-matched APIs before coding.

## Integration discipline

1. Inspect existing adapter and callers; do not duplicate a provider control plane.
2. Send only the task state and supported candidates. Validate every returned field before executing anything.
3. Preserve verbatim source values and distinguish extraction, semantic judgment, and deterministic execution.
4. Calibrate adoption on held-out examples. A minimum over every unrelated field can reject all useful answers; do not lower thresholds merely to improve development scores.
5. Provider unavailable / low confidence must have explicit behavior; a silent fallback with zero accepted model answers is not a shipped semantic improvement.
6. Use replay fixtures for ordinary tests. Live tests need bounded authorization, retained usage and no secret logs.

## Documentation

Start with `https://docs.typesafe.ai/llms.txt` when current API details are needed. Relevant pages: `/primitives/choice.md`, `/primitives/noul.md`, `/primitives/score.md`, `/confidence.md`, `/patterns/intent-routing.md`, `/cookbooks/pre_parsed_value_extraction_cookbook.md`.

Host/product code may still contain a historical Gateway-first adapter. That is stale implementation, not permission to use the disabled route; adjust the owning adapter under its project's change rules. Do not change unrelated production services while fixing a Skill.
