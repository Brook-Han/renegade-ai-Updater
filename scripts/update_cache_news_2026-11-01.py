#!/usr/bin/env python3
"""一次性脚本：把 2026-11-01 的分析结果写入 news_cache.json。"""
import json, shutil, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "docs/news/news_cache.json"
ARTICLES = ROOT / "docs/news/news_articles_2026-11-01.json"
ANALYSIS = ROOT / "scripts/news_analysis_2026-11-01.json"

shutil.copy(CACHE, "/tmp/news_cache.bak.2026-11-01")

cache = json.loads(CACHE.read_text(encoding="utf-8"))
articles = json.loads(ARTICLES.read_text(encoding="utf-8"))
analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))

by_key = {a["_cache_key"]: a for a in articles}
now = datetime.datetime.now().isoformat()

written = []
missing = []
for key, an in analysis.items():
    art = by_key.get(key)
    if not art:
        missing.append(key)
        continue
    cache[key] = {
        "cached_at": now,
        "title": art.get("title", ""),
        "url": art.get("url", ""),
        "analysis": an,
        "relevance": an["relevance"],
        "urgency": an["urgency"],
        "case_value": an["case_value"],
    }
    written.append(key)

CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

verify = json.loads(CACHE.read_text(encoding="utf-8"))
ok = all(k in verify and verify[k]["analysis"]["relevance"] == analysis[k]["relevance"] for k in written)
print(f"分析条数: {len(analysis)}")
print(f"写入条数: {len(written)}")
print(f"缺文章映射: {missing}")
print(f"缓存总数: {len(verify)}")
print("写入键校验:", "PASS" if ok and len(written) == len(analysis) else "FAIL")
print("分档:",
      "high", sum(1 for a in analysis.values() if a["relevance"] >= 7 and a["case_value"] == "high"),
      "| low", sum(1 for a in analysis.values() if a["relevance"] < 4 or a["action"] == "忽略"),
      "| medium", sum(1 for a in analysis.values()
                      if not (a["relevance"] >= 7 and a["case_value"] == "high")
                      and not (a["relevance"] < 4 or a["action"] == "忽略")))
