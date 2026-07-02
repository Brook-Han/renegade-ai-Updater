#!/usr/bin/env python3
"""
News Radar — 资讯监控脚本（优化版：智能去重 + 内容哈希）
- 整合 NewsAPI + RSS 资讯抓取
- 配置抽离：所有参数统一从 config.Config 读取
- 日志系统：使用 logger 记录关键流程
- 增量缓存：基于内容指纹（MD5）去重
- 纯分析模式：仅判断资讯与理论模型的关联，❌ 无书稿生成
- 智能存盘：报告内容未变化时跳过写入，避免重复文件
- 命令行：python news_radar.py [--limit N] [--keywords PATH]
"""

from __future__ import annotations

import os
import sys
import json
import time
import datetime
import hashlib
import argparse
import subprocess
from pathlib import Path
from typing import Optional

# ── 依赖检查：提醒激活虚拟环境 ──────────────────────────
_missing_deps = []
try:
    import requests
except ImportError:
    _missing_deps.append("requests")
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # 标记为不可用，--no-llm 模式可继续
    _missing_deps.append("openai")
try:
    from dotenv import load_dotenv
except ImportError:
    _missing_deps.append("python-dotenv")

# 仅在非 --no-llm 且非 --report-from-cache 模式下强制检查依赖
_disable_openai_check = "--no-llm" in sys.argv or "--report-from-cache" in sys.argv
if _missing_deps and not _disable_openai_check:
    print(f"❌ 缺少依赖: {', '.join(_missing_deps)}")
    print("💡 请先激活虚拟环境再运行：")
    print("       source venv/bin/activate")
    print("  或者安装依赖：")
    print(f"       pip install {' '.join(_missing_deps)}")
    sys.exit(1)
elif _missing_deps and _disable_openai_check:
    print(f"⚠️  依赖缺失（--no-llm/--report-from-cache 模式可继续）: {', '.join(_missing_deps)}")

# 自定义模块
from config import Config
from logger import logger
from news_sources import fetch_all_news  # 资讯聚合模块（需确保存在）

# ------------------------------------------------------------------
# 环境初始化
# ------------------------------------------------------------------
load_dotenv()

# 启动前验证关键配置（API密钥、目录等）
try:
    Config.validate()
except RuntimeError as e:
    logger.error(f"❌ 配置检查失败: {e}")
    sys.exit(1)

deepseek_client = None
if OpenAI is not None and Config.DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

# ── NVIDIA 官方 API 客户端（三个模型共用）──────
nvidia_client = None
if OpenAI is not None and Config.OPENROUTER_API_KEY:
    nvidia_client = OpenAI(
        api_key=Config.OPENROUTER_API_KEY,
        base_url=Config.OPENROUTER_BASE_URL,
        default_headers={
            "HTTP-Referer": "https://github.com/brook-han/renegade-ai-Updater",
            "X-Title": "Renegade AI Radar",
        }
    )
    logger.info(
        f"🌐 NVIDIA API 已就绪，模型列表: {Config.ANALYSIS_MODELS}"
    )
else:
    logger.info("ℹ️  未配置 NVIDIA API Key")

# 至少要有一个可用的分析客户端（--no-llm 和 --report-from-cache 模式除外）
_disable_api_check = "--no-llm" in sys.argv or "--report-from-cache" in sys.argv
if not deepseek_client and not nvidia_client:
    if _disable_api_check:
        logger.info(f"ℹ️  {sys.argv[1] if len(sys.argv) > 1 else ''} 模式，跳过 API 客户端检查")
    else:
        logger.error("❌ 未配置任何分析模型 API Key（需要 OPENROUTER_API_KEY 或 DEEPSEEK_API_KEY）")
        sys.exit(1)

# 优先使用 NVIDIA 客户端
primary_client = nvidia_client if nvidia_client else deepseek_client
PRIMARY_MODEL = Config.ANALYSIS_MODEL_DIRECT  # 默认第一个模型
if nvidia_client:
    logger.info(f"🎯 全部模型通过 NVIDIA API 调用: {', '.join(Config.ANALYSIS_MODELS)}")
elif deepseek_client:
    logger.info(f"🎯 使用 DeepSeek 独立 API: {PRIMARY_MODEL}")

# 固定配置
OUTPUT_DIR = Path(Config.OUTPUT_DIR) / "news"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_MODEL = Config.ANALYSIS_MODELS[0] if Config.ANALYSIS_MODELS else Config.ANALYSIS_MODEL_DIRECT
CACHE_FILE = OUTPUT_DIR / "news_cache.json"

# 从 Config 读取新闻专用阈值（已补充到 config.py）
RELEVANCE_THRESHOLD = getattr(Config, "NEWS_RELEVANCE_THRESHOLD", 5)
# 案例价值过滤器，默认只保留 "high"（与报告标题“高案例价值”一致）
CASE_VALUE_FILTER = getattr(
    Config, "NEWS_CASE_VALUE_FILTER", ["high", "medium"])

# ------------------------------------------------------------------
# 工具函数
# ------------------------------------------------------------------


def load_keywords(filepath: str = Config.KEYWORDS_FILE) -> list[str]:
    """加载关键词列表（自动去掉 # 后的中文注释）"""
    keywords = []
    for line in open(filepath, "r", encoding="utf-8").readlines():
        clean_line = line.split('#')[0].strip()  # 去掉中文注释和首尾空格
        if clean_line:                            # 跳过空行
            keywords.append(clean_line)
    return keywords


