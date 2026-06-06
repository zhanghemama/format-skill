# Article Typesetter Skill

## Description
A specialized skill to auto-format and typeset poorly structured text and articles into standard, highly compatible Markdown, HTML, native RTF, and platform-specific outputs. The skill is **semantically intelligent**: it identifies summary paragraphs, hidden bullet patterns, and tabular data, and applies the right structural emphasis instead of blanket-coloring every paragraph.

---

## Two-Phase Workflow (MANDATORY)

To avoid producing weird, over-formatted output, the skill runs in two strict phases. **Never skip Phase 1.**

### Phase 1 — Semantic Decision List

Before writing any structured Markdown or rendering, read the source and output a **decision checklist** in this exact shape:

```
## 排版决策清单

### Callout 块（段落级强调）
- 段落 "<前 15 字…>" → [!summary]  原因：开篇定调 / 文章总结
- 段落 "<前 15 字…>" → [!key]      原因：作者核心观点
- 段落 "<前 15 字…>" → [!note]     原因：补充说明 / 旁注

### 隐式 bullet → 显式列表
- 段落 "<前 15 字…>" 后的 N 行平铺并列 → 转 bullet
  保留衔接词：首先 / 其次 / 再次 / 另外 / 此外（不删除）
- 时间线 / 阶段演进 / "标题：说明" 结构 → [label-body / bullet / table]
  渲染策略：标题单独一行，说明保留一个完整段落 / 单层 bullet / 表格
  是否拆分说明句：是 / 否（默认否，除非原文已经分行或用户要求）

### 表格转换
- 原文 "<前 15 字…>" 中的对比结构（A 是 X，B 是 Y，C 是 Z 形式）→ 转 Markdown 表格
- 若无明显对比结构，写 "暂无"

### Inline 高亮（==text==）
- "<完整句子或短语>"  原因：金句 / 强调点
- 控制总量：每千字不超过 3 处，避免高亮疲劳

### 不动的段落
- 大段叙述、推理、过渡段一律保持普通 <p>，不加任何背景色或 callout

### 文档标题判断
- 第一行 "<前 15 字…>" → 文章题目 / 正文一级标题
- 若第一行不是文章题目，平台输出使用 `--no-document-title` 或等价处理，避免强制输出《标题》

### 平台列表策略
- 小红书：一级编号，label-body 说明行使用全角缩进，不使用 `-` / `◦` / `•`
- 知乎：一级 bullet，label-body 说明行使用全角缩进，不使用第二层 bullet
- 普通 Markdown：若是 label-body 结构，使用 "- 标题" + 下一行缩进说明，不使用嵌套 bullet
- 公众号 / HTML：可保留语义列表，但避免为自然段强行拆出多条子 bullet
```

Then **stop and wait for user confirmation or adjustment.** Do not generate the final Markdown or run the typeset script until the user approves.

### Phase 2 — Render

After the user confirms the decision list:
1. Apply only the approved structural changes to the original text.
2. Produce the structured Markdown.
3. Pass it through `typeset.py` with the requested theme to produce `.md`, `.html`, or `.rtf`.
4. Run the platform QA checklist before delivery.

---

## Semantic Decision Rules

### When to use a Callout block (段落级强调)

| 用途 | 语法 | 视觉效果 | 适用场景 |
|------|------|----------|----------|
| 总结段 | `> [!summary]` | 最强背景 + 粗体 | 全文/章节的总结性段落，通常 1–3 句 |
| 核心观点 | `> [!key]` | 强背景 + 粗体 | 作者的核心论断或金句段 |
| 备注 | `> [!note]` | 浅背景 | 旁注、补充说明、人物背景介绍 |
| 引用 | `> [!quote]` | 浅背景 + 斜体 | 引用原话或他人观点 |

**重要红线 —— 大段落不要加 callout。**
- 超过 4 行的叙述性段落、推理过程、过渡段，一律不要包成 callout，否则视觉上会变成「整篇刷色」，非常突兀。
- callout 是用来**强调短而关键的段落**的，不是装饰段落的背景。
- 一篇文章通常 0–2 个 `[!summary]`、0–3 个 `[!key]` 就够了，超过这个量级要重新审视。

### 隐式 bullet → 显式列表

当原文呈现「冒号 + 多个并列项」的形态时，转 bullet：
- 触发信号：句子以 `：` 结尾，后续 3+ 行结构相似（动宾结构 / 名词短语）。
- **衔接词保留规则（硬约束）**：转 bullet 时，"首先 / 其次 / 再次 / 另外 / 此外 / 同时 / 而且 / 因此 / 所以 / 然后 / 接着 / 最后" 等连接词必须保留在 bullet 内文，**不允许删除**。
- 例：原文 `首先 A。其次 B。再次 C。` → bullet:
  ```
  - 首先 A
  - 其次 B
  - 再次 C
  ```
- 错误示范（删了衔接词）：
  ```
  - A
  - B
  - C
  ```

### Label-body 结构（标题行 + 说明段）

