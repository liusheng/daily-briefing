# Cron Setup Reference

## Job Configuration

- **Job ID:** 3b93814c9436
- **Name:** AI Daily Briefing
- **Schedule:** Every day at 07:00 Beijing time
- **Skills loaded:** daily-briefing, feishu-doc-api
- **Delivery:** origin,feishu

## Data Sources (6 total)

| Source | Type | Status |
|--------|------|--------|
| GitHub HEAD Projects | Search API | ✅ |
| GitHub RISING Projects | Search API + filter | ✅ |
| Hacker News | Firebase API | ✅ |
| TechCrunch | HTML scrape | ✅ |
| 雷锋网AI频道 | HTML scrape | ✅ |
| IT之家AI标签 | HTML scrape | ✅ |

## Workflow

1. `bash collect-all.sh` → fetch all 6 sources
2. AI agent selects best items from combined output
3. `/root/create_daily_briefing_doc.py` → create Feishu doc
4. `generate-cover.py` → create cover image
5. 3 bare send_message calls: doc URL | title | MEDIA:cover

## Delivery Format (settled 2026.06.05)

Exactly 3 separate `send_message` calls to Feishu, NO extra text:
1. Bare doc URL only
2. Title text only
3. MEDIA:cover_path only
