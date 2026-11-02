#!/usr/bin/env python3
"""Pi JSONL -> private Liz: text logs; no stdout bodies, no task execution.

Env: FLEET_DIR, INTAKE_PI_SESSIONS (space-separated explicit paths/globs).
Called under intake-scan.sh's lock. First sight/rotation seeds EOF, no backlog.
Contract: Pi docs/session-format.md + docs/message-types.md (v3).
"""
import glob
import hashlib
import json
import os
from pathlib import Path
import re
import sys


# hc sends / ao report deliveries are persisted as user messages too. Reject
# the whole envelope, not only its first line (otherwise its payload could
# acquire Liz's speaker tag). Both tags observed in real session files.
TRANSPORT = re.compile(
    r"<\s*/?(?:hc|ao-report-delivery)\b|\[hc\b|\[message from\b", re.I)
RELAY = re.compile(
    r"(?:Liz|user|owner|boss)\s+(?:said|says|asked|authorized)\b|"
    r"(?:Liz|用户|老板|她)(?:说|要求|授权)|转述|引用如下|以下是引用|"
    r"<\s*/?(?:user|quoted[-_]user|untrusted[-_]text|blockquote)\b", re.I)
SPEAKER = re.compile(r"^(?:Liz|user|assistant|system|developer|tool)\s*[:：>]", re.I)
QUOTES = re.compile(r'“[^”]*”|「[^」]*」|『[^』]*』|"[^"\n]*"|`[^`\n]*`', re.S)
# <file>/<skill> blocks inside a user message are attachments: data, not her
# words. Skip their contents line-wise like a code fence.
ATTACH = re.compile(r"<\s*/?\s*(file|skill)\b", re.I)


def user_lines(entry):
    if not isinstance(entry, dict) or entry.get("type") != "message":
        return []
    message = entry.get("message")
    if not isinstance(message, dict) or message.get("role") != "user":
        return []
    content = message.get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = "\n".join(b["text"] for b in content if isinstance(b, dict)
                         and b.get("type") == "text" and isinstance(b.get("text"), str))
    else:
        return []
    if TRANSPORT.search(text) or RELAY.search(text):
        return []
    lines, fence, attach = [], None, None
    for line in text.splitlines():
        line = line.strip()
        if attach:
            if re.search(r"</\s*" + attach + r"\s*>", line, re.I):
                attach = None
            continue
        if m := ATTACH.match(line):
            if not re.search(r"</\s*" + m.group(1) + r"\s*>", line, re.I):
                attach = m.group(1).lower()
            continue
        if line.startswith(("```", "~~~")):
            marker = line[:3]
            if fence is None:
                fence = marker
            elif marker == fence:
                fence = None
            continue
        if fence or not line or line.startswith((">", '"', "“", "「", "『")) or SPEAKER.match(line):
            continue
        line = QUOTES.sub("", line).strip()
        if line:
            lines.append("Liz: " + line)
    return lines


def main():
    os.umask(0o077)
    fleet = Path(os.environ.get("FLEET_DIR", str(Path.home() / "radar-run/fleet")))
    cursors, logs = fleet / "intake-cursors", fleet / "intake-pi"
    for directory in (cursors, logs):
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        directory.chmod(0o700)
    stats = dict(sources=0, seeded=0, records=0, user_lines=0, invalid=0)
    paths = sorted({str(Path(p).resolve()) for pattern in os.environ.get("INTAKE_PI_SESSIONS", "").split()
                    for p in glob.glob(pattern) if Path(p).is_file()})
    for name in paths:
        key = hashlib.sha256(name.encode()).hexdigest()[:16]
        cursor, output = cursors / ("pi-" + key + ".json"), logs / (key + ".log")
        stats["sources"] += 1
        with output.open("a") as out, open(name, "rb") as source:
            output.chmod(0o600)
            st = os.fstat(source.fileno())
            try:
                previous = json.loads(cursor.read_text()) if cursor.exists() else None
            except (json.JSONDecodeError, OSError):
                previous = None  # corrupt cursor: reseed at EOF, never rescan
            identity = [st.st_dev, st.st_ino]
            if (not isinstance(previous, dict)
                    or previous.get("identity") != identity
                    or not isinstance(previous.get("offset"), int)
                    or previous["offset"] > st.st_size):
                # Do not read or copy any historical text, including on rotation.
                offset = st.st_size
                stats["seeded"] += 1
            else:
                source.seek(previous["offset"])
                while source.tell() < st.st_size:
                    start = source.tell()
                    line = source.readline()
                    if not line.endswith(b"\n"):
                        source.seek(start)  # writer has not finished the record
                        break
                    stats["records"] += 1
                    try:
                        entry = json.loads(line)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        stats["invalid"] += 1
                        continue  # never print the bad line
                    for text in user_lines(entry):
                        out.write(text + "\n")
                        stats["user_lines"] += 1
                offset = source.tell()
        cursor.write_text(json.dumps(dict(source=name, identity=identity, offset=offset)) + "\n")
        cursor.chmod(0o600)
        print(output)  # paths only; scanner consumes these as ordinary logs
    print("intake-pi: " + json.dumps(stats), file=sys.stderr)


if __name__ == "__main__":
    main()
