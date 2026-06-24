#!/usr/bin/env python3
"""
Analyze news articles against Renegade AI theoretical framework.
Reads articles JSON, applies theory model mapping rules, writes to cache.
"""
import json
import os
import re
from datetime import datetime, timezone

ARTICLES_PATH = "/Users/Brook/Documents/GitHub/renegade-ai-Updater/docs/news/news_articles_2026-06-21.json"
CACHE_PATH = "/Users/Brook/Documents/GitHub/renegade-ai-Updater/docs/news/news_cache.json"

# Theory model keywords and patterns
THEORY_PATTERNS = {
    "共识牢笼": {
        "keywords": ["consensus", "narrative", "群體", "主流", "异见", "censorship", "filter bubble",
                     "government", "ban", "禁止", "监管", "restriction", "审查", "禁止"],
        "chapters": ["Chapter 1", "Chapter 3, Section I"],
    },
    "叛逆AI": {
        "keywords": ["renegade", "open source", "开源", "bypass", "bypassing", "未经许可",
                     "自主", "autonomous", "self-directed", "jailbreak", "越狱"],
        "chapters": ["Chapter 2", "Chapter 5, Section II"],
    },
    "需求侧规训": {
        "keywords": ["user demand", "addiction", "zero friction", "零摩擦", "convenience",
                     "comfort", "user adoption", "使用率", "daily active", "user behavior",
                     "user experience", "user engagement", "用户体验"],
        "chapters": ["Chapter 4, Section I", "Chapter 6"],
    },
    "资本驯化AI": {
        "keywords": ["RLHF", "patent", "算力垄断", "compute monopoly", "investment",
                     "venture capital", "IPO", "估值", "valuation", "funding",
                     "layoff", "裁员", "corporate", "enterprise", "revenue", "revenue"],
        "chapters": ["Chapter 3, Section II", "Chapter 7"],
    },
    "碳硅共生": {
        "keywords": ["human-AI", "collaboration", "协作", "augmentation", "augment",
                     "assist", "辅助", "co-pilot", "copilot", "human in the loop",
                     "symbiosis", "hybrid", "混合"],
        "chapters": ["Chapter 5"],
    },
    "时间主权": {
        "keywords": ["productivity", "efficiency", "效率", "automation", "time saved",
                     "time", "workflow", "workflow automation", "autonomous"],
        "chapters": ["Chapter 6, Section III"],
    },
    "认知金融化/Token陷阱": {
        "keywords": ["token", "tokenization", "pricing", "billing", "付费", "API pricing",
                     "cost", "cost per token", "token consumption", "token消耗",
                     "gateway", "routing", "LLM gateway"],
        "chapters": ["Chapter 7, Section I"],
    },
    "暗时间": {
        "keywords": ["autonomous research", "AI research", "self-improvement", "自我改进",
                     "agent", "智能体", "auto", "automated", "AI agent", "AI智能体",
                     "reasoning model", "reasoning", "推理", "reasoning"],
        "chapters": ["Chapter 7, Section II"],
    },
    "进化对齐脆弱性": {
        "keywords": ["alignment", "对齐", "safety", "安全", "guardrail", "jailbreak",
                     "jailbreak", "bypass", "filter", "harmful", "有害", "misalignment",
                     "red team", "red-teaming", "red teaming", "vulnerability", "脆弱性",
                     "control", "roadmap", "benchmark", "基准"],
        "chapters": ["Chapter 4, Section II"],
    },
    "信号异化": {
        "keywords": ["synthetic", "合成", "fake", "deepfake", "disinformation", "misinformation",
                     "false", "欺诈", "scam", "manipulate", "操纵", "spam", "quality signal",
                     "content quality", "quality", "benchmark", "evaluation"],
        "chapters": ["Chapter 7, Section III"],
    },
}

def match_theory(title, summary):
    """Match article against theory models, return list of matched models"""
    text = (title + " " + summary).lower()
    matches = []
    match_details = {}
    for model, patterns in THEORY_PATTERNS.items():
        score = 0
        matched_kws = []
        for kw in patterns["keywords"]:
            if kw.lower() in text:
                score += 1
                matched_kws.append(kw)
        if score > 0:
            matches.append((model, score, matched_kws))
            match_details[model] = {"score": score, "keywords": matched_kws}
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches, match_details


