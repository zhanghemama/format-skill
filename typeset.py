#!/usr/bin/env python3
import re
import subprocess
import sys

# Styling Theme Databases
THEMES = {
    'modern-blue': {
        # fonts: (english, chinese)
        'fonts': ('Helvetica', 'PingFangSC-Regular'),
        'fonts_bold': ('Helvetica-Bold', 'PingFangSC-Medium'),
        # colors: (bg, text, accent, quote_bg, highlight, strong_bg, table_header_bg, table_border)
        'colors_rtf': (
            (255, 255, 255),  # 1 bg
            (44, 62, 80),     # 2 text
            (0, 122, 255),    # 3 accent (Apple blue)
            (242, 248, 255),  # 4 quote_bg
            (255, 235, 156),  # 5 highlight
            (255, 244, 199),  # 6 strong_bg (warm amber for summary/key)
            (232, 240, 254),  # 7 table_header_bg
            (200, 210, 225)   # 8 table_border
        ),
        'css': {
            'bg': '#ffffff',
            'text': '#2c3e50',
            'accent': '#007aff',
            'quote_bg': '#f2f8ff',
            'quote_border': '#007aff',
            'highlight': '#ffeb9c',
            'strong_bg': '#fff4c7',
            'strong_border': '#f4a300',
            'table_header_bg': '#e8f0fe',
            'table_border': '#c8d2e1',
            'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif'
        }
    },
    'minimalist': {
        'fonts': ('Helvetica', 'PingFangSC-Regular'),
        'fonts_bold': ('Helvetica-Bold', 'PingFangSC-Medium'),
        'colors_rtf': (
            (255, 255, 255),
            (30, 30, 30),
            (80, 80, 80),      # gray accent
            (250, 250, 250),   # very light gray
            (255, 255, 200),   # soft light yellow
            (240, 240, 240),   # strong_bg (light gray for emphasis)
            (245, 245, 245),   # table_header_bg
            (210, 210, 210)    # table_border
        ),
        'css': {
            'bg': '#ffffff',
            'text': '#1e1e1e',
            'accent': '#505050',
            'quote_bg': '#fafafa',
            'quote_border': '#cccccc',
            'highlight': '#ffffe0',
            'strong_bg': '#f0f0f0',
            'strong_border': '#505050',
            'table_header_bg': '#f5f5f5',
            'table_border': '#d2d2d2',
            'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif'
        }
    },
    'warm-peach': {
        'fonts': ('Georgia', 'SongtiSC-Regular'),
        'fonts_bold': ('Georgia-Bold', 'SongtiSC-Bold'),
        'colors_rtf': (
            (255, 255, 255),
            (50, 40, 35),      # dark brown text
            (230, 97, 74),     # warm coral
            (255, 251, 242),   # cream bg
            (255, 228, 196),   # soft gold/bisque
            (255, 218, 185),   # strong_bg (peach puff)
            (252, 240, 220),   # table_header_bg
            (220, 200, 180)    # table_border
        ),
        'css': {
            'bg': '#ffffff',
            'text': '#322823',
            'accent': '#e6614a',
            'quote_bg': '#fffbf2',
            'quote_border': '#e6614a',
            'highlight': '#ffe4c4',
            'strong_bg': '#ffdab9',
            'strong_border': '#e6614a',
            'table_header_bg': '#fcf0dc',
            'table_border': '#dcc8b4',
            'font_family': 'Georgia, "Songti SC", "STSong", "PingFang SC", serif'
        }
    },
    'dark-cyber': {
        'fonts': ('Helvetica', 'PingFangSC-Regular'),
        'fonts_bold': ('Helvetica-Bold', 'PingFangSC-Medium'),
        'colors_rtf': (
            (30, 30, 30),      # dark bg
            (220, 220, 220),   # white/gray text
            (0, 200, 180),     # teal accent
            (45, 45, 45),      # cyber dark gray
            (50, 80, 100),     # deep blue highlight
            (40, 70, 65),      # strong_bg (deep teal)
            (38, 50, 50),      # table_header_bg
            (60, 75, 75)       # table_border
        ),
        'css': {
            'bg': '#1e1e1e',
            'text': '#dcdcdc',
            'accent': '#00c8b4',
            'quote_bg': '#2d2d2d',
            'quote_border': '#00c8b4',
            'highlight': '#325064',
            'strong_bg': '#284641',
            'strong_border': '#00c8b4',
            'table_header_bg': '#263232',
            'table_border': '#3c4b4b',
            'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", sans-serif'
        }
    }
}

# Callout type configuration: maps Obsidian-style [!type] to visual roles.
# Roles:
#   'strong' -> use strong_bg (prominent), bold body
#   'soft'   -> use quote_bg (subtle), normal body
#   'soft_italic' -> use quote_bg, italic body
CALLOUT_TYPES = {
    'summary': {'role': 'strong', 'bold': True, 'italic': False},
    'key':     {'role': 'strong', 'bold': True, 'italic': False},
    'note':    {'role': 'soft',   'bold': False, 'italic': False},
    'quote':   {'role': 'soft',   'bold': False, 'italic': True},
}

def add_cjk_spacing(text):
    """
    Inserts a single space between Chinese characters (CJK) and English letters/digits.
    """
    cjk_re = r'[\u4e00-\u9fa5]'
    latin_re = r'[a-zA-Z0-9]'
    
    text = re.sub(f'({cjk_re})({latin_re})', r'\1 \2', text)
    text = re.sub(f'({latin_re})({cjk_re})', r'\1 \2', text)
    return text

