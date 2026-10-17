# talkcut · 剪口播

把一段（或几段）口播原片剪成能发的成片：**同一句说了好几遍，只留最后一遍；气口留着，长停顿压短；字幕和章节导航条一起出。**

```
素材 ──prep──▶ source.mp4 + audio.mp3 ──asr_volc──▶ transcript.json（字级时间戳）
     ──autocut + Agent 读稿──▶ 标记重说/口癖 ──review_server──▶ localhost 划线审核
     ──render──▶ cut.mp4 + cut.json ──subs──▶ 字幕（白字黑边 / 逐字高亮）
                                    ──navbar──▶ navbar.mp4（黑底白字蓝进度条，等长）
```

## 为什么又造一个

调研下来，现有项目本质都是**胶水层**：真正干活的是 ffmpeg（切、拼、烧字幕）和 ASR（时间戳）。它们各自做得不错，但没有一个刚好是「豆包语音转写 + 语义判断重说留最后一遍 + 轻量本地审核页 + 直接出片 + 导航条」这一套。talkcut 把这套压到几个零依赖的 Python 脚本和一个单文件 HTML 里，方便按自己的口味改。

## 需要

- Python 3.9+、ffmpeg/ffprobe；导航条需要 `pip install pillow` 和一款中文字体
- 火山引擎豆包语音「录音文件识别大模型」：`DOUBAO_API_KEY`（或 `VOLC_APP_ID` + `VOLC_ACCESS_TOKEN`），见 [references/volcengine-asr.md](references/volcengine-asr.md)

## 快速开始

```bash
S=skills/talkcut/scripts
python3 $S/prep.py a.mp4 b.mp4 -o work/
python3 $S/asr_volc.py work/audio.mp3 -o work/transcript.json
python3 $S/autocut.py work/transcript.json --pause 0.5      # Agent 再补一份 plan.json
python3 $S/review_server.py work/transcript.json            # http://127.0.0.1:8765
python3 $S/render.py work/transcript.json
python3 $S/subs.py work/cut.json --style karaoke --burn
python3 $S/navbar.py work/cut.json work/chapters.json
```

完整流程、AI 判断规则和数据格式见 [SKILL.md](SKILL.md)。

## 验证状态

- ✅ 合成视频（testsrc + 正弦音）+ 伪造逐字稿端到端跑通：拼接、规则去重说、剪切与时间重映射、SRT/ASS、两种字幕烧录、导航条（时长与成片一致）、审核页服务（页面、Range 拖动、保存）。
- ⏳ 未验证：火山 ASR 真实调用（需要 Key）、真人口播的语义剪辑质量、审核页在浏览器里的交互手感。

## References

- [dontbesilent2025/dbskill](https://github.com/dontbesilent2025/dbskill) — dontbesilent 的内容创作 Skill 工具箱；其中 `dbs-video-navigation` 由 Agent 读字幕分章，Swift/Pillow 画文字 PNG + ffmpeg `drawbox`/`sendcmd` 画进度条，输出独立导航 MP4。**我们的导航条样式（黑底白字、蓝色分段进度条）直接致敬它**，简化为 Pillow + drawbox 时间表达式，并与剪辑后的 `cut.json` 直接衔接。
- [Agentchengfeng/chengfeng-videocut-skills](https://github.com/Agentchengfeng/chengfeng-videocut-skills) — 乘风剪口播：Codex Plugin + 独立 Runtime/浏览器 Studio，火山 ASR，「删前保后」规则，HyperFrames 做花字。完整但重（插件/运行时/版本锁）；我们借「删前保后」，砍掉运行时。
- [lcbuaaliu/ai-jian-koubo](https://github.com/lcbuaaliu/ai-jian-koubo) — AI 剪口播：火山极速/标准版转写，AI 预标口误，带波形的本地审核网页，导出 FCPXML 交给剪映/FCP。我们参考了它的火山接口细节和审核页交互，区别是直接用 ffmpeg 出片而不是导工程。
- [fxl1209739475-fxl/ai-xunjian](https://github.com/fxl1209739475-fxl/ai-xunjian) — AI 驯剪：faster-whisper 词级时间戳，静音剪气口、相邻重复句留后一遍，React 可视化编辑器 + HyperFrames 动效。我们借「剪气口但保留上限」的思路，换成豆包 ASR。
- [modelscope/FunClip](https://github.com/modelscope/FunClip) — 阿里通义实验室开源：FunASR Paraformer 识别，Gradio 页面里选文字片段即剪，支持 LLM 智能剪辑和 SRT。经典「按文字剪视频」范式，我们沿用这个范式但不绑定 FunASR。
- [xixihhhh/hotclip](https://github.com/xixihhhh/hotclip) — `src/core/retakes.ts`：相邻句 bigram Dice ≥ 0.72、20 秒内、跨 ≤ 2 句判为重录，保留最后一遍。**`autocut.py` 的规则兜底直接采用这组保守参数**，再由 Agent 做语义补判。
- [Gitruck/cli](https://github.com/Gitruck/cli) — `gtrk oralcut`：付费云端口播粗剪，可按稿对齐，导出剪映/Premiere/FCPXML/OTIO。作为商业对照；talkcut 全本地、只为 ASR 付费。
- [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) — 用 HTML/CSS/GSAP 写视频并渲染成 MP4，带嵌入字幕等能力。不是剪辑器；需要比 ASS 更花的逐字动效时，可把 `cut.json` 喂给它。

## License

MIT
