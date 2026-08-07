#!/usr/bin/env python3
"""Runnable harness for evals/evals.json — infrastructure self-test + eval listing.

Usage:
  python3 run-evals.py --self-test          # execute audit subcommands on fixtures
  python3 run-evals.py --list             # print eval prompts + expected outputs
  python3 run-evals.py --check-response FILE  # keyword check a saved agent response
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

SKILL_ROOT = Path(__file__).resolve().parent.parent
EVALS_PATH = SKILL_ROOT / "evals" / "evals.json"
AUDIT = SKILL_ROOT / "scripts" / "audit.py"

REQUIRED_PATHS = [
    "SKILL.md",
    "pipeline.yaml",
    "scripts/audit.py",
    "scripts/capture.py",
    "scripts/capture-runtime.py",
    "scripts/validate-capture.py",
    "scripts/validate-signal.py",
    "references/failure-gallery.md",
    "references/signal-sheet.md",
    "references/gaps-template.md",
    "references/behavior-gates.md",
]

REQUIRED_AUDIT_FLAGS = [
    "--behavior",
    "--behavior-offline",
    "--scroll-length",
    "--reduced-motion",
    "--smooth-nav",
    "--replica-only",
]

REQUIRED_GALLERY = ["I — Static Snapshot", "J — Scroll Compress", "K — Inner Scroller", "L — Tunnel Hollow"]

REQUIRED_AUDIT_SYMBOLS = [
    "def _replica_only_motion",
    "def _continuous_pointer_delta",
    "THEATER_POINTER_SELECTORS",
    "SCROLL_SIGNAL_SELECTORS",
    "def _run_replica_session",
    "def _run_target_session",
]


def load_evals() -> dict:
    return json.loads(EVALS_PATH.read_text())


def cmd_list() -> int:
    data = load_evals()
    for ev in data.get("evals", []):
        print(f"\n=== Eval {ev['id']} ===")
        print(f"PROMPT: {ev['prompt']}")
        print("EXPECTED:")
        for line in ev.get("expected_output", []):
            print(f"  - {line}")
    return 0


def _run_audit(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(AUDIT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(SKILL_ROOT),
    )


def _playwright_missing(proc: subprocess.CompletedProcess) -> bool:
    blob = f"{proc.stderr or ''}\n{proc.stdout or ''}".lower()
    needles = (
        "no module named 'playwright'",
        "no module named \"playwright\"",
        "modulenotfounderror: no module named 'playwright'",
        "playwright is not installed",
        "executable doesn't exist",  # browsers not installed
    )
    if any(n in blob for n in needles):
        return True
    # Broader: import failure surface from nested -c scripts
    return "playwright" in blob and (
        "modulenotfound" in blob or "no module named" in blob or "not found" in blob
    )


def _make_solid_png(path: Path, rgb: tuple[int, int, int], size=(64, 64)) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(
            "Pillow required for --self-test fixtures. pip install -r scripts/requirements.txt"
        ) from exc
    Image.new("RGB", size, rgb).save(path)


def _start_fixture_server(root: Path) -> tuple[ThreadingHTTPServer, str]:
    handler = type(
        "Handler",
        (SimpleHTTPRequestHandler,),
        {"directory": str(root)},
    )

    class Quiet(handler):  # type: ignore[valid-type,misc]
        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Quiet)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    return server, f"http://{host}:{port}"


def _static_checks(errors: list[str]) -> None:
    for rel in REQUIRED_PATHS:
        if not (SKILL_ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")

    audit_src = (SKILL_ROOT / "scripts/audit.py").read_text()
    for flag in REQUIRED_AUDIT_FLAGS:
        if flag not in audit_src:
            errors.append(f"audit.py missing flag: {flag}")
    for sym in REQUIRED_AUDIT_SYMBOLS:
        if sym not in audit_src:
            errors.append(f"audit.py missing symbol: {sym}")

    gallery = (SKILL_ROOT / "references/failure-gallery.md").read_text()
    for heading in REQUIRED_GALLERY:
        if heading not in gallery:
            errors.append(f"failure-gallery missing: {heading}")

    data = load_evals()
    if data.get("skill_name") != "landing-page-replication-v5":
        errors.append("evals.json skill_name mismatch")
    if len(data.get("evals", [])) < 8:
        errors.append("evals.json should contain ≥8 eval cases")


def _execution_checks(errors: list[str], notes: list[str]) -> None:
    """Call each audit.py subcommand once with minimal fixtures — not string theatre."""
    with tempfile.TemporaryDirectory(prefix="lpr-v5-selftest-") as tmp:
        tmp_path = Path(tmp)
        target_png = tmp_path / "target.png"
        replica_png = tmp_path / "replica.png"
        heat_png = tmp_path / "heat.png"
        _make_solid_png(target_png, (20, 20, 20))
        _make_solid_png(replica_png, (24, 24, 24))

        # --imr
        proc = _run_audit(
            ["--imr", str(target_png), str(replica_png), "--tolerance", "8", "--bands", "1"]
        )
        if proc.returncode not in (0, 1):
            errors.append(f"--imr unexpected exit {proc.returncode}: {proc.stderr[:200]}")
        elif "target_IMR%" not in proc.stdout and "band" not in proc.stdout:
            errors.append("--imr missing expected table output")
        else:
            notes.append("--imr executed")

        # --diff
        proc = _run_audit(["--diff", str(target_png), str(replica_png), "--out", str(heat_png)])
        if proc.returncode != 0:
            errors.append(f"--diff failed: {proc.stderr[:200] or proc.stdout[:200]}")
        elif "mean_rgb_delta=" not in proc.stdout:
            errors.append("--diff missing mean_rgb_delta")
        else:
            notes.append("--diff executed")

        # --rhythm
        proc = _run_audit(["--rhythm", str(replica_png), "--bands", "3"])
        if proc.returncode != 0 or "imr_series=" not in proc.stdout:
            errors.append(f"--rhythm failed: {proc.stderr[:200] or proc.stdout[:200]}")
        else:
            notes.append("--rhythm executed")

        # Local HTML fixture for URL-based commands
        html = tmp_path / "index.html"
        html.write_text(
            """<!doctype html><html><head><meta charset="utf-8"><title>v5 fixture</title>
