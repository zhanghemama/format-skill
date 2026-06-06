import subprocess
import sys
from pathlib import Path

from typeset import (
    THEMES,
    markdown_to_html,
    markdown_to_platform_text,
    parse_cli_args,
    read_input_text,
)


SOURCE = """# 标题A

## 小节B

> [!summary] Josh是Baremetrics的创始人

这是==重点A==和[链接](https://example.com/a,b)。

- [x] 完成A
- [ ] 待办B

| 名称 | 描述 |
|---|---|
| A | Alpha |
"""


def test_zhihu_and_xhs_platform_text_use_visible_formatting():
    zhihu = markdown_to_platform_text(SOURCE, 'zhihu')
    xhs = markdown_to_platform_text(SOURCE, 'xhs')

    assert zhihu.startswith('《标题 A》\n')
    assert '一、小节 B' in zhihu
    assert 'Josh 是 Baremetrics 的创始人' in zhihu
    assert '「重点 A」' in zhihu
    assert '【摘要】' not in zhihu
    assert '【核心观点】' not in zhihu
    assert '【重点】' not in xhs
    assert '\n\n' not in zhihu
    assert '\n\n' not in xhs
    assert '• ■ 完成 A' in zhihu
    assert xhs.startswith('《标题 A》\n')
    assert '01｜小节 B' in xhs
    assert '1. ■ 完成 A' in xhs


def test_xhs_can_render_first_h1_as_section_without_document_title():
    xhs = markdown_to_platform_text(SOURCE, 'xhs', no_document_title=True)

    assert xhs.startswith('标题 A\n')
    assert not xhs.startswith('《标题 A》\n')
    assert '01｜小节 B' in xhs


def test_feishu_and_notion_reuse_portable_markdown():
    feishu = markdown_to_platform_text(SOURCE, 'feishu')
    notion = markdown_to_platform_text(SOURCE, 'notion')

    assert feishu == notion
    assert '> Josh 是 Baremetrics 的创始人' in feishu
    assert '摘要：' not in feishu
    assert '- [x] 完成 A' in feishu


def test_wechat_output_is_inline_html_without_style_block():
    rendered = markdown_to_platform_text(SOURCE, 'wechat', theme_name='github-light')

    assert rendered.startswith('<section style=')
    assert '<style>' not in rendered
    assert 'style=' in rendered
    assert '<section class="callout callout-summary"' in rendered
    assert 'background-color:' in rendered
    assert '<mark style=' in rendered


def test_html_callout_text_is_vertically_centered():
    rendered = markdown_to_html(SOURCE, theme_name='warm-peach')

    assert '.callout {' in rendered
    assert 'justify-content: center;' in rendered
    assert '.callout > p:last-child' in rendered

    wechat = markdown_to_platform_text(SOURCE, 'wechat', theme_name='warm-peach')
    assert 'display:flex;flex-direction:column;justify-content:center;' in wechat
    assert '<p style="margin:0;line-height:1.8;' in wechat


def test_feishu_and_notion_html_are_rich_paste_outputs():
    notion = markdown_to_platform_text(SOURCE, 'notion-html')
    feishu = markdown_to_platform_text(SOURCE, 'feishu-html')

    assert notion != feishu
    assert notion.startswith('<section style=')
    assert feishu.startswith('<section style=')
    assert '<h1 style=' in notion
    assert '<h1 style=' in feishu
    assert '<strong style=' in notion
    assert '<strong style=' in feishu
    assert '**重点 A**' not in notion
    assert '**重点 A**' not in feishu
    assert '<blockquote style=' in notion
    assert '<blockquote style=' in feishu
    assert '#f7f6f3' in notion
    assert '#3370ff' in feishu


def test_zhihu_html_is_compact_inline_rich_text():
    rendered = markdown_to_platform_text(SOURCE, 'zhihu-html')

    assert rendered.startswith('<section style=')
    assert '<style>' not in rendered
    assert '<h1 style=' in rendered
    assert '<blockquote style=' in rendered
    assert '<strong style=' in rendered
    assert '<strong style="font-weight:700;">Josh 是 Baremetrics 的创始人</strong>' in rendered
    assert 'color:' not in rendered
    assert 'background' not in rendered
    assert 'callout-summary' not in rendered
    assert '【摘要】' not in rendered


def test_html_title_override_and_new_themes():
    assert 'github-light' in THEMES
    assert 'serif-print' in THEMES

    rendered = markdown_to_html('# 文档标题', theme_name='github-light', title='手动标题')
    assert '<title>手动标题</title>' in rendered


def test_parse_cli_args_accepts_new_platforms_and_title():
    filepath, out_path, theme, platform, title, no_document_title = parse_cli_args([
        'input.md',
        'output.wechat.html',
        '--theme',
        'serif-print',
        '--title',
        '自定义',
    ])

    assert filepath == 'input.md'
    assert out_path == 'output.wechat.html'
    assert theme == 'serif-print'
    assert platform == 'wechat'
    assert title == '自定义'
    assert no_document_title is False


def test_parse_cli_args_accepts_no_document_title():
    filepath, out_path, theme, platform, title, no_document_title = parse_cli_args([
        'input.md',
        'output.xhs.txt',
        '--no-document-title',
    ])

    assert filepath == 'input.md'
    assert out_path == 'output.xhs.txt'
    assert theme == 'modern-blue'
    assert platform == 'xhs'
    assert title is None
    assert no_document_title is True


def test_parse_cli_args_auto_detects_zhihu_html():
    filepath, out_path, theme, platform, title, no_document_title = parse_cli_args([
        'input.md',
        'output.zhihu.html',
    ])

    assert filepath == 'input.md'
    assert out_path == 'output.zhihu.html'
    assert theme == 'modern-blue'
    assert platform == 'zhihu-html'
    assert title is None
    assert no_document_title is False


def test_parse_cli_args_auto_detects_feishu_and_notion_html():
    assert parse_cli_args(['input.md', 'output.feishu.html'])[3] == 'feishu-html'
    assert parse_cli_args(['input.md', 'output.notion.html'])[3] == 'notion-html'


def test_parse_cli_args_allows_stdin_mode():
    assert parse_cli_args([]) == (None, None, 'modern-blue', None, None, False)


def test_cli_stdin_preserves_code_and_url():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, 'typeset.py'],
        input='[链接](https://example.com/a,b) 和 `Josh是Baremetrics`。',
        text=True,
        capture_output=True,
        cwd=repo_root,
        check=True,
    )

    assert '[链接](https://example.com/a,b)' in result.stdout
    assert '`Josh是Baremetrics`' in result.stdout


def test_rtf_input_falls_back_to_striprtf(monkeypatch, tmp_path):
    path = tmp_path / 'sample.rtf'
    path.write_text(r'{\rtf1\ansi Hello RTF}', encoding='utf-8')

    def raise_missing_textutil(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, 'run', raise_missing_textutil)

    assert 'Hello RTF' in read_input_text(str(path))
