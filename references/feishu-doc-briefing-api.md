# Feishu Doc Briefing: Verified Script & API Reference

## Script Path
`/root/create_briefing_v2.py` — verified working Python script that:
1. Reads Feishu credentials from `~/.hermes/.env`
2. Creates a doc with the day's title
3. Writes content blocks in batches of 4
4. Outputs the doc URL

## Batch Writing Pattern
The API rejects >8 blocks in a single call. Always write in batches of 3-4 blocks:

```python
for i in range(0, len(children), 4):
    batch = children[i:i+4]
    r = api("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children", token,
            {"children": batch, "index": i})
```

The `index` parameter controls block position. Start at 0 and increment by the batch size.

## Block Reference (Verified Working)

| Block Type | Value | Field | Notes |
|-----------|:-----:|-------|-------|
| Text | 2 | `text` | Use `elements` array, each element = `{"text_run": {"content": "...", "text_element_style": {...}}}` |
| Heading 2 | 4 | `heading2` | Larger heading — NO text_color or align supported |
| Heading 3 | 5 | `heading3` | Medium heading — NO text_color or align supported |
| Divider | 22 | `divider` | Use `{}` as value |

## Common Failure Modes

| Error | Code | Cause |
|-------|:----:|-------|
| `field validation failed` | 99992402 | Invalid field on block (e.g. text_color on heading) |
| `invalid param` | 1770001 | Unsupported block type or field structure |
| `block not support to create` | 1770029 | Trying to add children to wrong block_type |
| HTTP 400 + empty body | — | Too many blocks in single API call |

## Token Lifecycle
- Tenant access token valid for ~2 hours
- Get fresh token per script run
- No need to refresh mid-run (script completes in <30s)

## Auth
Credentials in `~/.hermes/.env`:
```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
```
Read via `Path.home() / ".hermes" / ".env"`.
