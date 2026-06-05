# Feishu Doc Briefing Script

The canonical implementation script lives at: `/root/create_daily_briefing_doc.py`

This Python script creates a Feishu doc with the daily AI briefing using the Open API.
It handles auth (tenant_access_token), doc creation, and batch block writing.

## Key behavior
- Reads FEISHU_APP_ID / FEISHU_APP_SECRET from `~/.hermes/.env`
- Generates inline content (no external data fetch — content is hardcoded per run)
- Writes in batches of 4 blocks (API limit: 4 children per request)
- Outputs `DOC_URL:https://...` on success

## When to use
- User asks you to regenerate the daily briefing doc
- User corrects a format issue and you need to re-run

## ⚠️ Sync requirement
If you update the skill's format rules (SKILL.md), you MUST also update this script
to match. The two have drifted before and caused user frustration. See the
"Script-Skill Format Drift" pitfall in SKILL.md.

## Known format rules (must match)
- 🔥 GitHub 头部项目 + 🔥 新锐项目: TWO separate H2 headings, never merged
- Heat indicator: `🔥` emoji, never `\u01c0` (renders as ǀ)
- No "数据来源" footer
- Each content item: 2-3 sentences
- No "今日互动" section