<style>
  h1 { font-size: 72px; }
  body { font-size: 16px; margin: 0; }
  .pad { height: 2000px; }
  @keyframes spin { from { transform: rotate(0) } to { transform: rotate(360deg) } }
</style></head><body>
  <header><a href="#foot">Jump</a></header>
  <h1>Fixture</h1>
  <main><p>Body copy for typescale/density.</p>
  <div class="pad" id="mid">spacer</div>
  <footer id="foot">end</footer>
  </main>
</body></html>
""",
            encoding="utf-8",
        )
        offsets = tmp_path / "offsets.json"
        offsets.write_text(json.dumps({"maxScroll": 100}), encoding="utf-8")
        runtime = tmp_path / "runtime.json"
        runtime.write_text(
            json.dumps(
                {
                    "canvasCount": 0,
                    "webgl": False,
                    "hasLenis": False,
                    "maxScroll": 100,
                    "stickyCount": 0,
                }
            ),
            encoding="utf-8",
        )
        signal = tmp_path / "SIGNAL.md"
        signal.write_text("# SIGNAL\n\n## Sharp edges\n- none\n", encoding="utf-8")

        server, base = _start_fixture_server(tmp_path)
        try:
            url = f"{base}/index.html"

            def _url_cmd(name: str, argv: list[str], ok_check) -> None:
                proc = _run_audit(argv, timeout=120 if "behavior" in name else 90)
                if _playwright_missing(proc):
                    notes.append(f"{name} skipped (playwright unavailable)")
                    return
                if proc.returncode not in (0, 1):
                    errors.append(
                        f"{name} unexpected exit {proc.returncode}: "
                        f"{(proc.stderr or proc.stdout or '')[:240]}"
                    )
                    return
                ok_check(proc)

            def _typescale_ok(proc: subprocess.CompletedProcess) -> None:
                payload = proc.stdout.strip()
                start = payload.find("{")
                end = payload.rfind("}") + 1
                if start < 0 or end <= start:
                    errors.append("--typescale did not return JSON")
                    return
                try:
                    data = json.loads(payload[start:end])
                except json.JSONDecodeError:
                    errors.append("--typescale did not return JSON")
                    return
                if "tss" not in data and "error" not in data:
                    errors.append("--typescale JSON missing tss/error")
                else:
                    notes.append("--typescale executed")

            _url_cmd("--typescale", ["--typescale", url], _typescale_ok)

            def _density_ok(proc: subprocess.CompletedProcess) -> None:
                if "ed_page" not in proc.stdout and "leaves" not in proc.stdout:
                    errors.append("--density missing density fields")
                else:
                    notes.append("--density executed")

            _url_cmd("--density", ["--density", url], _density_ok)

            def _scroll_ok(proc: subprocess.CompletedProcess) -> None:
                if "replica_maxScroll" not in proc.stdout and "ratio" not in proc.stdout:
                    errors.append("--scroll-length missing ratio JSON")
                else:
                    notes.append("--scroll-length executed")

            _url_cmd(
                "--scroll-length",
                ["--scroll-length", str(offsets), url, "--min-ratio", "0.85"],
                _scroll_ok,
            )

            def _rm_ok(proc: subprocess.CompletedProcess) -> None:
                if "infiniteRunning" not in proc.stdout:
                    errors.append("--reduced-motion missing infiniteRunning")
                else:
                    notes.append("--reduced-motion executed")

            _url_cmd("--reduced-motion", ["--reduced-motion", url], _rm_ok)

            def _sn_ok(proc: subprocess.CompletedProcess) -> None:
                if "hasAnchor" not in proc.stdout and "SKIP" not in proc.stdout:
                    errors.append("--smooth-nav missing hasAnchor/SKIP")
                else:
                    notes.append("--smooth-nav executed")

            _url_cmd("--smooth-nav", ["--smooth-nav", url], _sn_ok)

            def _ro_ok(proc: subprocess.CompletedProcess) -> None:
                if "detected" not in proc.stdout:
                    errors.append("--replica-only missing detected field")
                else:
                    notes.append("--replica-only executed")

            _url_cmd(
                "--replica-only",
                ["--replica-only", url, "--signal", str(signal)],
                _ro_ok,
            )

            out_json = tmp_path / "behavior-diff.json"

            def _bo_ok(proc: subprocess.CompletedProcess) -> None:
                if not out_json.is_file():
                    errors.append("--behavior-offline did not write out JSON")
                    return
                report = json.loads(out_json.read_text())
                if "blockers" not in report or "parityScore" not in report:
                    errors.append("--behavior-offline JSON missing blockers/parityScore")
                elif report.get("mode") != "offline-target":
                    errors.append("--behavior-offline mode != offline-target")
                else:
                    notes.append("--behavior-offline executed")

            _url_cmd(
                "--behavior-offline",
                [
                    "--behavior-offline",
                    str(runtime),
                    url,
                    "--out",
                    str(out_json),
                    "--signal",
                    str(signal),
                ],
                _bo_ok,
            )

            # --behavior help path is live; we do NOT hit external targets in self-test.
            # Verify CLI accepts the flag via --help / argparse presence already covered.
            help_proc = _run_audit(["--help"], timeout=15)
            if "--behavior" not in help_proc.stdout or "--behavior-offline" not in help_proc.stdout:
                errors.append("audit --help missing behavior flags")
            else:
                notes.append("--behavior flag present (live probe not hit in self-test)")

        finally:
            server.shutdown()


def cmd_self_test() -> int:
    errors: list[str] = []
    notes: list[str] = []
    _static_checks(errors)
    if not errors:
        try:
            _execution_checks(errors, notes)
        except Exception as exc:  # noqa: BLE001 — surface fixture failures clearly
            errors.append(f"execution self-test crashed: {exc}")

    if errors:
        print("FAIL: eval harness self-test")
        for err in errors:
            print(f"  - {err}")
        for note in notes:
            print(f"  · {note}")
        return 1
    data = load_evals()
    print(f"PASS: eval harness self-test ({len(data.get('evals', []))} evals)")
    for note in notes:
        print(f"  · {note}")
    return 0


def cmd_check_response(path: Path, eval_id: int | None) -> int:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    data = load_evals()
    evals = data.get("evals", [])
    if eval_id is not None:
        evals = [e for e in evals if e.get("id") == eval_id]
    if not evals:
        print("No matching eval")
        return 2

    failed = 0
    for ev in evals:
        misses = []
        for expected in ev.get("expected_output", []):
            tokens = [t.lower() for t in expected.split() if len(t) >= 4]
            if tokens and not any(tok in text for tok in tokens[:3]):
                misses.append(expected)
        if misses:
            failed += 1
            print(f"Eval {ev['id']} FAIL — missing signals:")
            for m in misses:
                print(f"  - {m}")
        else:
            print(f"Eval {ev['id']} PASS")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="Print all eval prompts")
    ap.add_argument(
        "--self-test",
        action="store_true",
        help="Verify skill infrastructure by executing audit.py subcommands on fixtures",
    )
    ap.add_argument("--check-response", type=Path, metavar="FILE", help="Keyword-check agent response")
    ap.add_argument("--eval-id", type=int, help="Limit --check-response to one eval id")
    args = ap.parse_args()

    if args.self_test:
        return cmd_self_test()
    if args.list:
        return cmd_list()
    if args.check_response:
        return cmd_check_response(args.check_response, args.eval_id)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
