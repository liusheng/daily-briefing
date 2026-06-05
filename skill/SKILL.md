---
name: daily-briefing
description: "Set up and manage daily automated briefing jobs — cron-powered data collection from multiple sources (GitHub, ArXiv, Hacker News, RSS, APIs) with structured summarization and timed delivery."
version: 2.3.0
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

## Quick Reference

| Step | Action |
|------|--------|
| Create | `cronjob(action='create', name='...', schedule='0 1 * * *', prompt='...', skills=['...'])` |
| Update | `cronjob(action='update', job_id='...', prompt='...')` |
| Test | `cronjob(action='run', job_id='...')` then read output from `~/.hermes/cron/output/<job_id>/` |
| List | `cronjob(action='list')` |
| Remove | `cronjob(action='remove', job_id='...')` |

## Timezone Handling

The Hermes cron daemon runs in **UTC**. To schedule at the user's local time, convert:

| Local Time (Beijing UTC+8) | UTC Schedule |
|---------------------------|--------------|
| 09:00 | `0 1 * * *` |
| 08:00 | `0 0 * * *` |
| 20:00 | `0 12 * * *` |

**Rule:** `0 H * * *` where H = (local_hour - UTC_offset) in 0-23. For Beijing (UTC+8): `0 1 * * *` = 9 AM local.

## Designing a Self-Contained Cron Prompt

Cron jobs run in **isolated sessions** with no conversation history. The prompt must be fully self-contained. Critical design principles:

### 1. Be Explicit About Error Handling

```markdown
⚠️ **所有API调用设置 max-time 10-15秒超时，超时或失败则跳过。只要至少有一个数据源成功就生成报告，全部失败才输出 [SILENT]。**
```

### 2. Provide Exact curl Commands

Don't say "fetch GitHub trending" — say exactly how:

```markdown
curl -s --max-time 12 "https://api.github.com/search/repositories?q=ai+OR+machine+learning&sort=stars&order=desc&per_page=6"
```

### 3. Include Parse Instructions

Each data source should include a Python one-liner or snippet to parse the response into readable text. Cron agents have Python + stdlib available.

### 4. Specify Fallback Behavior Per Section

```markdown
If this source fails, skip it and continue. The final report should still include whatever sections have data.
```

### 5. Define the Exact Output Template

Provide a fill-in-the-blanks template the agent should populate. Include fallback text for empty sections:

```markdown
**🔥 重点趋势**
(如果有足够数据就写洞察, 否则写"暂无突出趋势")

**📄 最新论文**
(如果API失败则跳过此节)
```

### 6. Use `send_message` with Retry + `[SILENT]`

Instead of relying on framework-level delivery (which has no retry logic), have the agent deliver the content itself via the `send_message` tool, with retry for rate limits, and end with `[SILENT]` to prevent the framework from double-delivering:

**Feishu delivery (primary):** Exactly 3 bare messages in order. No extra text on any of them.
```markdown
send_message(target="feishu", message="DOC_URL")
send_message(target="feishu", message="TITLE")
send_message(target="feishu", message="MEDIA:/tmp/daily_cover.png")
```

**WeChat delivery (fallback):** Split into 2 messages with retry delay. Title first, then body + cover.
```markdown
send_message(target="weixin", message="AI 科技日报 | 主题 · 日期")
# wait 30+ seconds
send_message(target="weixin", message="MEDIA:{cover_path}\n\n━━━\n\n📌 Focus section\n\n🔥 GitHub section\n\n💬 HN section\n\n📝 Editorial section\n\n数据来源: ...")
```

If delivery fails (rate limited), wait 60s and retry up to 3 times. On success, end with `[SILENT]`.

## Common Data Sources & Their API Commands

### GitHub Trending (Most Reliable)

```bash
curl -s --max-time 12 "https://api.github.com/search/repositories?q=ai+OR+machine+learning+OR+LLM&sort=stars&order=desc&per_page=6"
```

