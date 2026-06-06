#!/usr/bin/env python3
"""Fetch GitHub rising projects (low-star but recently active AI repos)."""
import json, urllib.request, sys

from datetime import datetime, timedelta

week_ago = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
URL = f"https://api.github.com/search/repositories?q=ai+OR+agent+OR+LLM+stars:100..10000+pushed:>{week_ago}&sort=stars&order=desc&per_page=15"
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-DailyBriefing/1.0"})

try:
    data = json.loads(urllib.request.urlopen(req, timeout=12).read())
    items = data.get("items", [])
    rising = [r for r in items if 100 <= r["stargazers_count"] <= 10000][:5]
    print(f"=== GitHub RISING Projects ({len(rising)} repos) ===")
    for r in rising:
        desc = (r.get("description") or "No description")[:80]
        lang = r.get("language") or "N/A"
        print(f"🔥 {r['full_name']} ⭐{r['stargazers_count']:,}★")
        print(f"   {desc}")
        print(f"   Language: {lang}")
        print()
except Exception as e:
    import sys; print(f"[SKIP] GitHub RISING failed: {e}", file=sys.stderr)
    sys.exit(1)
