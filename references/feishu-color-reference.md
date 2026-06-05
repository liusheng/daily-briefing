# Feishu Doc API — text_color Reference

Tested via Feishu Open API on 2026-06-04. Only values 1–7 are valid.

## text_color Values

| Value | Color | Use Case |
|:-----:|-------|----------|
| 0 | ❌ Invalid (field validation failed) | — |
| **1** | **Red** | Warnings, errors |
| 2 | Orange / Yellow | Highlights, tags |
| 3 | Green | Success, positive signals |
| 4 | Teal / Cyan | Info, metadata |
| **5** | **Blue** ✅ | Section headings, links |
| 6 | Purple | Premium, special |
| 7 | Pink | Accents, calls to action |
| 8+ | ❌ Invalid | — |

## Where text_color Works

| Block Type | text_color | align (center) |
|------------|:----------:|:--------------:|
| text (2) | ✅ | ✅ |
| heading1 (3) | ✅ | ✅ |
| heading2 (4) | ✅ | ✅ |
| heading3 (5) | ✅ | ✅ |
| bullet (12) | ✅ | ❌ N/A |
| ordered (13) | ✅ | ❌ N/A |
| divider (22) | ❌ | ❌ |

## text_element_style Fields

```python
{
    "text_element_style": {
        "bold": True,          # bool
        "italic": True,        # bool
        "strikethrough": True, # bool
        "underline": True,     # bool
        "inline_code": True,   # bool
        "text_color": 5        # int, 1-7
    }
}
```

## Python Helper — Blue Centered Section Heading

```python
def H2(text):
    return {"block_type": 4, "heading2": {
        "elements": [{"text_run": {"content": text, "text_element_style": {"text_color": 5}}}],
        "style": {"align": 2}
    }}
```