def normalize_punctuation(text):
    """
    Normalizes punctuation in Chinese contexts.
    """
    cjk_char = r'[\u4e00-\u9fa5]'
    
    text = re.sub(f'({cjk_char}),', r'\1，', text)
    text = re.sub(f',({cjk_char})', r'，\1', text)
    
    text = re.sub(rf'({cjk_char})\.', r'\1。', text)
    text = re.sub(rf'\.({cjk_char})', r'。\1', text)

    text = re.sub(f'({cjk_char}):', r'\1：', text)
    text = re.sub(f':({cjk_char})', r'：\1', text)

    text = re.sub(f'({cjk_char});', r'\1；', text)
    text = re.sub(f';({cjk_char})', r'；\1', text)

    text = re.sub(rf'({cjk_char})\!', r'\1！', text)
    text = re.sub(rf'\!({cjk_char})', r'！\1', text)

    text = re.sub(rf'({cjk_char})\?', r'\1？', text)
    text = re.sub(rf'\?({cjk_char})', r'？\1', text)
    
    text = re.sub(r'\.{3,}', '……', text)
    return text

def normalize_newlines(text):
    """
    Collapses multiple empty lines and trims trailing spaces.
    """
    lines = [line.rstrip() for line in text.splitlines()]
    
    new_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                new_lines.append('')
                prev_empty = True
        else:
            new_lines.append(line)
            prev_empty = False
            
    return '\n'.join(new_lines)

def normalize_text_content(text):
    """
    Apply CJK spacing + punctuation normalization to a plain-text segment only.
    Callers must strip structural markers first so markers are never touched.
    """
    text = add_cjk_spacing(text)
    text = normalize_punctuation(text)
    return text

# A table separator row contains only pipes, dashes, colons and spaces.
_TABLE_SEP_RE = re.compile(r'^\|?[\s:|-]+\|?$')

def normalize_md_line(line):
    """
    Normalize a single Markdown line, leaving the line's structural markers
    intact and only transforming the text content.

    Inline markers (**bold**, ==highlight==) need no special handling: their
    marker characters (* =) are neither CJK nor Latin/digits, so the spacing
    and punctuation passes never split them apart, while the text *inside*
    them is still normalized as desired.
    """
    if not line.strip():
        return line

    indent_len = len(line) - len(line.lstrip())
    indent = line[:indent_len]
    body = line[indent_len:]

    # Heading: #{1,6} + space + text
    m = HEADING_RE.match(body)
    if m:
        return f'{indent}{m.group(1)} {normalize_text_content(m.group(2))}'

    # Table row: keep pipes, normalize each non-empty cell; skip separator rows.
    if body.startswith('|'):
        if '-' in body and _TABLE_SEP_RE.match(body):
            return line
        cells = body.split('|')
        cells = [normalize_text_content(c) if c.strip() else c for c in cells]
        return indent + '|'.join(cells)

    # Blockquote / callout: preserve '>' markers and an optional [!type] tag.
    if body.startswith('>'):
        mq = re.match(r'^(>+\s?)(.*)$', body)
        prefix, rest = mq.group(1), mq.group(2)
        mc = re.match(r'^(\[!\w+\]\s*)(.*)$', rest)
        if mc:
            return indent + prefix + mc.group(1) + normalize_text_content(mc.group(2))
        return indent + prefix + normalize_text_content(rest)

    # Unordered list marker
    mu = LIST_UL_RE.match(body)
    if mu:
        return indent + body[:mu.end()] + normalize_text_content(body[mu.end():])

    # Ordered list marker
    mo = LIST_OL_RE.match(body)
    if mo:
        return indent + body[:mo.end()] + normalize_text_content(body[mo.end():])

    # Plain paragraph line
    return indent + normalize_text_content(body)

def typeset_to_markdown(text):
    text = normalize_newlines(text)
    return '\n'.join(normalize_md_line(line) for line in text.split('\n'))

def text_to_rtf_content(text):
    result = []
    for char in text:
        val = ord(char)
        if val > 127:
            result.append(f'\\uc0\\u{val} ')
        else:
            if char in '\\{}':
                result.append(f'\\{char}')
            elif char == '\n':
                result.append('\\par ')
            else:
                result.append(char)
    return ''.join(result)

def format_markdown_inline_rtf(text):
    """
    Handles inline styling like bold **text** and ==highlights== in RTF.
    """
    escaped_text = text_to_rtf_content(text)
    # Convert bold **text** -> \b text\b0
    escaped_text = re.sub(r'\*\*([^\*]+)\*\*', r'\\b \1\\b0 ', escaped_text)
    # Convert highlight ==text== -> \highlight5 text\highlight0 (Index 5 in colors: bg, text, accent, quote_bg, highlight)
    escaped_text = re.sub(r'==([^=]+)==', r'\\highlight5 \1\\highlight0 ', escaped_text)
    return escaped_text

def render_table_rtf(header, rows):
    """Render a Markdown table as RTF using \\trowd / \\cellx / \\row."""
    num_cols = max(len(header), max((len(row) for row in rows), default=0))
    if num_cols == 0:
        return ''
    total_width = 9000  # available width in twips (approximation)
    col_width = total_width // num_cols
    parts = []

    def render_row(cells, is_header):
        bg_directive = '\\clcbpat7' if is_header else ''
        row_parts = ['\\trowd\\trgaph108\\trleft0']
        for col_index in range(num_cols):
            right_edge = col_width * (col_index + 1)
            row_parts.append(
                '\\clbrdrt\\brdrs\\brdrw10\\brdrcf8'
                '\\clbrdrl\\brdrs\\brdrw10\\brdrcf8'
                '\\clbrdrb\\brdrs\\brdrw10\\brdrcf8'
                '\\clbrdrr\\brdrs\\brdrw10\\brdrcf8'
                f'{bg_directive}\\cellx{right_edge}'
            )
        bold_open = '\\b ' if is_header else ''
        bold_close = '\\b0 ' if is_header else ''
        for col_index in range(num_cols):
            cell_text = cells[col_index] if col_index < len(cells) else ''
            cell_formatted = format_markdown_inline_rtf(cell_text)
            row_parts.append(
                f'\\pard\\intbl\\f1\\fs24\\cf2 {bold_open}{cell_formatted}{bold_close}\\cell'
            )
        row_parts.append('\\row')
        return ''.join(row_parts)

    parts.append('\\pard\\par')
    parts.append(render_row(header, is_header=True))
    for row in rows:
        parts.append(render_row(row, is_header=False))
    parts.append('\\pard\\par')
    return '\n'.join(parts)