Parse with:
```python
import sys, json
data = json.load(sys.stdin)
for repo in data.get('items', [])[:6]:
    desc = (repo.get('description') or 'No description')[:80]
    print(f"🔥 {repo['full_name']} ⭐{repo['stargazers_count']}★ — {desc} ({repo.get('language') or 'N/A'})")
```

### GitHub New Projects (Past Week)

```bash
curl -s --max-time 10 "https://api.github.com/search/repositories?q=created:>$DATE+AND+(ai+OR+llm+OR+machine+learning)&sort=stars&order=desc&per_page=3"
```

Where `$DATE` = `$(date -d '7 days ago' +%Y-%m-%d)`

### ArXiv Latest Papers

```bash
curl -s --max-time 12 "https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=5"
```

Parse with XML library (stdlib). Note: ArXiv API is slow and may time out — always set `--max-time 12`.

### Hacker News AI Stories

```bash
curl -s --max-time 8 "https://hacker-news.firebaseio.com/v0/topstories.json" | python3 -c "
import sys, json, urllib.request
ids = json.load(sys.stdin)[:30]
kw = ['ai','llm','gpt','chatgpt','openai','anthropic','claude','gemini','deepseek','machine learning','neural','transformer','rag','agent','copilot','qwen','mistral','llama','stable diffusion','sora','gen ai']
for item_id in ids:
    try:
        req = urllib.request.Request(f'https://hacker-news.firebaseio.com/v0/item/{item_id}.json', headers={'User-Agent': 'Mozilla/5.0'})
        item = json.loads(urllib.request.urlopen(req, timeout=4).read())
        if item and item.get('title') and item.get('type') == 'story':
            t = item['title']
            if any(k in t.lower() for k in kw):
                print(f'🗞️ {t} (score:{item.get(\\\"score\\\",0)})')
                print()
    except:
        pass
\"
```

### 🇨🇳 雷锋网AI频道 (Domestic — Verified Working 2026.06.05)

Delivers AI-focused tech news from Chinese sources. Covers deep-tech AI research, industry applications, and academic conferences.

```bash
curl -sL --max-time 12 "https://www.leiphone.com/category/ai" | python3 -c "
import sys, re
html = sys.stdin.read()
titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
for i, t in enumerate(titles[:10]):
    t2 = re.sub(r'<[^>]+>', '', t).strip()
    if len(t2) > 5:
        print(f'{i+1}. {t2}')
"
```

Fallback: if empty or timeout, skip without affecting other sources.

### 🇨🇳 IT之家AI标签 (Domestic — Verified Working 2026.06.05)

Real-time AI product/industry news. Covers OpenAI, Apple, Meta, and domestic AI product launches and updates.

```bash
curl -sL --max-time 10 "https://www.ithome.com/tag/ai" | python3 -c "
import sys, re
html = sys.stdin.read()
titles = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
for i, t in enumerate(titles[:10]):
    t2 = re.sub(r'<[^>]+>', '', t).strip()
    if len(t2) > 5:
        print(f'{i+1}. {t2}')
"
```

Fallback: if empty or timeout, skip without affecting other sources.

**Note:** Other Chinese sources tested but failed due to JS rendering or anti-scraping: 36氪 search API (blocked), 量子位 (JS), 虎嗅AI (JS), 澎湃AI (no AI content), 中国科技网 (no parseable content). Do not retry these unless the site structure changes.

## Settled Format

**CRITICAL: This format was validated through multiple iterations with user corrections. Do NOT merge sections, rename headings, or change block structure without explicit approval. Breaking validated format causes user frustration.**

Title: `今日AI简报 | {keyword1} · {keyword2} | {YYYY.MM.DD}`

**Total: 6-8 items.** One core focus per day. Quality over quantity.

| Section | Count | Notes |
|---------|:-----:|-------|
| Opening paragraph | 1 | Narrative, day's core trend |
| ▸ Key points preview | **2** | Bold keywords + one-liner |
| 🔥 Technology AI News | **2** | Domestic + international mixed, **no prioritization** |
| 🔥 GitHub Head Projects | **1-2** | High-star headliners — **keep SEPARATE from 新锐** |
| 🔥 Rising Projects | **2** | Emerging low-star projects — **keep SEPARATE from 头部** |
| 📝 Latest Papers | **0-1** | Skip if uninteresting |
| 💬 Community Hot Discussion | **0-2** | Only if good content exists |
| 📝 Editorial | 1-2 paragraphs | Deep analysis connecting threads |

