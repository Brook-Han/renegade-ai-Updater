# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    SEMANTIC_SCHOLAR_API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")

    # Fetch parameters
    MAX_RESULTS_PER_KEYWORD = int(os.getenv("MAX_RESULTS_PER_KEYWORD", "10"))
    ARXIV_PAGE_SIZE = int(os.getenv("ARXIV_PAGE_SIZE", "100"))
    ARXIV_DELAY_SECONDS = float(os.getenv("ARXIV_DELAY_SECONDS", "5.0"))

    # Model lists
    FREE_MODELS = [
        "google/gemini-2.0-flash-exp:free",
        "qwen/qwen3.6-plus-preview:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "nvidia/nemotron-3-super:free",
    ]
    CHEAP_PAID_MODELS = [
        "google/gemini-2.5-flash",
        "anthropic/claude-haiku-4.5",
    ]
    STRONG_PAID_MODELS = [
        "anthropic/claude-sonnet-4.5",
        "openai/gpt-4o-mini",
    ]
    ANALYSIS_MODELS = FREE_MODELS + CHEAP_PAID_MODELS
    DRAFTING_MODEL = "anthropic/claude-sonnet-4.5"

    # Path settings
    KEYWORDS_FILE = os.getenv("KEYWORDS_FILE", "keywords.txt")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "reports")
    SEEN_IDS_FILE = os.getenv("SEEN_IDS_FILE", "seen_ids.json")
    CACHE_FILE = os.getenv("CACHE_FILE", "paper_cache.json")

    # Rate limiting
    S2_RATE_LIMIT = float(os.getenv("S2_RATE_LIMIT", "1.0"))
    OPENROUTER_RATE_LIMIT = float(os.getenv("OPENROUTER_RATE_LIMIT", "3.0"))