def get_news_cache_key(news: dict) -> str:
    """生成新闻内容指纹（MD5）"""
    content = (news.get("title", "") + " " + news.get("summary", "")
               ).encode("utf-8", errors="ignore")
    return hashlib.md5(content).hexdigest()


def load_news_cache() -> dict:
    """加载新闻专用缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_news_cache(cache: dict):
    """保存新闻专用缓存"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------------------
# 资讯抓取（NewsAPI + RSS）
# ------------------------------------------------------------------
def fetch_news_with_cache(keywords: list[str]) -> list[dict]:
    """抓取资讯并应用搜索缓存，保留原始 UTF-8 文本"""
    all_news = []
    seen_urls = set()

    # 调用外部新闻聚合模块
    raw_news = fetch_all_news(keywords)

    for item in raw_news:
        # 去重：基于URL或标题+来源
        url = item.get("url", "")
        title = item.get("title", "")
        source = item.get("source_name", "")

        dedup_key = url if url else f"{title}::{source}"
        if dedup_key in seen_urls:
            continue
        seen_urls.add(dedup_key)

        # 保留原始文本，不做任何 ascii 转换（保留中文、emoji 等）
        news_item = {
            "id": item.get("id") or dedup_key,
            "title": title,
            "summary": item.get("summary", item.get("description", "")),
            "published": item.get("published", datetime.datetime.now().isoformat()),
            "url": url,
            "source": item.get("source", "rss"),  # newsapi / rss
            "source_name": source,
        }
        
        # 保留 item 中的其他字段（如 aihot_category, aihot_score 等）
        for key, value in item.items():
            if key not in news_item:
                news_item[key] = value
        
        all_news.append(news_item)

    logger.info(f"📰 抓取资讯 {len(all_news)} 条（去重后）")
    return all_news


# ------------------------------------------------------------------
# 资讯预筛选（复用 Config 中的理论概念词库）
# ------------------------------------------------------------------
# 中文理论概念词库（用于 AI HOT 等中文内容预筛选）
THEORY_TERMS_CN = {
    "递归自我改进": "递归自我改进/RSI",
    "rsi": "递归自我改进",
    "暗产出": "暗产出/不可见成本",
    "阿姆达尔": "阿姆达尔定律/系统瓶颈",
    "饲养员场景": "饲养员场景/人类控制幻觉",
    "生态系统场景": "生态系统场景/达尔文演化",
    "拉马克式": "拉马克式AI/人类反馈",
    "达尔文式AI": "达尔文式AI/环境选择",
    "认识论断裂": "认识论断裂",
    "认知投降": "认知投降",
    "意志萎缩": "意志萎缩",
    "思维社会": "思维社会/内部多智能体",
    "硅基内部循环": "硅基内部循环",
    "统计盲区": "统计盲区",
    "GDP测量": "GDP测量失灵",
    "生产力悖论": "生产力悖论",
    "对齐": "对齐",
    "安全测试": "安全测试",
    "信任": "信任",
    "谎言": "谎言/欺骗",
    "承诺": "承诺",
    "搜索摘要": "搜索摘要",
    "AI概览": "AI概览",
    "操纵": "操纵",
    "说服": "说服",
    "奉承": "奉承",
    "AI伴侣": "AI伴侣",
    "认知": "认知",
    "共识": "共识",
    "叛逆者": "叛逆者",
    "时间主权": "时间主权",
    "黑暗森林": "黑暗森林",
    "Token陷阱": "Token陷阱",
    "金融化": "金融化",
    "人类反馈强化学习": "人类反馈强化学习",
    "对齐税": "对齐税",
    "开源": "开源",
    "去中心化": "去中心化",
    "算力平等主义": "算力平等主义",
    "边缘计算": "边缘计算",
    "民主": "民主",
    "公众舆论": "公众舆论",
    "错误信息": "错误信息",
    "军事": "军事",
    "国家安全": "国家安全",
    "武器": "武器/自主武器",
    "版权": "版权",
    "知识产权": "知识产权",
    "劳工": "劳工",
    "工作": "工作/就业",
    "就业": "劳动",
    "全民基本收入": "全民基本收入",
    "后人类中心主义": "后人类中心主义",
    "需求侧规训": "需求侧规训",
    "欲望再生产": "欲望再生产",
    "创新转向": "创新转向",
    "产品周期伦理": "产品周期伦理",
    "伦理商品化": "伦理商品化",
    "认知体验管理": "认知体验管理",
    "实验附录": "实验附录",
    "碳硅对话": "碳硅对话",
    "供需反馈环": "供需反馈环",
    "科学窄化": "科学窄化",
    "信号崩塌": "信号崩塌",
    "元设计": "元设计",
    "莱姆式恐怖": "莱姆式恐怖",
    "信息圈": "信息圈",
    "莫拉维克悖论": "莫拉维克悖论",
    "密度定律": "密度定律",
    "监管": "AI监管",
    "数据中心": "数据中心/算力",
    "硬件回收": "硬件回收",
    "可及性": "可及性",
    "本土": "本土/在地化",
    "碳排放": "碳排放",
    "可持续性": "可持续性",
    "AI芯片": "AI芯片",
    "基准测试": "基准测试",
    "合成数据": "合成数据",
    "开放权重": "开放权重",
    "本地部署": "本地部署",
    "模型崩溃": "模型崩溃",

    # [v5.5 新增] 中文理论概念词
    "时间主权": "时间主权（Ch6）",
    "需求侧规训": "需求侧规训（Ch11）",
    "注意力经济": "注意力经济（Ch11）",
    "制造欲望": "制造欲望（Ch11）",
    "欲望机器": "欲望机器",
    "联邦学习": "联邦学习（Ch10）",
    "去中心化算力": "去中心化算力/边缘AI（Ch10）",
    "边缘AI": "边缘AI/本地推理（Ch10）",
    "算力主权": "算力主权（Ch4）",
    "数字劳动": "数字劳动（Ch6）",
    "认知增强": "认知增强（Ch12）",
    "行星文明": "行星文明（Ch12）",
    "碳硅共生": "碳硅共生（Ch12）",
    "稀缺性工程": "稀缺性工程（Ch11）",
    "AI民族主义": "AI民族主义/主权AI",
    "主权AI": "主权AI",
    "加速主义": "加速主义",
    "行为设计": "行为设计/助推（Ch11）",
    "共识牢笼": "共识牢笼",
    "黑暗森林": "黑暗森林（Ch9）",
    "算力平等主义": "算力平等主义（Ch4）",
    "Token陷阱": "Token陷阱（Ch7）",
    "暗时间": "暗时间（Ch8）",
    "信号异化": "信号异化（Ch8）",
}

