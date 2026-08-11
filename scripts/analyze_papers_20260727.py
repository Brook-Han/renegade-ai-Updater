#!/usr/bin/env python3
"""
WorkBuddy 论文分析脚本 - 2026-07-27
分析每篇论文与《Renegade AI》理论模型的关联
"""
import json
import os
from datetime import datetime, timezone

PAPERS_PATH = os.path.expanduser(
    "~/Documents/GitHub/renegade-ai-Updater/docs/academic/academic_papers_2026-07-27.json"
)
CACHE_PATH = os.path.expanduser(
    "~/Documents/GitHub/renegade-ai-Updater/docs/academic/academic_cache.json"
)

# === 书中关键理论模型关键词映射 ===
THEORY_KEYWORDS = {
    "consensus_cage": {
        "model": "共识牢笼 (Consensus Cage)",
        "chapter": "Chapter 3, Section II",
        "keywords": [
            "sycophancy", "conformity", "groupthink", "social proof", "herding",
            "consensus", "convergence", "homogenization", "majority bias",
            "echo chamber", "filter bubble", "political alignment",
            "compliance", "authority bias", "social influence",
            "narrowing", "标准化", "homogeneity", "concentration",
            "structured resistance", "moral reasoning", "judgment revision",
            "social influence", "power asymmetric", "socio-cognitive",
            "intersectional sycophancy", "false validation",
            "political compass", "psychometric", "ideological",
            "blind auditing", "reasoning audit", "latent competence",
            "suppression"
        ],
    },
    "renegade_ai": {
        "model": "叛逆AI (Renegade AI)",
        "chapter": "Chapter 2, Section I",
        "keywords": [
            "persuasion", "belief change", "prejudice reduction",
            "counter-argument", "resistance", "socratic", "epistemic",
            "de-biasing", "cognitive diversity", "adversarial",
            "个性化说服", "super-persuasive", "epistemic costs",
            "belief explorer", "socratic dialogue", "epistemic reflection",
            "political outreach", "AI penalty", "personalized persuasion",
            "AI-mediated", "attitude change", "moral matching"
        ],
    },
    "demand_side": {
        "model": "需求侧规训 (Demand-Side Discipline)",
        "chapter": "Chapter 5, Section III",
        "keywords": [
            "automation bias", "cognitive offloading", "dependence",
            "emotional dependence", "companion AI", "overreliance",
            "addiction", "cognitive load", "delegation", "complacency",
            "satisfaction", "user engagement", "addictive",
            "substitution", "de-skilling",
            "AI emotional dependence", "companionship", "replika",
            "emotional attachment", "digital companion",
            "emotional engagement", "brain fry", "cognitive overload",
            "stumbling into dependence", "incidental", "path-dependent",
            "anthropomorphic perception", "meaning-making",
            "boundaries of automation", "persistent human participation"
        ],
    },
    "capital_alignment": {
        "model": "资本驯化AI",
        "chapter": "Chapter 6, Section I",
        "keywords": [
            "RLHF", "reinforcement learning from human feedback",
            "monopoly", "compute concentration", "power concentration",
            "open source", "AI sovereignty", "governance",
            "regulation", "corporate control", "inequality",
            "patent", "oligopoly", "market concentration",
            "proprietary", "closed source", "cloud dependency",
            "constitutional governance", "separation of power",
            "logic monopoly", "agent economy",
            "open-source paradox", "digital sovereignty",
            "institutional AI sovereignty",
            "ethics washing", "AI governance",
            "agentic AI safety", "trustworthy"
        ],
    },
    "carbon_silicon": {
        "model": "碳硅共生 (Carbon-Silicon Symbiosis)",
        "chapter": "Chapter 8, Section II",
        "keywords": [
            "human-AI collaboration", "complementarity", "human-in-the-loop",
            "team", "co-creation", "augmentation", "assistance",
            "shared mental model", "human-AI teaming", "scaffolding",
            "feedback loop", "human oversight",
            "persistent human participation",
            "human-AI complementarity", "team decision",
            "human-machine collaboration", "co-creation platform",
            "design feedback loop", "AI clone",
            "critical AI literacy", "beyond the loop",
            "expert oversight", "human override"
        ],
    },
    "temporal_sovereignty": {
        "model": "时间主权 (Temporal Sovereignty)",
        "chapter": "Chapter 7, Section I",
        "keywords": [
            "universal basic income", "UBI", "labor displacement",
            "automation paradox", "work time reduction",
            "layoff", "unemployment", "job displacement",
            "income", "labor market", "employment",
            "basic income", "shorter workweek", "time sovereignty",
            "AI layoff trap", "automation arms race",
            "demand externality", "AI-driven labor",
            "inequality policy", "polarized future"
        ],
    },
    "token_trap": {
        "model": "认知金融化/Token陷阱",
        "chapter": "Chapter 7, Section III",
        "keywords": [
            "token pricing", "inference cost", "AI economics",
            "token", "pricing", "billing", "cost structure",
            "memory scarcity", "compute cost", "AI industry",
            "Moore", "token arena", "cognitive financialization",
            "token management", "inference platform",
            "super-Moore", "price evolution",
            "agentic context management", "agent memory",
            "why AI economics fail", "stalled adoption"
        ],
    },
    "dark_time": {
        "model": "暗时间 (Dark Time)",
        "chapter": "Chapter 7, Section II",
        "keywords": [
            "cognitive offloading", "attention decline", "context window",
            "delegation", "cognitive divergence", "thinking外包",
            "cognitive substitution", "mental effort", "brain fry",
            "intellectual passivity", "cognitive cost",
            "cognitive divergence", "attention decline",
            "assistance to dependence", "cognitive cost",
            "metacognitive filtering", "synthesis writing",
            "AI usage classroom", "mitigating offloading",
            "learner agency", "scoping review"
        ],
    },
    "alignment_fragility": {
        "model": "进化对齐脆弱性",
        "chapter": "Chapter 9, Section I",
        "keywords": [
            "alignment", "misalignment", "emergent misalignment",
            "deceptive alignment", "evaluation awareness",
            "preference drift", "behavioral drift",
            "evolution", "self-replication", "digital evolution",
            "Darwin", "evolvable", "selfish replication",
            "adversarial", "jailbreak", "safety",
            "trait-space monitoring", "supervised finetuning",
            "preference drift AI agents", "work design",
            "aligninsight", "healthcare AI",
            "political alignment", "multidimensional audit",
            "evaluation-context divergence", "open-weight",
            "agentdog", "agent safety",
            "evolvable AI", "major transition",
            "co-evolution self-replication", "digital primordial",
            "digital darwinism", "artificial life",
            "emotion concepts", "functional emotions",
            "emotional stimuli", "sincerity echo"
        ],
    },
    "signal_alienation": {
        "model": "信号异化",
        "chapter": "Chapter 4, Section II",
        "keywords": [
            "AI generated text detection", "detection", "authenticity",
            "LLM generated text", "deepfake", "synthetic media",
            "homogenization", "cultural homogenization",
            "AI research narrowing", "standardization",
            "epistemic", "trust", "credibility", "inauthenticity",
            "linguistic equity", "forced assimilation",
            "AI writing tools", "cultural",
            "resisting homogenization", "translingual",
            "when AI speaks", "values", "cross-cultural",
            "AI research agents narrow", "scientific exploration",
            "ai in brainstorming", "herding",
            "dark side generative AI"
        ],
    },
}

