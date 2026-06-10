import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（使用 __file__ 显式指定路径，避免 CWD 依赖）
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path)


# ═══════════════════════════════════════════════════════
#  模块级工具函数（放在类外，避免类属性调用报错）
# ═══════════════════════════════════════════════════════
def _parse_bool_env(key: str, default: bool = False) -> bool:
    """
    从环境变量读取布尔值
    支持 'true', '1', 'yes'（不区分大小写）
    用法示例：ENABLE_RSS = _parse_bool_env('ENABLE_RSS', True)
    """
    val = os.getenv(key, str(default))
    return val.lower() in ("true", "1", "yes")


class Config:
    """
    Renegade Radar 项目总配置类
    ---------------------------
    所有配置项集中管理，可通过 .env 文件覆盖默认值。

    使用方式：
        from config import Config
        key = Config.DEEPSEEK_API_KEY

    重要：启动不同模块时按需验证：
        - 新闻雷达（news_radar.py）：Config.validate()          # 只检查 DeepSeek
        - 学术雷达（academic_radar.py）：Config.validate(require_s2=True)  # 需要 Semantic Scholar
    """

    # =========================================================================
    #  基础路径（必须在最前面，供后续路径拼接使用）
    # =========================================================================
    BASE_DIR = Path(__file__).parent  # 项目根目录（本文件所在文件夹）

    # =========================================================================
    #  API 密钥
    # =========================================================================
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    SEMANTIC_SCHOLAR_API_KEY: str = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

    # =========================================================================
    #  抓取设置
    # =========================================================================
    MAX_RESULTS_PER_KEYWORD: int = int(os.getenv("MAX_RESULTS_PER_KEYWORD", "10"))
    ARXIV_PAGE_SIZE: int = int(os.getenv("ARXIV_PAGE_SIZE", "100"))
    ARXIV_DELAY_SECONDS: float = float(os.getenv("ARXIV_DELAY_SECONDS", "5.0"))

    # -------------------------------------------------------------------------
    #  arXiv API 限流设置（解决 429 Too Many Requests）
    # -------------------------------------------------------------------------
    ARXIV_INTER_KEYWORD_DELAY: float = float(os.getenv("ARXIV_INTER_KEYWORD_DELAY", "4.0"))
    # 每次关键词搜索之间额外等待秒数。
    # arxiv.Client 内置 delay_seconds=5s + 这里 4s = 约9秒间隔，远高于官方的"每3秒1次"

    ARXIV_RETRY_BASE_DELAY: float = float(os.getenv("ARXIV_RETRY_BASE_DELAY", "30.0"))
    # 遇到 429 限速后，指数退避的基础等待秒数
    # 依次等待: 30s → 60s → 120s → 240s → 480s（最长 600s=10分钟）

    ARXIV_MAX_RETRIES: int = int(os.getenv("ARXIV_MAX_RETRIES", "5"))
    # 429 限速时的最大重试次数（每次用指数退避）

    ARXIV_CLIENT_NUM_RETRIES: int = int(os.getenv("ARXIV_CLIENT_NUM_RETRIES", "2"))
    # arxiv 库内部的重试次数。设小一点：库内重试没有指数退避，
    # 遇到 429 时快速失败，交给上层脚本的指数退避+抖动来处理

    # =========================================================================
    #  模型配置 (2026-06-07 三模型并行 via NVIDIA API)
    #  策略：全部通过 NVIDIA 官方 API (https://integrate.api.nvidia.com/v1) 调用
    #   - nvidia/nemotron-3-ultra-550b-a55b  → 主分析模型（强推理）
    #   - deepseek-ai/deepseek-v4-flash        → 次模型（快速，低成本）
    #   - moonshotai/kimi-k2.6                 → 次模型（补充视角）
    #  三个模型并行分析后合并结果。
    # =========================================================================
    ANALYSIS_MODEL_DIRECT: str = os.getenv(
        "ANALYSIS_MODEL_DIRECT", "nvidia/nemotron-3-ultra-550b-a55b"
    )
    DRAFTING_MODEL: str = os.getenv(
        "DRAFTING_MODEL", "deepseek-ai/deepseek-v4-flash"
    )

    # -------------------------------------------------------------------------
    #  NVIDIA 官方 API 配置（所有模型共用）
    # -------------------------------------------------------------------------
    OPENROUTER_BASE_URL: str = os.getenv(
        "OPENROUTER_BASE_URL", "https://integrate.api.nvidia.com/v1"
    )

    # 并行分析模型列表（按优先级排序）
    ANALYSIS_MODELS: list[str] = os.getenv(
        "ANALYSIS_MODELS",
        "nvidia/nemotron-3-ultra-550b-a55b,deepseek-ai/deepseek-v4-flash,moonshotai/kimi-k2.6"
    ).split(",")

    # 草稿自动生成阈值
    DRAFT_RELEVANCE_THRESHOLD: int = int(os.getenv("DRAFT_RELEVANCE_THRESHOLD", "8"))
    DRAFT_URGENCY_REQUIRED: str = os.getenv(
        "DRAFT_URGENCY_REQUIRED", "immediate"
    )  # 可选 immediate / high / low

    # -------------------------------------------------------------------------
    #  DeepSeek V4 推理深度控制（正式启用，用于草稿生成）
    #  - REASONING_EFFORT：推理预算，low / medium / high
    #  - ENABLE_COT_PROMPT：是否在 Prompt 中显式引导分步推理
    # -------------------------------------------------------------------------
    REASONING_EFFORT: str = os.getenv("REASONING_EFFORT", "high")
    ENABLE_COT_PROMPT: bool = _parse_bool_env("ENABLE_COT_PROMPT", True)

    # -------------------------------------------------------------------------
    #  预留：万级文献缓存升级（当前使用 JSON，数据量激增后可启用 SQLite）
    #  注意：USE_SQLITE_CACHE 当前未生效，仅为后续扩展预留。
    # -------------------------------------------------------------------------
    USE_SQLITE_CACHE: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL", "renegade_radar.db")

    # =========================================================================
    #  资讯聚合 (News + RSS)
    # =========================================================================
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    ENABLE_NEWS_API: bool = _parse_bool_env("ENABLE_NEWS_API", False)
    ENABLE_RSS_FEEDS: bool = _parse_bool_env("ENABLE_RSS_FEEDS", True)
    NEWS_DAYS_BACK: int = int(os.getenv("NEWS_DAYS_BACK", "7"))
    ACADEMIC_DAYS_BACK: int = int(os.getenv("ACADEMIC_DAYS_BACK", "90"))  # 学术论文发布周期较慢，默认 90 天

    # -------------------------------------------------------------------------
    #  新闻分析筛选阈值（与 news_radar.py 联动）
    # -------------------------------------------------------------------------
    NEWS_RELEVANCE_THRESHOLD: int = int(os.getenv("NEWS_RELEVANCE_THRESHOLD", "5"))
    NEWS_CASE_VALUE_FILTER: list[str] = os.getenv(
        "NEWS_CASE_VALUE_FILTER", "high"
    ).split(",")

    # -------------------------------------------------------------------------
    #  RSS 源异常保护（预留占位，后续由 news_sources.py 实际使用）
    # -------------------------------------------------------------------------
    RSS_TIMEOUT: int = int(os.getenv("RSS_TIMEOUT", "10"))          # 单源超时（秒）
    RSS_MAX_FAILURES: int = int(os.getenv("RSS_MAX_FAILURES", "3")) # 连续失败自动暂停
    SUSPENDED_FEEDS: list[str] = []   # 运行时由监控模块动态填充，请勿手动修改
    # 预设的 RSS 订阅源（完整版，整合全量权威源）
    RSS_FEEDS: dict[str, str] = {
        # ===================== 1. 公司官方博客 =====================
        "OpenAI Blog": "https://openai.com/blog/rss.xml",
        # ❌ Anthropic Blog 已于 2025 年底改版为 Webflow，完全移除了 RSS feed
        #    替代渠道：Hacker News AI、Import AI、Interconnects 等都会覆盖 Anthropic 的重要发布
        # [新增] Anthropic 的深层研究与经济/安全团队动态（通过 Import AI 等渠道捕获）
        "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default",
        "DeepMind Blog": "https://deepmind.com/blog/feed/basic",
        "Meta Engineering Blog": "https://engineering.fb.com/feed/",
        "NVIDIA Blog": "https://blogs.nvidia.com/feed/",

        # ===================== 1.5 [新增] 顶级产业智库与深度研究 (核心补丁) =====================
        "SemiAnalysis": "https://semianalysis.substack.com/feed",  # 捕捉 Dark Output, 算力地缘政治
        "The Gradient": "https://thegradient.pub/rss/",           # 深度AI演化与认知科学交叉
        "AI Snake Oil (Arvind Narayanan)": "https://aisnakeoil.substack.com/feed/",
        
        # ===================== 2. 顶级科技媒体 =====================
        "MIT Technology Review AI": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "The Verge AI": "https://www.theverge.com/ai/rss/index.xml",
        "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "Ars Technica AI": "https://arstechnica.com/category/ai/feed/",
        "Wired AI": "https://www.wired.com/feed/category/ai/latest/rss",
        "404 Media": "https://www.404media.co/feed",

        # ===================== 3. 社区与论文源 =====================
        "Hacker News AI": "https://hnrss.org/ai",
        "HuggingFace Daily Papers": "https://huggingface.co/papers/rss",

        # ===================== 4. 行业顶级 Newsletter =====================
        "Import AI (Jack Clark)": "https://importai.substack.com/feed",
        "Ben's Bites": "https://bensbites.beehiiv.com/feed",
        "Latent Space": "https://www.latent.space/feed",
        "Interconnects (Nathan Lambert)": "https://interconnects.substack.com/feed",
        "AI Snake Oil (Arvind Narayanan)": "https://aisnakeoil.substack.com/feed",
        "One Useful Thing (Ethan Mollick)": "https://www.oneusefulthing.org/feed",

        # ===================== 5. 独立博客 =====================
        "Simon Willison's Weblog": "https://simonwillison.net/feed/",
    }

    # =========================================================================
    #  新闻预筛选关键词（完整词库，键为英文匹配词，值为中文注释）
    #  使用方法：遍历键名，检查新闻标题/摘要是否包含关键词（大小写不敏感）
    # =========================================================================
    NEWS_CONCEPT_TERMS: dict[str, str] = {
        # =========================================================================
        #  [新增] 架构演化与资本自噬 (触发 RSI 与 暗产出 警报)
        # =========================================================================
        "recursive self-improvement": "递归自我改进/RSI",
        "rsi": "递归自我改进",
        "dark output": "暗产出/不可见成本",
        "amdahl": "阿姆达尔定律/系统瓶颈",
        "breeder scenario": "饲养员场景/人类控制幻觉",
        "ecosystem scenario": "生态系统场景/达尔文演化",
        "lamarckian": "拉马克式AI/人类反馈",
        "darwinian ai": "达尔文式AI/环境选择",
        
        # [新增] 认知坍塌与主体性幽灵化
        "epistemological break": "认识论断裂",
        "cognitive surrender": "认知投降",
        "volitional atrophy": "意志萎缩",
        "society of thought": "思维社会/内部多智能体",
        "silicon internal loop": "硅基内部循环",
        
        # [新增] 宏观测量失灵
        "statistical blind spot": "统计盲区",
        "gdp measurement": "GDP测量失灵",
        "productivity paradox": "生产力悖论",

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
    #  路径配置（都已转为绝对路径，无论从哪里运行脚本都不会出错）
    # =========================================================================
    KEYWORDS_FILE: Path = BASE_DIR / os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR: Path = BASE_DIR / os.getenv("OUTPUT_DIR", "docs")
    LOG_DIR: Path = BASE_DIR / "logs"  # 日志目录（会自动创建）
    SEEN_IDS_FILE: Path = BASE_DIR / os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE: Path = BASE_DIR / os.getenv("CACHE_FILE", "paper_cache.json")

    # =========================================================================
    #  速率限制
    # =========================================================================
    S2_RATE_LIMIT: float = float(os.getenv("S2_RATE_LIMIT", "1.0"))

    # =========================================================================
    #  初始化 & 验证（按需检查密钥）
    # =========================================================================
    @classmethod
    def validate(cls, require_s2: bool = False) -> None:
        """
        启动时调用，检查必要的环境变量和目录。
        - require_s2=False：检查 DEEPSEEK_API_KEY 或 OPENROUTER_API_KEY 至少一个
        - require_s2=True ：额外检查 SEMANTIC_SCHOLAR_API_KEY（适用于 academic_radar）
        """
        missing_keys = []
        # 至少要有一个分析模型的 key
        if not cls.DEEPSEEK_API_KEY and not cls.OPENROUTER_API_KEY:
            missing_keys.append("DEEPSEEK_API_KEY 或 OPENROUTER_API_KEY")
        if require_s2 and not cls.SEMANTIC_SCHOLAR_API_KEY:
            missing_keys.append("SEMANTIC_SCHOLAR_API_KEY")
        if missing_keys:
            raise RuntimeError(
                f"缺少必要的环境变量，请在 .env 文件中设置：{', '.join(missing_keys)}"
            )

        # 确保输出和日志目录存在
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        if cls.OPENROUTER_API_KEY:
            print(f"🌐 NVIDIA API 已就绪，三模型并行: {', '.join(cls.ANALYSIS_MODELS)}")
        elif cls.DEEPSEEK_API_KEY:
            print(f"ℹ️  仅 DeepSeek 模式（无 NVIDIA API Key），模型: {cls.ANALYSIS_MODEL_DIRECT}")
        else:
            print("⚠️  未配置任何 API Key")

        print("✅ 配置验证通过，所有必要目录已就绪。")

    # =========================================================================
    #  安全：防止意外打印密钥（调试时更安全）
    # =========================================================================
    def __repr__(self) -> str:
        """避免在日志或错误输出中暴露真实 API 密钥"""
        return (
            f"<Config(NVIDIA_API_KEY={'***' if self.OPENROUTER_API_KEY else 'MISSING'}, "
            f"SEMANTIC_SCHOLAR_API_KEY={'***' if self.SEMANTIC_SCHOLAR_API_KEY else 'MISSING'})>"
        )


# =============================================================================
#  使用示例（小白友好，取消注释即可测试）
# =============================================================================
# if __name__ == "__main__":
#     print("🧪 配置类自检 ...")
#     # 模拟只运行新闻雷达时不检查 S2
#     Config.validate()                      # 只检查 DeepSeek
#     # Config.validate(require_s2=True)     # 如果要跑学术搜索，用这个
#     print(f"📌 分析模型：{Config.ANALYSIS_MODEL_DIRECT}")
#     print(f"📌 草稿模型：{Config.DRAFTING_MODEL}")
#     print(f"📌 推理深度：{Config.REASONING_EFFORT}")
#     print(f"📌 CoT引导：{'开启' if Config.ENABLE_COT_PROMPT else '关闭'}")
#     print(f"📌 输出目录：{Config.OUTPUT_DIR}")
#     print(f"📌 日志目录：{Config.LOG_DIR}")
#     print(Config())