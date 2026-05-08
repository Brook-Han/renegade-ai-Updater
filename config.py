# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ---------- API Keys ----------
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

    # ---------- Fetch settings ----------
    MAX_RESULTS_PER_KEYWORD = int(os.getenv("MAX_RESULTS_PER_KEYWORD", "10"))
    ARXIV_PAGE_SIZE = int(os.getenv("ARXIV_PAGE_SIZE", "100"))
    ARXIV_DELAY_SECONDS = float(os.getenv("ARXIV_DELAY_SECONDS", "5.0"))

    # ============================================================
    # 模型配置 (2026-05-07 最终版)
    # 策略：
    #   - 不用免费模型（避免 429 限流导致分析不完整）
    #   - DeepSeek V4 Flash 直连 → 大量分析任务（快速便宜）
    #   - DeepSeek 路由（OpenRouter）→ 辅助对比（消耗 OpenRouter 余额）
    #   - DeepSeek V4 Pro 直连 → 书稿草稿生成（少量调用，强推理）
    # ============================================================

    # OpenRouter 模型列表（全部使用 DeepSeek，稳定不掉线）
    OPENROUTER_MODELS = [
        "deepseek/deepseek-v4-pro",     # OpenRouter 自动路由到 DeepInfra/Novita
    ]

    # 实际分析模型列表（只在 OpenRouter 上跑的模型）
    ANALYSIS_MODELS = OPENROUTER_MODELS

    # ---------- 直连模型指定 ----------
    # 大量论文分析用（速度快、成本低，走 DeepSeek 官网余额）
    ANALYSIS_MODEL_DIRECT = "deepseek-v4-flash"
    # 书稿草稿生成用（需要强推理和写作能力，走 DeepSeek 官网余额）
    DRAFTING_MODEL = "deepseek-v4-pro"

    DRAFT_RELEVANCE_THRESHOLD = int(os.getenv("DRAFT_RELEVANCE_THRESHOLD", "8"))
    DRAFT_URGENCY_REQUIRED = os.getenv("DRAFT_URGENCY_REQUIRED", "immediate")

    # ---------- News aggregation ----------
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    ENABLE_NEWS_API = os.getenv("ENABLE_NEWS_API", "false").lower() in ("true", "1", "yes")
    ENABLE_RSS_FEEDS = os.getenv("ENABLE_RSS_FEEDS", "true").lower() in ("true", "1", "yes")
    NEWS_DAYS_BACK = int(os.getenv("NEWS_DAYS_BACK", "7"))

    # 预设的 RSS 订阅源，可直接在代码里增删，或留一个字符串在 .env 中解析
    RSS_FEEDS = {
       "MIT Tech Review": "https://www.technologyreview.com/feed/",
        "Hacker News (AI)": "https://hnrss.org/frontpage?q=AI+OR+artificial+intelligence",
        "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        "The Verge - AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    }
    
    # ---------- News pre‑screening (v1.1 追加 Zotero 词库) ----------
    # 字典结构: { "关键词": "中文释义", ... }
    NEWS_CONCEPT_TERMS = {
        # 公司/人物/事件
        "openai": "OpenAI公司",
        "anthropic": "Anthropic公司",
        "deepmind": "DeepMind公司",
        "google ai": "Google AI",
        "microsoft ai": "微软 AI",
        "musk": "马斯克",
        "altman": "奥特曼",
        "court": "法院/诉讼",
        "lawsuit": "诉讼/法律纠纷",
        "regulat": "监管",

        # AI 安全与对齐
        "align": "对齐",
        "safety test": "安全测试",
        "trust": "信任",
        "lie": "谎言/欺骗",
        "promise": "承诺",

        # 搜索与信息消费
        "search summar": "搜索摘要",
        "overview": "AI概览",
        "ai overview": "AI概览",
        "quote reddit": "引用Reddit",

        # 操纵与说服
        "manipulat": "操纵",
        "persua": "说服",
        "sycophan": "奉承",
        "companion": "AI伴侣",

        # 认知与共识
        "cognitive": "认知",
        "consensus": "共识",
        "renegade": "叛逆者",
        "time sovereignty": "时间主权",

        # 叙事与陷阱
        "dark forest": "黑暗森林",
        "token trap": "Token陷阱",
        "financialization": "金融化",

        # 技术与训练
        "rlhf": "人类反馈强化学习",
        "alignment tax": "对齐税",
        "open source": "开源",
        "decentraliz": "去中心化",
        "compute egalitarian": "算力平等主义",
        "edge computing": "边缘计算",

        # 社会与民主
        "democracy": "民主",
        "public opinion": "公众舆论",
        "misinformation": "错误信息",
        "military": "军事",
        "national security": "国家安全",
        "weapon": "武器/自主武器",

        # 知识产权与劳动
        "copyright": "版权",
        "ip": "知识产权",
        "intellectual property": "知识产权",
        "labor": "劳工",
        "job": "工作/就业",
        "work": "劳动",
        "ubi": "全民基本收入",
        "universal basic income": "全民基本收入",

        # Zotero 词库补充
        "post-anthropocentrism": "后人类中心主义",
        "demand-side discipline": "需求侧规训",
        "desire reproduction": "欲望再生产",
        "innovation turnaround": "创新转向",
        "product cycle ethics": "产品周期伦理",
        "commodification of ethics": "伦理商品化",
        "cognitive experience management": "认知体验管理",
        "experimental appendix": "实验附录",
        "carbon-silicon dialogue": "碳硅对话",
        "supply-demand feedback loop": "供需反馈环",
        "scientific narrowing": "科学窄化",
        "signal collapse": "信号崩塌",
        "society of thought": "思维社会",
        "meta-design": "元设计",
        "Lemian Terror": "莱姆式恐怖",
        "infosphere": "信息圈",
        "Moravec paradox": "莫拉维克悖论",
        "Densing Law": "密度定律",
    }

    # ---------- Paths ----------
    KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")
    SEEN_IDS_FILE = os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE = os.getenv("CACHE_FILE", "paper_cache.json")

    # ---------- Rate limiting ----------
    S2_RATE_LIMIT = float(os.getenv("S2_RATE_LIMIT", "1.0"))
    OPENROUTER_RATE_LIMIT = float(os.getenv("OPENROUTER_RATE_LIMIT", "3.0"))