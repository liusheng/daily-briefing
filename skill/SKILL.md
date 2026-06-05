---
name: daily-briefing
description: "Daily AI briefing pipeline — cron-powered 4-stage workflow: 6-source data collection (GitHub, HN, TechCrunch, 雷锋网, IT之家), Feishu doc generation, cover image, and 3-bare-message delivery."
version: 3.0.0
author: Hermes Agent
license: MIT
category: devops
metadata:
  hermes:
    tags: [cron, automation, briefing, news, digest, data-collection, scheduling]
    related_skills: [arxiv, blogwatcher, hermes-agent]
---

# Daily Briefing

Set up recurring cron jobs that collect data from multiple external sources and compile structured daily briefings delivered to the user.

## When to Load This Skill

- User asks: "每天帮我总结AI领域的科技动态", "set up a daily briefing", "每天推送新闻", "morning digest", "每日日报"
- User wants recurring automated data collection + summarization
- You are about to create a cron job for a periodic news/digest/briefing task

---

## System Architecture & Workflow

The daily briefing is a **pipeline** with 4 stages, orchestrated by a cron job. Here's the full execution flow:

```
┌─────────────────────────────────────────────────────┐
│ CRON JOB: 3b93814c9436                              │
│ Schedule: 0 7 * * * (UTC) = 15:00 Beijing           │
│ Skills loaded: daily-briefing, feishu-doc-api        │
│ Prompt: feishu-doc-briefing-prompt.md template       │
└──────────────┬──────────────────────────────────────┘
               │ triggers at scheduled time
               ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 1: DATA COLLECTION                            │
│ Runs: collect-all.sh                                │
│ Fires 6 Python fetchers in parallel:                │
│   ├─ fetch-github-head.py     → GitHub 头部 ⭐      │
│   ├─ fetch-github-rising.py   → GitHub 新锐         │
│   ├─ fetch-hackernews.py      → Hacker News AI 热帖 │
│   ├─ fetch-techcrunch.py      → TechCrunch 首页     │
│   ├─ fetch-leiphone.py        → 雷锋网 AI 频道      │
│   └─ fetch-ithome.py          → IT之家 AI 标签      │
│ Each source failure is isolated — one broken        │
│ source never blocks the rest.                       │
└──────────────┬──────────────────────────────────────┘
               │ raw headlines + metadata feed
               ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 2: CONTENT GENERATION                         │
│ Agent reads collected data, selects 6-8 items,      │
│ writes editorial analysis, updates and runs:         │
│ /root/create_daily_briefing_doc.py                  │
│ → Creates Feishu doc with structured blocks         │
│ → Outputs: DOC_URL + TITLE lines                    │
└──────────────┬──────────────────────────────────────┘
               │ DOC_URL, TITLE, selected headlines
               ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 3: COVER GENERATION                           │
│ Runs: scripts/generate-cover.py                     │
│ → 1200×630 PNG, dark navy gradient                  │
│ → Title: "监听站1379", subtitle: "DAILY BRIEFING"   │
│ → Up to 5 headlines + date                          │
└──────────────┬──────────────────────────────────────┘
               │ /tmp/daily_cover.png
               ▼
┌─────────────────────────────────────────────────────┐
│ STAGE 4: DELIVERY                                   │
│ Exactly 3 send_message calls (no extra text):       │
│   1. DOC_URL (bare link)                            │
│   2. TITLE (bare title text)                        │
│   3. MEDIA:/tmp/daily_cover.png (bare cover)         │
│ Retry on rate limit: 60s wait × 3                   │
│ End with [SILENT]                                   │
└─────────────────────────────────────────────────────┘
```

**Key files and their roles:**

| File | Role | Location |
|------|------|----------|
| Cron prompt | Orchestration script (the 4-stage instructions) | `templates/feishu-doc-briefing-prompt.md` |
| `collect-all.sh` | Runs all 6 data fetchers, aggregates output | `scripts/collect-all.sh` |
| `fetch-*.py` (×6) | One per data source, scrapes/API-calls, prints headlines | `scripts/` |
| `create_daily_briefing_doc.py` | Takes collected data → writes Feishu doc via API | `/root/create_daily_briefing_doc.py` |
| `generate-cover.py` | Generates daily cover image | `scripts/generate-cover.py` |
| SKILL.md | This document — spec, format rules, reference | `devops/daily-briefing/SKILL.md` |

