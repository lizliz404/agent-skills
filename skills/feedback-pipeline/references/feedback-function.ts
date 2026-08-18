/**
 * Portable feedback delivery for Cloudflare Pages Functions.
 * Copy to: functions/api/feedback.ts
 *
 * Success = any one channel delivered. Do not fail closed on partial channel errors.
 * Set APP_SLUG below (or send `app` from the client).
 */

type Env = {
  GITHUB_TOKEN?: string;
  GITHUB_REPO?: string;
  TELEGRAM_BOT_TOKEN?: string;
  TELEGRAM_CHAT_ID?: string;
};

type FeedbackPayload = {
  message?: string;
  /** Product slug for issue titles. Falls back to APP_SLUG. */
  app?: string;
  url?: string;
  userAgent?: string;
  locale?: string;
  route?: string;
  /**
   * Honeypot — real users leave empty. Bots that fill it get a fake 200.
   * Field name is deliberately boring ("website").
   */
  website?: string;
};

type ChannelAttempt = {
  channel: "github" | "telegram";
  status: "ok" | "skipped" | "failed";
  detail?: string;
  issueUrl?: string;
};

const APP_SLUG = "[app-name]"; // ← replace per project, e.g. "brain-rush"
const MIN_MESSAGE_LEN = 3;
const MAX_MESSAGE_LEN = 2000;
const TELEGRAM_TEXT_MAX = 3500;
const REPO_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });

function missingEnv(env: Env): string[] {
  const missing: string[] = [];
  if (!env.GITHUB_TOKEN) missing.push("GITHUB_TOKEN");
  if (!env.GITHUB_REPO) missing.push("GITHUB_REPO");
  if (!env.TELEGRAM_BOT_TOKEN) missing.push("TELEGRAM_BOT_TOKEN");
  if (!env.TELEGRAM_CHAT_ID) missing.push("TELEGRAM_CHAT_ID");
  return missing;
}

function isLabelError(status: number, body: string): boolean {
  if (status !== 422) return false;
  const b = body.toLowerCase();
  return b.includes("label") || b.includes("validation failed");
}

