#!/usr/bin/env python3
"""Fetch TechCrunch homepage headlines."""
import re, urllib.request, sys

URL = "https://techcrunch.com/"
req = urllib.request.Request(URL, headers={
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
})

try:
    html = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="replace")
    titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', html, re.DOTALL)
    seen = set()
    results = []
    for t in titles:
        t2 = re.sub(r'<[^>]+>', "", t).strip()
        t2 = t2.replace("&#8217;", "'").replace("&#038;", "&").replace("&amp;", "&")
        if len(t2) > 15 and t2 not in seen:
            seen.add(t2)
            results.append(t2)

    print(f"=== TechCrunch Headlines ({len(results)} items) ===")
    for t in results[:8]:
        print(f"📰  {t}")
        print()
except Exception as e:
    import sys; print(f"[SKIP] TechCrunch failed: {e}", file=sys.stderr)
    sys.exit(1)
