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
    # 模型配置 (2026-05-07 调整)
    # 说明：
    #   - DeepSeek V4 Pro 通过官网直连 (已在 scrape_and_analyze.py 中配置)
    #   - OpenRouter 仅用于免费/廉价模型 (避免 Anthropic/Google/OpenAI 因地区封禁 403)
    # ============================================================

    # OpenRouter 免费模型 (目前仅保留已验证可用的)
    FREE_MODELS = [
        "meta-llama/llama-3.3-70b-instruct:free",
    ]

    # OpenRouter 廉价付费模型 (避免 Anthropic/Google/OpenAI)
    CHEAP_PAID_MODELS = [
        "deepseek/deepseek-chat",     # OpenRouter 自动路由到 DeepInfra/Novita
    ]

    # 强推理模型 (暂不使用，因上游封禁)
    STRONG_PAID_MODELS = []

    # 实际分析模型列表
    ANALYSIS_MODELS = FREE_MODELS + CHEAP_PAID_MODELS

    # ---------- Draft generation ----------
    # 草稿模型先用 DeepSeek 直连 (因 Anthropic 被封禁)
    DRAFTING_MODEL = "deepseek-v4-pro"   # 注意：这是 DeepSeek 官网直连模型名
    DRAFT_RELEVANCE_THRESHOLD = int(os.getenv("DRAFT_RELEVANCE_THRESHOLD", "8"))
    DRAFT_URGENCY_REQUIRED = os.getenv("DRAFT_URGENCY_REQUIRED", "immediate")

    # ---------- Paths ----------
    KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")
    SEEN_IDS_FILE = os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE = os.getenv("CACHE_FILE", "paper_cache.json")

    # ---------- Rate limiting ----------
    S2_RATE_LIMIT = float(os.getenv("S2_RATE_LIMIT", "1.0"))
    OPENROUTER_RATE_LIMIT = float(os.getenv("OPENROUTER_RATE_LIMIT", "3.0"))