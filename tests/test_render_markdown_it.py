from typeset import markdown_to_html, markdown_to_portable_markdown


SAMPLE = """# 标题A

> [!key] Josh是Baremetrics的创始人

这是==重点A==和[链接](https://example.com/a,b)，代码 `Josh是Baremetrics`。

- [x] 完成A
  - 子项B

```python
print(1)
```

![Alt图](img.png)

~~删除A~~

| A | B |
|---|---|
| 1 | 2 |
"""


def test_html_uses_markdown_it_features_and_theme_shell():
    rendered = markdown_to_html(SAMPLE)

    assert '<title>标题 A</title>' in rendered
    assert '<div class="callout callout-key">' in rendered
    assert 'Josh 是 Baremetrics 的创始人' in rendered
    assert '<mark>重点 A</mark>' in rendered
    assert '<a href="https://example.com/a,b">链接</a>' in rendered
    assert '<code>Josh是Baremetrics</code>' in rendered
    assert 'class="task-list-item-checkbox" type="checkbox" disabled checked' in rendered
    assert '<pre><code class="language-python">print(1)' in rendered
    assert '<img src="img.png" alt="Alt图" />' in rendered
    assert '<s>删除 A</s>' in rendered
    assert '<table class="typeset-table">' in rendered


def test_html_escapes_raw_html_input():
    rendered = markdown_to_html('中文<span>raw</span>')

    assert '&lt;span&gt;raw&lt;/span&gt;' in rendered
    assert '<span>raw</span>' not in rendered


def test_portable_markdown_preserves_gfm_and_downgrades_private_markers():
    rendered = markdown_to_portable_markdown(SAMPLE)

    assert '# 标题 A' in rendered
    assert '> Josh 是 Baremetrics 的创始人' in rendered
    assert '核心观点：' not in rendered
    assert '这是**重点 A**和[链接](https://example.com/a,b)' in rendered
    assert '`Josh是Baremetrics`' in rendered
    assert '- [x] 完成 A' in rendered
    assert '    - 子项 B' in rendered
    assert '```python\nprint(1)\n```' in rendered
    assert '![Alt图](img.png)' in rendered
    assert '~~删除 A~~' in rendered
    assert '| A | B |' in rendered
