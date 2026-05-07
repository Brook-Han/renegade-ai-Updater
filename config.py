# config.py

# 先只用这一个，稳定跑通
CHEAP_PAID_MODELS = [
    "deepseek/deepseek-chat",   # OpenRouter 自动路由到 vercel 或 novita
]

# 免费模型暂时全部注释掉（429/404 问题太多）
FREE_MODELS = [
    # "meta-llama/llama-3.3-70b-instruct:free",
]

ANALYSIS_MODELS = FREE_MODELS + CHEAP_PAID_MODELS