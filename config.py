import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # =========================================================================
    #  API 密钥
    # =========================================================================
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

    # =========================================================================
    #  抓取设置
    # =========================================================================
    MAX_RESULTS_PER_KEYWORD = int(os.getenv("MAX_RESULTS_PER_KEYWORD", "10"))
    ARXIV_PAGE_SIZE = int(os.getenv("ARXIV_PAGE_SIZE", "100"))
    ARXIV_DELAY_SECONDS = float(os.getenv("ARXIV_DELAY_SECONDS", "5.0"))

    # =========================================================================
    #  模型配置 (2026-05-09 完美版)
    #  策略：全程 DeepSeek 官网直连，彻底弃用 OpenRouter
    #   - DeepSeek V4 Flash (deepseek-v4-flash) → 大量论文/资讯分析（快速便宜）
    #   - DeepSeek V4 Pro  (deepseek-v4-pro)  → 书稿草稿生成（强推理，少量调用）
    # =========================================================================
    ANALYSIS_MODEL_DIRECT = "deepseek-v4-flash"          # 分析专用
    DRAFTING_MODEL        = "deepseek-v4-pro"            # 草稿专用

    # 分析模型列表（目前只有直连，保留结构方便未来扩展）
    ANALYSIS_MODELS = [ANALYSIS_MODEL_DIRECT]

    # 草稿自动生成阈值
    DRAFT_RELEVANCE_THRESHOLD = int(os.getenv("DRAFT_RELEVANCE_THRESHOLD", "8"))
    DRAFT_URGENCY_REQUIRED    = os.getenv("DRAFT_URGENCY_REQUIRED", "immediate")

    # -------------------------------------------------------------------------
    #  预留：DeepSeek V4 推理深度控制（当前主流程未使用，可后续接入）
    # -------------------------------------------------------------------------
    REASONING_EFFORT = os.getenv("REASONING_EFFORT", "high")     # low / medium / high
    ENABLE_COT_PROMPT = os.getenv("ENABLE_COT_PROMPT", "true").lower() in ("true", "1", "yes")

    # -------------------------------------------------------------------------
    #  预留：万级文献缓存升级（当前使用 JSON，数据量激增后可启用 SQLite）
    # -------------------------------------------------------------------------
    USE_SQLITE_CACHE = False
    DATABASE_URL = os.getenv("DATABASE_URL", "renegade_radar.db")

    # =========================================================================
    #  资讯聚合 (News + RSS)
    # =========================================================================
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    ENABLE_NEWS_API = os.getenv("ENABLE_NEWS_API", "false").lower() in ("true", "1", "yes")
    ENABLE_RSS_FEEDS = os.getenv("ENABLE_RSS_FEEDS", "true").lower() in ("true", "1", "yes")
    NEWS_DAYS_BACK = int(os.getenv("NEWS_DAYS_BACK", "7"))

    # -------------------------------------------------------------------------
    #  预留：RSS 源异常保护（后续接入 news_sources.py，当前仅占位）
    # -------------------------------------------------------------------------
    RSS_TIMEOUT = int(os.getenv("RSS_TIMEOUT", "10"))          # 单源超时秒数
    RSS_MAX_FAILURES = int(os.getenv("RSS_MAX_FAILURES", "3")) # 连续失败次数后自动暂停
    SUSPENDED_FEEDS = []                                       # 自动暂停的源列表

    # 预设的 RSS 订阅源（完整版，共 16 个源）
    RSS_FEEDS = {
        # === 已有稳定源（保留）===
        "MIT Tech Review": "https://www.technologyreview.com/feed/",
        "Hacker News (AI)": "https://hnrss.org/frontpage?q=AI+OR+artificial-intelligence",
        "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        "The Verge - AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",

        # === 新增：权威科技与商业叙事 ===
        "WIRED - AI": "https://www.wired.com/feed/category/ai/latest/rss",
        "IEEE Spectrum - AI": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
        "Bloomberg - Technology": "https://feeds.bloomberg.com/technology/news.rss",

        # === 新增：深度分析与跨学科批判 ===
        "The Conversation - Tech": "https://theconversation.com/technology/articles.atom",
        "AIAAIC (AI争议库)": "https://www.aiaaic.org/feed",
        "Aeon - Technology": "https://aeon.co/feeds/technology",
        "Tech Policy Press": "https://techpolicy.press/feed",

        # === 新增：非西方视角 ===
        "Rest of World": "https://restofworld.org/feed/",
        "MIT News - AI": "https://news.mit.edu/rss/topic/artificial-intelligence2",

        # === 新增：开发者与社区视角 ===
        "TLDR AI": "https://tldr.tech/ai/rss",
        "Hugging Face Daily Papers": "https://huggingface.co/papers/feed.rss",
    }

    # =========================================================================
    #  新闻预筛选关键词（完整词库，带中文注释）
    # =========================================================================
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

        # 全球化/伦理/硬件等扩展主题
        "regulation": "AI监管",
        "data center": "数据中心/算力",
        "recycling": "硬件回收",
        "accessibility": "可及性",
        "indigenous": "本土/在地化",
        "carbon": "碳排放",
        "sustainability": "可持续性",
        "chip": "AI芯片",
        "benchmark": "基准测试",
        "synthetic data": "合成数据",
        "open weight": "开放权重",
        "local deployment": "本地部署",
        "model collapse": "模型崩溃",
    }

    # =========================================================================
    #  路径配置
    # =========================================================================
    BASE_DIR = Path(__file__).parent                         # 项目根目录
    KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")
    LOG_DIR = BASE_DIR / "logs"                             # 日志目录（自动创建）
    SEEN_IDS_FILE = os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE = os.getenv("CACHE_FILE", "paper_cache.json")

    # =========================================================================
    #  速率限制
    # =========================================================================
    S2_RATE_LIMIT = float(os.getenv("S2_RATE_LIMIT", "1.0"))

    # OpenRouter 相关配置已全部删除（2026-05-08）