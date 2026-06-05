# WeChat Official Account (公众号) Publishing Workflow

## Overview

For users without a business license (个人订阅号), the WeChat publish API is unavailable. The recommended workflow is:

1. **Hermes generates** the daily briefing + cover image + formatted text
2. **Deliver to WeChat** via `send_message` — includes cover image as MEDIA and formatted text as message body
3. **User saves cover image** to phone, opens WeChat Official Platform App, pastes content, publishes

This takes ~30 seconds per day with zero maintenance or risk.

## Style Rules (Final)

| Rule | Specification |
|------|--------------|
| **Tone** | Professional + lively. Accessible but not juvenile. |
| **Emoji** | ✅ Use as section headers only: 📌 🔥 💬 📝. Do NOT stack emoji or use in running text. |
| **Branding** | ❌ Never include "Hermes Agent", "hermes", or any AI-brand text in the output. The user's public account runs under their own name. |
| **Editorial header** | Use "编辑点评". NOT "小编点评". |
| **Footer** | Only: `数据来源: GitHub · Hacker News · ArXiv` — no generator credit. |
| **Cover image** | No text watermark, no generator branding in bottom bar. |
| **Data sources** | GitHub Trending (6 items) + Hacker News (5-6 items) + ArXiv (optional, 2-3 items). |
| **Length** | 600-800 chars for the body. Mobile-friendly. |

## Cover Image Generation

Use the included `scripts/generate-cover.py`:

```python
# In execute_code:
import subprocess, os, datetime
script = os.path.expanduser("~/.hermes/skills/devops/daily-briefing/scripts/generate-cover.py")

# Build headlines from collected data (up to 5, each <28 chars)
headlines = "|".join([
    "Claude Opus 4.8 发布 · Anthropic 融资650亿",
    "OpenClaw 破 37.5万星标 · 开源 AI 标杆",
    f"Headline 3",
    f"Headline 4",
    f"Headline 5",
])

# Chinese weekday mapping
date_obj = datetime.date.today()
weekdays_cn = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
cn_date = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日 · {weekdays_cn[date_obj.weekday()]}"

out_path = f"/root/.hermes/audio_cache/daily_cover_{date_obj.isoformat()}.png"
subprocess.run(["python3", script, "--date", cn_date, "--headlines", headlines, "--output", out_path])

# Then include in message:
send_message(message=f"MEDIA:{out_path}\\n\\n...rest of content...")
```

## WeChat Official Account Content Format

### Title Format

```
AI 科技日报 | {Key Topic 1} · {Key Topic 2} · {YYYY.MM.DD}
```

Example: `AI 科技日报 | Claude Opus 4.8 发布 · Anthropic 融资 650 亿 · 2026.05.29`

### Full Template (copy-paste ready for WeChat App)

```
📰 AI 科技日报 · {YYYY.MM.DD}

━━━━━━━━━━━━━━━━━━━━
以下内容可直接复制 → 微信公众平台 App → 新建图文 → 粘贴发布
━━━━━━━━━━━━━━━━━━━━

标题：{Title as above}

━━━━━━━━━━━━━━━━━━━━

📌 今日焦点

▸ {Key point 1}
▸ {Key point 2}
▸ {Key point 3}
▸ {Key point 4}
▸ {Key point 5}

━━━━━━━━━━━━━━━━━━━━

🔥 GitHub 热门项目

𝟭. {owner/repo} · ⭐{stars}k
{short description} · {language}
→ {one-line takeaway}

… (repeat for 6 items)

━━━━━━━━━━━━━━━━━━━━

💬 社区热议 Hacker News

𝟭. {Title} · 🔥{score}
{one-line summary}
→ {url without https://}

… (repeat for 5-6 items)

━━━━━━━━━━━━━━━━━━━━

📝 编辑点评

{2-3 paragraphs of analysis. Pick 2-3 themes from the day's news and write with genuine insight. Don't pad.}

━━━━━━━━━━━━━━━━━━━━
数据来源: GitHub Trending · Hacker News · ArXiv
━━━━━━━━━━━━━━━━━━━━

📎 三步发布
1. 保存上方封面图
2. 微信公众平台 App → 发表 → 新建图文
3. 上传封面 → 粘贴正文 → 发布（约 30 秒）
```

### Alternative Account Name

If the user chose a public account name other than "AI 科技日报" (e.g. "监听站1379"), adapt:

- **Title**: `监听站1379 | {Topic1} · {Topic2} · {YYYY.MM.DD}`
- **Cover title**: Change `AI 科技日报` to the account name in the script
- **Header**: Change `📰 AI 科技日报 · {date}` to `📡 监听站1379 · {date}`
- **Cover script**: Update the `f_title` text in `scripts/generate-cover.py` to match

## Formatting Rules

| Element | Rule |
|---------|------|
| **Title** | Max 64 chars. Include date + top 1-2 keywords. SEO-friendly. |
| **Section separators** | `━━━` repeated to full width. Clearly separates sections visually. |
| **Emoji markers** | 1 per section: 📌 focus, 🔥 GitHub, 💬 HN/discussion, 📝 editorial |
| **Project lists** | Use Unicode ordinal indicators: `𝟭. 𝟮. 𝟯.` (not 1. 2. 3. — better mobile rendering) |
| **HN scores** | Always suffix with 🔥emoji: `score 1,242🔥` |
| **URLs** | Strip `https://` prefix for cleaner display. Use `→ ` prefix. |
| **Editorial** | "编辑点评" section with real analysis, not boilerplate. Pick 2-3 themes. |
| **Source attribution** | Footer with data sources only. No generator credit. |
| **Publishing guide** | Bottom instruction block, just before closing separator. |

## Pitfalls

1. **Cover image branding**: The old script version had "由 Hermes Agent 自动生成" in the bottom bar. The current version removes this. Always verify no branding appears on the cover.
2. **Cover image size**: WeChat requires 1200×630 px exactly. The script produces this size.
3. **Markdown in WeChat App**: The Official Platform App has a limited rich-text editor. Stick to plain text with emoji and Unicode art (━━━ separators). Do NOT use markdown formatting (no `**bold**`, no `*italic*`, no `# headings`).
4. **Image delivery**: Include `MEDIA:/path/to/cover.png` in the send_message text. The WeChat gateway delivers it as a native image attachment. The user saves this to their phone and uploads as the article cover.
5. **Timing**: Send the push message *after* the daily briefing is fully generated, so the user can publish immediately.
6. **User's account name**: If the account name is not "AI 科技日报" (e.g. "监听站1379"), update the cover script's title text and all template headers accordingly.
7. **Rate limiting**: WeChat has low per-minute rate limits. Use retry logic (30s wait × 3 attempts) on `send_message`.
