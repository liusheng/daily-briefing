#!/usr/bin/env python3
"""Fetch 雷锋网 AI频道 headlines."""
import re, urllib.request, sys

URL = "https://www.leiphone.com/category/ai"
req = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
})

try:
    html = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="replace")
    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
    results = []
    for t in titles[:10]:
        t2 = re.sub(r'<[^>]+>', "", t).strip()
        if len(t2) > 5 and t2 not in results:
            results.append(t2)

    print(f"=== 雷锋网 AI频道 ({len(results)} items) ===")
    for t in results:
        print(f"🇨🇳 {t}")
        print()
except Exception as e:
    import sys; print(f"[SKIP] 雷锋网 failed: {e}", file=sys.stderr)
    sys.exit(1)
