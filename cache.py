# cache.py
# 版本：v2.1 清理死代码——paper_cache.json 已废弃，academic_radar.py 和 news_radar.py
#         各有独立缓存系统（academic_cache.json / news_cache.json）。
#         本文件仅保留 get_search_cache / set_search_cache（搜索结果缓存）。

import json
import os                       # 修复原有 NameError
import hashlib
import datetime
import time
from pathlib import Path
from config import Config

# ------------------------------------------------------------
# 基础工具
# ------------------------------------------------------------

def get_paper_fingerprint(paper):
    """生成论文标题+摘要的哈希指纹（MD5）"""
    content = (paper.get("title", "") + " " + paper.get("summary", "")).encode('utf-8', errors='ignore')
    return hashlib.md5(content).hexdigest()

# ------------------------------------------------------------
# 以下函数已废弃（dead code）
# paper_cache.json 已重命名为 paper_cache.json.bak (2026-06-10)
# academic_radar.py 使用自己的 CACHE_FILE = academic_cache.json
# news_radar.py 使用自己的 CACHE_FILE = news_cache.json
# 这些函数保留仅为向后兼容，不再被任何脚本调用。
# ------------------------------------------------------------

def load_cache():  # DEPRECATED —— 不再使用
    """加载主缓存文件"""
    cache_file = Config.CACHE_FILE
    if Path(cache_file).exists():
        with open(cache_file, encoding='utf-8') as f:
            return json.load(f)
    return {}

def is_paper_cached(paper, cache):  # DEPRECATED
    """检查论文是否已经缓存"""
    fp = get_paper_fingerprint(paper)
    return fp in cache

def mark_paper_cached(paper, analysis_result, cache):  # DEPRECATED
    """
    将分析结果存入缓存。
    现在会保存完整的 analysis_result，包括 summary_cn、implications 等。
    """
    fp = get_paper_fingerprint(paper)
    cache[fp] = {
        "cached_at": datetime.datetime.now().isoformat(),
        "title": paper.get("title", "")[:80],
        "analysis": analysis_result,          # 完整保留分析结果
        "relevance": analysis_result.get("relevance", 0),
        "urgency": analysis_result.get("urgency", "background"),
        "model_scores": analysis_result.get("model_scores", {}),
    }
    # 同时保留 id 映射，方便兼容旧逻辑
    if "id" in paper:
        cache[paper["id"]] = fp

    with open(Config.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def save_draft(paper, draft_text, cache):
    """将生成的 PRO 书稿段落存到缓存中（同一个条目下）"""
    fp = get_paper_fingerprint(paper)
    if fp in cache:
        cache[fp]["draft_paragraph"] = draft_text
        with open(Config.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

# ------------------------------------------------------------
# 搜索缓存（避免重复调用 arXiv/S2/NewsAPI）
# ------------------------------------------------------------

SEARCH_CACHE_DIR = Config.BASE_DIR / "cache" / "search_results"
SEARCH_CACHE_EXPIRY = {
    "papers": 7 * 24 * 3600,    # 7 天
    "news": 24 * 3600           # 1 天
}

def get_search_cache(source, query, cache_type="papers"):
    """
    读取搜索缓存。
    source: 'arxiv', 'semantic_scholar', 'newsapi' 等
    query: 搜索字符串
    cache_type: 'papers' 或 'news'（决定过期时间）
    返回缓存的结果列表，或 None（无缓存或已过期）
    """
    SEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(f"{source}_{query}".encode()).hexdigest()
    cache_file = SEARCH_CACHE_DIR / f"{key}.json"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, encoding='utf-8') as f:
            data = json.load(f)
        if time.time() - data["timestamp"] < SEARCH_CACHE_EXPIRY.get(cache_type, 86400):
            return data["results"]
    except Exception:
        pass
    return None

def set_search_cache(source, query, results, cache_type="papers"):
    """存储搜索缓存"""
    SEARCH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.md5(f"{source}_{query}".encode()).hexdigest()
    cache_file = SEARCH_CACHE_DIR / f"{key}.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.time(),
            "source": source,
            "query": query,
            "results": results
        }, f, ensure_ascii=False, indent=2)

# ------------------------------------------------------------
# 兼容旧版 seen_ids（逐渐废弃）
# ------------------------------------------------------------

def load_seen_ids():
    """从缓存中提取已分析过的 ID 集合（兼容旧逻辑）"""
    cache = load_cache()
    return {k for k, v in cache.items() if k.startswith("arxiv:") or k.startswith("s2_") or k.startswith("gnews_")}

def save_seen_ids(seen_ids):
    """旧版保留接口，不再写入文件"""
    pass