import json
import hashlib
import datetime
from pathlib import Path
from config import Config

def get_paper_fingerprint(paper):
    """生成论文/资讯唯一哈希指纹（标题+摘要，避免重复分析）"""
    content = (paper.get("title", "") + " " + paper.get("summary", "")).encode('utf-8', errors='ignore')
    return hashlib.md5(content).hexdigest()

def load_cache():
    """加载本地缓存文件，带异常处理"""
    cache_file = Path(Config.CACHE_FILE)
    if not cache_file.exists():
        return {}
    try:
        with open(cache_file, encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 缓存文件损坏时，返回空缓存不影响程序运行
        return {}

def is_paper_cached(paper, cache):
    """检查论文/资讯是否已缓存（去重核心）"""
    fp = get_paper_fingerprint(paper)
    return fp in cache

def mark_paper_cached(paper, analysis_result, cache):
    """标记为已缓存并写入文件，修复缓存Key冲突问题"""
    fp = get_paper_fingerprint(paper)
    # 写入缓存数据
    cache[fp] = {
        "cached_at": datetime.datetime.now().isoformat(),
        "title": paper.get("title", "")[:100],
        "relevance": analysis_result.get("relevance", 0),
        "urgency": analysis_result.get("urgency", "background"),
        "model_scores": analysis_result.get("model_scores", {}),
        "source_id": paper.get("id", "")  # 存储原始ID，兼容旧逻辑
    }

    # 安全写入文件，防止损坏
    with open(Config.CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def load_seen_ids():
    """兼容旧版：从缓存中提取已读取的ID集合，废弃seen_ids.json"""
    cache = load_cache()
    seen_ids = set()
    # 提取所有缓存条目的原始ID
    for data in cache.values():
        source_id = data.get("source_id", "")
        if source_id and any(source_id.startswith(prefix) for prefix in ["arxiv:", "s2_", "gnews_"]):
            seen_ids.add(source_id)
    return seen_ids

def save_seen_ids(seen_ids):
    """旧版兼容函数，新版统一使用cache管理，无需单独保存"""
    pass