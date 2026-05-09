import json
import hashlib
import os
import datetime
from pathlib import Path
from config import Config

# ======================
# 你原版的缓存逻辑（完整保留，无修改）
# ======================
def get_paper_fingerprint(paper):
    """生成论文/资讯标题+摘要的哈希指纹（MD5）"""
    content = (paper.get("title", "") + " " + paper.get("summary", "")).encode('utf-8', errors='ignore')
    return hashlib.md5(content).hexdigest()

def load_cache():
    cache_file = Path(Config.CACHE_FILE)
    if not cache_file.exists():
        return {}
    try:
        with open(cache_file, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def is_paper_cached(paper, cache):
    """判断是否有缓存（不校验过期，只判断是否存在）"""
    fp = get_paper_fingerprint(paper)
    return fp in cache

def is_cache_valid(cache_item, expire_days: int = 7) -> bool:
    """判断缓存是否在有效期内（默认7天过期重分析）"""
    try:
        cached_at = datetime.datetime.fromisoformat(cache_item["cached_at"])
        now = datetime.datetime.now()
        return (now - cached_at).days < expire_days
    except Exception:
        return False

def get_cached_analysis(paper, cache):
    """读取有效的缓存分析结果，过期返回None"""
    fp = get_paper_fingerprint(paper)
    if fp not in cache:
        return None
    item = cache[fp]
    if is_cache_valid(item, expire_days=7):
        return item.get("merged_result")
    return None

def mark_paper_cached(paper, merged_result, cache):
    """把完整合并分析结果写入缓存，下次直接复用省Token"""
    fp = get_paper_fingerprint(paper)
    cache[fp] = {
        "cached_at": datetime.datetime.now().isoformat(),
        "title": paper.get("title", "")[:100],
        "merged_result": merged_result
    }

    with open(Config.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# 保留原版空函数
def load_seen_ids():
    cache = load_cache()
    seen_ids = set()
    for data in cache.values():
        pass
    return seen_ids

def save_seen_ids(seen_ids):
    pass

# ======================
# 新增：省Token 分析+搜索缓存（完整保留）
# ======================
ANALYSIS_CACHE = "analysis_draft_cache.json"
SEARCH_CACHE = "search_results_cache.json"

# 分析 + 草稿 缓存
def load_analysis_cache():
    if os.path.exists(ANALYSIS_CACHE):
        with open(ANALYSIS_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_analysis_cache(data):
    with open(ANALYSIS_CACHE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_cached_analysis_single(paper):
    cache = load_analysis_cache()
    return cache.get(get_paper_fingerprint(paper))

def save_analysis(paper, analysis, draft=None):
    cache = load_analysis_cache()
    cache[get_paper_fingerprint(paper)] = {
        "title": paper["title"][:80],
        "analysis": analysis,
        "draft": draft
    }
    save_analysis_cache(cache)

# 搜索结果缓存
def load_search_cache():
    if os.path.exists(SEARCH_CACHE):
        with open(SEARCH_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_search_cache(key, results):
    cache = load_search_cache()
    cache[key] = results
    with open(SEARCH_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_search_cache(key):
    cache = load_search_cache()
    return cache.get(key)