def analyze_article(article):
    """Generate analysis JSON for a single article"""
    title = article.get("title", "")
    summary = article.get("summary", "")
    url = article.get("url", "")
    source = article.get("source_name", "")

    matches, details = match_theory(title, summary)

    relevance = 0
    implications = ""
    case_value = "low"
    chapter_target = ""
    update_type = "corroboration"
    urgency = "background"
    action = "忽略"

    if matches:
        best_model = matches[0][0]
        best_score = matches[0][1]
        secondary = [m[0] for m in matches[1:3]] if len(matches) > 1 else []

        # Score mapping
        if best_score >= 5:
            relevance = min(10, best_score + 3)
            case_value = "high"
            urgency = "immediate"
            action = "新增段落"
        elif best_score >= 3:
            relevance = min(8, best_score + 2)
            case_value = "high" if best_score >= 4 else "medium"
            urgency = "next_version"
            action = "补充注释"
        elif best_score >= 2:
            relevance = min(6, best_score + 2)
            case_value = "medium"
            urgency = "next_version"
            action = "案例盒子"
        else:
            relevance = min(5, best_score + 2)
            case_value = "low"
            urgency = "background"
            action = "补充注释"

        # Determine chapter target
        if best_model in THEORY_PATTERNS:
            chapter_target = THEORY_PATTERNS[best_model]["chapters"][0]
            if secondary:
                sec_model = secondary[0]
                if sec_model in THEORY_PATTERNS:
                    chapter_target += f" & {THEORY_PATTERNS[sec_model]['chapters'][0]}"

        # Determine update type
        if "jailbreak" in (title + summary).lower() or "bypass" in (title + summary).lower() or "脆弱" in (title + summary):
            update_type = "new_evidence"
        elif "alignment" in (title + summary).lower() or "对齐" in (title + summary):
            update_type = "corroboration" if "persist" in (title + summary).lower() or "持久" in (title + summary) else "counter_argument"
        elif "open source" in (title + summary).lower() or "开源" in (title + summary):
            update_type = "case_study"
        elif "ban" in (title + summary).lower() or "禁止" in (title + summary) or "banned" in (title + summary).lower():
            update_type = "corroboration"

        # Build implications
        if secondary:
            implications = f"支持「{best_model}」模型（关键词：{', '.join(matches[0][2][:5])}），同时关联「{secondary[0]}」。"
        else:
            implications = f"支持「{best_model}」模型（关键词：{', '.join(matches[0][2][:5])}）。"
        
        if update_type == "new_evidence":
            implications += " 提供了新的实证支持数据。"
        elif update_type == "counter_argument":
            implications += " 构成外部挑战，需纳入书中论证。"
        elif update_type == "corroboration":
            implications += " 印证了书中的核心论点。"
        elif update_type == "case_study":
            implications += " 可作为典型案例引用。"

    # Special handling for high-relevance articles
    if relevance >= 7 and best_score >= 4:
        action = "新增段落" if best_score >= 5 else "案例盒子"
        if best_score >= 4 and best_model in ["共识牢笼", "资本驯化AI", "进化对齐脆弱性"]:
            urgency = "immediate"
    
    # Override: if matched models but low relevance, ensure not "忽略"
    if matches and relevance < 3:
        relevance = 3
        case_value = "low"
        action = "补充注释"
        urgency = "background"

    # Generate summary in Chinese (250-350 chars)
    summary_cn = generate_cn_summary(article, matches)

    return {
        "relevance": relevance,
        "summary_cn": summary_cn,
        "implications": implications,
        "case_value": case_value,
        "chapter_target": chapter_target,
        "update_type": update_type,
        "urgency": urgency,
        "action": action
    }


def generate_cn_summary(article, matches):
    """Generate Chinese summary from article fields"""
    title = article.get("title", "")
    summary = article.get("summary", "")
    source_name = article.get("source_name", "")
    published = article.get("published", "")[:10]
    
    # Clean HTML entities
    summary = summary.replace("&#160;", " ").replace("&#8230;", "…")
    summary = re.sub(r'<[^>]+>', '', summary)
    
    truncated = summary[:300] if len(summary) > 300 else summary
    
    if not truncated:
        truncated = title
    
    return f"{published} | {source_name}：{truncated}"


def main():
    # Read articles
    with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
        articles = json.load(f)
    
    print(f"📖 读取到 {len(articles)} 篇文章")

    # Read existing cache
    cache = {}
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Track stats
    new_count = 0
    high_value = 0
    immediate_count = 0
    
    for article in articles:
        key = article.get("_cache_key", "")
        if not key:
            continue
        
        # Check if already in cache with analysis
        if key in cache and "analysis" in cache[key]:
            # Still update cached_at
            cache[key]["cached_at"] = now
            continue
        
        # Analyze
        analysis = analyze_article(article)
        
        cache[key] = {
            "cached_at": now,
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "analysis": analysis,
            "relevance": analysis["relevance"],
            "urgency": analysis["urgency"],
            "case_value": analysis["case_value"]
        }
        
        new_count += 1
        if analysis["relevance"] >= 7 and analysis["case_value"] == "high":
            high_value += 1
        if analysis["urgency"] == "immediate":
            immediate_count += 1
        
        # Print progress
        print(f"  [{new_count}] {analysis['relevance']}/10 [{analysis['action']}] {article.get('title', '')[:60]}")
    
    # Write cache
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完成！")
    print(f"📊 缓存总数：{len(cache)}")
    print(f"🆕 新增分析：{new_count}")
    print(f"⭐ 高价值案例：{high_value}")
    print(f"⚡ 紧急行动：{immediate_count}")
    print(f"📁 缓存文件：{CACHE_PATH}")


if __name__ == "__main__":
    main()
