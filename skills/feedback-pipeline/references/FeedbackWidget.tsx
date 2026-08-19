import { useEffect, useState } from "react";
import { Icon } from "@iconify/react";

/**
 * Feedback Widget — quiet paper/ink default, painted with host-product tokens.
 *
 * Placement: header utility cluster (next to lang switcher), NOT bottom-right FAB.
 * Interaction: light scrim, compact sheet, click-outside, Escape, obvious X.
 * Delivery: POST /api/feedback
 *
 * Preferred integration:
 *   <FeedbackTrigger onClick={() => setOpen(true)} language="zh" />  // in SiteNav / TopBar
 *   <FeedbackModal open={open} onOpenChange={setOpen} appName="my-app" language="zh" />  // once at app root
 *
 * Standalone <FeedbackWidget /> is a fallback for prototypes only (fixed top-right).
 */

const TRANSITION_MS = 220;

type FeedbackErrorBody = {
  ok?: boolean;
  error?: string;
  detail?: string;
  missing?: string[];
  attempts?: Array<{ channel: string; status: string; detail?: string }>;
};

function formatFeedbackError(
  status: number,
  body: FeedbackErrorBody | null,
  language: "en" | "zh",
): string {
  if (!body) {
    if (language === "zh") {
      return status ? `发送失败（HTTP ${status}）` : "网络异常，请重试";
    }
    return status ? `Send failed (HTTP ${status})` : "Network error — try again";
  }

  if (body.error === "No feedback delivery channel configured") {
    const missing = body.missing?.length ? body.missing.join(", ") : "unknown";
    if (language === "zh") {
      return `服务端尚未配置反馈渠道（缺少：${missing}）。请设置 Cloudflare Pages 环境变量后重新部署。`;
    }
    return `Server has no feedback channel (missing: ${missing}). Set CF Pages env vars, then redeploy.`;
  }

  if (body.error === "All delivery channels failed") {
    const detail =
      body.detail ||
      body.attempts
        ?.filter((a) => a.status === "failed")
        .map((a) => `${a.channel}: ${a.detail || "failed"}`)
        .join("; ");
    if (language === "zh") {
      return detail ? `发送失败：${detail}` : "所有反馈渠道均发送失败";
    }
    return detail ? `Delivery failed: ${detail}` : "All feedback channels failed";
  }

  if (body.error) {
    return body.detail ? `${body.error} — ${body.detail}` : body.error;
  }

  return language === "zh" ? `发送失败（HTTP ${status}）` : `Send failed (HTTP ${status})`;
}

type TriggerProps = {
  onClick: () => void;
  /** Match host chrome: landing dark header vs shell TopBar */
  surface?: "landing" | "shell";
  className?: string;
  label?: string;
  /** Wire this to the product locale; do not leave Chinese products in English. */
  language?: "en" | "zh";
};