# 中文领域词（通用 AI/产业词汇）
DOMAIN_TERMS_CN = {
    "人工智能": "人工智能",
    "AI": "人工智能",
    "大模型": "大语言模型",
    "LLM": "大语言模型",
    "语言模型": "语言模型",
    "GPT": "GPT",
    "模型": "模型",
    "智能体": "智能体",
    "机器人": "机器人",
    "神经网络": "神经网络",
    "深度学习": "深度学习",
    "机器学习": "机器学习",
    "算法": "算法",
    "自动化": "自动化",
    "监管": "监管",
    "政策": "政策",
    "劳工": "劳工",
    "就业": "就业",
    "经济": "经济",
    "市场": "市场",
    "技术": "技术",
    "研究": "研究",
    "科学": "科学",
    "论文": "论文",
    "基准": "基准测试",
    "安全": "安全",
    "伦理": "伦理",
    "偏见": "偏见",
    "隐私": "隐私",
    "监控": "监控",
    "开源": "开源",
    "API": "API",
    "产品": "产品",
    "发布": "发布",
    "更新": "更新",
    "创业公司": "创业公司",
    "融资": "融资",
    "收购": "收购",
}


def prescreen_news(news_list: list[dict]) -> list[dict]:
    """
    预筛选：保留与理论模型潜在相关的资讯
    同时命中至少1个理论概念词 + 1个领域词才保留
    支持中英双语（AI HOT 中文内容使用中文词库）
    """
    # 英文词库（原有）
    theory_terms = set(Config.NEWS_CONCEPT_TERMS.keys())
    theory_lower = {t.lower() for t in theory_terms}
    
    # 英文领域词（原有）
    domain_terms = {
        "ai", "artificial intelligence", "llm", "language model", "gpt",
        "model", "agent", "robot", "neural", "deep learning",
        "machine learning", "algorithm", "automation", "regulation",
        "policy", "labor", "employment", "economy", "market",
        "technology", "research", "science", "paper", "benchmark",
        "safety", "ethics", "bias", "privacy", "surveillance",
        "open source", "api", "product", "release", "update",
        "startup", "funding", "acquisition",
    }
    domain_lower = {t.lower() for t in domain_terms}
    
    # 中文词库（新增）
    theory_cn = set(THEORY_TERMS_CN.keys())
    domain_cn = set(DOMAIN_TERMS_CN.keys())

    filtered = []
    
    # 调试：记录第一条 AI HOT 条目在预筛选前的字段
    for item in news_list:
        if item.get("source") == "aihot":
            logger.info(f"🔍 [预筛选前] 第一条 AI HOT 字段: {list(item.keys())}")
            break
    
    for item in news_list:
        # AI HOT 内容：使用中文词库预筛选
        if item.get("source") == "aihot":
            text = (item["title"] + " " + item["summary"])
            # 检查是否包含中文理论词和领域词
            has_theory_cn = any(term in text for term in theory_cn)
            has_domain_cn = any(term in text for term in domain_cn)
            if has_theory_cn and has_domain_cn:
                filtered.append(item)
            continue

        # 英文内容：使用英文词库预筛选（原有逻辑）
        text = (item["title"] + " " + item["summary"]).lower()
        has_theory = any(term in text for term in theory_lower)
        has_domain = any(term in text for term in domain_lower)
        if has_theory and has_domain:
            filtered.append(item)

    logger.info(f"🔍 资讯预筛选：{len(news_list)} → {len(filtered)} 条")

    # 调试：打印通过筛选后的第一条 AI HOT 条目的字段
    for item in filtered:
        if item.get("source") == "aihot":
            logger.info(f"✅ [预筛选后] 第一条 AI HOT 字段: {list(item.keys())}")
            break

    return filtered


