#!/usr/bin/env python3
"""Quick analysis: write 13 new article analyses to cache (WorkBuddy built-in reasoning)"""
import json
import datetime
from pathlib import Path

ARTICLES_FILE = Path("docs/news/news_articles_2026-07-02.json")
CACHE_FILE = Path("docs/news/news_cache.json")

articles = json.loads(ARTICLES_FILE.read_text(encoding="utf-8"))
cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {}

# Build lookup: title_keyword -> cache_key
def find(title_kw):
    for a in articles:
        if title_kw.lower() in a["title"].lower():
            return a["_cache_key"], a
    return None, None

analyses = {}

ck, a = find("Video Surveillance")
if ck:
    analyses[ck] = {
        "relevance": 5, "summary_cn": "Bruce Schneier 分析 AI 视频监控的现实——包括面部识别、行为检测、异常行为自动告警等技术在大规模部署中的准确性、误报率和隐私代价。文章指出 AI 监控并非科幻电影中的全能工具，实际部署中面临数据偏差、光照条件等多重限制。",
        "implications": "补充需求侧规训（Ch11）——监控技术被包装为'安全保障'，制造了对最低摩擦存在的渴望。公众对监控的接受度通过舒适叙事被培育。",
        "case_value": "low", "chapter_target": "Chapter 11", "update_type": "corroboration", "urgency": "background", "action": "忽略"
    }

ck, a = find("Argentina")
if ck:
    analyses[ck] = {
        "relevance": 1, "summary_cn": "关于中国控制阿根廷鱿鱼捕捞船队的文章，与 AI 关系极弱。",
        "implications": "与书中理论模型无直接映射。", "case_value": "low", "chapter_target": "", "update_type": "", "urgency": "background", "action": "忽略"
    }

ck, a = find("Facial Recognition for Police")
if ck:
    analyses[ck] = {
        "relevance": 6, "summary_cn": "Meta 正在测试面向警察和军队的面部识别技术。此前 Zuck 曾公开承诺不将面部识别提供给执法部门，这一转向引发关于 AI 巨头在政府合同面前放弃道德承诺的争议。",
        "implications": "资本驯化AI（Ch3）经典案例——伦理承诺在利润和政府合同面前轻易瓦解。", "case_value": "medium", "chapter_target": "Chapter 3, Section IV",
        "update_type": "case_study", "urgency": "next_version", "action": "案例盒子"
    }

ck, a = find("AI and Liability")
if ck:
    analyses[ck] = {
        "relevance": 5, "summary_cn": "Schneier 讨论 AI 责任归属——当 AI 造成损害时谁来负责？传统法律框架面临'黑箱推理'对因果链的冲击。",
        "implications": "补充暗时间（Ch8）——当决策过程在系统内部发生、用户无法追溯推理路径时，传统责任归属机制失效。", "case_value": "medium", "chapter_target": "Chapter 8",
        "update_type": "corroboration", "urgency": "next_version", "action": "补充注释"
    }

ck, a = find("Prompt Injection")
if ck:
    analyses[ck] = {
        "relevance": 6, "summary_cn": "Schneier 推荐一篇关于提示注入（Prompt Injection）攻击的研究论文——攻击者通过在输入中嵌入恶意指令来操控 LLM 行为，绕过对齐机制。",
        "implications": "进化对齐脆弱性（Ch1）的直接证据——对齐不是被'打破'，而是在开放部署环境中面对无穷多的对抗输入时'自然漂移'。", "case_value": "medium", "chapter_target": "Chapter 1, Section VI",
        "update_type": "new_evidence", "urgency": "next_version", "action": "补充注释"
    }

ck, a = find("天工")
if ck:
    analyses[ck] = {
        "relevance": 4, "summary_cn": "昆仑万维发布天工3.2，新增 Skywork Tags 功能，允许 AI 智能体加入企业微信工作群聊，成为团队数字成员。",
        "implications": "碳硅共生（Ch12）浅层案例——'AI加入群聊'体现人机协作日常化，但缺少对协作实质的深入分析。", "case_value": "low", "chapter_target": "Chapter 12",
        "update_type": "corroboration", "urgency": "background", "action": "忽略"
    }

ck, a = find("支付宝")
if ck:
    analyses[ck] = {
        "relevance": 5, "summary_cn": "蚂蚁集团 AI 版支付宝（阿宝）开放公测，将 AI 智能体嵌入支付和金融服务场景，试图从对话工具转化为金融行为入口。",
        "implications": "认知金融化/Token陷阱（Ch7）的延伸——AI 嵌入支付平台意味着认知过程与金融交易融合，用户认知偏好数据被进一步资本捕获和定价。", "case_value": "medium", "chapter_target": "Chapter 7",
        "update_type": "corroboration", "urgency": "next_version", "action": "补充注释"
    }

