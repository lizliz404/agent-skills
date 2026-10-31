#!/usr/bin/env python3
"""Step 5: local review page. python3 review_server.py work/transcript.json [--port 8765]
Open http://127.0.0.1:8765 : click a sentence to select + jump the video, click its checkbox to cut/keep
(cut = struck through), Alt+click a word to cut it, double-click to play from there, Cmd/Ctrl+S saves back
to transcript.json. Listens on 127.0.0.1 only.
"""
import argparse, json, mimetypes, os, re, shutil
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument("transcript"); p.add_argument("--port", type=int, default=8765)
a = p.parse_args()
TP = Path(a.transcript).resolve()


class H(BaseHTTPRequestHandler):
    def log_message(self, *x):
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.send(200, (HERE / "review.html").read_bytes(), "text/html; charset=utf-8",
                             {"Cache-Control": "no-store",
                              "Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; media-src 'self'; connect-src 'self'"})
        if self.path == "/api/transcript":
            return self.send(200, TP.read_bytes(), extra={"Cache-Control": "no-store"})
        if self.path == "/media":
            try:
                f = (TP.parent / json.loads(TP.read_text(encoding="utf-8"))["media"]).resolve()
            except Exception:
                return self.send(404, b'{"error":"media file not found"}')
            if not f.is_file() or not f.is_relative_to(TP.parent):
                return self.send(404, b'{"error":"media file not found"}')
            return self.media(f)
        self.send(404, b"{}")

    def media(self, f):  # Range support so the video can seek
        size = f.stat().st_size
        m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range", ""))
        start, end = 0, size - 1
        if m:
            if m[1]:  # bytes=start- or bytes=start-end
                start = int(m[1])
                if m[2]:
                    end = int(m[2])
            elif m[2]:  # bytes=-N: the last N bytes
                start = max(0, size - int(m[2]))
            end = min(end, size - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
        self.send_response(206 if m else 200)
        self.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if m:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(f, "rb") as fh:
            fh.seek(start); left = end - start + 1
            try:
                while left > 0:
                    chunk = fh.read(min(1 << 16, left))
                    if not chunk: break
                    self.wfile.write(chunk); left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_POST(self):
        if self.path != "/api/transcript":
            return self.send(404, b"{}")
        try:
            data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert isinstance(data.get("sentences"), list)
        except Exception:
            return self.send(400, b'{"error":"bad transcript payload"}')
        shutil.copyfile(TP, TP.with_suffix(".bak.json"))
        tmp = TP.with_suffix(".tmp"); tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, TP)
        self.send(200, b'{"ok":true}')


print(f"Review page: http://127.0.0.1:{a.port}  (Ctrl+C to quit)")
ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