**⚠️ Data sources are defined in TWO places — keep them in sync:**
1. `scripts/collect-all.sh` — the actual execution (determines what gets fetched)
2. SKILL.md → Data Sources section below — the documentation (must match)

When adding a new source, update BOTH. When removing a source, update BOTH.

## Quick Reference

| Step | Action |
|------|--------|
| List jobs | `cronjob(action='list')` |
| Test run | `cronjob(action='run', job_id='3b93814c9436')` → check `~/.hermes/cron/output/<job_id>/` |
| Update prompt | Edit `templates/feishu-doc-briefing-prompt.md`, then `cronjob(action='update', job_id='...', prompt='<new prompt>')` |
| Add/remove source | Update both `scripts/collect-all.sh` AND the Data Sources section below |
| Create new job | `cronjob(action='create', name='...', schedule='0 1 * * *', prompt='...', skills=['daily-briefing', 'feishu-doc-api'])` |
| Remove job | `cronjob(action='remove', job_id='...')` |

## Data Sources

The briefing collects from **6 sources** via independent Python fetchers orchestrated by `collect-all.sh`. Each source runs in isolation — one failure never blocks the rest.

### Active Sources (matching collect-all.sh)

| # | Source | Script | Method | Category |
|---|--------|--------|--------|----------|
| 1 | **GitHub 头部项目** | `fetch-github-head.py` | Search API → high-star AI repos (⭐>) | 代码/开源 |
| 2 | **GitHub 新锐项目** | `fetch-github-rising.py` | Search API → emerging repos (<30k ⭐) | 代码/开源 |
| 3 | **Hacker News** | `fetch-hackernews.py` | Firebase API → AI keyword filter (min score ≥30) | 社区讨论 |
| 4 | **TechCrunch** | `fetch-techcrunch.py` | HTML scrape → h2/h3 headlines | 国际科技媒体 |
| 5 | **雷锋网 AI 频道** | `fetch-leiphone.py` | HTML scrape → h3 titles (leiphone.com/category/ai) | 国内科技媒体 |
| 6 | **IT之家 AI 标签** | `fetch-ithome.py` | HTML scrape → h2 titles (ithome.com/tag/ai) | 国内科技媒体 |

**The model (AI agent) decides final selection** — not all fetched headlines make it into the briefing. Quality > quantity: 6-8 items total across all sections. The agent reads the combined output and picks the most interesting/important items, mixing domestic and international sources freely.

### Adding a New Source

Two-file change required (keep them in sync):

1. **Create the fetcher script** at `scripts/fetch-<source>.py`
   - Accept no arguments, print headlines to stdout, exit 0 on success
   - On failure: print error to stderr, exit 1
   - Template pattern: see any existing fetcher (urllib + regex, ~30 lines)

2. **Register in `collect-all.sh`** — add an entry to the `sources` array:
   ```bash
   sources=(
       ...
       "新源名称:fetch-newsource.py"
   )
   ```

3. **Update this section** — add a row to the Active Sources table above

4. **Update the cron prompt template** at `templates/feishu-doc-briefing-prompt.md` — mention the new source in the Step 1 script description

### Source Failure Behavior

- Each fetcher exits 1 on failure (timeout, parse error, empty results)
- `collect-all.sh` captures failures and continues to the next source
- The model runs with whatever data is available
- If ALL sources fail → output `[SILENT]` (no delivery, no noise)

### Tested Sources That DON'T Work (do not retry)

| Source | Why Failed |
|--------|-----------|
| 36氪 search API | Anti-scraping block |
| 量子位 (jiqizhixin) | JS rendering required |
| 虎嗅AI | JS rendering required |
| 澎湃AI | No AI-specific content feed |
| 中国科技网 | No parseable article structure |

---

## Creating New Briefing Jobs

This section covers how to build a new cron job for a briefing — useful when setting up a fresh pipeline or creating a variant for a different topic/target.

### Timezone Handling

The Hermes cron daemon runs in **UTC**. To schedule at the user's local time, convert:

| Local Time (Beijing UTC+8) | UTC Schedule |
|---------------------------|--------------|
| 09:00 | `0 1 * * *` |
| 08:00 | `0 0 * * *` |
| 20:00 | `0 12 * * *` |

**Rule:** `0 H * * *` where H = (local_hour - UTC_offset) in 0-23. For Beijing (UTC+8): `0 1 * * *` = 9 AM local.