def parse_callout(block):
    """
    Parse Obsidian-style callout block.
    Returns (callout_type, content_text) or None if not a callout.
    Format:
        > [!summary] Optional title
        > content line 1
        > content line 2
    """
    lines = block.split('\n')
    if not lines or not lines[0].lstrip().startswith('>'):
        return None
    first = lines[0].lstrip()
    if first.startswith('> '):
        first = first[2:].strip()
    elif first.startswith('>'):
        first = first[1:].strip()
    match = re.match(r'^\[!(\w+)\]\s*(.*)$', first)
    if not match:
        return None
    callout_type = match.group(1).lower()
    if callout_type not in CALLOUT_TYPES:
        return None
    title = match.group(2).strip()
    content_lines = []
    if title:
        content_lines.append(title)
    for line in lines[1:]:
        line = line.strip()
        if line.startswith('> '):
            content_lines.append(line[2:].strip())
        elif line == '>':
            content_lines.append('')
        elif line.startswith('>'):
            content_lines.append(line[1:].strip())
    return callout_type, '\n'.join(content_lines)

def parse_table(block):
    """
    Parse a Markdown pipe table.
    Returns (header_cells, rows) or None if not a valid table.
    Format:
        | col1 | col2 |
        |------|------|
        | a    | b    |
    """
    lines = [ln.strip() for ln in block.split('\n') if ln.strip()]
    if len(lines) < 2:
        return None
    if not (lines[0].startswith('|') and lines[1].startswith('|')):
        return None
    # Separator row: cells must be only -, :, spaces
    sep_cells = [c.strip() for c in lines[1].strip('|').split('|')]
    if not all(re.match(r'^:?-+:?$', c) for c in sep_cells if c):
        return None
    def split_row(line):
        cells = [c.strip() for c in line.strip('|').split('|')]
        return cells
    header = split_row(lines[0])
    rows = [split_row(ln) for ln in lines[2:] if ln.startswith('|')]
    return header, rows

# Block-level parsing helpers (shared by HTML and RTF renderers)
HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
LIST_UL_RE = re.compile(r'^[-*]\s+')
LIST_OL_RE = re.compile(r'^(\d+)\.\s+')

# Heading font sizes (in RTF half-points) per level; body text is fs24.
HEADING_FS_RTF = {1: 44, 2: 36, 3: 30, 4: 26, 5: 24, 6: 22}

def classify_line(line):
    """Classify a single line into a block type for grouping."""
    s = line.strip()
    if not s:
        return 'blank'
    if HEADING_RE.match(s):
        return 'heading'
    if s.startswith('>'):
        return 'quote'
    if s.startswith('|'):
        return 'table'
    if LIST_UL_RE.match(s):
        return 'ul'
    if LIST_OL_RE.match(s):
        return 'ol'
    return 'para'

def parse_heading(line):
    """Return (level, text) for an ATX heading line."""
    m = HEADING_RE.match(line.strip())
    return len(m.group(1)), m.group(2).strip()

def split_blocks(md_text):
    """
    Split markdown into typed blocks robustly (line-based, not blank-line-based).

    Returns a list of (block_type, block_text) tuples. Unlike a naive
    split('\\n\\n'), this keeps multi-line constructs intact and tolerates blank
    lines inside lists, tables and blockquotes/callouts.
    """
    lines = md_text.split('\n')
    n = len(lines)
    blocks = []
    i = 0
    while i < n:
        t = classify_line(lines[i])
        if t == 'blank':
            i += 1
            continue
        if t == 'heading':
            blocks.append(('heading', lines[i].strip()))
            i += 1
            continue
        if t in ('quote', 'table'):
            # Gather consecutive lines of the same type, allowing single blank
            # lines in the middle (common in multi-paragraph callouts/tables).
            buf = []
            while i < n:
                ct = classify_line(lines[i])
                if ct == t:
                    buf.append(lines[i])
                    i += 1
                elif ct == 'blank':
                    j = i
                    while j < n and classify_line(lines[j]) == 'blank':
                        j += 1
                    if j < n and classify_line(lines[j]) == t:
                        i = j
                    else:
                        break
                else:
                    break
            blocks.append((t, '\n'.join(buf)))
            continue
        if t in ('ul', 'ol'):
            # Gather consecutive list items of the same type; tolerate blank
            # lines between items (loose lists) without breaking the list.
            buf = []
            while i < n:
                ct = classify_line(lines[i])
                if ct == t:
                    buf.append(lines[i])
                    i += 1
                elif ct == 'blank':
                    j = i
                    while j < n and classify_line(lines[j]) == 'blank':
                        j += 1
                    if j < n and classify_line(lines[j]) == t:
                        i = j
                    else:
                        break
                else:
                    break
            blocks.append((t, '\n'.join(buf)))
            continue
        # Paragraph: consecutive plain lines until a blank or special line.
        buf = []
        while i < n and classify_line(lines[i]) == 'para':
            buf.append(lines[i])
            i += 1
        blocks.append(('para', '\n'.join(buf)))
    return blocks

PORTABLE_CALLOUT_LABELS = {
    'summary': '摘要',
    'key': '核心观点',
    'note': '备注',
    'quote': '引用',
}

PLATFORM_ALIASES = {
    'zhihu': 'zhihu',
    'xhs': 'xhs',
    'xiaohongshu': 'xhs',
    'rednote': 'xhs',
}

def markdown_inline_to_portable(text):
    """Convert non-portable inline markers to widely supported Markdown."""
    return re.sub(r'==([^=]+)==', r'**\1**', text)

def render_portable_callout(callout_type, content):
    """Render typed callouts as ordinary blockquotes with bold labels."""
    label = PORTABLE_CALLOUT_LABELS.get(callout_type, callout_type)
    content = markdown_inline_to_portable(content)
    lines = content.split('\n') if content else ['']

    first_content = lines[0].strip() if lines else ''
    first_line = f'> **{label}**'
    first_line += f'：{first_content}' if first_content else '：'

    rendered = [first_line]
    for line in lines[1:]:
        rendered.append(f'> {line}' if line else '>')
    return '\n'.join(rendered)