/** Icon-only trigger — place next to LangSwitcher. */
export function FeedbackTrigger({
  onClick,
  surface = "landing",
  className = "",
  label,
  language = "en",
}: TriggerProps) {
  const accessibleLabel = label || (language === "zh" ? "反馈" : "Feedback");
  const surfaceClass =
    surface === "shell"
      ? "flex h-8 w-8 items-center justify-center rounded-md text-on-dark-muted transition hover:bg-shell-800 hover:text-on-dark"
      : "flex h-9 w-9 items-center justify-center text-on-dark-muted transition hover:text-on-dark";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${surfaceClass} ${className}`.trim()}
      aria-label={accessibleLabel}
      title={accessibleLabel}
    >
      <Icon icon="lucide:message-square" className="h-4 w-4" />
    </button>
  );
}

type ModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** Sent as `app` for issue titles */
  appName?: string;
  /** Wire to the app locale. Product copy can still override individual strings. */
  language?: "en" | "zh";
  copy?: Partial<{
    title: string;
    hint: string;
    placeholder: string;
    send: string;
    sending: string;
    received: string;
    close: string;
  }>;
};

const DEFAULT_COPY_EN = {
  title: "What felt off?",
  hint: "One sentence is enough.",
  placeholder: "Example: mobile controls feel awkward; export fails on…",
  send: "Send note",
  sending: "Sending…",
  received: "Got it. Thank you.",
  close: "Close",
};

const DEFAULT_COPY_ZH = {
  title: "哪里不对劲？",
  hint: "一句话就够。",
  placeholder: "例如：手机上的操作有点别扭；导出时……",
  send: "发送",
  sending: "发送中…",
  received: "记下了，谢谢。",
  close: "关闭",
};

/** Controlled modal — mount once at app root; headers own the trigger. */
export function FeedbackModal({
  open,
  onOpenChange,
  appName,
  language = "en",
  copy,
}: ModalProps) {
  const c = {
    ...(language === "zh" ? DEFAULT_COPY_ZH : DEFAULT_COPY_EN),
    ...copy,
  };
  const [render, setRender] = useState(open);
  const [closing, setClosing] = useState(false);
  const [text, setText] = useState("");
  const [honeypot, setHoneypot] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "submitted" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (open) {
      setRender(true);
      setClosing(false);
      return;
    }
    if (!render) return;
    setClosing(true);
    const timer = window.setTimeout(() => {
      setRender(false);
      setClosing(false);
    }, TRANSITION_MS);
    return () => window.clearTimeout(timer);
  }, [open, render]);

  useEffect(() => {
    if (render) return;
    setText("");
    setHoneypot("");
    setStatus("idle");
    setErrorMsg("");
  }, [render]);

  const close = () => onOpenChange(false);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  useEffect(() => {
    if (status !== "submitted") return;
    const t = window.setTimeout(() => close(), 1600);
    return () => window.clearTimeout(t);
  }, [status]);

  const submit = async () => {
    const message = text.trim();
    if (!message || status === "submitting") return;
    setStatus("submitting");
    setErrorMsg("");
    try {
      const res = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          app: appName,
          url: window.location.href,
          userAgent: navigator.userAgent,
          // Honeypot: humans leave empty
          website: honeypot,
        }),
      });

      let body: FeedbackErrorBody | null = null;
      try {
        body = (await res.json()) as FeedbackErrorBody;
      } catch {
        body = null;
      }

      if (res.ok) {
        setStatus("submitted");
        setText("");
        return;
      }

      setErrorMsg(formatFeedbackError(res.status, body, language));
      setStatus("error");
    } catch {
      setErrorMsg(
        language === "zh"
          ? "网络异常，请重试；也可以直接联系 Liz。"
          : "Network error — try again, or contact Liz directly.",
      );
      setStatus("error");
    }
  };

  if (!render) return null;

  return (
    <div
      className={`fixed inset-0 z-[70] flex items-end justify-center bg-black/20 px-3 pt-3 sm:items-start sm:justify-end sm:px-5 sm:py-14 ${
        closing ? "animate-fade-out" : "animate-fade-in"
      }`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="feedback-title"
      onClick={close}
    >
      <div
        className={`w-full max-w-[26rem] rounded-t-lg border border-border bg-canvas px-4 pb-4 pt-3 shadow-[0_12px_36px_rgba(0,0,0,0.12)] sm:rounded-sm ${
          closing ? "animate-sheet-out" : "animate-sheet-in"
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-start justify-between gap-4">
          <div className="min-w-0 pt-0.5">
            <h2 id="feedback-title" className="text-[15px] font-semibold leading-5 text-ink-900">
              {c.title}
            </h2>
            <p className="mt-1 text-xs leading-5 text-ink-500">{c.hint}</p>
          </div>
          <button
            type="button"
            onClick={close}
            aria-label={c.close}
            title={c.close}
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm border border-border text-ink-500 transition hover:bg-surface-2 hover:text-ink-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink-900"
          >
            <Icon icon="lucide:x" className="h-4 w-4" />
          </button>
        </div>

        {status === "submitted" ? (
          <div className="border-t border-border py-7" role="status" aria-live="polite">
            <p className="text-sm leading-6 text-ink-900">{c.received}</p>
          </div>
        ) : (
          <>
            {/* Honeypot: hidden from humans, not display:none so some bots still fill it */}
            <label
              className="absolute -left-[10000px] h-px w-px overflow-hidden"
              aria-hidden="true"
            >
              Website
              <input
                type="text"
                name="website"
                tabIndex={-1}
                autoComplete="off"
                value={honeypot}
                onChange={(e) => setHoneypot(e.target.value)}
              />
            </label>

            <textarea
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (status === "error") {
                  setStatus("idle");
                  setErrorMsg("");
                }
              }}
              placeholder={c.placeholder}
              rows={4}
              className="min-h-28 w-full resize-none rounded-sm border border-border bg-surface px-3 py-2.5 text-sm leading-6 text-ink-900 placeholder:text-ink-500 focus:border-ink-900 focus:outline-none"
              disabled={status === "submitting"}
              aria-invalid={status === "error"}
              aria-describedby={status === "error" ? "feedback-status" : undefined}
              autoFocus
            />
            <div className="mt-3 flex min-h-8 items-start justify-between gap-3 border-t border-border pt-3">
              <span
                id="feedback-status"
                className="min-w-0 flex-1 pt-1 text-[11px] leading-4 text-ink-500"
                aria-live="polite"
              >
                {status === "submitting" && c.sending}
                {status === "error" && <span className="text-line-cut">{errorMsg}</span>}
              </span>
              <button
                type="button"
                onClick={submit}
                disabled={!text.trim() || status === "submitting"}
                className="shrink-0 rounded-sm bg-ink-900 px-3.5 py-2 text-xs font-medium text-canvas transition hover:bg-ink-900/85 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ink-900 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {status === "submitting" ? c.sending : c.send}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/**
 * Prototype-only standalone: fixed top-right trigger + modal.
 * Prefer FeedbackTrigger-in-chrome + root FeedbackModal for real products.
 */
export function FeedbackWidget({
  surface = "landing",
  appName,
  language = "en",
}: {
  surface?: "landing" | "shell";
  appName?: string;
  language?: "en" | "zh";
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <div className="fixed right-4 top-4 z-40 flex items-center gap-1">
        <FeedbackTrigger onClick={() => setOpen(true)} surface={surface} language={language} />
      </div>
      <FeedbackModal
        open={open}
        onOpenChange={setOpen}
        appName={appName}
        language={language}
      />
    </>
  );
}