### Cron Prompt Design Principles

Cron jobs run in **isolated sessions** with no conversation history. The prompt must be fully self-contained.

**1. Be explicit about error handling:**
```markdown
⚠️ All API calls: 10-15s timeout. Skip on failure. Generate report if ≥1 source works. [SILENT] if all fail.
```

**2. Use scripts, not inline curl (preferred approach):**
For the current implementation, data collection is done via Python scripts run through `collect-all.sh`. This is cleaner than inline curl commands buried in a cron prompt. The scripts handle timeouts, error isolation, and output formatting. When building a new briefing, prefer this pattern.

If scripts aren't practical (one-off, simple source), provide exact curl commands with parse snippets.

**3. Define the exact output format:**
Provide a fill-in template the agent populates. Include fallback text for empty sections.

**4. Delivery via `send_message` with retry + `[SILENT]`:**
```markdown
If delivery fails (rate limited), wait 60s and retry up to 3 times.
On success, end with [SILENT] to prevent framework double-delivery.
```

### Data Source Reference (Raw API Commands)

These are the raw API/curl equivalents of what the Python fetcher scripts do. Kept for reference when debugging a broken script or adding a source without writing a full Python fetcher.

<details>
<summary>GitHub Trending (Search API)</summary>

```bash
curl -s --max-time 12 "https://api.github.com/search/repositories?q=ai+OR+machine+learning+OR+LLM&sort=stars&order=desc&per_page=5"
```
→ Fetcher: `fetch-github-head.py`
</details>

<details>
<summary>GitHub Rising (New/Active, <30k stars)</summary>

```bash
curl -s --max-time 10 "https://api.github.com/search/repositories?q=ai+OR+agent+OR+LLM&sort=stars&order=desc&per_page=10"
```
→ Fetcher: `fetch-github-rising.py` (API + post-filter)
</details>

<details>
<summary>Hacker News (Firebase API)</summary>

```bash
curl -s --max-time 8 "https://hacker-news.firebaseio.com/v0/topstories.json"
```
→ Fetcher: `fetch-hackernews.py` (fetches top 30, filters by AI keywords, min score 30)
</details>

<details>
<summary>TechCrunch (Homepage scrape)</summary>

```bash
curl -sL --max-time 12 -H "User-Agent: Mozilla/5.0" "https://techcrunch.com/"
```
→ Fetcher: `fetch-techcrunch.py` (extracts h2/h3, HTML entity decode, top 8)
</details>

<details>
<summary>雷锋网 AI 频道 (h3 scrape)</summary>

```bash
curl -sL --max-time 12 "https://www.leiphone.com/category/ai"
```
→ Fetcher: `fetch-leiphone.py`
</details>

<details>
<summary>IT之家 AI 标签 (h2 scrape)</summary>

```bash
curl -sL --max-time 10 "https://www.ithome.com/tag/ai"
```
→ Fetcher: `fetch-ithome.py`
</details>

### 🇨🇳 Domestic Source Guidelines

When including Chinese/domestic news sources in a briefing:

**DO:**
- Provide Python fetcher scripts (same pattern as international sources)
- Mark domestic sources as optional (skip if no value)
- Let the model decide inclusion based on merit
- Test each new source before adding to production

**DON'T:**
- Say "跳过或简单搜索" — gives the agent an excuse to skip
- Add hard requirements like "must include ≥1 domestic item"
- Assume a source works without testing (many Chinese tech sites use JS rendering)

---

## Content Format Rules

**⚠️ VALIDATED FORMAT — do not modify without user approval.** This format was settled through multiple correction iterations. Changing sections, headings, or structure causes user frustration.

### Title

`今日AI简报 | {关键词1} · {关键词2} | {YYYY.MM.DD}`

### Section Structure (fixed order)

**Total: 6-8 items.** One core focus per day. Quality over quantity.

| # | Section | Count | Rules |
|---|---------|:-----:|-------|
| 1 | 开场总述 | 1段 | Narrative, day's core trend |
| 2 | ▸ 要点预览 | **2** | Bold keywords + one-liner each |
| 3 | 🔥 科技圈AI动态 | **2** | Domestic + international mixed, no source priority |
| 4 | 🔥 GitHub 头部项目 | **1-2** | High-star repos — **KEEP SEPARATE from 新锐** |
| 5 | 🔥 新锐项目 | **2** | Emerging repos — **KEEP SEPARATE from 头部** |
| 6 | 💬 社区热议 | **0-2** | Only if good HN/TechCrunch content |
| 7 | 📝 编辑点评 | 1-2段 | Deep analysis, connecting threads |

