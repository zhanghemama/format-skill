# Article Typesetter Skill

## Description
A specialized skill to auto-format and typeset poorly structured text and articles into standard, highly compatible Markdown, HTML, and macOS native RTF. The skill is **semantically intelligent**: it identifies summary paragraphs, hidden bullet patterns, and tabular data, and applies the right structural emphasis instead of blanket-coloring every paragraph.

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

### 表格转换
- 原文 "<前 15 字…>" 中的对比结构（A 是 X，B 是 Y，C 是 Z 形式）→ 转 Markdown 表格
- 若无明显对比结构，写 "暂无"

### Inline 高亮（==text==）
- "<完整句子或短语>"  原因：金句 / 强调点
- 控制总量：每千字不超过 3 处，避免高亮疲劳

### 不动的段落
- 大段叙述、推理、过渡段一律保持普通 <p>，不加任何背景色或 callout
```

Then **stop and wait for user confirmation or adjustment.** Do not generate the final Markdown or run the typeset script until the user approves.

### Phase 2 — Render

After the user confirms the decision list:
1. Apply only the approved structural changes to the original text.
2. Produce the structured Markdown.
3. Pass it through `typeset.py` with the requested theme to produce `.md`, `.html`, or `.rtf`.

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

### Inline 高亮

`==text==` 用于**短句或短语**的内联强调（金句、关键定义、数字），不用于整段。
- 控制总量：每千字不超过 3 处。
- 不要嵌套在 callout 内部（callout 自身已经是强调，再加 highlight 是噪声）。

---

## Styling Templates (Themes)

四种主题，每种主题都已为新的 callout 和表格定义了配色：

1. **`modern-blue`**（默认 / 科技博客）：Apple 蓝 + 暖琥珀 summary 背景。
2. **`minimalist`**（正式打印稿）：高对比深灰，summary 用浅灰区分。
3. **`warm-peach`**（文艺编辑）：暖珊瑚 + 蜜桃色 summary 背景。
4. **`dark-cyber`**（深色模式）：青色 + 深青绿 summary 背景。

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

---

## Command Line Usage

```bash
# Markdown
python3 /path/to/format-skill/typeset.py input.md output.md

# HTML (Warm Peach Theme)
python3 /path/to/format-skill/typeset.py input.md output.html --theme warm-peach

# RTF (Dark Cyber Theme)
python3 /path/to/format-skill/typeset.py input.md output.rtf --theme dark-cyber
```

`input.md` 应当是 **Phase 2 已经加好结构标记的** Markdown 文件。`typeset.py` 只负责渲染，不做语义分析。
