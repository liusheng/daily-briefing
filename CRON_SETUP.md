# Cron Setup Reference

## Job Configuration

- **Job ID:** 3b93814c9436
- **Name:** AI Daily Briefing
- **Schedule:** Every day at 07:00 Beijing time (UTC 23:00 → converted to 0 7 * * * on host)
- **Skills loaded:** daily-briefing, feishu-doc-api
- **Delivery:** origin,feishu

## Delivery Format (settled 2026.06.05)

Exactly 3 separate `send_message` calls to Feishu:
1. 日报 — bare doc URL only
2. 标题 — title text only  
3. 封面 — MEDIA:cover_path only

No extra text, no prefixes, no emoji, no greetings on any of the 3 messages.