def markdown_to_portable_markdown(md_text):
    """
    Convert structured Markdown used by this renderer into portable Markdown.

    Portable Markdown keeps headings, lists, blockquotes, tables, and bold text,
    but removes renderer-specific markers such as [!summary] and ==highlight==.
    """
    rendered_blocks = []

    for btype, block in split_blocks(md_text):
        block = block.strip()
        if not block:
            continue

        if btype == 'quote':
            callout = parse_callout(block)
            if callout is not None:
                callout_type, content = callout
                rendered_blocks.append(render_portable_callout(callout_type, content))
                continue

            quote_lines = []
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith('> '):
                    quote_lines.append('> ' + markdown_inline_to_portable(line[2:].strip()))
                elif line == '>':
                    quote_lines.append('>')
                elif line.startswith('>'):
                    quote_lines.append('> ' + markdown_inline_to_portable(line[1:].strip()))
            rendered_blocks.append('\n'.join(quote_lines))
            continue

        if btype == 'table':
            table_lines = []
            for line in block.split('\n'):
                if '-' in line and _TABLE_SEP_RE.match(line):
                    table_lines.append(line)
                else:
                    table_lines.append(markdown_inline_to_portable(line))
            rendered_blocks.append('\n'.join(table_lines))
            continue

        rendered_blocks.append('\n'.join(
            markdown_inline_to_portable(line) for line in block.split('\n')
        ))

    return normalize_newlines('\n\n'.join(rendered_blocks))

def normalize_platform_name(platform):
    if not platform:
        return None
    return PLATFORM_ALIASES.get(platform.lower())

def chinese_ordinal(number):
    digits = '零一二三四五六七八九'
    if 1 <= number <= 10:
        return '十' if number == 10 else digits[number]
    if 11 <= number <= 19:
        return '十' + digits[number % 10]
    if 20 <= number <= 99:
        tens, ones = divmod(number, 10)
        return digits[tens] + '十' + (digits[ones] if ones else '')
    return str(number)

