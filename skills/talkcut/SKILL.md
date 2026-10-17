---
name: talkcut
description: >-
  剪口播：多段素材拼接 → 火山引擎豆包语音字级时间戳转写 → AI 按语义标记重说（同一句只留最后一遍）、
  口癖和过长停顿（保留气口）→ 本地 localhost 审核页划线增删 → ffmpeg 精确剪切并重映射时间轴 →
  字幕（白字黑边 / 逐字高亮）→ 黑底白字蓝进度条的章节导航条。用户要剪口播、去重说、加字幕或章节导航时使用。
license: MIT
metadata:
  version: "0.1.0"
  evidence-basis: "脚本已用合成视频 + 伪造逐字稿端到端跑通；火山 ASR 真实调用、真人口播的语义剪辑质量尚未验收"
---

# talkcut · 剪口播

重活交给 ffmpeg 和语音识别，Agent 只做两件它真正擅长的事：**读懂逐字稿**（哪句是重说、怎么分章），和**把各方粘起来**。
所有脚本在 `scripts/`，仅依赖 Python 3 标准库 + ffmpeg/ffprobe；导航条额外需要 Pillow。

## 工作流

所有产物放在同一个工作目录（下称 `work/`），脚本之间只通过 JSON 交接。

1. **拼接 + 抽音频**
   `python3 scripts/prep.py 素材1.mp4 素材2.mp4 … -o work/` → `work/source.mp4`、`work/audio.mp3`（16 kHz 单声道）。
   多段素材统一重编码后拼接，单段直接复制。按用户给的顺序拼，不擅自排序。

2. **转写（火山引擎豆包语音 · 大模型录音文件识别）**
   `python3 scripts/asr_volc.py work/audio.mp3 -o work/transcript.json`（极速版，同步）；
   音频超过极速版限制时加 `--standard`（标准版，异步 submit/query）。
   凭证只从环境变量读：`DOUBAO_API_KEY`（新版控制台）或 `VOLC_APP_ID` + `VOLC_ACCESS_TOKEN`（旧版）。
   只开 标点 + ITN + utterances（含字级 words），**关闭顺滑 `enable_ddc`**（语气词和重复要留给我们判断），不开说话人/情绪等附加项。
   接口细节与开通步骤见 [references/volcengine-asr.md](references/volcengine-asr.md)。缺凭证时停下，告诉用户去哪开通，不要换别的云服务。

3. **逐字稿** `work/transcript.json`（格式见下文「数据格式」）。原始响应同时存为 `transcript.raw.json`。

4. **AI 初剪**（只改 keep 标记，不动视频）
   - 先跑规则兜底：`python3 scripts/autocut.py work/transcript.json --pause 0.5`
     相邻句 bigram 相似度 ≥ 0.72、间隔 ≤ 20 s → 重说，删前面、保留最后一遍；整句纯语气词 → 删。
   - 然后 **Agent 必须通读全文**，按语义补判规则抓不到的情况，写 `work/plan.json` 再跑一次 `autocut.py work/transcript.json --plan work/plan.json`：
     - 换了说法的重说（意思相同、字面不同）→ 删前面的，留最后一遍。**最后一遍默认最好**，除非最后一遍明显是半截。
     - 残句、说错马上改口（「这个…不对，那个」）→ 用 `cut_words` 删到改口前。
     - 「嗯、啊、那个」等口癖：只删独立成段或明显卡顿的；语义需要的「那个」保留。
     - 拿不准就保留，写进 reason 让用户在审核页决定。宁可少剪，不能剪掉有意义的内容。
   - 气口：`pause_keep`（默认 0.5 s，可在 0.4–0.6 间调）。字与字之间 ≤ 该值的停顿原样保留，更长的压到该值。

5. **本地审核页**
   `python3 scripts/review_server.py work/transcript.json` → 打开 `http://127.0.0.1:8765`。
   单击句子切换保留/删除（删除显示为划线）；⌥/Alt+单击删单字；双击从此处播放；「预览成片效果」播放时跳过被删部分；拖动气口滑块；⌘/Ctrl+S 保存回 JSON（旧版本存为 `transcript.bak.json`）。
   告诉用户地址后**等用户确认**再出片。用户也可以直接在对话里说「第 12 句留着」，Agent 改 JSON 即可。

6. **出片** `python3 scripts/render.py work/transcript.json` → `work/cut.mp4` + `work/cut.json`（新时间轴逐字稿）。
   用 trim/atrim + concat 重编码，帧级精确；每个切点 10 ms 音频淡入淡出防爆音。

7. **字幕** `python3 scripts/subs.py work/cut.json --style simple|karaoke [--burn]`
   - `simple`：白字黑描边。`karaoke`：逐字高亮（当前字变色并放大 118%）。
   - 总会导出 `cut.srt`（可拖进剪映）和对应 `.ass`；`--burn` 再烧录出 `cut_<style>.mp4`。
   - 调整：`--max-chars` 每行字数，`--font` 字体名，`--highlight` 高亮色（ASS 的 `&HAABBGGRR`）。

8. **章节导航条**（样式致敬 [dbskill / dbs-video-navigation](https://github.com/dontbesilent2025/dbskill)）
   - Agent 通读 `cut.json`，按「在解决什么问题」分章，写 `work/chapters.json`：
     ```json
     {"chapters": [{"title": "第一部分：为什么要剪口播",
                    "segments": [{"start": 0, "desc": "剪映不懂语义"}, {"start": 12.3, "desc": "同一句只留最后一遍"}]}]}
     ```
     `start` 是成片时间（秒），取自 `cut.json` 的句子起点；第一段从 0 开始。标题上行写「现在讲到哪部分」，下行写「这一段在讲什么」，都要短到一行放得下。
   - `python3 scripts/navbar.py work/cut.json work/chapters.json` → `work/navbar.mp4`：与成片等长、无音轨、宽度同成片，黑底白字、蓝色进度条、章节间有缝。样式在 `assets/navbar-black-blue.json`。
   - 交付时说明：拖进剪映放在主轨上方、0 秒对齐、贴画面顶部；需要给导航条留位置时把原片等比缩小下移。

## 验收（每次出片后都做）

- `ffprobe` 核对 cut.mp4 / navbar.mp4 时长一致（navbar.py 会自动比对）。
- 抽几帧看：切点前后不吃字、字幕不出框、导航条最长标题不超宽（脚本会警告）、进度条最终填满。
- 向用户汇报：删了几句、成片多长、每个产物的路径。脚本跑通 ≠ 剪得好，语义质量要用户看过才算。

## 数据格式

`transcript.json`（render 之前）：
```json
{"version": 1, "media": "source.mp4", "pause_keep": 0.5,
 "sentences": [{"id": 0, "start": 0.3, "end": 2.4, "text": "大家好", "keep": true, "reason": "",
                "words": [{"text": "大", "start": 0.3, "end": 0.5, "keep": true}]}]}
```
`cut.json`（render 之后，时间是成片时间）：`{"media": "cut.mp4", "duration": …, "segments": [[原片起, 原片止], …], "sentences": [{id, start, end, text, words[]}]}`

## 边界

- 不上传到火山以外的任何服务；不提交、不打印凭证。
- 不覆盖用户原始素材；所有输出写进 `work/`。
- 不负责：调色、配乐、B-roll、封面。需要花字动画时可把 `cut.json` 交给 HyperFrames 一类工具。