- **No** 💡 Daily Interaction section (removed per user request)
- **Data sources:** Include both domestic (雷锋网, IT之家) and international (GitHub, HN, ArXiv), mixed together — do NOT prioritize one over the other
- **Rotate:** If many hot topics, pick ~2 and let the rest surface naturally in subsequent days
- **Style:** Narrative deep analysis, each item has independent angle, not a feed dump
- **No** "Hermes Agent" branding anywhere

## Common Pitfalls

### 0. CRITICAL: Never Merge or Rename Established Sections
The user's briefing format was validated through multiple iterations. **Do NOT merge "头部项目" and "新锐项目" into a single "GitHub Projects" section** — they are intentionally separate. Similarly, do not rename sections, add/remove sections, or change the block structure without explicit user approval. Breaking a validated format causes user frustration and requires re-iteration. 
If you think a structural change would improve the format, propose it first rather than making it unilaterally.

Switching delivery channel (WeChat → Feishu doc) must NOT change the content format. The format is platform-independent.

### 1. Agent Produces "Done" Without Content
If the cron job agent just says "日报已生成并发送！✅" or similar without actual report content, the prompt was too vague. Fix: provide exact data-fetching commands, parse instructions, and output templates.

### 2. API Timeouts
External APIs (ArXiv, HN) frequently time out in cron sessions. Always use `--max-time` on curl and provide fallback sections in the output template.
### 3. WeChat Delivery Rate Limiting

Some platforms (especially WeChat/Weixin) have low per-minute rate limits. If the framework-level delivery fails with `rate limited`, the report is silently dropped — the cron status says "ok" but the user sees nothing.

**Root cause:** WeChat's per-minute rate limit typically allows only 1–2 messages through. If the agent tries to send content as 3+ separate messages (cover image, then text part 1, then text part 2, etc.), **messages 3+ will be blocked** and stay blocked even with 30–60s retries.

**Critical nuance — prior messages consume the window:** If the current conversation already sent 2–3 messages (including other non-briefing messages) before delivery, the rate limit window may already be saturated. In that case, wait **90s+** before the first retry, not the usual 30s.

**Fix (two parts):**

**Part A — Split into title + body (2 messages):**
Send the title (NO emoji, pure text) as the first `send_message` call. Send the body (MEDIA:cover + all content) as the second `send_message` call, with at least **30s** pause between them:
```markdown
send_message(target="weixin", message="AI 科技日报 | 主题 · 日期")
# wait 30+ seconds
send_message(target="weixin", message="MEDIA:{cover_path}\\n\\n━━━\\n\\n📌 Focus section\\n\\n🔥 GitHub section\\n\\n💬 HN section\\n\\n📝 Editorial section\\n\\n数据来源: ...")
```
If other messages were sent earlier in this conversation, wait **60–90s** between the title and body instead.

Body must use ASCII digits (1. 2. 3.), `->` arrows (not →), no markdown syntax, no Unicode special chars that cause editor spacing issues. Body ends at data source footer — NO publishing guide appended.

**Part B — Retry with `[SILENT]` as safety net (see Section 6):**
If a message fails with `rate limited`, wait 60s (not 30s) and retry up to 3 times. On success, end with `[SILENT]` to prevent framework-level double-delivery. On total failure after 3 retries, still output `[SILENT]` — the user won't get the message but the agent doesn't loop forever.

