#!/usr/bin/env python3
"""Fetch IT之家 AI标签 headlines."""
import re, urllib.request, sys

URL = "https://www.ithome.com/tag/ai"
req = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
})

try:
    html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="replace")
    titles = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
    results = []
    for t in titles[:10]:
        t2 = re.sub(r'<[^>]+>', "", t).strip()
        if len(t2) > 5 and t2 not in results:
            results.append(t2)

    print(f"=== IT之家 AI标签 ({len(results)} items) ===")
    for t in results:
        print(f"🇨🇳 {t}")
        print()
except Exception as e:
    import sys; print(f"[SKIP] IT之家 failed: {e}", file=sys.stderr)
    sys.exit(1)