当原文呈现「短标签 / 时间段 / 阶段名 + 一段说明」时，优先使用 **label-body**，而不是嵌套 bullet 或表格。

适用信号：
- 时间线：`2023-2025 年：聊天机器人` 后面跟一段解释。
- 阶段 / 跨越：`跨越一：生产力大爆发` 后面跟一段解释。
- 判断项：`审查成为瓶颈` 后面跟一段解释。

默认输出形态：
```text
• 2023-2025 年：聊天机器人
　　利用早期聊天机器人协助部分流程，例如生成简短的代码片段。从最初的人类手动复制并粘贴到文本编辑器中，到后期逐步演变为补全和可以写一些代码。
```

约束：
- **标题和说明可以分行，但说明段不要再拆成多条 bullet。**
- 如果原文说明是一个自然段，渲染后仍保持一个自然段。
- 不要为了视觉层级把原文连续句子拆成多行。
- 只有当原文已经逐行列出，或用户明确要求细分时，才使用嵌套 bullet。
- 不要把 label-body 强行转成表格，除非用户明确要求或确实存在 N 个对象 × M 个属性的稳定对比。

平台渲染建议：
```text
小红书：
1. 2023-2025 年：聊天机器人
　　说明段保持一段，不加 bullet

知乎：
• 2023-2025 年：聊天机器人
　　说明段保持一段，不加 bullet

普通 Markdown：
- 2023-2025 年：聊天机器人
  说明段保持一段，不加嵌套 bullet
```

反例：
```text
• 2023-2025 年：聊天机器人
  • 利用早期聊天机器人协助部分流程...
  • 从最初的人类手动复制...
```

反例原因：知乎 / 小红书编辑器会把二级列表渲成额外圆点；用户看到的是双重 bullet，信息层级反而变乱。

### 表格转换

当原文呈现「N 个对象 × M 个相同属性」的对比结构时，转表格：
- 触发信号：同一段内出现 3+ 次「X 是 ...，Y 是 ...」「X 的 a 是…，b 是…」这种模板化复述。
- **衔接词保留规则同样适用**：若改写为表格会强行删除原文动词或连接词，宁可不转。
- Markdown 语法：
  ```
  | 项目 | 描述   | 备注 |
  |------|--------|------|
  | A    | 内容 1 | …    |
  | B    | 内容 2 | …    |
  ```

### 文档标题判断

平台输出通常会把 H1 当作文章题目：
- 小红书 / 知乎纯文本：`# 标题` → `《标题》`
- HTML / Markdown：`# 标题` 保留为一级标题

因此在 Phase 1 必须判断第一行身份：
- 若第一行是整篇文章题目：保留为 H1。
- 若第一行只是正文中的一级标题：不要强行输出《标题》，应使用 `--no-document-title` 或把它降级为章节标题。

示例：
```text
AI 记忆系统全面升级：Dreaming V3 和 Chronicle 来了

🛠 核心升级
```
第一行是文章题目，`🛠 核心升级` 是正文标题。

```text
🛠 核心升级
这次的记忆能力飞跃...
```
第一行更可能是正文一级标题；若用户没有提供文章题目，平台输出不要自动包成《🛠 核心升级》。

### Inline 高亮

`==text==` 用于**短句或短语**的内联强调（金句、关键定义、数字），不用于整段。
- 控制总量：每千字不超过 3 处。
- 不要嵌套在 callout 内部（callout 自身已经是强调，再加 highlight 是噪声）。

---

## Styling Templates (Themes)

主题都已为 callout、表格、链接、代码块、分隔线和图片定义了配色：

1. **`modern-blue`**（默认 / 科技博客）：Apple 蓝 + 暖琥珀 summary 背景。
2. **`minimalist`**（正式打印稿）：高对比深灰，summary 用浅灰区分。
3. **`warm-peach`**（文艺编辑）：暖珊瑚 + 蜜桃色 summary 背景。
4. **`dark-cyber`**（深色模式）：青色 + 深青绿 summary 背景。
5. **`github-light`**（技术文档）：接近 GitHub 阅读体验。
6. **`serif-print`**（打印长文）：衬线字体、打印友好。

---

## Universal Constraints

### 1. Zero Text Modification (CRITICAL)
- 严禁改写、改述、总结、增删任何**实词**。
- 允许的变更仅限于：空白、换行、标点风格（半角 → 全角）、Markdown 结构标记（`##`、`>`、`- `、`| ... |`、`==...==`、`> [!type]`）。
- **衔接词不允许删除**（见上）。

### 2. CJK / 西文混排空格
- 中文字符与英文字母、数字、拉丁符号之间插入一个空格。
  - 正确：`Josh Pigford 是 Baremetrics 的创始人`
  - 错误：`Josh Pigford是Baremetrics的创始人`
- CJK 全角标点与英文字母 / 数字之间**不**加空格。

### 3. 标点全角化
- 中文语境下使用全角标点（`，。：；！？`）。
- 三个及以上半角句点 `...` → 中文省略号 `……`。