def text_inline_to_platform(text):
    """Convert Markdown inline emphasis into visible plain-text markers."""
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1（\2）', text)
    text = re.sub(r'==([^=]+)==', r'【\1】', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'【\1】', text)
    text = re.sub(r'__([^_]+)__', r'【\1】', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = text.replace('\\*', '*').replace('\\_', '_')
    return text.strip()

def render_platform_heading(level, text, platform, counters):
    text = text_inline_to_platform(text)
    if level == 1:
        counters['h2'] = 0
        counters['h3'] = 0
        return text
    if level == 2:
        counters['h2'] += 1
        counters['h3'] = 0
        if platform == 'xhs':
            return f'{counters["h2"]:02d}｜{text}'
        return f'{chinese_ordinal(counters["h2"])}、{text}'
    if level == 3:
        counters['h3'] += 1
        if platform == 'xhs':
            return f'{counters["h2"]:02d}.{counters["h3"]} {text}'
        return f'{counters["h2"]}.{counters["h3"]} {text}'
    return text

def render_platform_callout(callout_type, content, platform):
    label = PORTABLE_CALLOUT_LABELS.get(callout_type, callout_type)
    if platform == 'xhs' and callout_type == 'key':
        label = '重点'
    content = text_inline_to_platform(content)
    if not content:
        return f'【{label}】'
    return f'【{label}】{content}'

def render_platform_list_item(index, text, platform):
    if platform == 'xhs':
        return f'{index}. {text}'
    return f'• {text}'

def render_platform_table(header, rows, platform):
    header = [text_inline_to_platform(cell) for cell in header]
    rows = [[text_inline_to_platform(cell) for cell in row] for row in rows]
    lines = []

    if len(header) == 2:
        for index, row in enumerate(rows, 1):
            left = row[0] if row else ''
            right = row[1] if len(row) > 1 else ''
            lines.append(render_platform_list_item(index, f'{left}：{right}', platform))
        return '\n'.join(lines)

    for index, row in enumerate(rows, 1):
        pairs = []
        for col_index, cell in enumerate(row):
            label = header[col_index] if col_index < len(header) else f'列 {col_index + 1}'
            pairs.append(f'{label}：{cell}')
        lines.append(render_platform_list_item(index, '｜'.join(pairs), platform))

    return '\n'.join(lines)

def markdown_to_platform_text(md_text, platform):
    """
    Render Markdown-like source into plain text suitable for Zhihu/Xiaohongshu.

    These platforms do not reliably parse pasted Markdown source. The output is
    therefore visible plain text: numbered headings, bracketed labels, safe list
    markers, and table rows flattened into readable lines.
    """
    platform = normalize_platform_name(platform)
    if platform not in ('zhihu', 'xhs'):
        raise ValueError(f"Unsupported platform: {platform}")

    rendered_blocks = []
    counters = {'h2': 0, 'h3': 0}

    for btype, block in split_blocks(md_text):
        block = block.strip()
        if not block:
            continue

        if btype == 'heading':
            level, text = parse_heading(block)
            rendered_blocks.append(render_platform_heading(level, text, platform, counters))
            continue

        if btype == 'quote':
            callout = parse_callout(block)
            if callout is not None:
                callout_type, content = callout
                rendered_blocks.append(render_platform_callout(callout_type, content, platform))
                continue

            lines = []
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith('> '):
                    lines.append(text_inline_to_platform(line[2:].strip()))
                elif line.startswith('>'):
                    lines.append(text_inline_to_platform(line[1:].strip()))
            quote_text = '\n'.join(line for line in lines if line)
            if quote_text:
                rendered_blocks.append(f'【引用】{quote_text}')
            continue

        if btype == 'table':
            table = parse_table(block)
            if table is not None:
                header, rows = table
                rendered_blocks.append(render_platform_table(header, rows, platform))
                continue

        if btype == 'ul':
            items = []
            index = 1
            for line in block.split('\n'):
                s = line.strip()
                m = LIST_UL_RE.match(s)
                if m:
                    items.append(render_platform_list_item(
                        index,
                        text_inline_to_platform(s[m.end():].strip()),
                        platform
                    ))
                    index += 1
            rendered_blocks.append('\n'.join(items))
            continue

        if btype == 'ol':
            items = []
            for line in block.split('\n'):
                s = line.strip()
                m = LIST_OL_RE.match(s)
                if m:
                    items.append(f'{m.group(1)}. {text_inline_to_platform(s[m.end():].strip())}')
            rendered_blocks.append('\n'.join(items))
            continue

        rendered_blocks.append('\n'.join(
            text_inline_to_platform(line) for line in block.split('\n') if line.strip()
        ))

    return normalize_newlines('\n\n'.join(block for block in rendered_blocks if block.strip()))

def markdown_to_rtf(md_text, theme_name='modern-blue'):
    """
    Converts Markdown to a gorgeous, native macOS RTF (Rich Text Format) file based on styling theme.
    """
    theme = THEMES.get(theme_name, THEMES['modern-blue'])
    font_eng, font_cjk = theme['fonts']
    font_eng_bold, font_cjk_bold = theme['fonts_bold']

    c_bg, c_txt, c_acc, c_qbg, c_hl, c_strong, c_thdr, c_tbrd = theme['colors_rtf']

    # RTF Color Table construction: \colortbl;\red[R]\green[G]\blue[B];...
    # Color indices (1-based after leading empty entry):
    # 1: bg, 2: text, 3: accent, 4: quote_bg, 5: highlight,
    # 6: strong_bg (summary/key callouts), 7: table_header_bg, 8: table_border
    colortbl = (
        f"\\red{c_bg[0]}\\green{c_bg[1]}\\blue{c_bg[2]};"
        f"\\red{c_txt[0]}\\green{c_txt[1]}\\blue{c_txt[2]};"
        f"\\red{c_acc[0]}\\green{c_acc[1]}\\blue{c_acc[2]};"
        f"\\red{c_qbg[0]}\\green{c_qbg[1]}\\blue{c_qbg[2]};"
        f"\\red{c_hl[0]}\\green{c_hl[1]}\\blue{c_hl[2]};"
        f"\\red{c_strong[0]}\\green{c_strong[1]}\\blue{c_strong[2]};"
        f"\\red{c_thdr[0]}\\green{c_thdr[1]}\\blue{c_thdr[2]};"
        f"\\red{c_tbrd[0]}\\green{c_tbrd[1]}\\blue{c_tbrd[2]};"
    )

    rtf_body = []

    for btype, block in split_blocks(md_text):
        block = block.strip()
        if not block:
            continue

        # Headings H1–H6 (accent color cf3, bold, size by level)
        if btype == 'heading':
            level, title = parse_heading(block)
            fs = HEADING_FS_RTF.get(level, 24)
            title_formatted = format_markdown_inline_rtf(title)
            rtf_body.append(f'\\par\\par \\pard\\pardirnatural\\partightenfactor0\\f1\\fs{fs}\\b\\cf3 {title_formatted}\\b0\\cf0\\f0\\fs24\\par')
            continue
        # Blockquote / typed callout
        if btype == 'quote':
            callout = parse_callout(block)
            if callout is not None:
                callout_type, content = callout
                cfg = CALLOUT_TYPES[callout_type]
                # Choose background color index based on role
                bg_idx = 6 if cfg['role'] == 'strong' else 4
                bold_open = '\\b ' if cfg['bold'] else ''
                bold_close = '\\b0 ' if cfg['bold'] else ''
                italic_open = '\\i ' if cfg['italic'] else ''
                italic_close = '\\i0 ' if cfg['italic'] else ''
                content_formatted = format_markdown_inline_rtf(content)
                rtf_body.append(
                    f'\\pard\\tx720\\li720\\ri720\\pardirnatural\\partightenfactor0'
                    f'\\f1\\fs24\\cb{bg_idx} {bold_open}{italic_open}{content_formatted}'
                    f'{italic_close}{bold_close}\\cb1\\par'
                )
                continue
            # Plain Blockquote (no callout type) — soft bg
            lines = []
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith('> '):
                    line = line[2:].strip()
                elif line == '>':
                    line = ''
                elif line.startswith('>'):
                    line = line[1:].strip()
                lines.append(line)
            quote_text = '\n'.join(lines)
            quote_formatted = format_markdown_inline_rtf(quote_text)
            rtf_body.append(f'\\pard\\tx720\\li720\\ri720\\pardirnatural\\partightenfactor0\\f1\\fs24\\cb4 {quote_formatted}\\par')
            continue
        # Markdown Table
        if btype == 'table':
            table = parse_table(block)
            if table is not None:
                header, rows = table
                rtf_body.append(render_table_rtf(header, rows))
                continue
            # Not a valid table; fall through to paragraph rendering below.
        # Unordered list (bullet character \u8226 with hanging indent)
        if btype == 'ul':
            list_items = []
            for line in block.split('\n'):
                s = line.strip()
                m = LIST_UL_RE.match(s)
                if m:
                    item_text = s[m.end():].strip()
                    item_formatted = format_markdown_inline_rtf(item_text)
                    list_items.append(f'\\pard\\tx720\\li720\\fi-360\\pardirnatural\\partightenfactor0\\f1\\fs24 \\uc0\\u8226  {item_formatted}\\par')
            rtf_body.append('\n'.join(list_items))
            continue
        # Ordered list (preserves the source numbers as a hanging label)
        if btype == 'ol':
            list_items = []
            for line in block.split('\n'):
                s = line.strip()
                m = LIST_OL_RE.match(s)
                if m:
                    num = m.group(1)
                    item_text = s[m.end():].strip()
                    item_formatted = format_markdown_inline_rtf(item_text)
                    list_items.append(f'\\pard\\tx720\\li720\\fi-360\\pardirnatural\\partightenfactor0\\f1\\fs24 {num}. {item_formatted}\\par')
            rtf_body.append('\n'.join(list_items))
            continue
        # Normal Paragraph (uses main text color cf2)
        para_formatted = format_markdown_inline_rtf(block)
        rtf_body.append(f'\\pard\\pardirnatural\\partightenfactor0\\f1\\fs24\\cf2 {para_formatted}\\par')
            
    rtf_content = '\n\n'.join(rtf_body)
    
    # Complete RTF template
    rtf_doc = f"""{{\\rtf1\\ansi\\ansicpg1252\\cocoartf2822
\\cocoatextscaling0\\cocoaplatform0{{\\fonttbl\\f0\\fswiss\\fcharset0 {font_eng};\\f1\\fnil\\fcharset134 {font_cjk};}}
{{\\colortbl;{colortbl}}}
{{\\*\\expandedcolortbl;;}}
\\paperw11900\\paperh16840\\margl1440\\margr1440\\vieww11520\\viewh8400\\viewkind0
\\cb1\\pard\\tx720\\tx1440\\tx2160\\tx2880\\tx3600\\tx4320\\tx5040\\tx5760\\tx6480\\tx7200\\tx7920\\tx8640\\pardirnatural\\partightenfactor0
{rtf_content}
}}"""
    return rtf_doc

def format_inline_html(text):
    """Apply inline bold (**text**) transform.
    Input should already be HTML-escaped for < and >.
    Highlight (==text==) is handled as a separate pass in markdown_to_html.
    """
    text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)
    return text