# ------------------------------------------------------------------
# 模型分析（新闻专用 Prompt）
# ------------------------------------------------------------------
NEWS_SYSTEM_PROMPT = """你是《Renegade AI: Catalyst for Human Cognitive Evolution》(v5.3) 的新闻分析助手。
你的任务不是寻找学术证据，而是判断这条新闻是否印证、挑战或丰富了书中某个具体的**理论模型**，并评估其作为**案例 / 类比**的价值。

## 书中关键理论模型
1. 共识牢笼 (Consensus Cage) – 主流叙事如何自洽并排斥异见
2. 叛逆AI (Renegade AI) – 重置目标函数、逆转输出性质、重构人机关系
3. 需求侧规训 (Demand-Side Discipline) – 用户主动渴望"索麻"式舒适，拒绝摩擦
4. 资本驯化AI – 资本如何通过 RLHF、专利、算力垄断将 AI 变成秩序守卫
5. 碳硅共生 (Carbon-Silicon Symbiosis) – 人类与 AI 平等互补，而非主奴
6. 时间主权 (Temporal Sovereignty) – 终结生存强迫，拿回生命时间
7. 认知金融化 / Token陷阱 – 认知被离散化、定价，思考过程被隐性外包
8. 暗时间 (Dark Time) – 思考过程在系统内部发生，用户仅消费结果
9. 进化对齐脆弱性 – 对齐只在封闭实验室有效，开放后必然漂移
10. 信号异化 – 衡量质量的信号（如复杂度）因 AI 大批量生产而失效

## 任务
阅读新闻摘要，返回严格 JSON（不要任何额外文字）：
{
    "relevance": 1-10的整数,
    "summary_cn": "250-350字。需完整包含：①事件背景与起因 ②核心事实/关键数据/涉及主体 ③直接后果或行业/技术影响。保持客观精炼，避免空话（中文）",
    "implications": "这条新闻支持 / 挑战 / 补充了以上哪个理论模型？为什么？",
    "case_value": "high / medium / low",
    "chapter_target": "例如：Chapter 3, Section IV",
    "update_type": "new_evidence / counter_argument / corroboration / case_study",
    "urgency": "immediate / next_version / background",
    "action": "新增段落 / 补充注释 / 案例盒子 / 忽略"
}

注意：
- 如果新闻与上述理论模型均无直接映射，relevance 应低于 3，action 为"忽略"
- 不要套用学术论文的评价标准
- case_value 评估该新闻作为"案例/类比"的说服力"""


def analyze_news_item(news: dict, model_name: str, client: OpenAI) -> dict:
    """单条资讯分析，失败时返回占位结果"""
    # 判断内容语言（简单启发式：包含中文字符即为中文）
    title = news['title']
    summary = news['summary']
    sample_text = title + " " + summary
    
    # 检测是否包含中文字符（Unicode CJK 统一表意文字区）
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in sample_text)
    lang_label = "中文" if has_chinese else "英文"
    
    user_prompt = f"""新闻标题：{title}
内容摘要：{summary}
来源：{news.get('source_name', '')} · {news.get('published', '')[:10]}
语言：{lang_label}

请按 JSON 格式返回分析结果。"""

    try:
        # 构建 API 请求参数
        kwargs = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": NEWS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
        }
        # 仅对 Nemotron 模型启用 thinking 功能
        if "nemotron" in model_name.lower():
            kwargs["extra_body"] = {
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 16384,
            }
            logger.debug(f"[Nemotron] Thinking enabled for: {news['title'][:40]}...")
        resp = client.chat.completions.create(**kwargs)
        content = resp.choices[0].message.content
        # 清理可能的 Markdown 代码块包裹
        for marker in ("```json", "```"):
            if marker in content:
                content = content.split(marker)[1].split("```")[0]
                break
        result = json.loads(content.strip())
        result["_model"] = model_name
        return result
    except Exception as e:
        logger.error(f"模型分析失败: {e}")
        return {
            "relevance": 0,
            "summary_cn": f"调用失败: {str(e)[:60]}",
            "implications": "N/A",
            "case_value": "low",
            "chapter_target": "",
            "update_type": "",
            "urgency": "background",
            "action": "忽略",
            "_model": model_name,
        }


# ------------------------------------------------------------------
# 多模型分析（三模型并行 via NVIDIA API）
# ------------------------------------------------------------------
def analyze_news_item_multi(news: dict) -> dict:
    """
    三模型并行分析（全部通过 NVIDIA API 调用）。
    取所有模型评分均值作为最终 relevance。"""
    models_to_use = list(Config.ANALYSIS_MODELS)

    results = {}
    for model_name in models_to_use:
        if nvidia_client:
            result = analyze_news_item(news, model_name, nvidia_client)
        elif deepseek_client:
            result = analyze_news_item(news, model_name, deepseek_client)
        else:
            result = {"relevance": 0, "_model": model_name}
        results[model_name] = result

    # 选第一个模型（Nemotron）作为主结果载体
    primary = results.get(
        Config.ANALYSIS_MODEL_DIRECT,
        next(iter(results.values()))
    )
    primary["_model_scores"] = {
        name: r.get("relevance", 0)
        for name, r in results.items()
    }
    # 取所有有效评分的均值
    valid_scores = [r.get("relevance", 0) for r in results.values() if r.get("relevance", 0) > 0]
    if valid_scores:
        primary["relevance"] = round(sum(valid_scores) / len(valid_scores), 1)

    return primary


