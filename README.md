# Article Typesetter

把结构松散的中文文章整理成更适合阅读、发布和复制的 Markdown、HTML、RTF。

这是一个普通命令行工具，不依赖 Codex。你可以直接在终端里运行 `typeset.py`，把 `.rtf`、`.txt` 或 `.md` 转成通用 Markdown、HTML、RTF、知乎文本或小红书文本。

这个项目包含两部分：

- `typeset.py`：普通 Python CLI，负责读取输入、做基础结构化、渲染输出。
- `SKILL.md`：给 Codex 使用的进阶排版工作流说明，负责更细的语义判断。

## 两种使用方式

### 1. 直接命令行使用

适合快速处理文章，不需要 Codex 参与。脚本会做保守的自动结构化：

- RTF 自动转纯文本。
- 第一行转成标题。
- 短章节行转成小标题。
- 明显的内联并列项转成列表。
- 输出知乎 / 小红书平台安全文本。

示例：

```bash
python3 typeset.py ~/Desktop/codex.rtf output.zhihu.txt --platform zhihu
python3 typeset.py ~/Desktop/codex.rtf output.xhs.txt --platform xhs
python3 typeset.py ~/Desktop/codex.rtf output.html --theme modern-blue
```

### 2. 配合 Codex 精排

适合需要摘要、核心观点、金句高亮、表格重构等语义排版的文章。

Codex 先按 `SKILL.md` 做 Phase 1 / Phase 2，生成 `*-source.md` 结构化源稿；然后你可以继续用命令行渲染：

```bash
python3 typeset.py article-source.md article.html --theme modern-blue
python3 typeset.py article-source.md article.zhihu.txt --platform zhihu
python3 typeset.py article-source.md article.xhs.txt --platform xhs
```

## 适用场景

- 从 RTF、PDF 复制文本、笔记草稿中整理长文。
- 给文章补标题层级、摘要、重点段、列表和表格。
- 输出适合网页浏览的单文件 HTML。
- 输出适合富文本编辑器粘贴的 RTF。
- 输出尽量通用、可复制的 Markdown。

## 核心概念

项目里有两种 Markdown，不要混用。

### 1. 结构化源 Markdown

结构化源稿是给 `typeset.py` 渲染用的中间格式，通常命名为：

```text
*-source.md
```

它允许使用这些内部标记：

```md
> [!summary] 摘要段
> [!key] 核心观点段
==重点短语==
```

这些标记可以被 `typeset.py` 转成 HTML/RTF 里的视觉样式，但它们不是通用 Markdown。直接复制到很多地方时，可能会原样显示。

### 2. 通用 Markdown

通用 Markdown 是给人阅读、复制和发布用的版本，通常命名为：

```text
*.md
```

推荐使用更兼容的写法：

```md
> **摘要**：摘要段
> **核心观点**：核心观点段
**重点短语**
```

这样在 GitHub、Notion、飞书、语雀、微信公众号编辑器等环境里更容易保持基本格式。

## Codex 精排工作流

这一节只适用于配合 Codex 做语义排版。直接命令行使用时，可以跳过这里，直接看“命令用法”。

### Phase 1：排版决策

先阅读原文，列出排版决策清单：

- 哪些短段落适合做摘要或核心观点。
- 哪些平铺内容适合转成列表。
- 哪些对比结构适合转成表格。
- 哪些短语适合重点强调。
- 哪些大段推理应保持普通段落。

这一阶段只做判断，不生成最终文件。

### Phase 2：生成文件

确认决策后：

1. 创建 `*-source.md`，写入结构化源 Markdown。
2. 用 `typeset.py` 渲染 HTML、RTF、通用 Markdown 或平台纯文本。
3. `.md`、知乎、小红书输出会自动去掉 `[!summary]`、`[!key]`、`==...==` 等内部标记，换成更兼容的可见格式。

## 命令用法

查看帮助：

```bash
python3 typeset.py --help
```

直接按下面格式使用：

```bash
python3 typeset.py input.md output.html --theme modern-blue
python3 typeset.py input.md output.rtf --theme modern-blue
python3 typeset.py input.md output.md modern-blue
python3 typeset.py input.md output.zhihu.txt --platform zhihu
python3 typeset.py input.md output.xhs.txt --platform xhs
```

输入支持 `.md`、`.txt` 和 `.rtf`。其中 `.rtf` 会先通过 macOS 自带的 `textutil` 转成纯文本，再进入排版流程。对于没有 Markdown 标记的纯文本输入，脚本会保守地自动识别第一行标题、短章节标题和明显的内联并列项，生成 `#` / `##` 层级和 bullet 列表。

例如：