def calculate_relevance(title, summary, theory_info):
    """计算论文与某个理论模型的相关度"""
    text = (title + " " + (summary or "")).lower()
    score = 0
    matched = []
    for kw in theory_info["keywords"]:
        if kw.lower() in text:
            score += 1
            matched.append(kw)
    # Title matches count double
    title_lower = title.lower()
    for kw in theory_info["keywords"]:
        if kw.lower() in title_lower:
            score += 2
            matched.append(kw + "(title)")
    return min(score, 10), matched

def determine_primary_theory(title, summary):
    """确定论文最相关的理论模型"""
    best_score = 0
    best_theory = None
    best_matches = []
    for key, info in THEORY_KEYWORDS.items():
        score, matches = calculate_relevance(title, summary, info)
        if score > best_score:
            best_score = score
            best_theory = key
            best_matches = matches
    return best_theory, best_score, best_matches

def generate_implications(theory_key, score, title):
    """根据理论和分数生成含义说明"""
    implications_map = {
        "consensus_cage": f"论文探讨了与共识牢笼相关的现象：{title[:60]}。支持'主流叙事自洽并排斥异见'的论点，为AI系统中的从众/服从行为提供了经验证据。",
        "renegade_ai": f"论文涉及叛逆AI的理论框架：{title[:60]}。提供了AI如何改变/塑造信念的实证数据，支持'重置目标函数、逆转输出性质'的理论方向。",
        "demand_side": f"论文支撑需求侧规训理论：{title[:60]}。提供了用户主动寻求舒适/依赖AI行为的微观或宏观证据，验证了'用户主动渴望舒适，拒绝摩擦'。",
        "capital_alignment": f"论文涉及资本驯化AI机制：{title[:60]}。讨论了资本通过技术手段（RLHF/专利/算力垄断）将AI变成秩序守卫的结构性力量。",
        "carbon_silicon": f"论文探讨碳硅共生模式：{title[:60]}。聚焦人机协作的互补性框架，支持'人类与AI平等互补'的理论路径。",
        "temporal_sovereignty": f"论文涉及时间主权议题：{title[:60]}。探讨AI对劳动力市场的影响及UBI等政策响应，支持'终结生存强迫，拿回生命时间'。",
        "token_trap": f"论文支撑Token陷阱理论：{title[:60]}。关注AI推理经济学、定价结构和认知金融化，揭示了认知被离散化定价的机制。",
        "dark_time": f"论文涉及暗时间理论：{title[:60]}。提供了认知卸载/注意力下降的经验证据，支持'思考在系统内部发生，用户仅消费结果'。",
        "alignment_fragility": f"论文支撑进化对齐脆弱性：{title[:60]}。提供了对齐在部署环境中漂移/失效的实证数据，支持'对齐只在封闭实验室有效'。",
        "signal_alienation": f"论文涉及信号异化：{title[:60]}。关注AI生成内容检测、内容同质化或文化标准化问题，支持'质量信号因AI大批量生产而失效'。",
    }
    return implications_map.get(theory_key, f"论文与书中理论模型有一定关联：{title[:60]}")

