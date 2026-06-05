#!/usr/bin/env python3
"""Fetch Hacker News top stories and filter AI-related ones."""
import json, urllib.request, sys

AI_KEYWORDS = [
    "ai", "llm", "gpt", "chatgpt", "openai", "anthropic", "claude",
    "gemini", "deepseek", "machine learning", "neural", "transformer",
    "rag", "agent", "copilot", "qwen", "mistral", "llama",
    "stable diffusion", "sora", "gen ai", "artificial intelligence",
]

def fetch_json(url, timeout=4):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

try:
    top_ids = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=8)[:30]
    hits = []
    for item_id in top_ids:
        try:
            item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=4)
            if item and item.get("title") and item.get("type") == "story":
                title = item["title"]
                score = item.get("score", 0)
                if any(k in title.lower() for k in AI_KEYWORDS) and score >= 30:
                    hits.append((score, title))
        except:
            pass

    hits.sort(reverse=True)
    print(f"=== Hacker News AI Stories ({len(hits)} items) ===")
    for score, title in hits[:5]:
        print(f"🗞️  {title} (score:{score})")
        print()
except Exception as e:
    import sys; print(f"[SKIP] HN failed: {e}", file=sys.stderr)
    sys.exit(1)