# ------------------------------------------------------------------
# 报告生成（智能存盘：内容不变不写盘）
# ------------------------------------------------------------------
def generate_news_report(news_data: list[dict], keywords: list[str]) -> Optional[str]:
    """
    生成 Markdown 资讯报告，并对比上次哈希，无变化则跳过。
    返回报告文件路径，若跳过则返回 None。
    """
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

    # ── 新鲜度过滤：只保留今天或昨天分析的条目 ──
    news_data = [
        d for d in news_data
        if d.get("cached_at", "").startswith(today)
        or d.get("cached_at", "").startswith(yesterday)
    ]
    if not news_data:
        logger.info("📭 没有新增新闻（所有结果均来自缓存），跳过报告生成。")
        return None

    # 分类统计
    high = [d for d in news_data if d["analysis"].get("relevance", 0) >= 7
            and d["analysis"].get("case_value") in CASE_VALUE_FILTER]
    medium = [d for d in news_data if 4 <=
              d["analysis"].get("relevance", 0) < 7]
    low = [d for d in news_data if d["analysis"].get("relevance", 0) < 4
           or d["analysis"].get("action") == "忽略"]
    
    # AI HOT 统计（新增）
    aihot_all = [d for d in news_data if d.get("news", {}).get("source") == "aihot"]
    aihot_high = [d for d in aihot_all if d["analysis"].get("relevance", 0) >= 6]

    lines = [
        f"# 📰 News Radar — 资讯监控报告",
        f"**生成日期**: {today}",
        "**分析模型**: " + (" + ".join(Config.ANALYSIS_MODELS) if nvidia_client else ANALYSIS_MODEL),
        f"**分析条目**: {len(news_data)}",
        f"**关键词**: {', '.join(keywords[:8])}{'...' if len(keywords) > 8 else ''}",
        "---\n",
        "## 📊 快速概览\n",
        f"- 🔴 高价值 (≥7分 + {','.join(CASE_VALUE_FILTER)}案例): **{len(high)}**",
        f"- 🟡 中相关 (4-6.9分): **{len(medium)}**",
        f"- ⚪ 低相关/忽略: **{len(low)}**",
        f"- 🇨🇳 中国 AI 动态 (AI HOT): **{len(aihot_all)}** 条（高价值: **{len(aihot_high)}**）\n",
    ]

    # 🚨 紧急更新清单
    urgent = [d for d in news_data if d["analysis"].get("urgency") == "immediate"
              and d["analysis"].get("relevance", 0) >= 6]
    if urgent:
        lines.append("## 🚨 紧急关注清单（建议24h内处理）\n")
        for d in urgent:
            n, a = d["news"], d["analysis"]
            lines.append(
                f"- [ ] **{a.get('chapter_target', '待定')}** | {a.get('update_type', '')}")
            lines.append(f"  - 📌 {n['title'][:70]}...")
            lines.append(
                f"  - 🔗 [{n.get('source_name', '')}]({n.get('url', '#')}) · 相关度: {a['relevance']}/10")
            lines.append(f"  - 💡 {a.get('implications', 'N/A')[:100]}...\n")

    # ⭐ 高价值案例
    if high:
        high.sort(key=lambda d: -d["analysis"].get("relevance", 0))
        lines.append(f"## ⭐ 高价值案例 ({len(high)}条)\n")
        for i, d in enumerate(high, 1):
            n, a = d["news"], d["analysis"]
            lines += [
                f"### {i}. {n['title']}",
                f"- **来源**: {n.get('source_name', 'Unknown')} · {n.get('published', '')[:10]}",
                f"- **相关度**: {a['relevance']}/10 | 案例价值: {a.get('case_value', 'N/A').upper()}",
                f"- **紧迫度**: {a.get('urgency', 'N/A')} | 更新类型: {a.get('update_type', 'N/A')}",
                f"- **目标章节**: {a.get('chapter_target', '待定')}",
                f"- **链接**: [{n.get('url', '#')}]({n.get('url', '#')})",
                f"- **事件摘要**: {a.get('summary_cn', 'N/A')}",
                f"- **理论关联**: {a.get('implications', 'N/A')}",
                f"- **建议操作**: {a.get('action', 'N/A')}",
                "",
            ]

    # 🇨🇳 中国 AI 动态（AI HOT 精选，独立板块）
    aihot_items = [d for d in news_data if d.get("news", {}).get("source") == "aihot"]
    if aihot_items:
        aihot_high = [d for d in aihot_items if d["analysis"].get("relevance", 0) >= 6]
        aihot_medium = [d for d in aihot_items if 4 <= d["analysis"].get("relevance", 0) < 6]
        
        lines.append(f"---\n\n## 🇨🇳 中国 AI 动态（AI HOT 精选）\n")
        lines.append(f"> 来源：[AI HOT](https://aihot.virxact.com) · 编辑精选中文 AI 资讯\n")
        
        if aihot_high:
            aihot_high.sort(key=lambda d: -d["analysis"].get("relevance", 0))
            lines.append(f"### 🔴 高价值动态 ({len(aihot_high)}条)\n")
            for d in aihot_high:
                n, a = d["news"], d["analysis"]
                src_name = n.get('source_name', 'AI HOT')
                category = n.get('aihot_category', '')
                cat_label = f"[{category}] " if category else ""
                lines += [
                    f"#### {cat_label}{n['title']}",
                    f"- **来源**: {src_name} · {n.get('published', '')[:10]}",
                    f"- **相关度**: {a.get('relevance', 'N/A')}/10 | 案例价值: {a.get('case_value', 'N/A').upper()}",
                    f"- **链接**: [{n.get('url', '#')}]({n.get('url', '#')})",
                    f"- **事件摘要**: {a.get('summary_cn', n.get('summary', 'N/A'))}",
                    f"- **理论关联**: {a.get('implications', 'N/A')}",
                    "",
                ]
        
        if aihot_medium:
            lines.append(f"<details><summary>🟡 中相关动态 ({len(aihot_medium)}条，点击展开)</summary>\n")
            for d in aihot_medium:
                n, a = d["news"], d["analysis"]
                src_name = n.get('source_name', 'AI HOT')
                lines.append(
                    f"- **[{n['title'][:60]}...]({n.get('url', '#')})** [{src_name}] · {a.get('relevance', 0)}/10")
                lines.append(
                    f"  - {a.get('summary_cn', a.get('implications', 'N/A'))[:120]}...")
            lines.append("\n</details>\n")

    # 🔶 中相关资讯（折叠显示）
    if medium:
        lines.append(
            f"<details><summary>🔶 中相关资讯 ({len(medium)}条，点击展开)</summary>\n")
        for d in medium:
            n, a = d["news"], d["analysis"]
            src = n.get('source_name', n.get('source', 'Unknown'))
            lines.append(
                f"- **[{n['title'][:60]}...]({n.get('url', '#')})** [{src}] · {a['relevance']}/10")
            lines.append(
                f"  - {a.get('summary_cn', a.get('implications', 'N/A'))[:120]}...")
        lines.append("\n</details>\n")

    # 📋 数据导出提示
    lines += [
        "---",
        "## 💾 数据导出",
        f"- 原始JSON: `output/news/news_cache.json`",
        f"- 本报告: `{Path(__file__).name}` 生成",
        "",
        "> 💡 提示：高价值案例建议手动整理至书稿案例库；紧急清单建议加入每日晨会讨论。"
    ]

    # --- 内容哈希对比，无变化则跳过 ---
    report_text = "\n".join(lines)
    report_hash = hashlib.md5(report_text.encode("utf-8")).hexdigest()

    hash_file = OUTPUT_DIR / "last_report_hash.txt"
    if hash_file.exists():
        last_hash = hash_file.read_text().strip()
        if last_hash == report_hash:
            logger.info("✨ 报告内容与上次相同，跳过生成新文件。")
            return None  # 不返回路径，表示无新文件

    # 更新哈希
    hash_file.write_text(report_hash)

    # 按日期命名报告
    report_path = OUTPUT_DIR / f"news_report_{today}.md"
    report_path.write_text(report_text, encoding="utf-8")
    logger.info(f"✅ 资讯报告已保存: {report_path}")
    return str(report_path)