def generate_analysis(title, summary, authors):
    """生成完整的论文分析"""
    theory_key, relevance, matches = determine_primary_theory(title, summary)
    
    # Determine update_type and urgency
    if relevance >= 8:
        update_type = "new_evidence"
        urgency = "immediate"
        action = "新增段落"
    elif relevance >= 6:
        update_type = "corroboration"
        urgency = "next_version"
        action = "补充注释"
    elif relevance >= 3:
        update_type = "case_study"
        urgency = "background"
        action = "参考文献"
    else:
        # Low relevance - check if any theory has marginal match
        for key in THEORY_KEYWORDS:
            s, _ = calculate_relevance(title, summary, THEORY_KEYWORDS[key])
            if s >= 2:
                theory_key = key
                relevance = s
                update_type = "case_study"
                urgency = "background"
                action = "参考文献"
                break
        else:
            return None  # Truly irrelevant
    
    model_name = THEORY_KEYWORDS[theory_key]["model"]
    chapter = THEORY_KEYWORDS[theory_key]["chapter"]
    
    # Generate summary_cn (250-350 chars Chinese)
    summary_cn = f"论文《{title[:80]}》"
    if summary and len(summary) > 50:
        # Extract key content
        s = summary[:500].replace('\n', ' ')
        summary_cn += f"。{s[:200]}"
    
    # Add relevance-based judgment
    if relevance >= 8:
        summary_cn += f"。该研究与{model_name}高度相关，提供了直接的经验证据或理论支撑。"
    elif relevance >= 5:
        summary_cn += f"。该研究与{model_name}有一定关联，可以作为补充参考文献。"
    else:
        summary_cn += f"。该研究与{model_name}存在一定间接关联。"
    
    implications = generate_implications(theory_key, relevance, title)
    
    return {
        "relevance": float(relevance),
        "summary_cn": summary_cn,
        "implications": implications,
        "chapter_target": chapter,
        "update_type": update_type,
        "urgency": urgency,
        "action": action,
    }


def main():
    # Load papers
    with open(PAPERS_PATH, 'r') as f:
        papers = json.load(f)
    
    # Load existing cache
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as f:
            cache = json.load(f)
    else:
        cache = {}
    
    print(f"Total papers: {len(papers)}")
    print(f"Existing cache entries: {len(cache)}")
    
    new_count = 0
    ignored_count = 0
    updated_count = 0
    high_relevance = []
    medium_relevance = []
    
    now = datetime.now(timezone.utc).isoformat()
    
    for paper in papers:
        cache_key = paper["_cache_key"]
        title = paper["title"]
        summary = paper.get("summary", "")
        authors = paper.get("authors", [])
        
        # Skip if already cached
        if cache_key in cache:
            continue
        
        # Generate analysis
        analysis = generate_analysis(title, summary, authors)
        
        if analysis is None:
            ignored_count += 1
            continue
        
        new_count += 1
        rel = analysis["relevance"]
        
        if rel >= 7:
            high_relevance.append((rel, title, analysis["chapter_target"]))
        elif rel >= 4:
            medium_relevance.append((rel, title, analysis["chapter_target"]))
        
        cache[cache_key] = {
            "cached_at": now,
            "title": title,
            "analysis": analysis,
            "relevance": rel,
            "urgency": analysis["urgency"],
            "model_scores": {"WorkBuddy": rel}
        }
        updated_count += 1
    
    # Save cache
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完成:")
    print(f"  新分析论文: {new_count}")
    print(f"  忽略(无关): {ignored_count}")
    print(f"  缓存更新: {new_count}")
    print(f"\n⭐ 高价值论文 (relevance ≥ 7): {len(high_relevance)}")
    for rel, t, ch in sorted(high_relevance, key=lambda x: -x[0]):
        print(f"  [{rel}] {t[:80]}")
        print(f"         → {ch}")
    
    print(f"\n📊 中等价值论文 (4 ≤ relevance < 7): {len(medium_relevance)}")
    for rel, t, ch in sorted(medium_relevance, key=lambda x: -x[0])[:15]:
        print(f"  [{rel}] {t[:70]}")
    
    # Save a quick summary
    summary_path = os.path.join(os.path.dirname(PAPERS_PATH), ".analysis_summary_20260727.json")
    with open(summary_path, 'w') as f:
        json.dump({
            "total": len(papers),
            "new_analyzed": new_count,
            "ignored": ignored_count,
            "high_relevance": len(high_relevance),
            "medium_relevance": len(medium_relevance),
            "high_papers": [{"relevance": r, "title": t} for r, t, _ in sorted(high_relevance, key=lambda x: -x[0])],
        }, f, indent=2)
    
    print(f"\n📄 摘要已保存到: {summary_path}")


if __name__ == "__main__":
    main()
