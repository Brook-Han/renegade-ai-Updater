# cache.py
import json
import hashlib
import datetime
from pathlib import Path
from config import Config

def get_paper_fingerprint(paper):
    """生成论文标题+摘要的哈希指纹（MD5）"""
    content = (paper.get("title", "") + " " + paper.get("summary", "")).encode('utf-8', errors='ignore')
    return hashlib.md5(content).hexdigest()

def load_cache():
    cache_file = Config.CACHE_FILE
    if Path(cache_file).exists():
        with open(cache_file, encoding='utf-8') as f:
            return json.load(f)
    return {}

def is_paper_cached(paper, cache):
    fp = get_paper_fingerprint(paper)
    return fp in cache

def mark_paper_cached(paper, analysis_result, cache):
    fp = get_paper_fingerprint(paper)
    cache[fp] = {
        "cached_at": datetime.datetime.now().isoformat(),
        "title": paper.get("title", "")[:80],
        "relevance": analysis_result.get("relevance", 0),
        "urgency": analysis_result.get("urgency", "background"),
        "model_scores": analysis_result.get("model_scores", {}),
    }
    # 同时保留原始 ID 以便兼容旧逻辑
    if "id" in paper:
        cache[paper["id"]] = fp   # 建立 id → 指纹的映射
    
    with open(Config.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def load_seen_ids():
    # 从旧 seen_ids.json 迁移或直接使用缓存中的 id 集合
    # 这一步可以逐渐废弃，但先保留兼容
    cache = load_cache()
    # 只返回那些 id 类型的 key 作为已分析过的 ID 集合
    return {k for k, v in cache.items() if k.startswith("arxiv:") or k.startswith("s2_") or k.startswith("gnews_")}

def save_seen_ids(seen_ids):
    # 用缓存替代，不再单独写入 seen_ids.json，但保留兼容性
    pass