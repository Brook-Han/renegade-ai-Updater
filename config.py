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
    # 模型配置 (2026-05-07 优化)
    # 原则：
    #   - 分析任务（大量调用）→ deepseek-v4-flash 直连（便宜快速）
    #   - 草稿任务（少量调用）→ deepseek-v4-pro 直连（强推理）
    #   - 辅助对比 → 保留 OpenRouter 免费模型
    #   - 移除 OpenRouter 中的 DeepSeek 路由（避免 double billing）
    # ============================================================

    # OpenRouter 免费模型（辅助对比，提供第二意见）
    FREE_MODELS = [
        "meta-llama/llama-3.3-70b-instruct:free",
    ]

    # OpenRouter 付费模型（当前不使用，避免重复计费）
    CHEAP_PAID_MODELS = []

    # 强推理模型（暂不使用，因上游封禁）
    STRONG_PAID_MODELS = []

    # 实际分析模型列表（只包含通过 OpenRouter 调用的模型）
    # 注意：DeepSeek V4 Flash 直连是在脚本中单独添加的，不在这里
    ANALYSIS_MODELS = FREE_MODELS + CHEAP_PAID_MODELS

    # ---------- 直连模型指定 ----------
    # 用于大量论文分析的模型（速度快、成本低）
    ANALYSIS_MODEL_DIRECT = "deepseek-v4-flash"
    # 用于生成书稿草稿的模型（需要强推理和写作能力）
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