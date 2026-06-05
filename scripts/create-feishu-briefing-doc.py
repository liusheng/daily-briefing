#!/usr/bin/env python3
"""
Create a Feishu doc with formatted content blocks.
Reads credentials from ~/.hermes/.env.
Usage: python3 create-feishu-briefing-doc.py
"""
import json, datetime
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
    data = json.dumps(body).encode() if body else None
    req = Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        if hasattr(e, 'read'):
            return json.loads(e.read().decode())
        raise

# Get token
r = api("POST", "/open-apis/auth/v3/tenant_access_token/internal", None,
        {"app_id": app_id, "app_secret": app_secret})
token = r["tenant_access_token"]

# Create document
r = api("POST", "/open-apis/docx/v1/documents", token, {"title": "My Document"})
doc_id = r["data"]["document"]["document_id"]
doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"
print(f"DOC_URL:{doc_url}")

# Build blocks
def TX(elements):
    if not isinstance(elements, list): elements = [elements]
    return {"block_type": 2, "text": {"elements": elements}}

def H2(text):
    return {"block_type": 4, "heading2": {"elements": [{"text_run": {"content": text}}]}}

def DV():
    return {"block_type": 22, "divider": {}}

def B(content, bold=False):
    el = {"text_run": {"content": content}}
    if bold:
        el["text_run"]["text_element_style"] = {"bold": True}
    return el

def P(text):
    return TX([B(text)])

def SP():
    return TX([B("")])

children = [
    P("Opening paragraph here."),
    DV(),
    H2("Section Title"),
    SP(),
    P("Content paragraph."),
    DV(),
    P("Footer: data sources here."),
]

# Write in batches of 4
for i in range(0, len(children), 4):
    batch = children[i:i+4]
    api("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children", token,
        {"children": batch, "index": i})

print(f"DONE: {doc_url}")
