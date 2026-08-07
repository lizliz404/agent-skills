#!/usr/bin/env python3
"""口播脚本字数核验:统计口播正文(只删行首节标题),查脏字/金句/关键元素在位。

用法:
    python3 count_spoken_chars.py <SCRIPT.md> [<节起始标记>] [<节结束标记>]

默认节区间:【开场·前5秒】 → # 可裁剪(可覆盖)。
双口径输出:
  - 汉字数(≈实播时长主估)
  - 含标点总字符(去空白;对照目标带 850-950)
检查项可在 CHECK_WORDS / HARD_WORDS 自定义。

踩坑备忘:
- 只删「行首独占一行的节标题」;行内【待 Liz 填 N】式占位符必须保留,
  naive re.sub(r'【[^】]+】', ...) 会把占位符当节标题误删,导致字数虚低、核验误报。
- 含空格的元素(geo job hunting)要在保留空白的原文上查,去空白后子串会失配。
- CHECK_WORDS 默认列表是 geo-job 遗留;跨题材请按本稿金句自建,勿被 MISS 误导。
"""
import re
import sys


def load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_body(text: str, start: str = "【开场·前5秒】", end: str = "# 可裁剪") -> str:
    """取出口播正文:从 start 到 end 之间的内容。找不到任一标记则整段返回。"""
    s = text.find(start)
    if s == -1:
        return text
    body = text[s:]
    e = body.find(end)
    if e != -1:
        body = body[:e]
    return body


def strip_beat_labels(body: str) -> str:
    """只删「行首独占一行」的节标题(【开场·前5秒】等),保留行内占位符。"""
    lines = body.split("\n")
    return "\n".join(l for l in lines if not re.match(r"^【[^】]+】\s*$", l))


def count_hanzi(text: str) -> int:
    """统计汉字数(含扩展 A);不含标点与拉丁字母。"""
    return len(re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    start = sys.argv[2] if len(sys.argv) > 2 else "【开场·前5秒】"
    end = sys.argv[3] if len(sys.argv) > 3 else "# 可裁剪"

    text = load(path)
    body_raw = strip_beat_labels(extract_body(text, start, end))
    compact = re.sub(r"\s+", "", body_raw)
    total = len(compact)
    hanzi = count_hanzi(compact)
    print(f"口播正文汉字数: {hanzi}  (≈实播时长主估)")
    print(f"口播正文总字数(含标点): {total}  (目标约 850-950)")

    # 硬审核词:应为 0
    HARD_WORDS = ["他妈的", "我操", "意淫", "自慰", "操蛋", "傻逼"]
    hits = [w for w in HARD_WORDS if w in body_raw]
    print(f"脏字/硬审核词(应为0或按裁决为1): {hits if hits else '无'}")

    # 金句/关键元素:至少各 1(按需增删)
    # 默认列表是 geo-job 遗留;跨题材请替换为本稿金句
    CHECK_WORDS = [
        "房门钥匙", "不准看啊", "磕一个", "翻来翻去", "geo job hunting",
        "lizliz", "待 Liz 填 N", "关我屁事", "对我有屁用",
    ]
    for w in CHECK_WORDS:
        n = body_raw.count(w)
        flag = "OK " if n >= 1 else "MISS"
        print(f"  [{flag}] {w}: {n}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
