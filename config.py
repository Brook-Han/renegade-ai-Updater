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
        "deepseek/deepseek-chat",     # OpenRouter 自动路由到 DeepInfra/Novita
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

    # ---------- Paths ----------
    KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")
    SEEN_IDS_FILE = os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE = os.getenv("CACHE_FILE", "paper_cache.json")

    # ---------- Rate limiting ----------
    S2_RATE_LIMIT = float(os.getenv("S2_RATE_LIMIT", "1.0"))
    OPENROUTER_RATE_LIMIT = float(os.getenv("OPENROUTER_RATE_LIMIT", "3.0"))