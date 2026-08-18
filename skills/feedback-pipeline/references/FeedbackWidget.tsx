import { useEffect, useState } from "react";
import { Icon } from "@iconify/react";

/**
 * Feedback Widget — structure from dieline-generator, chrome rules from BrainRush.
 *
 * Placement: header utility cluster (next to lang switcher), NOT bottom-right FAB.
 * Interaction: fade in/out, click-outside, Escape, X.
 * Delivery: POST /api/feedback
 *
 * Preferred integration:
 *   <FeedbackTrigger onClick={() => setOpen(true)} />  // in SiteNav / TopBar
 *   <FeedbackModal open={open} onOpenChange={setOpen} appName="my-app" />  // once at app root
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

function formatFeedbackError(status: number, body: FeedbackErrorBody | null): string {
  if (!body) {
    return status ? `Send failed (HTTP ${status})` : "Network error — try again";
  }

  if (body.error === "No feedback delivery channel configured") {
    const missing = body.missing?.length ? body.missing.join(", ") : "unknown";
    return `Server has no feedback channel (missing: ${missing}). Set CF Pages env vars, then redeploy.`;
  }

  if (body.error === "All delivery channels failed") {
    const detail =
      body.detail ||
      body.attempts
        ?.filter((a) => a.status === "failed")
        .map((a) => `${a.channel}: ${a.detail || "failed"}`)
        .join("; ");
    return detail ? `Delivery failed: ${detail}` : "All feedback channels failed";
  }

  if (body.error) {
    return body.detail ? `${body.error} — ${body.detail}` : body.error;
  }

  return `Send failed (HTTP ${status})`;
}

type TriggerProps = {
  onClick: () => void;
  /** Match host chrome: landing dark header vs shell TopBar */
  surface?: "landing" | "shell";
  className?: string;
  label?: string;
};

/** Icon-only trigger — place next to LangSwitcher. */
export function FeedbackTrigger({
  onClick,
  surface = "landing",
  className = "",
  label = "Feedback",
}: TriggerProps) {
  const surfaceClass =
    surface === "shell"
      ? "flex h-8 w-8 items-center justify-center rounded-md text-on-dark-muted transition hover:bg-shell-800 hover:text-on-dark"
      : "flex h-9 w-9 items-center justify-center text-on-dark-muted transition hover:text-on-dark";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`${surfaceClass} ${className}`.trim()}
      aria-label={label}
      title={label}
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
  /** Optional product-owned strings (defaults are plain EN) */
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

const DEFAULT_COPY = {
  title: "Suggest a fix",
  hint: "One sentence about what felt wrong is enough.",
  placeholder: "Example: mobile controls feel awkward; export fails on…",
  send: "Submit feedback",
  sending: "Sending…",
  received: "Received. Thank you.",
  close: "Close",
};

/** Controlled modal — mount once at app root; headers own the trigger. */
export function FeedbackModal({ open, onOpenChange, appName, copy }: ModalProps) {
  const c = { ...DEFAULT_COPY, ...copy };
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

      setErrorMsg(formatFeedbackError(res.status, body));
      setStatus("error");
    } catch {
      setErrorMsg("Network error — try again, or contact Liz directly.");
      setStatus("error");
    }
  };

  if (!render) return null;

  return (
    <div
      className={`fixed inset-0 z-[70] flex items-start justify-center bg-black/55 px-4 pt-20 backdrop-blur-md ${
        closing ? "animate-fade-out" : "animate-fade-in"
      }`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="feedback-title"
      onClick={close}
    >
      <div
        className={`w-full max-w-md border border-border bg-surface p-5 shadow-2xl ${
          closing ? "animate-pop-out" : "animate-pop-in"
        }`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-start justify-between gap-3">
          <div>
            <h2 id="feedback-title" className="text-base font-semibold text-ink-900">
              {c.title}
            </h2>
            <p className="mt-1 text-xs leading-relaxed text-ink-500">{c.hint}</p>
          </div>
          <button
            type="button"
            onClick={close}
            aria-label={c.close}
            className="flex h-8 w-8 items-center justify-center text-ink-500 transition hover:bg-surface-2 hover:text-ink-900"
          >
            <Icon icon="lucide:x" className="h-4 w-4" />
          </button>
        </div>

        {status === "submitted" ? (
          <p className="flex items-center justify-center gap-2 py-8 text-sm text-accent">
            <Icon icon="lucide:check-circle" className="h-4 w-4" />
            {c.received}
          </p>
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
              className="w-full resize-none border border-border bg-canvas px-3 py-2 text-sm text-ink-900 placeholder:text-ink-500 focus:border-brand focus:outline-none"
              disabled={status === "submitting"}
              autoFocus
            />
            <div className="mt-3 flex items-start justify-between gap-3">
              <span className="min-w-0 flex-1 text-[11px] leading-snug text-ink-500">
                {status === "submitting" && c.sending}
                {status === "error" && <span className="text-line-cut">{errorMsg}</span>}
              </span>
              <button
                type="button"
                onClick={submit}
                disabled={!text.trim() || status === "submitting"}
                className="shrink-0 bg-ink-900 px-4 py-1.5 text-xs font-medium text-canvas transition hover:bg-ink-900/80 disabled:opacity-40"
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
}: {
  surface?: "landing" | "shell";
  appName?: string;
}) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <div className="fixed right-4 top-4 z-40 flex items-center gap-1">
        <FeedbackTrigger onClick={() => setOpen(true)} surface={surface} />
      </div>
      <FeedbackModal open={open} onOpenChange={setOpen} appName={appName} />
    </>
  );
}