### Non-Negotiable Rules

| Rule | Detail |
|------|--------|
| **No section merging** | 头部项目 and 新锐项目 MUST be separate sections |
| **No 今日互动** | This section was removed per user request |
| **No 数据来源 footer** | No "数据来源：..." line at the bottom of the doc |
| **Heat indicator** | Must use `🔥` (U+1F525), NOT `\u01c0` (renders as ǀ) |
| **Entry length** | 2-3 sentences per item (not 1, not 4+) |
| **Quote handling** | Use single-quote Python strings when content has Chinese `""` quotes |
| **Style** | Narrative analysis, each item has independent angle, not a feed dump |
| **Rotation** | Hot topics: pick ~2, let the rest surface on subsequent days |
| **No branding** | Never add "Hermes Agent" branding |
| **Platform-independent** | Format is the same whether delivering to Feishu doc or WeChat |

---

## Delivery Rules

### Feishu (Primary — Active)

Exactly **3 bare `send_message` calls**, in this order, with zero additional text on any of them:

```
1. send_message(target="feishu", message="DOC_URL")
2. send_message(target="feishu", message="TITLE")
3. send_message(target="feishu", message="MEDIA:/tmp/daily_cover.png")
```

**No prefixes, no emoji, no explanations, no greetings, no punctuation.** The user said: "不要任何无关的信息".

If any send fails (rate limited): wait 60s, retry up to 3 times. End with `[SILENT]`.

### WeChat (Fallback)

Personal subscription accounts (个人订阅号) cannot auto-publish via API. Workflow:

```
Hermes generates → sends to user's WeChat → user pastes in 微信公众平台 App (~30s/day)
```

Delivery: split into 2 messages with 30-90s delay. Title (no emoji) first, then MEDIA:cover + body. See `references/wechat-official-account-format.md` for full template.

### [SILENT] Protocol

- **All sources fail** → output `[SILENT]`, no delivery attempted
- **Delivery succeeds after retry** → output `[SILENT]` (prevents framework double-delivery)
- **Delivery fails after 3 retries** → output `[SILENT]`, check `~/.hermes/cron/output/<job_id>/` for saved content

---

## Common Pitfalls

### P1: Data Source Mismatch (Script vs Skill Doc)
**Symptom:** `collect-all.sh` fetches sources not listed in SKILL.md, or SKILL.md documents sources not in the script.
**Fix:** When adding/removing a source, update BOTH `scripts/collect-all.sh` AND the Data Sources section above. The Data Sources section is the authoritative list — scripts are the implementation.

### P2: Merging 头部项目 + 新锐项目 Sections
**Symptom:** Briefing has a single "GitHub Projects" section instead of two separate ones.
**Fix:** These are intentionally separate. Always use two H2 headings with SP() divider between them.

### P3: Script-Skill Format Drift
**Symptom:** `/root/create_daily_briefing_doc.py` output doesn't match the Format Rules table.
**Fix:** Every time format rules change, update the script. The skill is the spec, the script is the implementation. Verified drift patterns:
- `\u01c0` instead of `🔥` for heat indicators
- "数据来源" footer sneaking back in
- 1-sentence entries where 2-3 required
- Double-quoted P("...") strings breaking on Chinese `""` quotes → use P('...')

### P4: Feishu Delivery Has Extra Text
**Symptom:** Messages include prefixes like "日报链接：" or "完整日报：".
**Fix:** 3 bare messages. Nothing else. The user was explicit about this.

### P5: Empty GitHub Rising Results
**Symptom:** `q=created:>$DATE+AND+(ai+OR+agent+OR+LLM)` returns 0 results.
**Fix:** Broad search without date filter + post-filter by star count and activity. Or scrape GitHub trending directly. 1 result is acceptable — don't pad.

### P6: Agent Produces "Done" Without Content
**Symptom:** Cron output is "日报已生成！✅" with no actual content.
**Fix:** The prompt template already includes explicit data collection + format instructions. If this happens, the agent didn't follow the template — check the cron output file for what actually happened.

### P7: WeChat Rate Limiting
**Symptom:** Messages 3+ silently blocked.
**Fix:** For WeChat, use 2-message split. If prior messages were sent, wait 90s+ between sends. Body uses ASCII digits + `->` arrows, no markdown, no Unicode special chars.

