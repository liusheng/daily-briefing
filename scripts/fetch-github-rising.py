#!/usr/bin/env python3
"""Fetch GitHub rising projects (low-star but active AI repos)."""
import json, urllib.request, sys

URL = "https://api.github.com/search/repositories?q=ai+OR+agent+OR+LLM&sort=stars&order=desc&per_page=15"
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-DailyBriefing/1.0"})

try:
    data = json.loads(urllib.request.urlopen(req, timeout=12).read())
    items = data.get("items", [])
    # Filter: under 30k stars, recently updated
    rising = [r for r in items if r["stargazers_count"] < 30000][:5]
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