async function createGitHubIssue(
  env: Env,
  title: string,
  body: string,
  withLabels: boolean,
): Promise<{ ok: true; issueUrl?: string } | { ok: false; detail: string; status: number; raw: string }> {
  const res = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/issues`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "User-Agent": `${APP_SLUG}-feedback`.replace(/[^a-zA-Z0-9._-]+/g, "-"),
      "X-GitHub-Api-Version": "2022-11-28",
    },
    body: JSON.stringify(
      withLabels ? { title, body, labels: ["feedback"] } : { title, body },
    ),
  });

  const raw = await res.text();
  if (!res.ok) {
    const clipped = raw.slice(0, 400);
    return {
      ok: false,
      detail: `HTTP ${res.status}${clipped ? `: ${clipped}` : ""}`,
      status: res.status,
      raw: clipped,
    };
  }

  let issueUrl: string | undefined;
  try {
    const parsed = JSON.parse(raw) as { html_url?: string };
    issueUrl = parsed.html_url;
  } catch {
    /* ignore */
  }
  return { ok: true, issueUrl };
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  let payload: FeedbackPayload;
  try {
    payload = await request.json();
  } catch {
    return json({ ok: false, error: "Invalid JSON" }, 400);
  }

  // Honeypot: pretend success, deliver nowhere.
  if (typeof payload.website === "string" && payload.website.trim() !== "") {
    return json({ ok: true, deliveredTo: [], attempts: [], dropped: "honeypot" });
  }

  const message = payload.message?.trim();
  if (!message) {
    return json({ ok: false, error: "Feedback message is required" }, 400);
  }
  if (message.length < MIN_MESSAGE_LEN) {
    return json(
      { ok: false, error: `Message too short (min ${MIN_MESSAGE_LEN} characters)`, minLength: MIN_MESSAGE_LEN },
      400,
    );
  }
  if (message.length > MAX_MESSAGE_LEN) {
    return json(
      { ok: false, error: `Message too long (max ${MAX_MESSAGE_LEN} characters)`, maxLength: MAX_MESSAGE_LEN },
      413,
    );
  }

  const app = (payload.app || APP_SLUG).trim() || APP_SLUG;
  const title = `[${app}] ${message.slice(0, 72).replace(/\s+/g, " ")}`.slice(0, 240);
  const metaLines = [
    `URL: ${payload.url || "unknown"}`,
    payload.route ? `Route: ${payload.route}` : null,
    payload.locale ? `Locale: ${payload.locale}` : null,
    `User-Agent: ${payload.userAgent || request.headers.get("user-agent") || "unknown"}`,
  ].filter(Boolean) as string[];

  const body = [message, "", "---", ...metaLines].join("\n");

  const repoOk = Boolean(env.GITHUB_REPO && REPO_RE.test(env.GITHUB_REPO));
  const hasGitHub = Boolean(env.GITHUB_TOKEN && repoOk);
  const hasTelegram = Boolean(env.TELEGRAM_BOT_TOKEN && env.TELEGRAM_CHAT_ID);
  const attempts: ChannelAttempt[] = [];
  const deliveredTo: string[] = [];

  if (!hasGitHub && !hasTelegram) {
    return json(
      {
        ok: false,
        error: "No feedback delivery channel configured",
        missing: missingEnv(env),
        hint: "Configure at least one complete channel in Cloudflare Pages → Settings → Environment variables (Production + Preview), then redeploy.",
        githubNeeds: ["GITHUB_TOKEN", "GITHUB_REPO"],
        telegramNeeds: ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"],
        repoFormat: env.GITHUB_REPO && !repoOk ? "GITHUB_REPO must look like owner/repo" : undefined,
      },
      503,
    );
  }

  if (!hasGitHub) {
    const githubMissing = [
      !env.GITHUB_TOKEN ? "GITHUB_TOKEN" : null,
      !env.GITHUB_REPO ? "GITHUB_REPO" : null,
      env.GITHUB_REPO && !repoOk ? "GITHUB_REPO (invalid format, want owner/repo)" : null,
    ].filter(Boolean) as string[];
    attempts.push({
      channel: "github",
      status: "skipped",
      detail: `incomplete config (missing ${githubMissing.join(", ")})`,
    });
  }

  if (!hasTelegram) {
    const telegramMissing = [
      !env.TELEGRAM_BOT_TOKEN ? "TELEGRAM_BOT_TOKEN" : null,
      !env.TELEGRAM_CHAT_ID ? "TELEGRAM_CHAT_ID" : null,
    ].filter(Boolean) as string[];
    attempts.push({
      channel: "telegram",
      status: "skipped",
      detail: `incomplete config (missing ${telegramMissing.join(", ")})`,
    });
  }

  const jobs: Array<Promise<void>> = [];

  if (hasGitHub) {
    jobs.push(
      (async () => {
        try {
          let result = await createGitHubIssue(env, title, body, true);
          if (!result.ok && isLabelError(result.status, result.raw)) {
            result = await createGitHubIssue(env, title, body, false);
            if (result.ok) {
              deliveredTo.push("github");
              attempts.push({
                channel: "github",
                status: "ok",
                detail: "created without labels (label feedback missing or rejected)",
                issueUrl: result.issueUrl,
              });
              return;
            }
          }
          if (result.ok) {
            deliveredTo.push("github");
            attempts.push({ channel: "github", status: "ok", issueUrl: result.issueUrl });
          } else {
            attempts.push({ channel: "github", status: "failed", detail: result.detail });
          }
        } catch (err) {
          attempts.push({
            channel: "github",
            status: "failed",
            detail: err instanceof Error ? err.message : "network error",
          });
        }
      })(),
    );
  }

  if (hasTelegram) {
    jobs.push(
      (async () => {
        try {
          const text = `${title}\n\n${body}`.slice(0, TELEGRAM_TEXT_MAX);
          const res = await fetch(
            `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                chat_id: env.TELEGRAM_CHAT_ID,
                text,
                disable_web_page_preview: true,
              }),
            },
          );
          if (res.ok) {
            deliveredTo.push("telegram");
            attempts.push({ channel: "telegram", status: "ok" });
          } else {
            const errText = (await res.text()).slice(0, 200);
            attempts.push({
              channel: "telegram",
              status: "failed",
              detail: `HTTP ${res.status}${errText ? `: ${errText}` : ""}`,
            });
          }
        } catch (err) {
          attempts.push({
            channel: "telegram",
            status: "failed",
            detail: err instanceof Error ? err.message : "network error",
          });
        }
      })(),
    );
  }

  await Promise.all(jobs);

  if (deliveredTo.length === 0) {
    const failed = attempts
      .filter((a) => a.status === "failed")
      .map((a) => `${a.channel}: ${a.detail || "failed"}`)
      .join("; ");
    return json(
      {
        ok: false,
        error: "All delivery channels failed",
        detail: failed || "No channel succeeded",
        attempts,
      },
      502,
    );
  }

  return json({ ok: true, deliveredTo, attempts });
};

/** Smoke-test friendly: non-POST is explicit 405 (method-specific exports only — no onRequest dual-export). */
export const onRequestGet: PagesFunction = async () =>
  json({ ok: false, error: "Method not allowed", allow: ["POST"] }, 405);