def render_table_html(header, rows, css):
    parts = ['<table class="typeset-table">']
    parts.append('<thead><tr>')
    for cell in header:
        parts.append(f'<th>{format_inline_html(cell)}</th>')
    parts.append('</tr></thead>')
    parts.append('<tbody>')
    for row in rows:
        parts.append('<tr>')
        for cell in row:
            parts.append(f'<td>{format_inline_html(cell)}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table>')
    return ''.join(parts)

def markdown_to_html(md_text, theme_name='modern-blue', title="Typeset Article"):
    """
    Converts simple Markdown text to highly compatible, beautifully styled HTML based on styling theme.
    Block-by-block parsing: Heading(H1-H6) -> Callout -> Blockquote -> Table -> List(ul/ol) -> Paragraph.
    """
    theme = THEMES.get(theme_name, THEMES['modern-blue'])
    css = theme['css']

    def esc(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    rendered_blocks = []

    for btype, block in split_blocks(md_text):
        block = block.strip()
        if not block:
            continue

        # Headings H1–H6 — parse structure first, escape only the text content
        if btype == 'heading':
            level, text = parse_heading(block)
            rendered_blocks.append(f'<h{level}>{format_inline_html(esc(text))}</h{level}>')
            continue
        # Blockquote / typed callout — parse on raw block (before escaping) so '>' is recognized
        if btype == 'quote':
            callout = parse_callout(block)
            if callout is not None:
                callout_type, content = callout
                cfg = CALLOUT_TYPES[callout_type]
                content_html = format_inline_html(esc(content)).replace('\n', '<br>')
                if cfg['bold']:
                    content_html = f'<strong>{content_html}</strong>'
                if cfg['italic']:
                    content_html = f'<em>{content_html}</em>'
                css_class = f'callout callout-{callout_type}'
                rendered_blocks.append(f'<div class="{css_class}">{content_html}</div>')
                continue
            # Plain Blockquote
            lines = []
            for line in block.split('\n'):
                line = line.strip()
                if line.startswith('> '):
                    lines.append(line[2:].strip())
                elif line == '>':
                    lines.append('')
                elif line.startswith('>'):
                    lines.append(line[1:].strip())
            inner = format_inline_html(esc('\n'.join(lines))).replace('\n', '<br>')
            rendered_blocks.append(f'<blockquote>{inner}</blockquote>')
            continue
        # Table
        if btype == 'table':
            table = parse_table(block)
            if table is not None:
                header, rows = table
                escaped_header = [esc(c) for c in header]
                escaped_rows = [[esc(c) for c in r] for r in rows]
                rendered_blocks.append(render_table_html(escaped_header, escaped_rows, css))
                continue
            # Not a valid table; fall through to paragraph rendering below.
        # Unordered list
        if btype == 'ul':
            items = []
            for line in block.split('\n'):
                s = line.strip()
                m = LIST_UL_RE.match(s)
                if m:
                    items.append(f'<li>{format_inline_html(esc(s[m.end():].strip()))}</li>')
            rendered_blocks.append('<ul>' + ''.join(items) + '</ul>')
            continue
        # Ordered list
        if btype == 'ol':
            items = []
            for line in block.split('\n'):
                s = line.strip()
                m = LIST_OL_RE.match(s)
                if m:
                    items.append(f'<li>{format_inline_html(esc(s[m.end():].strip()))}</li>')
            rendered_blocks.append('<ol>' + ''.join(items) + '</ol>')
            continue
        # Normal Paragraph
        para = format_inline_html(esc(block)).replace('\n', '<br>')
        rendered_blocks.append(f'<p>{para}</p>')

    html_body = '\n\n'.join(rendered_blocks)

    # Highlight pass (inline ==text==). Runs on already-escaped body so == markers are preserved.
    highlight_style = (
        f"background-color: {css['highlight']}; color: inherit; "
        "padding: 2px 4px; border-radius: 3px;"
    )
    html_body = re.sub(
        r'==([^=]+)==',
        lambda m: f'<mark style="{highlight_style}">{m.group(1)}</mark>',
        html_body
    )
    
    # Dynamic dark mode text-color handling
    accent_text = css['accent']
    border_color = css['quote_border']
    
    template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{
    font-family: {css['font_family']};
    line-height: 1.8;
    color: {css['text']};
    background-color: {css['bg']};
    max-width: 680px;
    margin: 40px auto;
    padding: 0 20px;
    font-size: 16px;
  }}
  h1 {{
    font-size: 24px;
    color: {accent_text};
    margin-bottom: 20px;
    text-align: center;
  }}
  h2 {{
    font-size: 20px;
    color: {accent_text};
    margin-top: 35px;
    margin-bottom: 18px;
    padding-bottom: 8px;
    border-bottom: 2px solid {border_color};
  }}
  h3 {{
    font-size: 18px;
    color: {accent_text};
    margin-top: 28px;
    margin-bottom: 14px;
  }}
  h4 {{
    font-size: 16px;
    color: {css['text']};
    margin-top: 24px;
    margin-bottom: 12px;
  }}
  h5 {{
    font-size: 15px;
    color: {css['text']};
    margin-top: 20px;
    margin-bottom: 10px;
  }}
  h6 {{
    font-size: 14px;
    color: {css['text']};
    margin-top: 18px;
    margin-bottom: 10px;
    opacity: 0.85;
  }}
  p {{
    margin-top: 0;
    margin-bottom: 20px;
    text-align: justify;
    word-break: break-word;
  }}
  blockquote {{
    border-left: 4px solid {border_color};
    background-color: {css['quote_bg']};
    padding: 12px 20px;
    margin: 24px 0;
    color: inherit;
    opacity: 0.9;
    border-radius: 0 6px 6px 0;
  }}
  blockquote strong {{
    color: inherit;
  }}
  .callout {{
    padding: 14px 20px;
    margin: 24px 0;
    border-radius: 6px;
    border-left: 4px solid {border_color};
    background-color: {css['quote_bg']};
    color: inherit;
  }}
  .callout-summary, .callout-key {{
    background-color: {css['strong_bg']};
    border-left-color: {css['strong_border']};
  }}
  .callout-quote {{
    font-style: italic;
  }}
  table.typeset-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 24px 0;
    font-size: 15px;
  }}
  table.typeset-table th,
  table.typeset-table td {{
    border: 1px solid {css['table_border']};
    padding: 8px 12px;
    text-align: left;
    vertical-align: top;
  }}
  table.typeset-table th {{
    background-color: {css['table_header_bg']};
    font-weight: 600;
    color: {accent_text};
  }}
  ul, ol {{
    margin-top: 0;
    margin-bottom: 20px;
    padding-left: 24px;
  }}
  li {{
    margin-bottom: 8px;
  }}
  strong {{
    color: inherit;
  }}
