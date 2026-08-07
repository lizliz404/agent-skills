#!/usr/bin/env python3
"""Clean a final-vN.md into speakable plain text for TTS.
Usage: python3 strip-for-tts.py <input.md> [output.txt]

Strips: YAML frontmatter, HTML tags (especially <a id>), citation links [N](#ref-N),
footnote markers [^N], Markdown syntax, References/Footnotes/Sources/Claim Check
sections (EN+ZH headings). Saves result to /tmp for auditability — never modify
the source manuscript.
"""
import re, sys

if len(sys.argv) < 2:
    print("Usage: python3 strip-for-tts.py <input.md> [output.txt]", file=sys.stderr)
    sys.exit(1)

inpath = sys.argv[1]
outpath = sys.argv[2] if len(sys.argv) > 2 else "/tmp/tts-cleaned.txt"

with open(inpath) as f:
    text = f.read()

# 1. Strip YAML frontmatter (--- ... ---)
text = re.sub(r'^---\n.*?---\n', '', text, flags=re.DOTALL)

# 2. Cut everything from References / Footnotes / Sources / Claim Check onward
text = re.split(
    r'\n##\s+(References|参考资料|Footnotes|脚注|Sources|引用|Claim Check)\b',
    text,
    maxsplit=1,
)[0]

# 3. Strip HTML tags entirely (<a id="...">, </a>, <span>, etc.)
text = re.sub(r'<[^>]+>', '', text)

# 4. Strip citation link numbers [N](#ref-N) entirely
text = re.sub(r'\s*\[\d+\]\(#ref-\d+\)', '', text)

# 5. Strip footnote markers [^N] (body references only, defs already cut)
text = re.sub(r'\[\^\d+\]', '', text)

# 6. Strip Markdown syntax
text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # headings
text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)                  # bold
text = re.sub(r'\*(.+?)\*', r'\1', text)                      # italic
text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)          # remaining MD links
text = re.sub(r'!\[.*?\]\([^)]+\)', '', text)                 # images
text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)      # horizontal rules
text = re.sub(r'`([^`]+)`', r'\1', text)                      # inline code
text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)         # blockquotes

# 7. Strip section anchors left as bare text (id-based)
text = re.sub(r'<a\s+id="[^"]*"></a>', '', text)

# 8. Collapse multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text)

# 9. Strip leading/trailing whitespace
text = text.strip()

with open(outpath, 'w') as f:
    f.write(text)

print(f"Cleaned: {inpath} → {outpath}")
print(f"Chars: {len(text)}")
