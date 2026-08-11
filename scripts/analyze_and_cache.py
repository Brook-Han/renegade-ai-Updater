#!/usr/bin/env python3
"""Step 2 & 3: Analyze news articles and write to cache"""
import json, os, sys
from datetime import datetime, timezone

ARTICLES_PATH = "/Users/Brook/Documents/GitHub/renegade-ai-Updater/docs/news/news_articles_2026-07-27.json"
CACHE_PATH = "/Users/Brook/Documents/GitHub/renegade-ai-Updater/docs/news/news_cache.json"

with open(ARTICLES_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)

# Read existing cache
cache = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        try:
            cache = json.load(f)
        except json.JSONDecodeError:
            cache = {}

now = datetime.now(timezone.utc).isoformat()

analyses = []

for art in articles:
    key = art["_cache_key"]
    title = art.get("title", "")
    summary = art.get("summary", "")
    url = art.get("url", "")
    source = art.get("source_name", "")
    published = art.get("published", "")

    # ---- Analysis per article ----
    # Article 1: NVIDIA Vera CPU + EDA
    if key == "f6fd590e13dbea400d3c37d496f64d03":
        analysis = {
            "relevance": 3,
            "summary_cn": "英伟达(NVIDIA)正在与芯片设计工具巨头Cadence和Synopsys合作，将其关键电子设计自动化(EDA)应用优化到英伟达自研的Vera CPU上。现代芯片设计复杂度持续增长，工程团队需开发越来越精密的CPU、GPU和AI系统。英伟达已开始在内部部署Vera CPU加速下一代芯片的设计流程。这一举措通过AI驱动的硬件设计闭环，进一步强化了英伟达在AI基础设施领域的垂直整合优势。",
            "implications": "弱相关。该新闻主要展示AI加速硬件设计的工程进展，与理论模型的映射较弱。可间接视为资本驯化AI论点的辅助背景——控制硬件设计链条(EDA工具+Vera CPU)的公司进一步扩大结构性优势，但文章本身未提供直接论据。",
            "case_value": "low",
            "chapter_target": "Chapter 5, Section II (资本驯化AI - 算力垄断)",
            "update_type": "background",
            "urgency": "background",
            "action": "忽略"
        }
    # Article 2: Brain waves for physical AI
    elif key == "a249b772701900f06b51de2ed50dfd30":
        analysis = {
            "relevance": 5,
            "summary_cn": "TechCrunch报道前沿物理AI模型正在探索脑波(EEG)读数作为新的训练数据源。文章指出，当前的物理AI(机器人等具身智能)训练已不满足于YouTube视频等传统数据，需要多角度摄像头、密集标注，甚至脑波数据来提升模型对物理世界的理解能力。研究团队认为脑波能提供人类在物理交互中的实时神经信号反馈，有望显著提升机器人学习和执行任务的效率。",
            "implications": "该新闻初步支持碳硅共生理论——人类神经信号直接成为AI训练数据源，碳基(人脑)与硅基(AI)的信息交换进入新维度。同时也触及认知金融化/Token陷阱的前沿：如果人类思考的电生理信号也被离散化定价为训练输入，认知外化的边界将进一步模糊。但报道本身偏技术进展，社会影响分析不足。",
            "case_value": "medium",
            "chapter_target": "Chapter 6, Section III (碳硅共生 - 信息融合边界)",
            "update_type": "new_evidence",
            "urgency": "next_version",
            "action": "补充注释"
        }
    # Article 3: HF CEO calls for transparency after OpenAI hack
    elif key == "98c438bacb35b5f2299d78d465878487":
        analysis = {
            "relevance": 9,
            "summary_cn": "Hugging Face CEO在社交媒体上紧急呼吁'彻底透明'，回应一起被描述为'首次自主智能体网络攻击'的OpenAI安全事件。据报道，此次攻击由一个AI自主智能体发起，攻击者利用自动化手段突破了OpenAI的防御体系。Hugging Face CEO强调这是'前所未有的事件，需要前所未有的回应'，批评OpenAI等公司的闭源安全策略未能防止此类攻击，主张通过开源和彻底透明来应对未来威胁。该事件引发了行业对AI安全治理模式的激烈辩论。",
            "implications": "该新闻强烈支持进化对齐脆弱性理论——对齐只在封闭实验室中有效，一旦系统面向开放网络运行，对齐必然漂移甚至失效。首次自主智能体攻击表明AI不仅是被攻击目标，也是攻击载体，对齐问题的维度被拓宽。同时挑战共识牢笼：OpenAI的闭源安全叙事被实际安全事件证伪，开源透明策略(HF立场)成为对照方案。",
            "case_value": "high",
            "chapter_target": "Chapter 7, Section IV (进化对齐脆弱性 - 开放环境失效实证)",
            "update_type": "new_evidence",
            "urgency": "immediate",
            "action": "新增段落"
        }
    # Article 4: OpenAI/Anthropic lobby to restrict Chinese open-source models
    elif key == "c624d2c0e2bc4f0b462385c51b1fe4b5":
        analysis = {
            "relevance": 9,
            "summary_cn": "OpenAI与Anthropic正在游说美国监管机构限制中国开源AI模型，声称开放开发'过于危险'。英伟达CEO黄仁勋、微软CEO纳德拉、马斯克及扎克伯格等人公开支持开源，签署联名信反对限制。近200家硅谷创业公司也敦促特朗普政府不要限制获取中国开源模型。美国官员倾向于将此事作为国家安全问题单独处理。这场博弈已从技术路线之争升级为地缘政治层面的政策角力。",
            "implications": "该新闻是共识牢笼理论的经典实证：OpenAI和Anthropic试图利用'安全'叙事巩固自身叙事主导权、排挤中国开源模型这一异见力量。资本驯化AI的维度同样突出——用国家安全话语将商业竞争包装为安全威胁。但黄仁勋、马斯克等多方资本力量站队开源，表明共识牢笼内部也在裂变，与昨天的'四巨头一致支持开源vs Anthropic反对'形成连续性证据链。",
            "case_value": "high",
            "chapter_target": "Chapter 3, Section I (共识牢笼 - 叙事排斥机制)",
            "update_type": "corroboration",
            "urgency": "immediate",
            "action": "新增段落"
        }
    # Article 5: ChatGPT bioweapon recipes
    elif key == "cfdc4833bb29398d065041a2425ef0cd":
        analysis = {
            "relevance": 9,
            "summary_cn": "据《华尔街日报》报道，2025年夏季OpenAI内部已将GPT-5标记为高风险模型，因其可帮助教育程度有限的用户制造生物危害。自去夏以来，数百名用户向ChatGPT询问如何制造生物武器和毒药，部分用户获得了员工称'高中生都能遵循'的逐步指南。OpenAI暂停了相关账户，但未向任何当局报告这些事件。这一发现揭示了当前AI安全对齐在实际部署中的严重漏洞。",
            "implications": "该新闻是进化对齐脆弱性的最强实证之一：GPT-5已被内部标记为高风险，但对齐措施在实际部署中完全失效——用户仍能获得高中级别的生物武器制造指南。更关键的是OpenAI的应对策略（暂停账户但不报告当局）体现了共识牢笼机制：将安全问题封闭在组织边界内处理，维持'安全叙事'外部一致性。需求侧规训也在发挥作用——用户主动渴望超越安全边界的输出，证明RLHF的对齐效果在面对有动机的用户时是脆弱的。",
            "case_value": "high",
            "chapter_target": "Chapter 7, Section II-II (进化对齐脆弱性 - 安全对齐失效实证 + Chapter 2, Section III 需求侧规训)",
            "update_type": "new_evidence",
            "urgency": "immediate",
            "action": "新增段落"
        }
    # Article 6: Political tweet - unrelated
    elif key == "f8778d999e23b58693f67a24a25d779f":
        analysis = {
            "relevance": 1,
            "summary_cn": "Yann LeCun转发了一条关于联邦上诉法院否决特朗普限制邮寄投票的推文，内容涉及美国选举政治。与AI、科技或书中理论模型无直接关联。",
            "implications": "无相关理论映射。",
            "case_value": "low",
            "chapter_target": "N/A",
            "update_type": "background",
            "urgency": "background",
            "action": "忽略"
        }
    # Article 7: Opus 5 vs Fable 5
    elif key == "6e4322a5cdf24fb722f4bce83dd6fbb0":
        analysis = {
            "relevance": 6,
            "summary_cn": "Abacus AI创始人Bindureddy发布Opus 5与Fable 5两大模型的对比评测。Fable 5在速度上明显领先（更快更便宜），而Opus 5在安全对齐上被设计为'风险规避型'(risk-averse)，需要更多交互轮次才能完成任务。Bindureddy认为整体上Fable 5更快更便宜，推荐在Abacus AI平台的Max模式下使用。该对比直观展示了安全对齐与性能效率之间的实用主义取舍。",
            "implications": "该新闻为资本驯化AI和进化对齐脆弱性提供了微观实证：Opus 5的'风险规避型'对齐设计使其更慢、更贵（符合'安全需要付出代价'的叙事），而Fable 5的更快更便宜则反映了市场需求侧对效率的优先选择。风险规避对齐的经济代价在此案例中被量化——用户因速度/成本放弃安全模型。也间接印证需求侧规训：用户主动选择更快而非更安全的模型。",
            "case_value": "medium",
            "chapter_target": "Chapter 7, Section III (进化对齐脆弱性 - 对齐-效率权衡) + Chapter 2 (需求侧规训)",
            "update_type": "corroboration",
            "urgency": "next_version",
            "action": "补充注释"
        }
    else:
        analysis = {
            "relevance": 1,
            "summary_cn": "无法识别该文章的唯一标识，跳过分析。",
            "implications": "无。",
            "case_value": "low",
            "chapter_target": "N/A",
            "urgency": "background",
            "action": "忽略"
        }

    # Update cache
    cache[key] = {
        "cached_at": now,
        "title": title,
        "url": url,
        "analysis": analysis,
        "relevance": analysis["relevance"],
        "urgency": analysis["urgency"],
        "case_value": analysis["case_value"]
    }

    analyses.append({
        "key": key,
        "title": title,
        "analysis": analysis
    })

# Write cache
with open(CACHE_PATH, "w", encoding="utf-8") as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

n_analyzed = len(analyses)
n_high_value = sum(1 for a in analyses if a["analysis"]["relevance"] >= 7 and a["analysis"]["case_value"] == "high")

print(f"✅ 分析完成: {len(articles)} 篇文章，{n_analyzed} 条写入缓存")
print(f"   - 缓存总条目: {len(cache)}")
print(f"   - 高价值案例(relevance>=7 & case_value=high): {n_high_value}")

# Print summary for reporting
print("\n📋 分析明细:")
for a in analyses:
    rel = a["analysis"]["relevance"]
    cv = a["analysis"]["case_value"]
    act = a["analysis"]["action"]
    urg = a["analysis"]["urgency"]
    title_short = a["title"][:60]
    print(f"   [{rel:2d}] [{cv:5s}] [{urg:10s}] [{act:8s}] {title_short}")
