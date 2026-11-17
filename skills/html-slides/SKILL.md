---
name: html-slides
description: "学术HTML幻灯片生成技能。从确认的outline生成1920x1080 HTML slides，严格模板系统，统一字体，Chart.js图表，Playwright截图，组装PPTX。触发词: 做PPT, 生成slides, make slides, 开始做幻灯片"
metadata:
  version: "1.0"
  last_updated: "2026-04-05"
---

# HTML Slides — 学术幻灯片生成

从 `presentation-logic` skill 输出的 `presentation_outline.md` 生成HTML学术slides。

## 前置条件

**必须有 `presentation_outline.md`**。如果没有，先运行 `presentation-logic` skill。

## 设计系统（不可违反）

### 字体规格（绝对值，不允许inline覆盖）

| 元素 | 大小 | CSS class |
|------|------|-----------|
| 标题页主标题 | 52px | `.title-slide h1` |
| 内容页标题 | 36px | `.header h1` |
| 内容页副标题 | 20px | `.header .subtitle` |
| 正文/要点 | 18px | `.body-text` |
| 表格内容 | 15px | `.data-table td` |
| 卡片标题 | 16px | `.card-title` |
| 卡片正文 | 15px | `.card p` |
| 参考文献 | 14px | `.ref` |
| 页脚 | 14px | `.footer span` |
| Key Finding框 | 18px | `.key-finding .text` |

### 禁止规则

1. **禁止inline font-size** — 所有字体大小通过CSS class控制
2. **禁止card-value超过40px** — 大数字展示最大40px
3. **禁止在正文中使用超过20px的字体**
4. **禁止同一数据点出现在多张slide上** — 引用outline检查

### 配色方案

```css
--primary: #0f4c75      /* 主色-深蓝 */
--primary-light: #3282b8 /* 浅蓝 */
--primary-dark: #0b2545  /* 深蓝 */
--accent: #00b4d8        /* 强调色-青 */
--success: #38a169       /* 正面/好的 */
--danger: #e53e3e        /* 负面/差的 */
--warning: #d69e2e       /* 中等/注意 */
```

### Slide模板类型

每张slide必须选择以下模板之一：

#### Template 1: 标题页 (title-slide)
- 渐变背景，居中大标题，作者，单位

#### Template 2: 论点页 (argument-slide)
- 标题（回答一个问题）
- 两栏或单栏正文
- 底部key-finding框（可选）
- 底部参考文献

#### Template 3: 研究展示页 (study-slide)
- 顶部study-header（期刊badge + 标题 + 设计/样本量）
- 左侧：结果表格或要点
- 右侧：Chart.js图表
- 底部：key finding + 参考文献

#### Template 4: 数据对比页 (comparison-slide)
- 标题
- 全宽表格或并排卡片
- 底部综合解读

#### Template 5: 框架/流程页 (framework-slide)
- 标题
- 流程图/框架图（用CSS flexbox构建）
- 底部说明

#### Template 6: 总结页 (summary-slide)
- 编号要点列表
- 每条带简短支撑证据

#### Template 7: 结束页 (thankyou-slide)
- 渐变背景，谢谢，联系方式

## 工作流程

### Step 1: 读取 outline
读取 `presentation_outline.md`，确认slide数量和每张的内容要求。

### Step 2: 准备 theme.css
检查是否存在theme.css，如不存在则生成。theme.css包含所有CSS class定义，不允许在HTML中写inline style（除了layout相关的flex/padding）。

### Step 3: 生成 HTML
为每张slide生成独立HTML文件：
- 文件名：`slide_NN_shortname.html`
- 每个文件link到theme.css
- Chart.js通过CDN引入
- 选择合适的模板类型
- **不允许inline font-size**

可以使用subagent并行生成，但必须给每个agent：
- theme.css内容
- 一个示例slide HTML
- 该agent负责的slides的outline内容
- 对应的论文笔记文件路径

### Step 4: 截图预览
使用Node.js + Playwright截图：

```javascript
// screenshot.cjs — 截图所有slides
const { chromium } = require('playwright-core');
// browser: C:/Users/86138/AppData/Local/ms-playwright/chromium-1193/chrome-win/chrome.exe
// viewport: { width: 1920, height: 1080 }
// waitForTimeout: 1500ms (等待字体+图表加载)
```

### Step 5: 自检
截图后检查：
- [ ] 所有slide字体一致（标题36px，正文18px）
- [ ] 没有内容溢出slide边界
- [ ] 图表正确渲染
- [ ] 中文字体正确显示
- [ ] 参考文献在底部

### Step 6: 预览页
生成 `preview.html`，支持左右箭头键翻页，iframe加载每张slide。

### Step 7: 组装PPTX（可选）
如果用户需要PPTX输出：
1. 截图所有slides为PNG
2. 用python-pptx将PNG作为全页背景图插入
3. 输出.pptx文件

或者使用LibreOffice将HTML转PDF：
```
powershell.exe -NoProfile -Command "Start-Process -FilePath 'C:\Program Files\LibreOffice\program\soffice.exe' -ArgumentList '--headless','--convert-to','pdf',... -Wait -NoNewWindow"
```

## Chart.js 使用规范

```javascript
// CDN
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

// 字体统一
font: { family: 'Noto Sans SC', size: 13 }

// 颜色使用CSS变量对应的值
// success: rgba(56,161,105,0.8)
// danger: rgba(229,62,62,0.8)
// warning: rgba(214,158,46,0.8)
// primary: rgba(15,76,117,0.8)
```

## 输出目录

```
项目目录/output/
├── slides/
│   ├── theme.css
│   ├── preview.html
│   ├── slide_01_title.html
│   ├── slide_02_xxx.html
│   └── ...
├── screenshots/
│   ├── slide_01_title.png
│   └── ...
└── final.pptx (可选)
```
