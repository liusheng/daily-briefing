---
name: feishu-doc-api
description: "Create and write content to Feishu (Lark) documents via the Open API — create docs, add text/headings/lists/divider blocks with rich text formatting (bold, italic, inline code)."
version: 1.0.0
author: Hermes Agent
category: productivity
metadata:
  hermes:
    tags: [feishu, lark, doc, api, document]
---

# Feishu Doc API

Create Feishu (飞书) documents and write formatted content to them using the Open API. This skill documents the correct API usage, block types, and formatting.

## Prerequisites

- `FEISHU_APP_ID` and `FEISHU_APP_SECRET` configured in `~/.hermes/.env`
- Readable via `Path.home() / ".hermes" / ".env"`
- Python 3 + lark_oapi SDK (included in Hermes venv)

## How It Works

The Feishu docx v1 API works in two steps:
1. **Create document** → Get `document_id`
2. **Add content blocks** as children of the root page block

**Important:** Document root block_id = document_id. When adding children, use `document_id` as both the `document_id` and `block_id` parameter.

## Block Types That Work

| Block Type | Value | Field Name | Description |
|-----------|:-----:|-----------|-------------|
| Text | 2 | `text` | Normal text (NOT block_type 1 — that's Page) |
| Heading 1 | 3 | `heading1` | Large heading |
| Heading 2 | 4 | `heading2` | Medium heading |
| Heading 3 | 5 | `heading3` | Small heading |
| Unordered list | 12 | `bullet` | Bullet point |
| Ordered list | 13 | `ordered` | Numbered list |
| Divider | 22 | `divider` | Horizontal line |

## API Endpoints

### 1. Create Document

```
POST /open-apis/docx/v1/documents
Body: {"title": "Document Title"}
Response: {"data": {"document": {"document_id": "xxx"}}}
Document URL: https://bytedance.feishu.cn/docx/{document_id}
```

### 2. Add Content Blocks

```
POST /open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children
Body: {
  "children": [...],
  "index": 0
}
```

Where `index=0` appends after the title (first position), and both `document_id` and `block_id` are the same `doc_id`.

## Block Structure

### Text block (block_type=2)
```json
{
  "block_type": 2,
  "text": {
    "elements": [{"text_run": {"content": "Hello world"}}]
  }
}
```

### Headings (block_type=3/4/5)
```json
{
  "block_type": 3,
  "heading1": {
    "elements": [{"text_run": {"content": "Heading Text"}}]
  }
}
```

### Lists (block_type=12 bullet, 13 ordered)
```json
{
  "block_type": 12,
  "bullet": {
    "elements": [{"text_run": {"content": "List item"}}]
  }
}
```

### Divider (block_type=22)
```json
{"block_type": 22, "divider": {}}
```

### Rich Text Styling

Apply styles via `text_element_style` on `text_run`:

```json
{
  "text_run": {
    "content": "styled text",
    "text_element_style": {
      "bold": true,
      "italic": true,
      "inline_code": true
    }
  }
}
```

### Mixed-styled text (multiple elements in one block)
```json
{
  "block_type": 2,
  "text": {
    "elements": [
      {"text_run": {"content": "Normal "}},
      {"text_run": {"content": "Bold", "text_element_style": {"bold": true}}},
      {"text_run": {"content": " Italic", "text_element_style": {"italic": true}}}
    ]
  }
}
```

## Full Python Example

```python
import json
from pathlib import Path
from urllib.request import Request, urlopen

env_path = Path.home() / ".hermes" / ".env"
app_id = app_secret = None
for line in env_path.read_text().splitlines():
    if line.startswith("FEISHU_APP_ID="):
        app_id = line.split("=", 1)[1].strip().strip("\"'")
    elif line.startswith("FEISHU_APP_SECRET="):
        app_secret = line.split("=", 1)[1].strip().strip("\"'")

BASE = "https://open.feishu.cn"

def api(method, path, token, body=None):
    """Make Feishu API call. Token must be retrieved first."""
    data = json.dumps(body, ensure_ascii=False).encode() if body else None
    req = Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode())
        raise

# Step 0: Get token
r = api("POST", "/open-apis/auth/v3/tenant_access_token/internal", None,
        {"app_id": app_id, "app_secret": app_secret})
token = r["tenant_access_token"]

# Step 1: Create document
r = api("POST", "/open-apis/docx/v1/documents", token, {"title": "My Doc"})
doc_id = r["data"]["document"]["document_id"]
doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"

# Step 2: Add content blocks
children = [
    {"block_type": 2, "text": {"elements": [{"text_run": {"content": "Hello!"}}]}},
    {"block_type": 22, "divider": {}},
    {"block_type": 2, "text": {"elements": [
        {"text_run": {"content": "Bold text", "text_element_style": {"bold": True}}}
    ]}},
]
api("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children", token, {
    "children": children, "index": 0
})
```

## Token Handling

Always get a fresh `tenant_access_token` for each batch of operations:

```python
r = api("POST", "/open-apis/auth/v3/tenant_access_token/internal", None,
        {"app_id": app_id, "app_secret": app_secret})
token = r["tenant_access_token"]  # valid for ~2 hours
```

## Known Limitations

- **Heading blocks (heading2/3):** Do NOT support `text_color`, `align` (centering), or custom styling on the heading field. These cause `field validation failed` (code 99992402) or `invalid param` (code 1770001). Only plain text elements with `bold` work reliably on heading blocks.
- **Code blocks** (block_type=16) do NOT work via the children API (field validation fails)
- **Quote/Blockquote** (block_type=26) does NOT work (invalid param error)
- Only one level of nesting (children of root page block)
- **Write blocks in batches of 3-4 per API call** — ~42+ blocks in one call fails with 400. Use incrementing index for each batch.
- The Feishu lark_oapi SDK's `CreateDocumentBlockChildrenRequest` builder may fail with domain=None when requests are manually constructed — prefer raw HTTP API

## Script: create-feishu-briefing-doc.py

See `scripts/create-feishu-briefing-doc.py` for a working example. It reads credentials from `~/.hermes/.env`, creates a doc, writes blocks in batches of 4, and prints the doc URL.
