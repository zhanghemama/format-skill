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

    assert '一、小节 B' in zhihu
    assert '【摘要】Josh 是 Baremetrics 的创始人' in zhihu
    assert '【重点 A】' in zhihu
    assert '• ■ 完成 A' in zhihu
    assert '01｜小节 B' in xhs
    assert '1. ■ 完成 A' in xhs


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
    assert 'callout-summary' in rendered
    assert '<mark style=' in rendered


def test_html_title_override_and_new_themes():
    assert 'github-light' in THEMES
    assert 'serif-print' in THEMES

    rendered = markdown_to_html('# 文档标题', theme_name='github-light', title='手动标题')
    assert '<title>手动标题</title>' in rendered


def test_parse_cli_args_accepts_new_platforms_and_title():
    filepath, out_path, theme, platform, title = parse_cli_args([
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


def test_parse_cli_args_allows_stdin_mode():
    assert parse_cli_args([]) == (None, None, 'modern-blue', None, None)


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
