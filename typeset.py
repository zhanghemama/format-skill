#!/usr/bin/env python3
import html
import re
import subprocess
import sys

from markdown_it import MarkdownIt
from markdown_it.token import Token

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
            'code_bg': '#f5f7fb',
            'code_text': '#1f2937',
            'link_color': '#006adc',
            'hr_color': '#c8d2e1',
            'img_caption': '#5f6f83',
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
            'code_bg': '#f6f6f6',
            'code_text': '#202020',
            'link_color': '#404040',
            'hr_color': '#d2d2d2',
            'img_caption': '#666666',
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
            'code_bg': '#fff6ea',
            'code_text': '#4a342b',
            'link_color': '#d64f3c',
            'hr_color': '#e7c7ad',
            'img_caption': '#7a6258',
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
            'code_bg': '#262b2f',
            'code_text': '#e8f5f2',
            'link_color': '#54e7d4',
            'hr_color': '#3c4b4b',
            'img_caption': '#aab8b6',
            'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", sans-serif'
        }
    },
    'github-light': {
        'fonts': ('Helvetica', 'PingFangSC-Regular'),
        'fonts_bold': ('Helvetica-Bold', 'PingFangSC-Medium'),
        'colors_rtf': (
            (255, 255, 255),
            (36, 41, 47),
            (9, 105, 218),
            (246, 248, 250),
            (255, 245, 176),
            (221, 244, 255),
            (246, 248, 250),
            (208, 215, 222)
        ),
        'css': {
            'bg': '#ffffff',
            'text': '#24292f',
            'accent': '#0969da',
            'quote_bg': '#f6f8fa',
            'quote_border': '#d0d7de',
            'highlight': '#fff5b1',
            'strong_bg': '#ddf4ff',
            'strong_border': '#0969da',
            'table_header_bg': '#f6f8fa',
            'table_border': '#d0d7de',
            'code_bg': '#f6f8fa',
            'code_text': '#24292f',
            'link_color': '#0969da',
            'hr_color': '#d0d7de',
            'img_caption': '#57606a',
            'font_family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif'
        }
    },
    'serif-print': {
        'fonts': ('Georgia', 'SongtiSC-Regular'),
        'fonts_bold': ('Georgia-Bold', 'SongtiSC-Bold'),
        'colors_rtf': (
            (255, 255, 255),
            (32, 31, 29),
            (92, 65, 40),
            (248, 248, 246),
            (255, 241, 184),
            (247, 232, 201),
            (244, 241, 236),
            (205, 197, 186)
        ),
        'css': {
            'bg': '#ffffff',
            'text': '#201f1d',
            'accent': '#5c4128',
            'quote_bg': '#f8f8f6',
            'quote_border': '#a58b72',
            'highlight': '#fff1b8',
            'strong_bg': '#f7e8c9',
            'strong_border': '#8a633f',
            'table_header_bg': '#f4f1ec',
            'table_border': '#cdc5ba',
            'code_bg': '#f5f3ef',
            'code_text': '#2d2926',
            'link_color': '#684a2f',
            'hr_color': '#cdc5ba',
            'img_caption': '#6f675e',
            'font_family': 'Georgia, "Times New Roman", "Songti SC", "STSong", "PingFang SC", serif'
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

CALLOUT_RE = re.compile(r'^\[!(\w+)\]\s*')
TASK_RE = re.compile(r'^\[([ xX])\]\s+')
HIGHLIGHT_RE = re.compile(r'==([^=]+)==')

def build_parser():
    """Build the CommonMark/GFM parser used by the new token pipeline."""
    return (
        MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
        .enable(["table", "strikethrough"])
    )

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
    text = text.replace('\u2028', '\n').replace('\u2029', '\n')
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

def _container_end(tokens, start_index):
    """Return the inclusive close-token index for a block token."""
    level = 0
    for index in range(start_index, len(tokens)):
        level += tokens[index].nesting
        if index > start_index and level == 0:
            return index
    return len(tokens) - 1

def _first_inline_index(tokens, start_index, end_index):
    for index in range(start_index + 1, end_index):
        if tokens[index].type == 'inline':
            return index
    return None

def _is_inside_open_token(tokens, index, token_type):
    depth = 0
    for current in reversed(tokens[:index]):
        if current.type == token_type.replace('_open', '_close'):
            depth += 1
        elif current.type == token_type:
            if depth == 0:
                return True
            depth -= 1
    return False

def _first_text_child(inline_token):
    if not inline_token.children:
        return None
    first_child = inline_token.children[0]
    return first_child if first_child.type == 'text' else None

def _refresh_inline_content(inline_token):
    if not inline_token.children:
        inline_token.content = ''
        return
    inline_token.content = ''.join(
        child.content for child in inline_token.children
        if child.type in ('text', 'code_inline', 'html_inline')
    )

def _make_text_token(content, base_token):
    token = Token('text', '', 0)
    token.content = content
    token.level = base_token.level
    return token

def _make_mark_token(token_type, nesting, base_token):
    token = Token(token_type, 'mark', nesting)
    token.markup = '=='
    token.level = base_token.level
    return token

def _make_strong_token(token_type, nesting, base_token):
    token = Token(token_type, 'strong', nesting)
    token.markup = '**'
    token.level = base_token.level
    return token

def _wrap_inline_children_in_strong(inline_token):
    if not inline_token.children:
        return
    inline_token.children = [
        _make_strong_token('strong_open', 1, inline_token),
        *inline_token.children,
        _make_strong_token('strong_close', -1, inline_token),
    ]
    _refresh_inline_content(inline_token)

def _transform_text_child(child):
    """Normalize a text token and split ==highlight== into mark tokens."""
    pieces = []
    cursor = 0
    for match in HIGHLIGHT_RE.finditer(child.content):
        before = child.content[cursor:match.start()]
        if before:
            pieces.append(_make_text_token(normalize_text_content(before), child))
        pieces.append(_make_mark_token('mark_open', 1, child))
        pieces.append(_make_text_token(normalize_text_content(match.group(1)), child))
        pieces.append(_make_mark_token('mark_close', -1, child))
        cursor = match.end()

    after = child.content[cursor:]
    if after:
        pieces.append(_make_text_token(normalize_text_content(after), child))

    if pieces:
        return pieces

    child.content = normalize_text_content(child.content)
    return [child] if child.content else []

def _transform_inline(inline_token):
    if not inline_token.children:
        return

    transformed = []
    for child in inline_token.children:
        if child.type == 'text':
            transformed.extend(_transform_text_child(child))
        else:
            transformed.append(child)

    inline_token.children = transformed
    _refresh_inline_content(inline_token)

def _transform_callout(tokens, blockquote_index):
    end_index = _container_end(tokens, blockquote_index)
    inline_index = _first_inline_index(tokens, blockquote_index, end_index)
    if inline_index is None:
        return

    first_child = _first_text_child(tokens[inline_index])
    if first_child is None:
        return

    match = CALLOUT_RE.match(first_child.content)
    if not match:
        return

    callout_type = match.group(1).lower()
    if callout_type not in CALLOUT_TYPES:
        return

    tokens[blockquote_index].meta['callout'] = callout_type
    first_child.content = first_child.content[match.end():]
    _refresh_inline_content(tokens[inline_index])

def _transform_task_item(tokens, list_item_index):
    end_index = _container_end(tokens, list_item_index)
    inline_index = _first_inline_index(tokens, list_item_index, end_index)
    if inline_index is None:
        return

    first_child = _first_text_child(tokens[inline_index])
    if first_child is None:
        return

    match = TASK_RE.match(first_child.content)
    if not match:
        return

    tokens[list_item_index].meta['task'] = {'checked': match.group(1).lower() == 'x'}
    first_child.content = first_child.content[match.end():]
    _refresh_inline_content(tokens[inline_index])

def transform_tokens(tokens):
    """Apply Article Typesetter additions on top of markdown-it-py's token stream."""
    for index, token in enumerate(tokens):
        if token.type == 'blockquote_open':
            _transform_callout(tokens, index)
        elif token.type == 'list_item_open':
            _transform_task_item(tokens, index)

    for token in tokens:
        if token.type == 'inline':
            _transform_inline(token)

    return tokens

def parse_markdown_tokens(text, parser=None):
    """Parse Markdown and apply token-level transformations."""
    md = parser or build_parser()
    tokens = md.parse(text)
    return transform_tokens(tokens)

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

def render_table_rtf_cells(header, rows):
    """Render already-formatted RTF cell contents as a table."""
    num_cols = max(len(header), max((len(row) for row in rows), default=0))
    if num_cols == 0:
        return ''

    total_width = 9000
    col_width = total_width // num_cols
    parts = ['\\pard\\par']

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
            row_parts.append(
                f'\\pard\\intbl\\f1\\fs24\\cf2 {bold_open}{cell_text}{bold_close}\\cell'
            )
        row_parts.append('\\row')
        return ''.join(row_parts)

    parts.append(render_row(header, is_header=True))
    for row in rows:
        parts.append(render_row(row, is_header=False))
    parts.append('\\pard\\par')
    return '\n'.join(parts)

def inline_tokens_to_rtf(children):
    if not children:
        return ''

    parts = []
    link_stack = []
    for child in children:
        if child.type == 'text':
            parts.append(text_to_rtf_content(child.content))
        elif child.type == 'code_inline':
            parts.append(f'\\f2\\fs22\\cf3 {text_to_rtf_content(child.content)}\\cf2\\f1\\fs24 ')
        elif child.type == 'softbreak':
            parts.append('\\line ')
        elif child.type == 'hardbreak':
            parts.append('\\line ')
        elif child.type == 'strong_open':
            parts.append('\\b ')
        elif child.type == 'strong_close':
            parts.append('\\b0 ')
        elif child.type == 'em_open':
            parts.append('\\i ')
        elif child.type == 'em_close':
            parts.append('\\i0 ')
        elif child.type == 's_open':
            parts.append('\\strike ')
        elif child.type == 's_close':
            parts.append('\\strike0 ')
        elif child.type == 'mark_open':
            parts.append('\\highlight5 ')
        elif child.type == 'mark_close':
            parts.append('\\highlight0 ')
        elif child.type == 'link_open':
            link_stack.append(child.attrGet('href') or '')
            parts.append('\\cf3 ')
        elif child.type == 'link_close':
            href = link_stack.pop() if link_stack else ''
            if href:
                parts.append(f'\\cf2 {text_to_rtf_content(" (" + href + ")")}')
            else:
                parts.append('\\cf2 ')
        elif child.type == 'image':
            alt = child.content or child.attrGet('alt') or '图片'
            parts.append(text_to_rtf_content(f'[图片：{alt}]'))
        elif child.content:
            parts.append(text_to_rtf_content(child.content))
    return ''.join(parts)

def _inline_tokens_to_plain_text(children):
    if not children:
        return ''
    parts = []
    for child in children:
        if child.type in ('text', 'code_inline', 'image'):
            parts.append(child.content)
    return ''.join(parts)

def _collect_table_rtf(tokens, start_index):
    end_index = _container_end(tokens, start_index)
    rows = []
    current_row = None
    index = start_index + 1

    while index < end_index:
        token = tokens[index]
        if token.type == 'tr_open':
            current_row = []
        elif token.type == 'tr_close':
            if current_row is not None:
                rows.append(current_row)
            current_row = None
        elif token.type in ('th_open', 'td_open') and current_row is not None:
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            cell_text = ''
            if inline_index is not None:
                cell_text = inline_tokens_to_rtf(tokens[inline_index].children)
            current_row.append(cell_text)
        index += 1

    header = rows[0] if rows else []
    body_rows = rows[1:] if len(rows) > 1 else []
    return header, body_rows, end_index

def _collect_plain_rtf_lines(tokens):
    lines = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.type in ('paragraph_open', 'heading_open'):
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            if inline_index is not None:
                lines.append(inline_tokens_to_rtf(tokens[inline_index].children))
            index = _container_end(tokens, index) + 1
            continue
        if token.type in ('bullet_list_open', 'ordered_list_open'):
            rendered, end_index = _render_list_rtf(tokens, index, depth=1)
            lines.append(rendered)
            index = end_index + 1
            continue
        if token.type in ('fence', 'code_block'):
            lines.append(text_to_rtf_content(token.content.rstrip('\n')))
        index += 1
    return lines

def _render_blockquote_rtf(tokens, start_index):
    end_index = _container_end(tokens, start_index)
    callout_type = tokens[start_index].meta.get('callout')
    lines = _collect_plain_rtf_lines(tokens[start_index + 1:end_index])
    content = '\\par '.join(line for line in lines if line)

    cfg = CALLOUT_TYPES.get(callout_type or 'note', CALLOUT_TYPES['note'])
    bold_open = '\\b ' if cfg['bold'] else ''
    bold_close = '\\b0 ' if cfg['bold'] else ''
    italic_open = '\\i ' if cfg['italic'] else ''
    italic_close = '\\i0 ' if cfg['italic'] else ''

    rendered = (
        f'\\pard\\tx720\\li720\\ri720\\pardirnatural\\partightenfactor0'
        f'\\f1\\fs24\\cf2 {bold_open}{italic_open}'
        f'{content}'
        f'{italic_close}{bold_close}\\par'
    )
    return rendered, end_index

def _render_list_rtf(tokens, start_index, depth=0):
    end_index = _container_end(tokens, start_index)
    ordered = tokens[start_index].type == 'ordered_list_open'
    start_number = tokens[start_index].attrGet('start')
    number = int(start_number) if start_number else 1
    rendered = []
    index = start_index + 1
    li = 720 + depth * 360

    while index < end_index:
        token = tokens[index]
        if token.type != 'list_item_open':
            index += 1
            continue

        item_end = _container_end(tokens, index)
        inline_index = _first_inline_index(tokens, index, item_end)
        item_text = inline_tokens_to_rtf(tokens[inline_index].children) if inline_index is not None else ''

        task = token.meta.get('task')
        if task is not None:
            marker = '☑' if task.get('checked') else '☐'
        elif ordered:
            marker = f'{number}.'
        else:
            marker = '•'

        rendered.append(
            f'\\pard\\tx{li}\\li{li}\\fi-360\\pardirnatural\\partightenfactor0'
            f'\\f1\\fs24\\cf2 {text_to_rtf_content(marker)} {item_text}\\par'
        )
        number += 1

        child_index = index + 1
        while child_index < item_end:
            child = tokens[child_index]
            if child.type in ('bullet_list_open', 'ordered_list_open'):
                nested, nested_end = _render_list_rtf(tokens, child_index, depth + 1)
                rendered.append(nested)
                child_index = nested_end + 1
                continue
            child_index += 1

        index = item_end + 1

    return '\n'.join(rendered), end_index

def _render_code_rtf(token):
    lines = token.content.rstrip('\n').split('\n') if token.content else ['']
    rendered = [
        '\\pard\\li360\\ri360\\pardirnatural\\partightenfactor0\\f2\\fs22\\cf3 '
        + text_to_rtf_content(line)
        + '\\par'
        for line in lines
    ]
    rendered.append('\\cf2\\f1\\fs24')
    return '\n'.join(rendered)

def render_rtf_tokens(tokens):
    parts = []
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token.type == 'heading_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            title = inline_tokens_to_rtf(tokens[inline_index].children) if inline_index is not None else ''
            level = int(token.tag[1]) if token.tag.startswith('h') else 1
            fs = HEADING_FS_RTF.get(level, 24)
            parts.append(
                f'\\par\\par \\pard\\pardirnatural\\partightenfactor0'
                f'\\f1\\fs{fs}\\b\\cf3 {title}\\b0\\cf2\\f1\\fs24\\par'
            )
            index = _container_end(tokens, index) + 1
            continue

        if token.type == 'paragraph_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            text = inline_tokens_to_rtf(tokens[inline_index].children) if inline_index is not None else ''
            parts.append(f'\\pard\\pardirnatural\\partightenfactor0\\f1\\fs24\\cf2 {text}\\par')
            index = _container_end(tokens, index) + 1
            continue

        if token.type == 'blockquote_open':
            rendered, end_index = _render_blockquote_rtf(tokens, index)
            parts.append(rendered)
            index = end_index + 1
            continue

        if token.type in ('bullet_list_open', 'ordered_list_open'):
            rendered, end_index = _render_list_rtf(tokens, index)
            parts.append(rendered)
            index = end_index + 1
            continue

        if token.type == 'table_open':
            header, rows, end_index = _collect_table_rtf(tokens, index)
            parts.append(render_table_rtf_cells(header, rows))
            index = end_index + 1
            continue

        if token.type in ('fence', 'code_block'):
            parts.append(_render_code_rtf(token))
            index += 1
            continue

        if token.type == 'hr':
            parts.append('\\pard\\qc\\cf3 - - -\\cf2\\par')
            index += 1
            continue

        index += 1

    return '\n\n'.join(part for part in parts if part)

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

PLATFORM_ALIASES = {
    'zhihu': 'zhihu',
    'zhihu-html': 'zhihu-html',
    'zhihu_html': 'zhihu-html',
    'zhihu-rich': 'zhihu-html',
    'zhihu_rich': 'zhihu-html',
    'zhihuhtml': 'zhihu-html',
    'xhs': 'xhs',
    'xiaohongshu': 'xhs',
    'rednote': 'xhs',
    'feishu': 'feishu',
    'lark': 'feishu',
    'wechat': 'wechat',
    'weixin': 'wechat',
    'wx': 'wechat',
    'gongzhonghao': 'wechat',
    'notion': 'notion',
}

def markdown_inline_to_portable(text):
    """Convert non-portable inline markers to widely supported Markdown."""
    return re.sub(r'==([^=]+)==', r'**\1**', text)

def render_portable_callout(callout_type, content):
    """Render typed callouts as ordinary unlabeled blockquotes."""
    content = markdown_inline_to_portable(content)
    lines = content.split('\n') if content else ['']

    rendered = []
    for line in lines:
        rendered.append(f'> {line}' if line else '>')
    return '\n'.join(rendered)

def markdown_to_portable_markdown(md_text):
    """
    Convert structured Markdown into portable GFM.

    Standard Markdown/GFM structures are preserved. Article Typesetter private
    markers are downgraded: typed callouts become ordinary blockquotes, and
    ==highlight== becomes bold text.
    """
    return render_portable_markdown(parse_markdown_tokens(md_text))

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
    text = re.sub(r'==([^=]+)==', r'「\1」', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'「\1」', text)
    text = re.sub(r'__([^_]+)__', r'「\1」', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = text.replace('\\*', '*').replace('\\_', '_')
    return text.strip()

def render_platform_heading(level, text, platform, counters):
    text = text_inline_to_platform(text)
    if level == 1:
        counters['h2'] = 0
        counters['h3'] = 0
        return f'《{text}》'
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
    content = text_inline_to_platform(content)
    return content

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

def inline_tokens_to_platform_text(children, platform):
    if not children:
        return ''

    parts = []
    link_stack = []
    for child in children:
        if child.type == 'text':
            parts.append(child.content)
        elif child.type == 'code_inline':
            parts.append(child.content)
        elif child.type in ('strong_open', 'mark_open'):
            parts.append('「')
        elif child.type in ('strong_close', 'mark_close'):
            parts.append('」')
        elif child.type == 'link_open':
            link_stack.append(child.attrGet('href') or '')
        elif child.type == 'link_close':
            href = link_stack.pop() if link_stack else ''
            if href:
                parts.append(f'（{href}）')
        elif child.type == 'image':
            alt = child.content or child.attrGet('alt') or '图片'
            parts.append(f'[图片：{alt}]')
        elif child.content:
            parts.append(child.content)
    return ''.join(parts).strip()

def _collect_table_for_platform(tokens, start_index, platform):
    end_index = _container_end(tokens, start_index)
    rows = []
    current_row = None
    index = start_index + 1

    while index < end_index:
        token = tokens[index]
        if token.type == 'tr_open':
            current_row = []
        elif token.type == 'tr_close':
            if current_row is not None:
                rows.append(current_row)
            current_row = None
        elif token.type in ('th_open', 'td_open') and current_row is not None:
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            cell_text = ''
            if inline_index is not None:
                cell_text = inline_tokens_to_platform_text(tokens[inline_index].children, platform)
            current_row.append(cell_text)
        index += 1

    header = rows[0] if rows else []
    body_rows = rows[1:] if len(rows) > 1 else []
    return header, body_rows, end_index

def _render_code_platform(token):
    lines = token.content.rstrip('\n').split('\n') if token.content else ['']
    return ['    ' + line for line in lines]

def _render_list_platform(tokens, start_index, platform, indent=0):
    end_index = _container_end(tokens, start_index)
    ordered = tokens[start_index].type == 'ordered_list_open'
    start_number = tokens[start_index].attrGet('start')
    number = int(start_number) if start_number else 1
    rendered = []
    index = start_index + 1

    while index < end_index:
        token = tokens[index]
        if token.type != 'list_item_open':
            index += 1
            continue

        item_end = _container_end(tokens, index)
        inline_index = _first_inline_index(tokens, index, item_end)
        text = ''
        if inline_index is not None:
            text = inline_tokens_to_platform_text(tokens[inline_index].children, platform)

        task = token.meta.get('task')
        if task is not None:
            task_box = '■' if task.get('checked') else '□'
            text = f'{task_box} {text}'.strip()

        if ordered:
            line = f'{number}. {text}'
        else:
            line = render_platform_list_item(number, text, platform)
        rendered.append(' ' * indent + line)
        number += 1

        child_index = index + 1
        while child_index < item_end:
            child = tokens[child_index]
            if child.type in ('bullet_list_open', 'ordered_list_open'):
                nested, nested_end = _render_list_platform(tokens, child_index, platform, indent + 2)
                rendered.extend(nested)
                child_index = nested_end + 1
                continue
            child_index += 1

        index = item_end + 1

    return rendered, end_index

def _render_blockquote_platform(tokens, start_index, platform, counters, indent=0):
    end_index = _container_end(tokens, start_index)
    inner_lines = _render_blocks_platform(tokens[start_index + 1:end_index], platform, counters, indent=0)
    inner_text = normalize_newlines('\n'.join(_trim_blank_lines(inner_lines)))
    callout_type = tokens[start_index].meta.get('callout')

    if callout_type:
        return [render_platform_callout(callout_type, inner_text, platform)], end_index
    if inner_text:
        return [f'「{inner_text}」'], end_index
    return [], end_index

def _render_blocks_platform(tokens, platform, counters, indent=0):
    lines = []
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token.type == 'heading_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            text = inline_tokens_to_platform_text(tokens[inline_index].children, platform) if inline_index is not None else ''
            level = int(token.tag[1]) if token.tag.startswith('h') else 1
            _append_block(lines, [' ' * indent + render_platform_heading(level, text, platform, counters)])
            index = _container_end(tokens, index) + 1
            continue

        if token.type == 'paragraph_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            text = inline_tokens_to_platform_text(tokens[inline_index].children, platform) if inline_index is not None else ''
            _append_block(lines, [' ' * indent + text] if text else [])
            index = _container_end(tokens, index) + 1
            continue

        if token.type in ('bullet_list_open', 'ordered_list_open'):
            block_lines, end_index = _render_list_platform(tokens, index, platform, indent)
            _append_block(lines, block_lines)
            index = end_index + 1
            continue

        if token.type == 'blockquote_open':
            block_lines, end_index = _render_blockquote_platform(tokens, index, platform, counters, indent)
            _append_block(lines, [' ' * indent + line for line in block_lines])
            index = end_index + 1
            continue

        if token.type == 'table_open':
            header, rows, end_index = _collect_table_for_platform(tokens, index, platform)
            rendered = render_platform_table(header, rows, platform).splitlines()
            _append_block(lines, [' ' * indent + line for line in rendered])
            index = end_index + 1
            continue

        if token.type in ('fence', 'code_block'):
            _append_block(lines, _render_code_platform(token))
            index += 1
            continue

        if token.type == 'hr':
            _append_block(lines, ['——'])
            index += 1
            continue

        index += 1

    return _trim_blank_lines(lines)

def _compact_platform_lines(lines):
    """Remove empty spacer lines that social editors expand into large gaps."""
    compacted = []
    for line in lines:
        if not line.strip():
            continue
        compacted.append(line.rstrip())
    return compacted

def render_plain_platform_text(tokens, platform):
    counters = {'h2': 0, 'h3': 0}
    return '\n'.join(_compact_platform_lines(_render_blocks_platform(tokens, platform, counters)))

def markdown_to_platform_text(md_text, platform, theme_name='modern-blue'):
    """
    Render Markdown-like source into platform-oriented text or inline HTML.

    Zhihu/Xiaohongshu get visible plain text. Feishu/Notion get portable
    Markdown. WeChat gets inline-styled HTML for pasting into the editor.
    """
    platform = normalize_platform_name(platform)
    if platform not in ('zhihu', 'zhihu-html', 'xhs', 'feishu', 'wechat', 'notion'):
        raise ValueError(f"Unsupported platform: {platform}")

    if platform in ('feishu', 'notion'):
        return markdown_to_portable_markdown(md_text)
    if platform == 'zhihu-html':
        return markdown_to_zhihu_html(md_text, theme_name=theme_name)
    if platform == 'wechat':
        return markdown_to_wechat_html(md_text, theme_name=theme_name)

    return render_plain_platform_text(parse_markdown_tokens(md_text), platform)

def markdown_to_rtf(md_text, theme_name='modern-blue'):
    """
    Render Markdown to native RTF using the markdown-it-py token pipeline.
    """
    theme = THEMES.get(theme_name, THEMES['modern-blue'])
    font_eng, font_cjk = theme['fonts']

    c_bg, c_txt, c_acc, c_qbg, c_hl, c_strong, c_thdr, c_tbrd = theme['colors_rtf']
    if sum(c_bg) < 384:
        # RTF readers render dark page backgrounds inconsistently. Keep RTF on
        # a light canvas and preserve the theme through accent colors instead.
        c_bg = (255, 255, 255)
        c_txt = (36, 41, 47)
        c_qbg = (246, 248, 250)
        c_hl = (255, 245, 176)
        c_strong = (221, 244, 240)
        c_thdr = (246, 248, 250)
        c_tbrd = (208, 215, 222)

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

    rtf_content = render_rtf_tokens(parse_markdown_tokens(md_text))
    
    rtf_doc = f"""{{\\rtf1\\ansi\\ansicpg1252\\cocoartf2822
\\cocoatextscaling0\\cocoaplatform0{{\\fonttbl\\f0\\fswiss\\fcharset0 {font_eng};\\f1\\fnil\\fcharset134 {font_cjk};\\f2\\fmodern\\fcharset0 Courier;}}
{{\\colortbl;{colortbl}}}
{{\\*\\expandedcolortbl;;}}
\\paperw11900\\paperh16840\\margl1440\\margr1440\\vieww11520\\viewh8400\\viewkind0
\\pard\\tx720\\tx1440\\tx2160\\tx2880\\tx3600\\tx4320\\tx5040\\tx5760\\tx6480\\tx7200\\tx7920\\tx8640\\pardirnatural\\partightenfactor0
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

def inline_tokens_to_portable(children):
    if not children:
        return ''

    parts = []
    link_stack = []
    for child in children:
        if child.type == 'text':
            parts.append(child.content)
        elif child.type == 'code_inline':
            parts.append(f'`{child.content}`')
        elif child.type in ('strong_open', 'mark_open'):
            parts.append('**')
        elif child.type in ('strong_close', 'mark_close'):
            parts.append('**')
        elif child.type == 'em_open':
            parts.append('*')
        elif child.type == 'em_close':
            parts.append('*')
        elif child.type == 's_open':
            parts.append('~~')
        elif child.type == 's_close':
            parts.append('~~')
        elif child.type == 'link_open':
            link_stack.append(child.attrGet('href') or '')
            parts.append('[')
        elif child.type == 'link_close':
            href = link_stack.pop() if link_stack else ''
            parts.append(f']({href})')
        elif child.type == 'image':
            alt = child.content or child.attrGet('alt') or ''
            src = child.attrGet('src') or ''
            title = child.attrGet('title')
            title_part = f' "{title}"' if title else ''
            parts.append(f'![{alt}]({src}{title_part})')
        elif child.content:
            parts.append(child.content)
    return ''.join(parts)

def _trim_blank_lines(lines):
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines

def _append_block(lines, block_lines):
    block_lines = _trim_blank_lines(list(block_lines))
    if not block_lines:
        return
    if lines and lines[-1] != '':
        lines.append('')
    lines.extend(block_lines)
    lines.append('')

def _render_table_portable(tokens, start_index):
    end_index = _container_end(tokens, start_index)
    rows = []
    current_row = None
    index = start_index + 1

    while index < end_index:
        token = tokens[index]
        if token.type == 'tr_open':
            current_row = []
        elif token.type == 'tr_close':
            if current_row is not None:
                rows.append(current_row)
            current_row = None
        elif token.type in ('th_open', 'td_open') and current_row is not None:
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            cell_text = ''
            if inline_index is not None:
                cell_text = inline_tokens_to_portable(tokens[inline_index].children)
            current_row.append(cell_text.replace('|', '\\|').strip())
        index += 1

    if not rows:
        return [], end_index

    header = rows[0]
    body_rows = rows[1:]
    separator = ['---'] * len(header)
    rendered = [
        '| ' + ' | '.join(header) + ' |',
        '| ' + ' | '.join(separator) + ' |',
    ]
    for row in body_rows:
        padded = row + [''] * (len(header) - len(row))
        rendered.append('| ' + ' | '.join(padded[:len(header)]) + ' |')
    return rendered, end_index

def _render_list_item_portable(tokens, start_index, end_index, marker, indent):
    lines = []
    first_text = ''
    child_blocks = []
    index = start_index + 1

    while index < end_index:
        token = tokens[index]
        if token.type == 'paragraph_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            if inline_index is not None:
                text = inline_tokens_to_portable(tokens[inline_index].children)
                if not first_text:
                    first_text = text
                elif text:
                    child_blocks.append(('paragraph', [text]))
            index = _container_end(tokens, index) + 1
            continue
        if token.type in ('bullet_list_open', 'ordered_list_open'):
            nested, nested_end = _render_list_portable(tokens, index, indent + 2)
            child_blocks.append(('list', nested))
            index = nested_end + 1
            continue
        if token.type == 'blockquote_open':
            quote_lines, quote_end = _render_blockquote_portable(tokens, index, indent + 2)
            child_blocks.append(('quote', quote_lines))
            index = quote_end + 1
            continue
        if token.type in ('fence', 'code_block'):
            child_blocks.append(('code', _render_code_portable(token, indent + 2)))
        index += 1

    task = tokens[start_index].meta.get('task')
    if task is not None:
        checked = 'x' if task.get('checked') else ' '
        first_text = f'[{checked}] {first_text}'.rstrip()

    prefix = ' ' * indent + marker
    lines.append(prefix + first_text)
    continuation_prefix = ' ' * (indent + len(marker))
    for _, block_lines in child_blocks:
        for line in _trim_blank_lines(list(block_lines)):
            lines.append(continuation_prefix + line if line else '')
    return lines

def _render_list_portable(tokens, start_index, indent=0):
    end_index = _container_end(tokens, start_index)
    ordered = tokens[start_index].type == 'ordered_list_open'
    start_number = tokens[start_index].attrGet('start')
    number = int(start_number) if start_number else 1
    rendered = []
    index = start_index + 1

    while index < end_index:
        token = tokens[index]
        if token.type == 'list_item_open':
            marker = f'{number}. ' if ordered else '- '
            item_end = _container_end(tokens, index)
            rendered.extend(_render_list_item_portable(tokens, index, item_end, marker, indent))
            number += 1
            index = item_end + 1
            continue
        index += 1
    return rendered, end_index

def _render_code_portable(token, indent=0):
    if token.type == 'fence':
        info = token.info.strip()
        lines = [' ' * indent + f'```{info}'.rstrip()]
        lines.extend(' ' * indent + line for line in token.content.rstrip('\n').split('\n'))
        lines.append(' ' * indent + '```')
        return lines

    lines = []
    for line in token.content.rstrip('\n').split('\n'):
        lines.append(' ' * indent + '    ' + line)
    return lines

def _render_blockquote_portable(tokens, start_index, indent=0):
    end_index = _container_end(tokens, start_index)
    inner_lines = _render_blocks_portable(tokens[start_index + 1:end_index], indent=0)
    inner_lines = _trim_blank_lines(inner_lines)

    rendered = []
    quote_prefix = ' ' * indent + '> '
    for line in inner_lines:
        rendered.append((' ' * indent + '>' if not line else quote_prefix + line))
    return rendered, end_index

def _render_blocks_portable(tokens, indent=0):
    lines = []
    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token.type == 'heading_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            text = inline_tokens_to_portable(tokens[inline_index].children) if inline_index is not None else ''
            level = int(token.tag[1]) if token.tag.startswith('h') else 1
            _append_block(lines, [' ' * indent + ('#' * level) + ' ' + text])
            index = _container_end(tokens, index) + 1
            continue

        if token.type == 'paragraph_open':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            text = inline_tokens_to_portable(tokens[inline_index].children) if inline_index is not None else ''
            _append_block(lines, [' ' * indent + text] if text else [])
            index = _container_end(tokens, index) + 1
            continue

        if token.type in ('bullet_list_open', 'ordered_list_open'):
            block_lines, end_index = _render_list_portable(tokens, index, indent)
            _append_block(lines, block_lines)
            index = end_index + 1
            continue

        if token.type == 'blockquote_open':
            block_lines, end_index = _render_blockquote_portable(tokens, index, indent)
            _append_block(lines, block_lines)
            index = end_index + 1
            continue

        if token.type == 'table_open':
            block_lines, end_index = _render_table_portable(tokens, index)
            _append_block(lines, [' ' * indent + line for line in block_lines])
            index = end_index + 1
            continue

        if token.type in ('fence', 'code_block'):
            _append_block(lines, _render_code_portable(token, indent))
            index += 1
            continue

        if token.type == 'hr':
            _append_block(lines, [' ' * indent + '---'])
            index += 1
            continue

        index += 1

    return _trim_blank_lines(lines)

def render_portable_markdown(tokens):
    return normalize_newlines('\n'.join(_render_blocks_portable(tokens)))

def _inline_plain_text(children):
    if not children:
        return ''
    parts = []
    for child in children:
        if child.type in ('text', 'code_inline', 'image'):
            parts.append(child.content)
    return ''.join(parts).strip()

def extract_title_from_tokens(tokens, fallback='Typeset Article'):
    for index, token in enumerate(tokens):
        if token.type == 'heading_open' and token.tag == 'h1':
            inline_index = _first_inline_index(tokens, index, _container_end(tokens, index))
            if inline_index is not None:
                title = _inline_plain_text(tokens[inline_index].children)
                if title:
                    return title
    return fallback

def _html_checkbox_token(checked, base_token):
    token = Token('html_inline', '', 0)
    token.level = base_token.level
    checked_attr = ' checked' if checked else ''
    token.content = (
        f'<input class="task-list-item-checkbox" type="checkbox" disabled{checked_attr}> '
    )
    return token

def prepare_tokens_for_html(tokens):
    for index, token in enumerate(tokens):
        if token.type == 'blockquote_open' and token.meta.get('callout'):
            callout_type = token.meta['callout']
            token.tag = 'div'
            token.attrJoin('class', f'callout callout-{callout_type}')
            end_index = _container_end(tokens, index)
            tokens[end_index].tag = 'div'
        elif token.type == 'table_open':
            token.attrJoin('class', 'typeset-table')
        elif token.type == 'list_item_open' and token.meta.get('task') is not None:
            token.attrJoin('class', 'task-list-item')
            end_index = _container_end(tokens, index)
            inline_index = _first_inline_index(tokens, index, end_index)
            if inline_index is not None and tokens[inline_index].children is not None:
                checked = tokens[index].meta['task'].get('checked')
                tokens[inline_index].children.insert(
                    0,
                    _html_checkbox_token(checked, tokens[inline_index])
                )
                _refresh_inline_content(tokens[inline_index])
    return tokens

def _append_inline_style(token, style):
    existing = token.attrGet('style')
    token.attrSet('style', f'{existing}; {style}' if existing else style)

def prepare_tokens_for_wechat(tokens, theme):
    css = theme['css']
    prepare_tokens_for_html(tokens)

    accent = css['accent']
    text = css['text']
    quote_bg = css['quote_bg']
    quote_border = css['quote_border']
    strong_bg = css['strong_bg']
    strong_border = css['strong_border']
    code_bg = css.get('code_bg', quote_bg)
    code_text = css.get('code_text', text)
    link_color = css.get('link_color', accent)
    table_border = css['table_border']

    heading_styles = {
        'h1': f'font-size:24px;line-height:1.5;color:{accent};text-align:center;margin:0 0 24px;font-weight:700;',
        'h2': f'font-size:20px;line-height:1.5;color:{accent};margin:32px 0 16px;padding-bottom:8px;border-bottom:2px solid {quote_border};font-weight:700;',
        'h3': f'font-size:18px;line-height:1.5;color:{accent};margin:28px 0 14px;font-weight:700;',
    }

    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            _append_inline_style(
                token,
                heading_styles.get(
                    token.tag,
                    f'font-size:16px;line-height:1.6;color:{text};margin:22px 0 12px;font-weight:700;'
                )
            )
        elif token.type == 'paragraph_open':
            margin = '0' if _is_inside_open_token(tokens, index, 'blockquote_open') else '0 0 18px'
            _append_inline_style(token, f'margin:{margin};line-height:1.8;color:{text};font-size:16px;')
        elif token.type == 'blockquote_open':
            if token.meta.get('callout') in ('summary', 'key'):
                _append_inline_style(
                    token,
                    f'margin:24px 0;padding:14px 18px;border-left:4px solid {strong_border};'
                    f'background:{strong_bg};border-radius:6px;color:{text};font-weight:600;'
                    'display:flex;flex-direction:column;justify-content:center;'
                )
            else:
                _append_inline_style(
                    token,
                    f'margin:24px 0;padding:12px 18px;border-left:4px solid {quote_border};'
                    f'background:{quote_bg};border-radius:0 6px 6px 0;color:{text};'
                    'display:flex;flex-direction:column;justify-content:center;'
                )
                if token.meta.get('callout') == 'quote':
                    _append_inline_style(token, 'font-style:italic;')
        elif token.type == 'table_open':
            _append_inline_style(token, 'width:100%;border-collapse:collapse;margin:24px 0;font-size:15px;')
        elif token.type in ('th_open', 'td_open'):
            bg = f'background:{css["table_header_bg"]};font-weight:600;color:{accent};' if token.type == 'th_open' else ''
            _append_inline_style(
                token,
                f'border:1px solid {table_border};padding:8px 10px;text-align:left;vertical-align:top;{bg}'
            )
        elif token.type in ('bullet_list_open', 'ordered_list_open'):
            _append_inline_style(token, 'margin:0 0 18px;padding-left:24px;')
        elif token.type == 'list_item_open':
            _append_inline_style(token, 'margin:0 0 8px;line-height:1.8;')
        elif token.type in ('fence', 'code_block'):
            _append_inline_style(
                token,
                f'background:{code_bg};color:{code_text};padding:12px;border-radius:6px;'
                'font-size:14px;line-height:1.6;overflow-x:auto;'
            )
        elif token.type == 'hr':
            _append_inline_style(token, f'border:0;border-top:1px solid {table_border};margin:28px auto;width:42%;')

        if token.type == 'inline' and token.children:
            for child in token.children:
                if child.type == 'link_open':
                    _append_inline_style(child, f'color:{link_color};text-decoration:underline;')
                elif child.type == 'mark_open':
                    _append_inline_style(
                        child,
                        f'background:{css["highlight"]};color:inherit;padding:2px 4px;border-radius:3px;'
                    )
                elif child.type == 'code_inline':
                    _append_inline_style(
                        child,
                        f'background:{code_bg};color:{code_text};padding:2px 5px;border-radius:4px;'
                        'font-family:Menlo,Monaco,Consolas,monospace;font-size:0.92em;'
                    )
                elif child.type == 'image':
                    _append_inline_style(
                        child,
                        'display:block;max-width:100%;height:auto;margin:20px auto;border-radius:6px;'
                    )

    return tokens

def prepare_tokens_for_zhihu_html(tokens):
    """
    Prepare compact inline HTML for Zhihu's rich-text editor.

    Zhihu strips most color, background, and border styling on paste. Keep the
    HTML semantic and compact so the pasted result still works after sanitizing.
    """
    border = '#d0d7de'

    heading_styles = {
        'h1': (
            'margin:0 0 14px;font-size:24px;line-height:1.45;font-weight:700;text-align:left;'
        ),
        'h2': (
            'margin:22px 0 10px;font-size:20px;line-height:1.5;font-weight:700;'
        ),
        'h3': (
            'margin:18px 0 8px;font-size:18px;line-height:1.5;font-weight:700;'
        ),
    }

    for index, token in enumerate(tokens):
        if token.type == 'blockquote_open' and token.meta.get('callout') in ('summary', 'key'):
            end_index = _container_end(tokens, index)
            for child_index in range(index + 1, end_index):
                if tokens[child_index].type == 'inline':
                    _wrap_inline_children_in_strong(tokens[child_index])

        if token.type == 'list_item_open' and token.meta.get('task') is not None:
            end_index = _container_end(tokens, index)
            inline_index = _first_inline_index(tokens, index, end_index)
            if inline_index is not None and tokens[inline_index].children is not None:
                marker = '■ ' if token.meta['task'].get('checked') else '□ '
                tokens[inline_index].children.insert(0, _make_text_token(marker, tokens[inline_index]))
                _refresh_inline_content(tokens[inline_index])

        if token.type == 'heading_open':
            _append_inline_style(
                token,
                heading_styles.get(
                    token.tag,
                    'margin:16px 0 8px;font-size:16px;line-height:1.6;font-weight:700;'
                )
            )
        elif token.type == 'paragraph_open':
            _append_inline_style(token, 'margin:0 0 10px;font-size:16px;line-height:1.75;')
        elif token.type == 'blockquote_open':
            _append_inline_style(
                token,
                f'margin:12px 0;padding:0 0 0 12px;border-left:4px solid {border};line-height:1.75;'
            )
            if token.meta.get('callout') == 'quote':
                _append_inline_style(token, 'font-style:italic;')
        elif token.type == 'table_open':
            _append_inline_style(token, 'width:100%;border-collapse:collapse;margin:12px 0;font-size:15px;')
        elif token.type in ('th_open', 'td_open'):
            bg = 'font-weight:700;' if token.type == 'th_open' else ''
            _append_inline_style(
                token,
                f'border:1px solid {border};padding:6px 8px;text-align:left;vertical-align:top;line-height:1.65;{bg}'
            )
        elif token.type in ('bullet_list_open', 'ordered_list_open'):
            _append_inline_style(token, 'margin:0 0 10px;padding-left:22px;')
        elif token.type == 'list_item_open':
            _append_inline_style(token, 'margin:2px 0;line-height:1.75;')
        elif token.type in ('fence', 'code_block'):
            _append_inline_style(
                token,
                f'margin:12px 0;padding:10px;border:1px solid {border};border-radius:4px;'
                'font-size:14px;line-height:1.6;white-space:pre-wrap;'
            )
        elif token.type == 'hr':
            _append_inline_style(token, f'border:0;border-top:1px solid {border};margin:18px 0;')

        if token.type == 'inline' and token.children:
            for child in token.children:
                if child.type == 'link_open':
                    _append_inline_style(child, 'text-decoration:underline;')
                elif child.type == 'mark_open':
                    child.tag = 'strong'
                    _append_inline_style(child, 'font-weight:700;')
                elif child.type == 'mark_close':
                    child.tag = 'strong'
                elif child.type == 'strong_open':
                    _append_inline_style(child, 'font-weight:700;')
                elif child.type == 'code_inline':
                    _append_inline_style(
                        child,
                        'padding:1px 4px;border-radius:3px;'
                        'font-family:Menlo,Monaco,Consolas,monospace;font-size:0.92em;'
                    )
                elif child.type == 'image':
                    _append_inline_style(child, 'display:block;max-width:100%;height:auto;margin:12px auto;')

    return tokens

def markdown_to_zhihu_html(md_text, theme_name='modern-blue'):
    md = build_parser()
    tokens = prepare_tokens_for_zhihu_html(parse_markdown_tokens(md_text, parser=md))
    body = md.renderer.render(tokens, md.options, {})
    section_style = (
        'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",'
        '"Microsoft YaHei",Arial,sans-serif;font-size:16px;line-height:1.75;'
    )
    return f'<section style="{html.escape(section_style, quote=True)}">\n{body}</section>'

def markdown_to_wechat_html(md_text, theme_name='modern-blue'):
    theme = THEMES.get(theme_name, THEMES['modern-blue'])
    md = build_parser()
    tokens = prepare_tokens_for_wechat(parse_markdown_tokens(md_text, parser=md), theme)
    body = md.renderer.render(tokens, md.options, {})
    css = theme['css']
    section_style = (
        f'font-family:{css["font_family"]};color:{css["text"]};'
        'font-size:16px;line-height:1.8;'
    )
    return f'<section style="{html.escape(section_style, quote=True)}">\n{body}</section>'

def markdown_to_html(md_text, theme_name='modern-blue', title=None):
    """
    Render Markdown to themed HTML using the markdown-it-py token pipeline.
    """
    theme = THEMES.get(theme_name, THEMES['modern-blue'])
    css = theme['css']
    md = build_parser()
    tokens = prepare_tokens_for_html(parse_markdown_tokens(md_text, parser=md))
    fallback_title = title or 'Typeset Article'
    html_title = fallback_title if title else extract_title_from_tokens(tokens, fallback_title)
    html_body = md.renderer.render(tokens, md.options, {})

    accent_text = css['accent']
    border_color = css['quote_border']
    code_bg = css.get('code_bg', css.get('quote_bg', '#f6f8fa'))
    code_text = css.get('code_text', css['text'])
    link_color = css.get('link_color', css['accent'])
    hr_color = css.get('hr_color', css['table_border'])
    img_caption = css.get('img_caption', css['text'])
    
    template = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(html_title)}</title>
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
  blockquote > p:last-child {{
    margin-bottom: 0;
  }}
  .callout {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 14px 20px;
    margin: 24px 0;
    border-radius: 6px;
    border-left: 4px solid {border_color};
    background-color: {css['quote_bg']};
    color: inherit;
  }}
  .callout > p:last-child {{
    margin-bottom: 0;
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
  a {{
    color: {link_color};
    text-decoration: none;
    border-bottom: 1px solid transparent;
  }}
  a:hover {{
    border-bottom-color: {link_color};
  }}
  strong {{
    color: inherit;
  }}
  em {{
    font-style: italic;
  }}
  del, s {{
    text-decoration: line-through;
    opacity: 0.8;
  }}
  mark {{
    background-color: {css['highlight']};
    color: inherit;
    padding: 2px 4px;
    border-radius: 3px;
  }}
  code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    font-size: 0.92em;
    background-color: {code_bg};
    color: {code_text};
    padding: 2px 5px;
    border-radius: 4px;
  }}
  pre {{
    background-color: {code_bg};
    color: {code_text};
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
    line-height: 1.6;
    margin: 24px 0;
  }}
  pre code {{
    display: block;
    padding: 0;
    background: transparent;
    color: inherit;
  }}
  img {{
    display: block;
    max-width: 100%;
    height: auto;
    margin: 24px auto;
    border-radius: 6px;
  }}
  figcaption {{
    color: {img_caption};
    opacity: 0.75;
    text-align: center;
    font-size: 14px;
    margin-top: -12px;
    margin-bottom: 24px;
  }}
  hr {{
    border: 0;
    border-top: 1px solid {hr_color};
    margin: 32px auto;
    width: 40%;
  }}
  .task-list-item {{
    list-style: none;
    margin-left: -1.4em;
  }}
  .task-list-item-checkbox {{
    margin-right: 8px;
    vertical-align: -0.1em;
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
  python3 typeset.py input.md output.html --theme github-light --title "Custom Title"
  python3 typeset.py input.md output.rtf --theme warm-peach
  python3 typeset.py input.md output.md modern-blue
  python3 typeset.py input.md output.zhihu.txt --platform zhihu
  python3 typeset.py input.md output.zhihu.html --platform zhihu-html
  python3 typeset.py input.md output.xhs.txt --platform xhs
  python3 typeset.py input.md output.feishu.md --platform feishu
  python3 typeset.py input.md output.wechat.html --platform wechat
  python3 typeset.py input.md output.notion.md --platform notion

Inputs:
  .md/.txt files are read as UTF-8 text.
  .rtf files are converted to plain text with macOS textutil, or striprtf as fallback.
  Plain text without Markdown markers gets conservative headings and bullets.

Themes:
  {', '.join(THEMES.keys())}

Note:
  Themes affect HTML/RTF visual styling. Markdown output is portable Markdown.
  Platform output supports Zhihu/Xiaohongshu plain text, Zhihu rich HTML,
  Feishu/Notion Markdown, and WeChat inline HTML.
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
            return result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                from striprtf.striprtf import rtf_to_text
            except ImportError as exc:
                raise RuntimeError(
                    'RTF input requires macOS textutil or the striprtf Python package.'
                ) from exc
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                return rtf_to_text(f.read())

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
    if re.search(r'https?://|www\.|@', s, re.I):
        return False
    if re.search(r'[。！!；;]$', s):
        return False
    previous_blank = index == 0 or not lines[index - 1].strip()
    next_has_content = any(line.strip() for line in lines[index + 1:index + 3])
    # Avoid promoting labels that are just numbers or punctuation fragments.
    if not re.search(r'[\u4e00-\u9fa5A-Za-z]', s):
        return False
    if previous_blank:
        return True

    # RTF/textutil often loses visual blank lines. Promote short title-like
    # lines after a completed paragraph, but avoid list labels after a colon.
    previous_text = lines[index - 1].strip()
    if not next_has_content:
        return False
    if previous_text.endswith(('：', ':')):
        return False
    if not re.search(r'[。！？!?]$', previous_text):
        return False
    if re.search(r'[，,：:]', s):
        return False
    if not (s.endswith(('？', '?')) or re.match(r'^(先看|为什么|怎么|如何|它具体|具体|结论|总结|写在最后|最后)', s)):
        return False
    return len(s) <= 24

def is_plain_list_label(text):
    """Return True for short option labels in plain text."""
    s = text.strip()
    if not s:
        return False
    if has_markdown_structure(s):
        return False
    if len(s) > 30:
        return False
    if re.search(r'https?://|www\.|@', s, re.I):
        return False
    if re.search(r'[。！？!?；;：:]$', s):
        return False
    return bool(re.search(r'[\u4e00-\u9fa5A-Za-z]', s))

def collect_plain_list_after_colon(lines, start_index):
    """Collect simple labels or label-description pairs after a colon line."""
    first_label = lines[start_index].strip() if start_index < len(lines) else ''
    second_line = lines[start_index + 1].strip() if start_index + 1 < len(lines) else ''
    if is_plain_list_label(first_label) and is_plain_list_label(second_line):
        items = []
        index = start_index
        while index < len(lines):
            label = lines[index].strip()
            if not is_plain_list_label(label):
                break
            items.append(label)
            index += 1
        if len(items) < 2:
            return None, start_index
        return items, index

    items = []
    index = start_index

    while index < len(lines):
        label = lines[index].strip()
        if not label:
            break
        if not is_plain_list_label(label):
            break

        next_index = index + 1
        next_line = lines[next_index].strip() if next_index < len(lines) else ''
        if next_line and not is_plain_list_label(next_line) and not is_plain_section_heading(lines, next_index):
            items.append(f'{label}：{next_line}')
            index += 2
            continue

        items.append(label)
        index += 1

    if len(items) < 2:
        return None, start_index
    return items, index

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
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if i == first_content_index and s:
            out.append(f'# {s}')
            out.append('')
            i += 1
            continue

        if s.endswith(('：', ':')):
            converted_intro = convert_inline_list_to_markdown_lines(line)
            out.extend(converted_intro)
            items, next_index = collect_plain_list_after_colon(lines, i + 1)
            if items:
                if out and out[-1] != '':
                    out.append('')
                out.extend(f'{item_index}. {item}' for item_index, item in enumerate(items, 1))
                out.append('')
                i = next_index
                continue
            i += 1
            continue

        if i != first_content_index and is_plain_section_heading(lines, i):
            if out and out[-1] != '':
                out.append('')
            out.append(f'## {s}')
            out.append('')
            i += 1
            continue
        out.extend(convert_inline_list_to_markdown_lines(line))
        i += 1

    return normalize_newlines('\n'.join(out))

def prepare_markdown_input(content):
    """Prepare raw text for the renderer without overwriting existing Markdown."""
    if has_markdown_structure(content):
        return content
    return auto_structure_plain_text(content)

def parse_cli_args(argv):
    theme = 'modern-blue'
    platform = None
    title = None
    args = list(argv)

    if args and args[0] in ('-h', '--help'):
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
                    print("Error: --platform must be one of: zhihu, zhihu-html, xhs, feishu, wechat, notion", file=sys.stderr)
                    sys.exit(1)
                args.pop(idx+1)
                args.pop(idx)
            else:
                print("Error: --platform requires a value", file=sys.stderr)
                sys.exit(1)
        except ValueError:
            pass

    if '--title' in args:
        try:
            idx = args.index('--title')
            if idx + 1 < len(args):
                title = args[idx+1]
                args.pop(idx+1)
                args.pop(idx)
            else:
                print("Error: --title requires a value", file=sys.stderr)
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
        if lower_out.endswith(('.zhihu.html', '.zhihu-rich.html', '.zhihu.rich.html')):
            platform = 'zhihu-html'
        elif lower_out.endswith('.zhihu.txt'):
            platform = 'zhihu'
        elif lower_out.endswith(('.xhs.txt', '.xiaohongshu.txt', '.rednote.txt')):
            platform = 'xhs'
        elif lower_out.endswith(('.feishu.txt', '.lark.txt', '.feishu.md', '.lark.md')):
            platform = 'feishu'
        elif lower_out.endswith(('.wechat.html', '.weixin.html', '.wx.html')):
            platform = 'wechat'
        elif lower_out.endswith(('.notion.md', '.notion.txt')):
            platform = 'notion'

    if platform is not None and platform not in ('zhihu', 'zhihu-html', 'xhs', 'feishu', 'wechat', 'notion'):
        print("Error: --platform must be one of: zhihu, zhihu-html, xhs, feishu, wechat, notion", file=sys.stderr)
        sys.exit(1)

    return filepath, out_path, theme, platform, title

def main():
    filepath, out_path, theme, platform, title = parse_cli_args(sys.argv[1:])

    if filepath:
        try:
            markdown_out = prepare_markdown_input(read_input_text(filepath))

            if out_path:
                if platform:
                    platform_text_out = markdown_to_platform_text(markdown_out, platform, theme_name=theme)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(platform_text_out)
                    print(f"Successfully saved {platform} platform output to {out_path}")
                elif out_path.endswith('.html'):
                    html_out = markdown_to_html(markdown_out, theme_name=theme, title=title)
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
                    portable_md_out = markdown_to_portable_markdown(markdown_out)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(portable_md_out)
                    print(f"Successfully typeset and saved normalized text to {out_path}")
            else:
                if platform:
                    print(markdown_to_platform_text(markdown_out, platform, theme_name=theme))
                else:
                    # Print Markdown to stdout
                    print(markdown_to_portable_markdown(markdown_out))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Stream standard input
        content = sys.stdin.read()
        markdown_out = prepare_markdown_input(content)
        if platform:
            print(markdown_to_platform_text(markdown_out, platform, theme_name=theme), end='')
        else:
            print(markdown_to_portable_markdown(markdown_out), end='')

if __name__ == '__main__':
    main()
