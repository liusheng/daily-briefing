#!/usr/bin/env python3
"""Fetch GitHub head projects (high-star AI repos)."""
import json, urllib.request, sys

URL = "https://api.github.com/search/repositories?q=ai+OR+machine+learning+OR+LLM&sort=stars&order=desc&per_page=5"
req = urllib.request.Request(URL, headers={"User-Agent": "Hermes-DailyBriefing/1.0"})

try:
    data = json.loads(urllib.request.urlopen(req, timeout=12).read())
    items = data.get("items", [])
    print(f"=== GitHub HEAD Projects ({len(items)} repos) ===")
    for r in items[:5]:
        desc = (r.get("description") or "No description")[:80]
        lang = r.get("language") or "N/A"
        print(f"🔥 {r['full_name']} ⭐{r['stargazers_count']:,}★")
        print(f"   {desc}")
        print(f"   Language: {lang}")
        print()
except Exception as e:
    import sys; print(f"[SKIP] GitHub HEAD failed: {e}", file=sys.stderr)
    sys.exit(1)
