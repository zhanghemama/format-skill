from typeset import build_parser, parse_markdown_tokens


def inline_children(tokens):
    children = []
    for token in tokens:
        if token.type == 'inline' and token.children:
            children.extend(token.children)
    return children


def test_text_is_normalized_but_code_and_url_are_preserved():
    source = (
        'Josh是Baremetrics的创始人，'
        '[链接](https://example.com/a,b?x=1) '
        '和 `Josh是Baremetrics`。'
    )
    tokens = parse_markdown_tokens(source)
    children = inline_children(tokens)

    assert any(
        child.type == 'text' and 'Josh 是 Baremetrics 的创始人' in child.content
        for child in children
    )
    assert any(
        child.type == 'code_inline' and child.content == 'Josh是Baremetrics'
        for child in children
    )

    link_open = next(child for child in children if child.type == 'link_open')
    assert link_open.attrGet('href') == 'https://example.com/a,b?x=1'


def test_highlight_marker_becomes_mark_tokens_and_skips_inline_code():
    tokens = parse_markdown_tokens('这是==重点A==，代码 `x==1`。')
    children = inline_children(tokens)

    assert [child.type for child in children] == [
        'text',
        'mark_open',
        'text',
        'mark_close',
        'text',
        'code_inline',
        'text',
    ]
    assert children[2].content == '重点 A'
    assert next(child for child in children if child.type == 'code_inline').content == 'x==1'


def test_callout_is_tagged_and_prefix_is_removed():
    tokens = parse_markdown_tokens('> [!SUMMARY] Josh是Baremetrics的创始人')
    blockquote = next(token for token in tokens if token.type == 'blockquote_open')
    children = inline_children(tokens)

    assert blockquote.meta['callout'] == 'summary'
    assert children[0].type == 'text'
    assert children[0].content == 'Josh 是 Baremetrics 的创始人'


def test_task_items_are_tagged_and_marker_is_removed():
    tokens = parse_markdown_tokens('- [x] 完成A\n- [ ] 待办B')
    list_items = [token for token in tokens if token.type == 'list_item_open']
    text_children = [child for child in inline_children(tokens) if child.type == 'text']

    assert list_items[0].meta['task'] == {'checked': True}
    assert list_items[1].meta['task'] == {'checked': False}
    assert [child.content for child in text_children] == ['完成 A', '待办 B']


def test_parser_enables_tables_and_strikethrough_without_raw_html():
    md = build_parser()
    table_tokens = md.parse('| A | B |\n|---|---|\n| 1 | 2 |')
    strike_tokens = md.parse('~~删除~~')
    html_tokens = md.parse('<span>raw</span>')

    assert any(token.type == 'table_open' for token in table_tokens)
    assert any(
        child.type == 's_open'
        for token in strike_tokens
        for child in (token.children or [])
    )
    assert not any(token.type == 'html_inline' for token in html_tokens)