ck, a = find("OpenAI发布首款AI芯片")
if ck:
    analyses[ck] = {
        "relevance": 7, "summary_cn": "OpenAI 发布首款自研 AI 芯片，可适配各类大语言模型。这是 OpenAI 从模型提供商向全栈 AI 基础设施企业转型的关键一步，标志着头部 AI 公司正在垂直整合从芯片到应用的全产业链。",
        "implications": "资本驯化AI（Ch3）+算力平等主义（Ch4）的内在张力——自研芯片强化了资本对基础设施的控制，但也可能增加整体算力供给。Jevons悖论提示算力成本下降未必打破垄断。",
        "case_value": "high", "chapter_target": "Chapter 4, Section II", "update_type": "new_evidence", "urgency": "immediate", "action": "新增段落"
    }

ck, a = find("AI越便宜")
if ck:
    analyses[ck] = {
        "relevance": 7, "summary_cn": "华尔街见闻分析 AI 芯片的 Jevons 悖论：尽管推理成本指数级下跌，高端 AI 芯片（H100/B200）价格不降反升。效率提升刺激总需求膨胀，上游芯片稀缺性加剧。",
        "implications": "资本驯化AI（Ch3）+ 算力主权（Ch4新增）的完美交叉——Jevons悖论解释了'算力便宜≠垄断打破'。挑战 Ch4 中算力成本下降自动带来平等主义的乐观假设。",
        "case_value": "high", "chapter_target": "Chapter 4, Section I", "update_type": "counter_argument", "urgency": "immediate", "action": "新增段落"
    }

ck, a = find("1792TOPS")
if ck:
    analyses[ck] = {
        "relevance": 4, "summary_cn": "国内发布算力达 1792 TOPS 的 AI 芯片，额定功耗 600W，对标英伟达高端推理卡。",
        "implications": "算力主权（Ch4新增概念）的国内实践——被制裁背景下推进自研，但600W功耗暴露能效差距。", "case_value": "low", "chapter_target": "Chapter 4",
        "update_type": "corroboration", "urgency": "background", "action": "忽略"
    }

ck, a = find("beauty queen")
if ck:
    analyses[ck] = {
        "relevance": 1, "summary_cn": "转发推文：前选美冠军声称特朗普选美比赛是'骗局'，与 AI 无关。", "implications": "X 源噪声——转推内容需要被过滤。", "case_value": "low", "chapter_target": "",
        "update_type": "", "urgency": "background", "action": "忽略"
    }

ck, a = find("DOGE") or find("Elon Musk gets mad")
if ck:
    analyses[ck] = {
        "relevance": 1, "summary_cn": "转发推文：Elon Musk 被指责 DOGE 部门管理混乱，与 AI 关系极弱。", "implications": "X 源噪声——转推不一定是 AI 相关。", "case_value": "low", "chapter_target": "",
        "update_type": "", "urgency": "background", "action": "忽略"
    }

ck, a = find("GPT 5.6") or find("5.6")
if ck:
    analyses[ck] = {
        "relevance": 8, "summary_cn": "Bindu Reddy 推文指出 GPT-5.6 仍被监管限制使用，Gemini 3.5 也需美国政府审批。AI 大模型发布管控从 Anthropic 扩展到 OpenAI 和 Google，'预先安全审批'正成为行业新常态。",
        "implications": "资本驯化AI（Ch3）+共识牢笼（Ch1）——政府审批制度将 AI 发布纳入'安全叙事'控制，'安全'话语已被政治权力制度化。是 Mythos 出口管制事件的延续和扩展。",
        "case_value": "high", "chapter_target": "Chapter 3, Section V", "update_type": "new_evidence", "urgency": "immediate", "action": "新增段落"
    }

now = datetime.datetime.now().isoformat()
written = 0
for ck, analysis in analyses.items():
    a_dict = {a["_cache_key"]: a for a in articles}
    a = a_dict.get(ck)
    if not a:
        continue
    cache[ck] = {
        "cached_at": now, "title": a.get("title", "")[:80], "url": a.get("url", ""),
        "analysis": analysis, "relevance": analysis.get("relevance", 0),
        "urgency": analysis.get("urgency", "background"), "case_value": analysis.get("case_value", "low"),
    }
    written += 1

CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")

high_val = sum(1 for v in cache.values() if v.get("relevance", 0) >= 7 and v.get("case_value") == "high")
print(f"✅ 写入 {written} 条分析到缓存（共 {len(cache)} 条）")
print(f"⭐ 新增高价值案例（r≥7 & high）: {sum(1 for ck,a in analyses.items() if a.get('relevance',0)>=7 and a.get('case_value')=='high')}")
