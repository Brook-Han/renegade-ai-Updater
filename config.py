import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

    # Fetch settings
    MAX_RESULTS_PER_KEYWORD = int(os.getenv("MAX_RESULTS_PER_KEYWORD", "10"))
    ARXIV_PAGE_SIZE = int(os.getenv("ARXIV_PAGE_SIZE", "100"))
    ARXIV_DELAY_SECONDS = float(os.getenv("ARXIV_DELAY_SECONDS", "5.0"))

    # Model lists (minimal working set)
    FREE_MODELS = [
        "meta-llama/llama-3.3-70b-instruct:free",
    ]
    CHEAP_PAID_MODELS = [
        "deepseek/deepseek-chat",   # OpenRouter will route to v3
    ]
    ANALYSIS_MODELS = FREE_MODELS + CHEAP_PAID_MODELS

    # Draft generation
    DRAFTING_MODEL = "anthropic/claude-sonnet-4.5"
    DRAFT_RELEVANCE_THRESHOLD = int(os.getenv("DRAFT_RELEVANCE_THRESHOLD", "8"))
    DRAFT_URGENCY_REQUIRED = os.getenv("DRAFT_URGENCY_REQUIRED", "immediate")

    # Paths
    KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")
    SEEN_IDS_FILE = os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE = os.getenv("CACHE_FILE", "paper_cache.json")

    # Rate limiting
    S2_RATE_LIMIT = float(os.getenv("S2_RATE_LIMIT", "1.0"))
    OPENROUTER_RATE_LIMIT = float(os.getenv("OPENROUTER_RATE_LIMIT", "3.0"))