## Testing a Briefing Job

1. Test with `cronjob(action='run', job_id='<id>')`
2. Check output at `~/.hermes/cron/output/<job_id>/<timestamp>.md` — look for the "## Response" section
3. If response is empty or says "done" without content, the prompt needs more structure

---

## Reference: Templates & Assets

### Cron Prompt Templates

| File | Status | Description |
|------|--------|-------------|
| `templates/feishu-doc-briefing-prompt.md` | **Canonical** (v2.3) | Uses collect-all.sh, 6 sources, 3-bare-message Feishu delivery |
| `templates/ai-daily-briefing-prompt.md` | Legacy | Inline curl commands, old delivery format. Kept for reference. |

### Reference Docs

| File | Content |
|------|---------| 
| `references/feishu-doc-briefing-api.md` | Feishu doc creation API: auth, block types, batching, failure modes |
| `references/feishu-color-reference.md` | Complete tested color table for Feishu text_color |
| `references/wechat-official-account-format.md` | WeChat OA publishing template and formatting guide |
| `references/wechat-account-setup.md` | WeChat OA registration: type comparison, API permissions |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/collect-all.sh` | Orchestrator — runs all 6 fetchers sequentially |
| `scripts/fetch-github-head.py` | GitHub Search API → high-star AI repos |
| `scripts/fetch-github-rising.py` | GitHub Search API → emerging repos (<30k ⭐) |
| `scripts/fetch-hackernews.py` | HN Firebase API → AI keyword filter |
| `scripts/fetch-techcrunch.py` | TechCrunch HTML scrape → h2/h3 headlines |
| `scripts/fetch-leiphone.py` | 雷锋网 AI 频道 HTML scrape → h3 titles |
| `scripts/fetch-ithome.py` | IT之家 AI 标签 HTML scrape → h2 titles |
| `scripts/generate-cover.py` | 1200×630 PNG cover image (Pillow + Noto Sans CJK) |

### External Files (outside skill dir, in active use)

| File | Role |
|------|------|
| `/root/create_daily_briefing_doc.py` | Writes briefing content to Feishu doc via Open API |

### GitHub Repo

All assets tracked at `github.com/liusheng/daily-briefing`. Push updates when prompt, script, or format rules change.

---

## Reference: Feishu API Quick Reference

Kept for the `create_daily_briefing_doc.py` script authoring.

### Block Types

| Type | Value | Field |
|------|:-----:|-------|
| Text | 2 | text |
| Heading 1 | 3 | heading1 |
| Heading 2 | 4 | heading2 |
| Heading 3 | 5 | heading3 |
| Bullet | 12 | bullet |
| Ordered | 13 | ordered |
| Divider | 22 | divider |

### text_color Mapping

| Value | Color |
|:-----:|-------|
| 1 | Red |
| 2 | Orange / Yellow |
| 3 | Green |
| 4 | Teal / Cyan |
| **5** | **Blue** ✅ (section headings) |
| 6 | Purple |
| 7 | Pink |

### H2 Helper

```python
def H2(text):
    return {"block_type": 4, "heading2": {
        "elements": [{"text_run": {"content": text, "text_element_style": {"text_color": 5}}}],
        "style": {"align": 2}
    }}
```

---

## Reference: WeChat OA Formatting Cheatsheet

For the fallback WeChat delivery workflow (user copy-pastes from WeChat to 公众号 App).

| Element | Rule |
|---------|------|
| Title | Pure text, NO emoji: `AI 科技日报 | {主题} · {YYYY年M月D日}` |
| Section separators | `━━━` (Unicode box-drawing) |
| Emoji (body) | 📌 focus · 🔥 GitHub · 💬 discussion · 📝 editorial |
| Numbering | ASCII digits: `1. 2. 3.` (NOT Unicode ordinals) |
| Links | `-> ` prefix (ASCII arrow, not →) |
| Footer | `数据来源: GitHub · Hacker News · TechCrunch · 雷锋网 · IT之家` |
| Editorial | `编辑点评` (never `小编点评`) |
| No Markdown | WeChat App strips `**bold**`, `[links]`, etc. |
| Body tail | Ends at data source footer. NO publishing instructions. |

---

## Related Skills

- **`feishu-doc-api`** — Create Feishu docs and write formatted blocks. Used for the doc generation stage.