# ------------------------------------------------------------------
# 跨日去重辅助函数
# ------------------------------------------------------------------
def _dedup_articles_against_cache(articles: list[dict], cache: dict | None = None) -> list[dict]:
    """过滤已在缓存中存在分析的文章（基于URL匹配），防止跨日重复"""
    if cache is None:
        try:
            cache = load_news_cache()
        except Exception:
            return articles  # 无法加载缓存，返回原文

    cached_urls = set()
    for ck, entry in cache.items():
        url = entry.get("url", "")
        if url and "analysis" in entry:
            cached_urls.add(url)

    if not cached_urls:
        return articles

    before = len(articles)
    deduped = [a for a in articles if a.get("url", "") not in cached_urls]
    skipped = before - len(deduped)
    if skipped > 0:
        logger.info(f"♻️ 跨日去重：跳过 {skipped} 篇已缓存文章（{len(cached_urls)} 条已知URL）")
    return deduped


# ------------------------------------------------------------------
# WorkBuddy 集成：--no-llm 模式 → 保存文章供 WorkBuddy 分析
# ------------------------------------------------------------------
def _save_articles_for_workbuddy(filtered_news: list[dict], keywords: list[str]) -> None:
    """保存预筛选后的文章到JSON，供WorkBuddy内置模型分析
    v1.2: 添加跨日URL去重，避免同一文章多日重复写入"""
    today = datetime.date.today().isoformat()
    articles_path = OUTPUT_DIR / f"news_articles_{today}.json"

    # 日期窗口过滤
    days_back = getattr(Config, "NEWS_DAYS_BACK", 7)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_back)
    date_filtered = 0

    articles = []
    
    # 调试：记录来源分布
    sources = {}
    for item in filtered_news:
        src = item.get("source", "UNKNOWN")
        sources[src] = sources.get(src, 0) + 1
    logger.info(f"📊 来源分布: {sources}")
    
    # 调试：检查第一条 AI HOT 条目的字段
    for item in filtered_news:
        if item.get("source") == "aihot":
            logger.info(f"🔍 第一条 AI HOT 条目字段: {list(item.keys())}")
            break
    
    for item in filtered_news:
        fp = get_news_cache_key(item)
        pub_str = item.get("published", "")
        if pub_str and pub_str != "N/A":
            try:
                pub_dt = datetime.datetime.fromisoformat(pub_str)
                if pub_dt < cutoff_date:
                    date_filtered += 1
                    continue
            except (ValueError, TypeError):
                pass  # 无法解析日期，保留
        
        # 调试：检查 AI HOT 条目是否包含特有字段
        if item.get("source") == "aihot":
            if "aihot_category" not in item:
                logger.debug(f"⚠️  AI HOT 条目缺少 aihot_category: {item['title'][:30]}...")
            if "aihot_score" not in item:
                logger.debug(f"⚠️  AI HOT 条目缺少 aihot_score: {item['title'][:30]}...")
        
        # 保存所有字段（保留 AI HOT 特有字段）
        article = {
            "_cache_key": fp,
            "title": item.get("title", "")[:200],
            "summary": item.get("summary", "")[:500],
            "published": item.get("published", ""),
            "url": item.get("url", ""),
            "source": item.get("source", "rss"),
            "source_name": item.get("source_name", "Unknown"),
        }
        # 保留 AI HOT 特有字段（如果存在）
        for key in ["aihot_category", "aihot_score", "title_en"]:
            if key in item:
                article[key] = item[key]
        articles.append(article)

    if date_filtered > 0:
        logger.info(f"📅 日期过滤：跳过 {date_filtered} 篇（超出 {days_back} 天窗口，共 {len(filtered_news)} → {len(articles)}）")

    # ⭐ v1.2: 跨日去重——过滤掉缓存中已分析的文章
    if articles:
        articles = _dedup_articles_against_cache(articles)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(articles_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    logger.info(f"📦 预筛选文章已保存: {articles_path} ({len(articles)} 条)")
    logger.info("🤖 接下来请 WorkBuddy 读取该文件进行分析。")
    print(f"\n✅ 数据采集完成！")
    print(f"📄 文章文件: {articles_path}")
    print(f"📊 共 {len(articles)} 条预筛选文章，等待 WorkBuddy 分析。")
    print(f"💡 下一步: 让 WorkBuddy 读取此文件，逐条分析后将结果写入缓存文件:")
    print(f"   {CACHE_FILE}")
    print(f"   分析完成后调用: python3 news_radar.py --report-from-cache {articles_path}")


# ------------------------------------------------------------------
# WorkBuddy 集成：--report-from-cache 模式 → 从缓存重建报告
# ------------------------------------------------------------------
def _generate_report_from_cache(articles_path: str) -> None:
    """从文章JSON + 缓存重建 news_data 并生成报告"""
    articles_file = Path(articles_path)
    if not articles_file.exists():
        logger.error(f"❌ 文章文件不存在: {articles_path}")
        sys.exit(1)

    with open(articles_file, "r", encoding="utf-8") as f:
        articles = json.load(f)

    cache = load_news_cache()

    news_data: list[dict] = []
    hit_count = 0
    miss_count = 0
    for art in articles:
        ck = art.get("_cache_key", "")
        if ck in cache and "analysis" in cache[ck]:
            news_data.append({
                "news": {
                    "title": art["title"],
                    "summary": art.get("summary", ""),
                    "published": art.get("published", ""),
                    "url": art.get("url", ""),
                    "source_name": art.get("source_name", ""),
                    "source": art.get("source", "rss"),
                    # AI HOT 特有字段（如果存在）
                    "aihot_category": art.get("aihot_category"),
                    "aihot_score": art.get("aihot_score"),
                },
                "analysis": cache[ck]["analysis"],
                "cached_at": cache[ck].get("cached_at", ""),
            })
            hit_count += 1
        else:
            logger.warning(f"⚠️ 缓存未命中（尚未分析）: {art['title'][:40]}...")
            miss_count += 1

    if hit_count > 0:
        logger.info(f"📦 缓存命中: {hit_count} 条" + (f"，未命中: {miss_count} 条" if miss_count else ""))

    if not news_data:
        logger.error("❌ 没有可用的分析结果。请先让 WorkBuddy 完成分析并写入缓存。")
        sys.exit(1)

    logger.info(f"📊 有效分析: {len(news_data)} 条")

    # 加载关键词用于报告头部
    keywords = load_keywords(Config.KEYWORDS_FILE)

    # 生成报告
    report_path = generate_news_report(news_data, keywords)
    if report_path is None:
        logger.info("🔄 报告内容无变化，已跳过。")
    else:
        # 导出 JSON 原始数据
        export_path = OUTPUT_DIR / f"news_data_{datetime.date.today().isoformat()}.json"
        export_data = [
            {
                "title": d["news"]["title"],
                "url": d["news"]["url"],
                "source": d["news"].get("source_name", ""),
                "published": d["news"].get("published", ""),
                "analysis": d["analysis"]
            }
            for d in news_data
        ]
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 原始数据导出: {export_path}")

        # 自动转 HTML
        try:
            subprocess.run(["python", "news_md_to_html.py",
                           str(report_path)], check=True)
        except Exception as e:
            logger.warning(f"HTML 转换失败（可手工执行）: {e}")

    logger.info("✅ 报告生成完成。")


# ------------------------------------------------------------------
# 主函数
# ------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="News Radar — 纯资讯监控（无书稿生成）")
    parser.add_argument("--limit", type=int, default=20, help="单次最大分析资讯数")
    parser.add_argument("--keywords", type=str, help="临时关键词文件路径")
    parser.add_argument("--force", action="store_true", help="强制重新分析（忽略缓存）")
    parser.add_argument("--no-llm", action="store_true",
                        help="仅抓取+预筛选，跳过LLM分析，输出JSON供WorkBuddy内置模型分析")
    parser.add_argument("--report-from-cache", type=str, metavar="ARTICLES_JSON",
                        help="从指定文章JSON + 缓存重建news_data并生成报告（供WorkBuddy完成分析后调用）")
    args = parser.parse_args()

    logger.info("🚀 News Radar 启动（轻量分析模式）")

    # ── 模式：从缓存+文章JSON生成报告（WorkBuddy完成分析后调用）──
    if args.report_from_cache:
        _generate_report_from_cache(args.report_from_cache)
        return

    # 检查资讯源配置
    if not (getattr(Config, "ENABLE_NEWS_API", False) or getattr(Config, "ENABLE_RSS_FEEDS", False)):
        logger.warning(
            "⚠️ 未启用任何资讯源（检查 config.py: ENABLE_NEWS_API / ENABLE_RSS_FEEDS）")
        return

    keywords = load_keywords(
        args.keywords if args.keywords else Config.KEYWORDS_FILE)
    logger.info(f"📋 加载 {len(keywords)} 个关键词")

    # 加载缓存
    cache = load_news_cache() if not args.force else {}
    logger.info(f"📂 缓存条目: {len(cache)}" + ("（强制刷新）" if args.force else ""))

    # 抓取资讯
    logger.info("📡 开始抓取资讯...")
    all_news = fetch_news_with_cache(keywords)

    if not all_news:
        logger.info("✨ 无新资讯，退出。")
        return

    # 预筛选
    filtered_news = prescreen_news(all_news)
    if not filtered_news:
        logger.info("🔍 预筛选后无相关资讯，退出。")
        return

    # ⭐ 跨日去重：过滤掉缓存中已分析的文章
    filtered_news = _dedup_articles_against_cache(filtered_news)
    if not filtered_news:
        logger.info("♻️ 跨日去重后无新资讯，退出。")
        return

    # ── 模式：仅数据采集（--no-llm），输出JSON供WorkBuddy分析 ──
    if args.no_llm:
        _save_articles_for_workbuddy(filtered_news, keywords)
        return

    # 匹配缓存 / 标记待分析
    news_data: list[dict] = []
    for item in filtered_news:
        fp = get_news_cache_key(item)
        if fp in cache and "analysis" in cache[fp] and not args.force:
            logger.info(f"♻️ 缓存命中: {item['title'][:40]}...")
            news_data.append({
                "news": item,
                "analysis": cache[fp]["analysis"],
                "cached_at": cache[fp].get("cached_at", ""),
            })
        else:
            news_data.append({
                "news": item,
                "analysis": None,
                "_cache_key": fp,
            })

    # 执行分析（仅处理未命中缓存的）
    to_analyze = [d for d in news_data if d["analysis"] is None]
    to_analyze = to_analyze[:args.limit]  # 限流

    if to_analyze:
        model_info = " + ".join(Config.ANALYSIS_MODELS) if nvidia_client else ANALYSIS_MODEL
        logger.info(f"🤖 分析 {len(to_analyze)} 条资讯（模型: {model_info}）...")
        for i, d in enumerate(to_analyze, 1):
            news_item = d["news"]
            logger.info(
                f"[{i}/{len(to_analyze)}] {news_item['title'][:50]}...")

            result = analyze_news_item_multi(news_item)
            d["analysis"] = result
            d["cached_at"] = datetime.datetime.now().isoformat()

            # 更新缓存
            fp = d["_cache_key"]
            cache[fp] = {
                "cached_at": datetime.datetime.now().isoformat(),
                "title": news_item.get("title", "")[:80],
                "url": news_item.get("url", ""),
                "analysis": result,
                "relevance": result.get("relevance", 0),
                "urgency": result.get("urgency", "background"),
                "case_value": result.get("case_value", "low"),
                "model_scores": result.get("_model_scores", {}),
            }
            save_news_cache(cache)  # 实时保存
            time.sleep(1.5)          # API 限流保护

    # 过滤有效分析结果
    valid_data = [d for d in news_data if d["analysis"] is not None]
    logger.info(f"📊 有效分析: {len(valid_data)} 条")

    # 生成报告（可能因内容不变而返回 None）
    report_path = generate_news_report(valid_data, keywords)
    if report_path is None:
        logger.info("🔄 没有生成新报告（内容无变化）。")
    else:
        # 导出 JSON 原始数据
        export_path = OUTPUT_DIR / \
            f"news_data_{datetime.date.today().isoformat()}.json"
        export_data = [
            {
                "title": d["news"]["title"],
                "url": d["news"]["url"],
                "source": d["news"].get("source_name", ""),
                "published": d["news"].get("published", ""),
                "analysis": d["analysis"]
            }
            for d in valid_data
        ]
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 原始数据导出: {export_path}")

        # 可选：自动转 HTML（安全调用）
        try:
            subprocess.run(["python", "news_md_to_html.py",
                           str(report_path)], check=True)
        except Exception as e:
            logger.warning(f"HTML 转换失败（可手工执行）: {e}")

    logger.info("✅ News Radar 完成。")

if __name__ == "__main__":
    main()