### 4. 段落与换行
- 段落之间空一行。
- 合并 PDF 复制造成的句中断行。
- 不要把原文一个自然段拆成多条 bullet 或多行说明，除非原文已分行或用户明确要求。
- label-body 的标题和说明可以分为两行；说明本身保持一个自然段。

---

## Platform Rendering Rules

### 小红书 (`xhs`)

- 文章题目可用 `《标题》`。
- 章节标题使用 `01｜标题`。
- 一级列表使用 `1. 2. 3.`。
- label-body 说明行使用全角缩进 `　　`，不要使用 `-`、`•`、`◦`。
- 避免嵌套列表；小红书编辑器可能自动生成圆点，手写符号会出现双重 bullet。

### 知乎 (`zhihu`)

- 文章题目可用 `《标题》`。
- 章节标题使用 `一、标题`。
- 一级列表使用 `•`。
- label-body 说明行使用全角缩进 `　　`，不要使用第二层 `•`。
- 避免颜色 / 背景作为核心信息，知乎编辑器可能清理样式。

### 普通 Markdown

- 标准段落、标题、引用和加粗保持 Markdown 语义。
- 对 label-body，不要使用嵌套 bullet；使用：
  ```md
  - 标题
    说明段保持一段
  ```
- 如果需要真正的多级列表，必须是原文已有并列层级，或用户明确要求。

### 公众号 (`wechat`)

- 使用内联 HTML 输出。
- 可以保留视觉 callout 和列表，但不要把自然段强行拆成多个子 bullet。
- 若从浏览器复制渲染内容到公众号编辑器，优先检查列表缩进、标题层级和 callout 背景是否被保留。

---

## Platform QA Checklist

交付前必须抽查最终输出，而不是只看源 Markdown：

- 是否出现重复编号：`01｜1️⃣`、`一、1.`、`01｜一、`。
- 第一行是否被错误包成《标题》；若不是文章题目，是否已使用 `--no-document-title` 或等价处理。
- 是否出现双重 bullet：`•` 下又有 `•`，或编辑器会显示圆点 + `-` / `◦`。
- label-body 说明是否保持一个自然段，没有被拆成多条 bullet。
- 二级标题和说明是否粘连在同一行；若用户需要标题 / 内容分开，应为标题一行、说明一行。
- 是否把适合 label-body 的阶段说明误转成表格，导致信息过密。
- 是否有平台特化符号污染其它版本，例如把小红书缩进符号带进普通 Markdown。
- 是否保留了原文实词，未改写、删减、扩写内容。

---

## Command Line Usage

```bash
# Markdown
python3 /path/to/format-skill/typeset.py input.md output.md

# HTML (Warm Peach Theme)
python3 /path/to/format-skill/typeset.py input.md output.html --theme warm-peach

# HTML title override
python3 /path/to/format-skill/typeset.py input.md output.html --theme github-light --title "Custom Title"

# RTF (Dark Cyber Theme)
python3 /path/to/format-skill/typeset.py input.md output.rtf --theme dark-cyber

# Platform outputs
python3 /path/to/format-skill/typeset.py input.md output.zhihu.txt --platform zhihu
python3 /path/to/format-skill/typeset.py input.md output.zhihu.html --platform zhihu-html
python3 /path/to/format-skill/typeset.py input.md output.xhs.txt --platform xhs
python3 /path/to/format-skill/typeset.py input.md output.xhs.txt --platform xhs --no-document-title
python3 /path/to/format-skill/typeset.py input.md output.feishu.md --platform feishu
python3 /path/to/format-skill/typeset.py input.md output.feishu.html --platform feishu-html
python3 /path/to/format-skill/typeset.py input.md output.wechat.html --platform wechat
python3 /path/to/format-skill/typeset.py input.md output.notion.md --platform notion
python3 /path/to/format-skill/typeset.py input.md output.notion.html --platform notion-html
```

知乎会清理粘贴进编辑器的颜色、背景和边框样式。`zhihu-html` 只承诺保留标题、列表、表格、引用块和重点加粗，不把主题色作为核心效果。
Notion 和飞书如果直接粘贴 Markdown 源码，可能不会自动解析 `**粗体**`；需要粘贴后保留富文本时，优先生成 `notion-html` / `feishu-html`，打开 HTML 后复制渲染内容。

`input.md` 应当是 **Phase 2 已经加好结构标记的** Markdown 文件。`typeset.py` 只负责基础结构化和渲染，不做摘要、核心观点、金句等深度语义判断。

Renderer notes:
- Markdown parsing is handled by `markdown-it-py`, so links, images, inline code, fenced code blocks, strikethrough, nested lists, task lists, tables, and horizontal rules are supported.
- Zhihu/Notion/Feishu rich HTML output is compact inline HTML for copying rendered browser content into platform editors; emphasis should use semantic bold instead of relying on color or background fills.
- WeChat output is inline-styled HTML without a `<style>` block.
- RTF input prefers macOS `textutil`, with `striprtf` fallback on other environments.
- RTF image output is `[图片：alt]` placeholder in the current version.