</style>
</head>
<body>
{html_body}
</body>
</html>
"""
    return template

USAGE = f"""Usage:
  python3 typeset.py input.md output.html --theme modern-blue
  python3 typeset.py input.md output.rtf --theme warm-peach
  python3 typeset.py input.md output.md modern-blue
  python3 typeset.py input.md output.zhihu.txt --platform zhihu
  python3 typeset.py input.md output.xhs.txt --platform xhs

Inputs:
  .md/.txt files are read as UTF-8 text.
  .rtf files are converted to plain text with macOS textutil before typesetting.
  Plain text without Markdown markers gets conservative headings and bullets.

Themes:
  {', '.join(THEMES.keys())}

Note:
  Themes affect HTML/RTF visual styling. Markdown output is portable Markdown.
  Platform output is plain text designed for pasting into Zhihu/Xiaohongshu.
"""

def read_input_text(filepath):
    """Read Markdown/plain text, or convert RTF input to plain text first."""
    if filepath.lower().endswith('.rtf'):
        try:
            result = subprocess.run(
                ['textutil', '-convert', 'txt', '-stdout', filepath],
                check=True,
                capture_output=True,
                encoding='utf-8',
                errors='replace'
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                'RTF input requires macOS textutil. Convert the RTF to .txt first, '
                'then run typeset.py on the .txt file.'
            ) from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() if exc.stderr else str(exc)
            raise RuntimeError(f'Failed to convert RTF input with textutil: {detail}') from exc
        return result.stdout

    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return f.read()

def has_markdown_structure(text):
    """Return True when the input already contains block-level Markdown."""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if (
            HEADING_RE.match(s)
            or s.startswith('>')
            or s.startswith('|')
            or LIST_UL_RE.match(s)
            or LIST_OL_RE.match(s)
        ):
            return True
    return False

def is_plain_section_heading(lines, index):
    """Heuristic for short standalone section titles in plain text."""
    s = lines[index].strip()
    if not s:
        return False
    if has_markdown_structure(s):
        return False
    if len(s) > 36:
        return False
    if re.search(r'[。！？!?；;]$', s):
        return False
    previous_blank = index == 0 or not lines[index - 1].strip()
    if not previous_blank:
        return False
    # Avoid promoting labels that are just numbers or punctuation fragments.
    return bool(re.search(r'[\u4e00-\u9fa5A-Za-z]', s))

def split_inline_list_items(items_text):
    """Split a short Chinese inline enumeration into bullet items."""
    if '、' not in items_text:
        return None
    if re.search(r'[“”"\'「」『』]', items_text):
        return None
    normalized = re.sub(r'\s*和\s*(?=[^、，。；;]+$)', '、', items_text.strip())
    items = [item.strip(' \t，,。；;') for item in normalized.split('、')]
    items = [item for item in items if item]
    if len(items) < 3:
        return None
    if any(len(item) > 24 for item in items):
        return None
    if any(re.search(r'[。；;：:]', item) for item in items):
        return None
    return items

def find_inline_list_end(after_trigger):
    """Find the end of the list portion after a trigger word."""
    delimiters = ('，并', '，同时', '，且', '。', '；', ';')
    candidates = []
    for delimiter in delimiters:
        idx = after_trigger.find(delimiter)
        if idx >= 0:
            candidates.append((idx, delimiter))
    if not candidates:
        return len(after_trigger), ''
    return min(candidates, key=lambda item: item[0])

def convert_inline_list_to_markdown_lines(line):
    """
    Convert obvious inline enumerations into Markdown bullets.

    Examples:
      包括文档、报告、表格。 -> 包括： / - 文档 / - 报告 / - 表格
      覆盖数据分析、销售和投行等场景，并... -> 覆盖： / bullets / 并...
    """
    stripped = line.strip()
    if not stripped or has_markdown_structure(stripped):
        return [line]

    for trigger in ('包括', '覆盖', '分别是', '是'):
        search_from = 0
        while True:
            pos = stripped.find(trigger, search_from)
            if pos < 0:
                break

            before = stripped[:pos]
            after = stripped[pos + len(trigger):].lstrip(' ：:')
            end_idx, delimiter = find_inline_list_end(after)
            items_text = after[:end_idx].strip()
            items = split_inline_list_items(items_text)
            if not items:
                search_from = pos + len(trigger)
                continue

            intro = f'{before}{trigger}'.rstrip('，,：: ') + '：'
            suffix = after[end_idx:]
            if delimiter and suffix.startswith(delimiter):
                suffix = suffix[len(delimiter):]
                if delimiter.startswith('，'):
                    suffix = delimiter[1:] + suffix
            suffix = suffix.strip()

            converted = [intro, '']
            converted.extend(f'- {item}' for item in items)
            if suffix:
                converted.extend(['', suffix])
            return converted

    return [line]

def auto_structure_plain_text(text):
    """
    Add basic Markdown structure to plain text.

    This is intentionally conservative: it only marks a likely document title,
    short section headings, and obvious inline enumerations. Semantic callouts,
    highlights, and tables still belong in the human/LLM decision phase
    described by SKILL.md.
    """
    text = normalize_newlines(text)
    if has_markdown_structure(text):
        return text

    lines = text.splitlines()
    first_content_index = next((i for i, line in enumerate(lines) if line.strip()), None)
    if first_content_index is None:
        return text

    out = []
    for i, line in enumerate(lines):
        s = line.strip()
        if i == first_content_index and s:
            out.append(f'# {s}')
            out.append('')
            continue
        if i != first_content_index and is_plain_section_heading(lines, i):
            if out and out[-1] != '':
                out.append('')
            out.append(f'## {s}')
            out.append('')
            continue
        out.extend(convert_inline_list_to_markdown_lines(line))

    return normalize_newlines('\n'.join(out))

def prepare_markdown_input(content):
    """Prepare raw text for the renderer without overwriting existing Markdown."""
    if has_markdown_structure(content):
        return content
    return auto_structure_plain_text(content)

def parse_cli_args(argv):
    theme = 'modern-blue'
    platform = None
    args = list(argv)

    if not args or args[0] in ('-h', '--help'):
        print(USAGE)
        sys.exit(0)

    if '--theme' in args:
        try:
            idx = args.index('--theme')
            if idx + 1 < len(args):
                theme = args[idx+1]
                # Remove --theme and its value
                args.pop(idx+1)
                args.pop(idx)
            else:
                print("Error: --theme requires a value", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            pass

    if '--platform' in args:
        try:
            idx = args.index('--platform')
            if idx + 1 < len(args):
                platform = normalize_platform_name(args[idx+1])
                if platform is None:
                    print("Error: --platform must be one of: zhihu, xhs", file=sys.stderr)
                    sys.exit(1)
                args.pop(idx+1)
                args.pop(idx)
            else:
                print("Error: --platform requires a value", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            pass

    # Friendly shorthand: python3 typeset.py input output modern-blue
    if len(args) >= 3 and args[2] in THEMES:
        theme = args[2]
        args.pop(2)

    # Friendly shorthand: python3 typeset.py input output zhihu
    if len(args) >= 3 and normalize_platform_name(args[2]):
        platform = normalize_platform_name(args[2])
        args.pop(2)

    if theme not in THEMES:
        print(f"Warning: Theme '{theme}' not found. Defaulting to 'modern-blue'.", file=sys.stderr)
        print(f"Available themes: {', '.join(THEMES.keys())}", file=sys.stderr)
        theme = 'modern-blue'

    if len(args) > 2:
        print(f"Error: Unexpected argument: {args[2]}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)

    filepath = args[0] if len(args) > 0 else None
    out_path = args[1] if len(args) > 1 else None

    if platform is None and out_path:
        lower_out = out_path.lower()
        if lower_out.endswith('.zhihu.txt'):
            platform = 'zhihu'
        elif lower_out.endswith(('.xhs.txt', '.xiaohongshu.txt', '.rednote.txt')):
            platform = 'xhs'

    if platform is not None and platform not in ('zhihu', 'xhs'):
        print("Error: --platform must be one of: zhihu, xhs", file=sys.stderr)
        sys.exit(1)

    return filepath, out_path, theme, platform

def main():
    filepath, out_path, theme, platform = parse_cli_args(sys.argv[1:])

    if filepath:
        try:
            content = prepare_markdown_input(read_input_text(filepath))
            markdown_out = typeset_to_markdown(content)
	            
            if out_path:
                if platform:
                    platform_text_out = markdown_to_platform_text(markdown_out, platform)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(platform_text_out)
                    print(f"Successfully saved {platform} platform text to {out_path}")
                elif out_path.endswith('.html'):
                    html_out = markdown_to_html(markdown_out, theme_name=theme)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(html_out)
                    print(f"Successfully typeset and saved {theme} HTML Rich Text to {out_path}")
                elif out_path.endswith('.rtf'):
                    rtf_out = markdown_to_rtf(markdown_out, theme_name=theme)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(rtf_out)
                    print(f"Successfully typeset and saved {theme} RTF Rich Text to {out_path}")
                elif out_path.endswith(('.md', '.markdown')):
                    portable_md_out = markdown_to_portable_markdown(markdown_out)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(portable_md_out)
                    print(f"Successfully typeset and saved portable Markdown to {out_path}")
                else:
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_out)
                    print(f"Successfully typeset and saved normalized text to {out_path}")
            else:
                if platform:
                    print(markdown_to_platform_text(markdown_out, platform))
                else:
                    # Print Markdown to stdout
                    print(markdown_to_portable_markdown(markdown_out))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Stream standard input
        content = sys.stdin.read()
        markdown_out = typeset_to_markdown(prepare_markdown_input(content))
        if platform:
            print(markdown_to_platform_text(markdown_out, platform), end='')
        else:
            print(markdown_to_portable_markdown(markdown_out), end='')

if __name__ == '__main__':
    main()