```bash
python3 typeset.py ~/Desktop/codex.rtf output.md modern-blue
python3 typeset.py ~/Desktop/codex.rtf output.html --theme modern-blue
python3 typeset.py ~/Desktop/codex.rtf output.zhihu.txt --platform zhihu
python3 typeset.py ~/Desktop/codex.rtf output.xhs.txt --platform xhs
```

注意：`.md` 输出会转换为通用 Markdown。脚本会把 `[!summary]`、`[!key]`、`==...==` 这类结构化源标记转换成更兼容的引用块和加粗文本。

Markdown 本身不支持主题色、背景色、边框和卡片样式。因此 `modern-blue`、`minimalist`、`warm-peach`、`dark-cyber` 这些主题只影响 HTML 和 RTF 的视觉表现；Markdown 输出保留的是标题、引用、加粗、列表、表格等结构样式。

另外，脚本不会自动判断摘要、核心观点、金句高亮、表格转换等语义结构。这些仍然应该先通过 `SKILL.md` 的 Phase 1/Phase 2 生成 `*-source.md`，再交给 `typeset.py` 渲染。

## 平台输出

知乎和小红书都不适合直接粘贴 Markdown 源码。平台输出模式会生成“可见即格式”的纯文本：

- Markdown 标题会转成 `一、标题` 或 `01｜标题`。
- Markdown bullet 在知乎会转成 `• 项目`，在小红书会转成 `1. 项目`。
- 表格会被压平成逐行数据。
- `[!summary]`、`[!key]` 会转成 `【摘要】`、`【核心观点】` 或 `【重点】`。
- `==重点==` 和 `**重点**` 会转成 `【重点】`，避免平台不识别 Markdown 加粗。

知乎输出：

```bash
python3 typeset.py codex-for-every-role-source.md codex-for-every-role.zhihu.txt --platform zhihu
```

小红书输出：

```bash
python3 typeset.py codex-for-every-role-source.md codex-for-every-role.xhs.txt --platform xhs
```

也可以省略 `--platform`，通过文件名自动识别：

```bash
python3 typeset.py input.md output.zhihu.txt
python3 typeset.py input.md output.xhs.txt
```

## 支持主题

可用主题定义在 `typeset.py` 的 `THEMES` 中：

| 主题 | 适合场景 |
| --- | --- |
| `modern-blue` | 默认科技博客风格 |
| `minimalist` | 正式、打印友好的简洁稿 |
| `warm-peach` | 偏文艺、温暖的文章视觉 |
| `dark-cyber` | 深色模式、技术感文章 |

示例：

```bash
python3 typeset.py codex-for-every-role-source.md codex-for-every-role.html --theme modern-blue
python3 typeset.py codex-for-every-role-source.md codex-for-every-role.rtf --theme modern-blue
```

## 输出格式选择

| 输出 | 推荐用途 | 注意事项 |
| --- | --- | --- |
| HTML | 浏览器预览、网页发布、保存完整视觉样式 | 当前输出为单文件内嵌 CSS |
| RTF | 复制到富文本编辑器、TextEdit、Word | 比 Markdown 更容易保留视觉格式 |
| 通用 Markdown | GitHub、笔记软件、文档系统 | 自动把 `[!type]` 和 `==...==` 转成兼容写法，但不包含主题色 |
| 平台纯文本 | 知乎、小红书正文编辑器 | 不依赖 Markdown 解析，复制后更稳 |
| 结构化源 Markdown | 给 `typeset.py` 渲染 | 不适合作为最终发布稿 |

## 当前示例文件

```text
codex-for-every-role-source.md  # 结构化源稿，给 typeset.py 使用
codex-for-every-role.md         # 通用 Markdown，适合复制和发布
codex-for-every-role.html       # 单文件 HTML
codex-for-every-role.rtf        # 富文本 RTF
```

## 已知限制

- `typeset.py` 会做基础结构化和渲染，但不会做深度语义判断；摘要、核心观点、金句高亮、表格重构等仍应由 `SKILL.md` 的两阶段流程完成。
- Markdown 本身是纯文本格式，复制到目标软件后能否保留格式，取决于目标软件是否解析 Markdown。
- 如果目标是最大程度保留视觉样式，优先使用 HTML 或 RTF。

## 可选增强

当前 `markdown_to_portable_markdown()` 已经会把结构化源标记转换成通用 Markdown：

```md
> [!summary] xxx
> [!key] xxx
==xxx==
```

会输出为：

```md
> **摘要**：xxx
> **核心观点**：xxx
**xxx**
```

如果未来确实需要在 Markdown 里保留接近 HTML 的视觉样式，可以额外增加一种 `styled-markdown` 输出模式，用内联 HTML 表达颜色和背景。但这种写法兼容性较差，很多平台会过滤 `style` 属性，因此不建议作为默认输出。
