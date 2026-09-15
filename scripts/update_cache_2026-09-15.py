#!/usr/bin/env python3
"""一次性脚本：将 2026-09-15 的分析结果合并进 docs/news/news_cache.json"""
import json
import os
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(BASE, "docs/news/news_articles_2026-09-15.json")
PAYLOAD = os.path.join(BASE, "scripts/analysis_2026-09-15.json")
CACHE = os.path.join(BASE, "docs/news/news_cache.json")

with open(ARTICLES, encoding="utf-8") as f:
    articles = json.load(f)
with open(PAYLOAD, encoding="utf-8") as f:
    payload = json.load(f)
with open(CACHE, encoding="utf-8") as f:
    cache = json.load(f)

before = len(cache)
now = datetime.now().isoformat()
updated = 0
missing = []

for art in articles:
    key = art["_cache_key"]
    analysis = payload.get(key)
    if not analysis:
        missing.append(key)
        continue
    cache[key] = {
        "cached_at": now,
        "title": art["title"],
        "url": art["url"],
        "analysis": analysis,
        "relevance": analysis["relevance"],
        "urgency": analysis["urgency"],
        "case_value": analysis["case_value"],
    }
    updated += 1

with open(CACHE, "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

high = sum(
    1
    for a in articles
    if (payload.get(a["_cache_key"], {}).get("relevance", 0) >= 7
        and payload.get(a["_cache_key"], {}).get("case_value") == "high")
)

print(f"articles={len(articles)} updated={updated} cache {before} -> {len(cache)}")
print(f"high_value={high}")
if missing:
    print("MISSING:", missing)