Test runs: if a test delivery fails from rate limiting, check the saved output at `~/.hermes/cron/output/<job_id>/` and show the user the content directly in the chat (don't keep hammering the platform).

### 4. WeChat Account Limitations

Personal subscription accounts (个人订阅号) **cannot auto-publish** via API — they lack `draft/free_publish` endpoints. Playwright browser automation is risky (cookie expiry 1–7 days, captcha/风控 triggers). The recommended semi-automated workflow is:

```
Hermes generates → sends to user's WeChat → user saves cover + pastes body in 微信公众平台 App (~30s/day)
```

If the user asks about full automation, explain the limitation and recommend this workflow. See `references/wechat-account-setup.md` for account type comparison, registration flow, and API permission details.

### 5. Script-Skill Format Drift

If the briefing is generated via a standalone Python script (e.g. `/root/create_daily_briefing_doc.py`), that script can silently diverge from the skill's format rules. Every time the skill's format table or rules change, **check and update the script** too. The script is the actual implementation — the skill doc is the spec. They must match.

Common drifts seen in production:
- Script merges 🔥 GitHub 头部项目 + 🔥 新锐项目 into a single "GitHub 项目" section (always use two separate H2 headings with SP() divider between them)
- Script uses `\\u01c0` (renders as ǀ) instead of `🔥` for heat indicators — both in tech news AND community section (HN scores like "594🔥")
- Script includes a "数据来源: ..." footer that was previously removed from the spec
- Script has 1-sentence entries where the spec says 2-3 sentences
- Script uses double-quoted Python strings `P("...")` when content contains Chinese curly quotes `""` — causes SyntaxError. Fix: use single-quote Python strings `P('...')` with `\\"` for Chinese quotes

When regenerating, always verify the output matches the format table below, not what the script happened to produce last time.
Cron agents work best with structured prompts that clearly separate "steps" from "format" from "rules". Use markdown headings to break it up.

### 6. Missing [SILENT] Handling
If there's genuinely nothing to report (all sources failed), the agent should output exactly `[SILENT]` to suppress delivery. Include this instruction explicitly.

### 7. GitHub New Projects API Returns Empty
When searching for new/rising AI repos, `q=created:>$DATE+AND+(ai+OR+agent+OR+LLM)` often returns 0 results even when trending repos exist. Fallback strategies:

- Remove the date filter and search broadly: `q=ai+OR+agent+OR+LLM&sort=stars&order=desc&per_page=10`, then filter results to repos under 30k stars that are recently active
- Scrape GitHub trending page directly: `curl -sL "https://github.com/trending/python?since=daily"` and extract repo links
- Use the expanded AI keyword list from the skill's HN section to broaden the query
- If only 1 new project is found, that's acceptable — do NOT pad with old projects

### 8. Feishu 3-Message Delivery: No Extra Text

For Feishu delivery (the primary channel for this user), send exactly 3 bare messages with zero additional text:
1. `send_message(target="feishu", message="DOC_URL")` — just the URL
2. `send_message(target="feishu", message="TITLE")` — just the title
3. `send_message(target="feishu", message="MEDIA:/tmp/daily_cover.png")` — just the cover

**Do NOT** add any prefix, emoji, explanation, greeting, or punctuation to any of these 3 messages. The user was explicit: "不要任何无关的信息". No "日报链接：", no "完整日报：", no "📄", no "⬇️ 封面", no "标题：".

**Why 3 separate messages:** The user deliberately requested this split. Sending everything in one message or adding explanatory text violates their settled preference. If you're unsure, err on the side of fewer characters — a bare URL for message 1, bare title for message 2, bare MEDIA: for message 3, and nothing else.

### 9. 🇨🇳 Domestic Source Collection — Provide Exact Commands, Let Model Decide

When including Chinese/domestic news sources in a briefing prompt, follow these rules:

**DO:**
- Provide exact curl commands with Python parse snippets (same as international sources)
- Mark domestic sources as optional (failure is acceptable, skip if empty)
- Let the model decide whether to include domestic items based on value and importance
- Test each proposed source before adding it to a cron prompt — many Chinese tech sites use JS rendering

**DON'T:**
- Say "跳过或简单搜索" — this gives the agent an excuse to skip all domestic collection
- Add hard requirements like "must include ≥1 domestic item" — the user explicitly rejected this
- Assume 36氪 works — its search API was tested and blocked by anti-scraping measures

**Tested Chinese sources for AI news (as of 2026.06):**
- ✅ 雷锋网AI频道 (leiphone.com/category/ai) — works, curl + h3 title scrape
- ✅ IT之家AI标签 (ithome.com/tag/ai) — works, curl + h2 title scrape
- ❌ 36氪 search API — blocked
- ❌ 量子位 / 虎嗅AI / 澎湃AI — JS rendering or no AI content

## Testing a Briefing Job

1. Create the job with `cronjob(action='create', ...)`
2. Test with `cronjob(action='run', job_id='...')`
3. Check output at `~/.hermes/cron/output/<job_id>/<timestamp>.md`
4. Look for actual content in the "## Response" section at the end of the file
5. If the response is empty, meta-only, or says "done" without data — **the prompt needs more structure**
6. Iterate: update the prompt with `cronjob(action='update', job_id='...', prompt='...')`, then re-run

## Reference Templates & Assets

This skill includes several reference files and scripts:

### 📡 Data Collection Scripts (`scripts/`)

These Python scripts fetch headlines from each source independently:

| Script | Source | Method |
|--------|--------|--------|
| `fetch-github-head.py` | GitHub high-star AI repos | Search API |
| `fetch-github-rising.py` | GitHub low-star active repos | Search API + filter |
| `fetch-hackernews.py` | Hacker News AI stories | Firebase API + keyword filter |
| `fetch-techcrunch.py` | TechCrunch homepage | HTML scrape (h2/h3) |
| `fetch-leiphone.py` | 雷锋网AI频道 | HTML scrape (h3) |
| `fetch-ithome.py` | IT之家AI标签 | HTML scrape (h2) |

**`collect-all.sh`** — Run all 6 fetchers sequentially and combine output:
```bash
bash ~/.hermes/skills/devops/daily-briefing/scripts/collect-all.sh
```
Each script exits 1 on failure and `collect-all.sh` continues anyway, so one broken source won't block the rest. The combined output is a clean text feed the AI agent can read and select from.

### Other Assets

- **`templates/ai-daily-briefing-prompt.md`** — Full AI news briefing cron prompt template with exact curl commands, parse snippets, error handling, and output format. Load with `skill_view('daily-briefing', 'templates/ai-daily-briefing-prompt.md')` and adapt.
- **`references/wechat-official-account-format.md`** — Complete formatting guide, template, and workflow for publishing daily briefings to WeChat Official Account (个人订阅号). Includes cover image workflow, title format, section structure, and publishing instructions.
- **`references/wechat-account-setup.md`** — WeChat Official Account registration guide: type comparison (personal vs enterprise), registration flow, naming advice, avatar design tips, and API permission limitations.
- **`references/feishu-doc-briefing-api.md`** — Working API sequence and Python template for creating Feishu doc briefings. Covers auth, block types, batching rules, and common failure modes.
- **scripts/generate-cover.py** — Self-contained Python script to generate a 1200×630 cover image (Pillow + Noto Sans CJK + DejaVu). Dark navy gradient, "监听站1379" title (user's 公众号 name), "DAILY BRIEFING" tagline, date, up to 5 headlines, decorative dots, no data source footer. Run via `python3 generate-cover.py --date "..." --headlines "h1|h2|h3|h4|h5" --output out.png`.
- **GitHub repo** — Full briefing system assets (skill, scripts, references, templates) are tracked at `github.com/liusheng/daily-briefing`. Push updates there when the cron prompt, script, or format rules change.

## Related Skills

- **`feishu-doc-api`** — Create Feishu docs and write formatted content (text, headings, lists, rich text). Used for Format C (飞书文档版) briefing delivery.

## Feishu Doc Delivery + Cover Image Workflow

### Feishu Delivery: 3 Bare Messages (verified 2026.06.05)

**CRITICAL: The user requires exactly 3 separate `send_message` calls with NO extra text on any of them. No explanations, prefixes, emoji, greetings, or punctuation. Each message is exactly one thing — bare.**

Per user request (settled 2026.06.05), the daily briefing workflow is:

1. **Generate Feishu doc** — write structured content via `/root/create_daily_briefing_doc.py`
2. **Extract TITLE** — script outputs `TITLE:今日AI简报 | ...` and `DOC_URL:https://...`
3. **Generate cover image** — use `scripts/generate-cover.py` with up to 5 headlines
4. **Send exactly 3 messages, in this order, each with nothing else:**

```python
# Message 1: doc link only (no prefix, no emoji)
send_message(target="feishu", message=doc_url)

# Message 2: title text only (no prefix, no emoji)
send_message(target="feishu", message=title)

# Message 3: cover image only (no caption, no prefix)
send_message(target="feishu", message=f"MEDIA:{cover_path}")
```

If any send fails (rate limited), wait 60s and retry up to 3 times. Output `[SILENT]` after all 3 are sent.

The cover script produces 1200×630 PNG, no data source footer, title reads "监听站1379".
Full briefing system assets mirrored at `github.com/liusheng/daily-briefing`.

### Format Rules (User-Verified) — 精确计数版

**核心原则:** 每天一个核心焦点角度, 总产量 **6-8条**, 宁缺毋滥, 岔开发。

| 板块 | 数量 | 结构 |
|------|:----:|------|
| 开场总述 | 1段 | 当日核心焦点叙事 |
| ▸ 要点预览 | **2条** | 加粗关键词 + 一句话 |
| 🔥 科技圈AI动态 | **2条** | 国际+国内混排,不分来源,不优先 |
| 🔥 GitHub 头部项目 | **1-2条** | 独立板块, 不合并 |
| 🔥 新锐项目 | **2条** | 独立板块, 不合并 |
| 📝 最新论文 | **0-1条** | 不重要跳过 |
| 💬 社区热议 | **0-2条** | 有好内容才放 |
- **标题:** `今日AI简报 | {关键词1} · {关键词2} | {YYYY.MM.DD}`
- **数据源:** 国内外兼顾(雷锋网, IT之家, GitHub, HN, ArXiv), 不优先任何一方
- **岔开发:** 热门多则只选2条, 剩下的自然在后续出现
- **去掉**"今日互动"板块
- **去掉**底部"数据来源: ..."行 — 文档中不使用数据来源标注
- **热度标记:** 必须使用实际🔥（U+1F525）emoji，不要使用 `\u01c0`（渲染为竖线 ǀ）或其他替代字符 — 社区热议板块中也使用🔥表示HN热度（如"594🔥"）
- **内容长度:** 每条正文 2-3 句，不要只有 1 句过短，也不要超过 4 句过长
- **引号处理:** 使用中文引号时，Python字符串外层用单引号`'...'`避免与中文引号`"..."`冲突
- **风格:** 叙事型深度分析, 每条有独立角度, 非信息堆砌
- **不加** "Hermes Agent" 品牌标识

### Workflow

```
Collect data (GitHub, HN, ArXiv)
       |
       ▼
Generate briefing content as structured sections
       |
       ▼
Create Feishu doc via Open API
  - Get tenant_access_token
  - POST /open-apis/docx/v1/documents
  - POST .../blocks/{doc_id}/children (text, headings, lists, dividers)
       |
       ▼
Deliver doc link via send_message
       |
       ▼
User: open doc → copy → paste into WeChat OA App (≈20s)
```

### Supported Block Types

| Type | Value | Field |
|------|:-----:|-------|
| Text | 2 | text |
| Heading 1 | 3 | heading1 |
| Heading 2 | 4 | heading2 | ✅ supports text_color:5 (蓝色) + align |
| Heading 3 | 5 | heading3 |
| Bullet | 12 | bullet |
| Ordered | 13 | ordered |
| Divider | 22 | divider |

Rich text via `text_element_style`: bold, italic, inline_code.

### Feishu text_color Mapping (Tested)

| Value | Color |
|:-----:|-------|
| 1 | Red |
| 2 | Orange / Yellow |
| 3 | Green |
| 4 | Teal / Cyan |
| **5** | **Blue** ✅ (use for section headings) |
| 6 | Purple |
| 7 | Pink |

### H2 Helper — Blue Centered Heading

Use `text_color=5` (blue) and `style.align=2` (center) on heading2 blocks:

```python
def H2(text):
    return {"block_type": 4, "heading2": {
        "elements": [{"text_run": {"content": text, "text_element_style": {"text_color": 5}}}],
        "style": {"align": 2}
    }}
```

See `references/feishu-color-reference.md` for the complete tested color table.

### Why Format C

- Feishu renders headings, lists, and rich text properly (unlike WeChat's plain text)
- User can copy-paste from Feishu doc to WeChat OA App
- No rate limiting issues (one doc link = one message)
- Doc URL is compact and shareable

See `feishu-doc-api` skill for full API reference and code.

## WeChat Official Account (公众号) Publishing

For users who want to push daily briefings to a WeChat Official Account but only have a **personal subscription account** (no publish API), use this workflow:

### Workflow

```
Hermes generates daily briefing (data + analysis)
       │
       ▼
generate-cover.py ─────→ 1200×630 cover image (WeChat size)
       │
       ▼
Format content per WeChat App template (see references/)
       │
       ▼
Send to user's WeChat via send_message (MEDIA:cover.png + formatted text)
       │
       ▼
User: save cover → open 微信公众平台 App → paste → publish (≈30s)
```

### Steps

1. **Collect data** from GitHub, HN, ArXiv, etc. (standard daily-briefing process)
2. **Generate cover image** using `scripts/generate-cover.py`:
   ```python
   import subprocess, os, datetime
   script = os.path.expanduser("~/.hermes/skills/devops/daily-briefing/scripts/generate-cover.py")
   out = f"/root/.hermes/audio_cache/cover_{datetime.date.today().isoformat()}.png"
   # Build headlines from your data
   headlines = "|".join([item1, item2, item3, item4])
   subprocess.run(["python3", script, "--date", cn_date, "--headlines", headlines, "--output", out])
   ```
3. **Format content** per the template in `references/wechat-official-account-format.md`
4. **Deliver** to user's WeChat: send title (no emoji) as first message, wait 30s+, then send MEDIA:cover + body as second message

### Formatting Cheatsheet (WeChat Official Account)

| Element | Rule |
|---------|------|
| Title | Pure text, NO emoji: `AI 科技日报 | {主题} · {YYYY年M月D日}` |
| Section separators | `━━━` (Unicode box-drawing), repeated to full width |
| Emoji per section | 📌 focus · 🔥 GitHub · 💬 discussion · 📝 editorial (body only, NOT title) |
| Project numbering | ASCII digits: `1. 2. 3.` — do NOT use Unicode ordinals (𝟭. 𝟮.) which cause spacing issues |
| Links | Full URL on its own line, prefixed with `-> ` (ASCII arrow, not →) |
| Footer | Sources only: `数据来源: GitHub · Hacker News · ArXiv` — no generator credit |
| Editorial header | Use `编辑点评` — never `小编点评` |
| Account name | Adapt cover title + template headers to match user's public account name |
| No Markdown | WeChat App editor strips it. No **bold**, no [links](url), plain text + emoji + Unicode separators only |
| Body tail | Content ends at the data source footer line. NO publishing guide, no "三步发布", no instructions |

See `references/wechat-official-account-format.md` for the complete template and examples.

## Verification Checklist

- [ ] All API calls have `--max-time N` (10-15 seconds)
- [ ] Each data source has parse instructions (Python snippet)
- [ ] Output template has fallback text for empty sections
- [ ] Timezone conversion is correct (UTC vs local)
- [ ] Prompt includes `send_message` with retry + `[SILENT]` delivery pattern (Section 6 of Cron Prompt guide)
- [ ] [SILENT] instruction included for total-failure case
- [ ] Skills that might help (e.g. arxiv) are listed in the cron job's skills parameter
- [ ] Feishu delivery uses exactly 3 bare messages: doc URL | title | MEDIA:cover — no extra text on any
