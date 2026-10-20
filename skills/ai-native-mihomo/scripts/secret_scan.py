#!/usr/bin/env python3
"""扫描 git 跟踪的文件，确认没有节点密钥 / 订阅内容泄露。退出码 0 = 干净。

本地 Git 也按「随时可能被 push」的标准检查。
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SELF = Path(__file__).resolve()

PATTERNS = [
    ("subscription-host", re.compile(r"\b(gfw2500\.com|lxy1015\.top|7770006\.xyz|4563845\.xyz)\b", re.I)),
    ("uuid", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    ("reality-key", re.compile(r"(?:public-key|short-id|pbk|sid)\s*[:=]\s*[A-Za-z0-9_\-]{10,}")),
    ("api-secret", re.compile(r"(?m)^\s*secret\s*:\s*[0-9a-fA-F]{16,}\s*$")),
    ("bare-server-ip", re.compile(r"(?m)^\s*server\s*:\s*\d{1,3}(?:\.\d{1,3}){3}\s*$")),
    ("long-b64", re.compile(r"[A-Za-z0-9+/]{60,}={0,2}")),
]

ALLOW_SUBSTRINGS = (
    "00000000-0000-0000-0000-0000000000",  # fixture 用的全零 UUID
)
ALLOW_IP_PREFIXES = ("198.51.100.", "203.0.113.192.")  # TEST-NET-2 / TEST-NET-3


def tracked_files():
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        print("ERROR: 这个目录还不是 git 仓库（先 git init）", file=sys.stderr)
        sys.exit(2)
    return [REPO / p for p in out.stdout.split("\0") if p]


def is_allowed(match_text: str) -> bool:
    if any(s in match_text for s in ALLOW_SUBSTRINGS):
        return True
    if any(p in match_text for p in ALLOW_IP_PREFIXES):
        return True
    # 纯十六进制的长串是 sha256，不是 base64 凭据
    if re.fullmatch(r"[0-9a-fA-F]{60,}={0,2}", match_text):
        return True
    return False


def main() -> int:
    findings = []
    files = tracked_files()
    for path in files:
        if path.resolve() == SELF:
            continue  # 这个文件里写着检测模式本身
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, pattern in PATTERNS:
                for m in pattern.finditer(line):
                    if is_allowed(m.group(0)):
                        continue
                    findings.append((label, path.relative_to(REPO), lineno, m.group(0)[:80]))

    if findings:
        print(f"发现 {len(findings)} 处可疑内容：")
        for label, rel, lineno, snippet in findings:
            print(f"  [{label}] {rel}:{lineno}  {snippet}")
        return 1
    print(f"干净：{len(files)} 个被跟踪文件，没有发现节点密钥或订阅内容。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
