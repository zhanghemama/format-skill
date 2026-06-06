from typeset import markdown_to_rtf, text_to_rtf_content


def test_rtf_renderer_uses_token_features():
    source = """# 标题A

> [!quote] 引用A

这是==重点A==和[链接](https://example.com/a,b)，代码 `Josh是Baremetrics`。

- [x] 完成A

```python
print(1)
```

![Alt图](img.png)

~~删除A~~
"""

    rendered = markdown_to_rtf(source)

    assert r'\f2\fmodern' in rendered
    assert r'\highlight5' in rendered
    assert 'https://example.com/a,b' in rendered
    assert r'\f2\fs22\cf3 print(1)' in rendered
    assert r'\cb6' not in rendered
    assert r'\cb7' not in rendered
    assert r'\u9745' in rendered
    assert 'Alt' in rendered
    assert r'\strike' in rendered
    assert text_to_rtf_content('引用 A') in rendered
    assert text_to_rtf_content('引用：') not in rendered
    assert r'\i ' in rendered


def test_rtf_renderer_hides_semantic_callout_labels():
    source = """> [!summary] 把机械的交给 AI。

> [!key] 把有趣的留给人类。
"""

    rendered = markdown_to_rtf(source)

    assert text_to_rtf_content('把机械的交给 AI。') in rendered
    assert text_to_rtf_content('把有趣的留给人类。') in rendered
    assert text_to_rtf_content('摘要：') not in rendered
    assert text_to_rtf_content('核心观点：') not in rendered
