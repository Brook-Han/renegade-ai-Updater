# renegade-ai-Updater — Project CLAUDE.md

## 架构
- **news_radar.py** — 新闻雷达（24 个 RSS 源 + NewsAPI），每天运行
- **academic_radar.py** — 学术雷达（arXiv + Semantic Scholar），每天运行
- **radar_index_generator.py** — 生成 docs/index.html 归档主页
- **config.py** — 集中配置：API 密钥、模型选择、RSS 源列表、约 80 个概念关键词
- **notify/** — 通知子系统（钉钉 + Telegram），通过 `python -m notify --type news|papers` 调用
- **scripts/daily_update.sh** — 本地 Mac 启动脚本（launchd 07:00）
- **.github/workflows/daily-radar.yml** — CI 调度（UTC 22:00 ≈ 北京时间 06:00）

## 弃用文件（请勿修改/使用）
- `dingtalk.py` / `notify_dingtalk.py` → 迁移至 `notify/` 包
- `.github/workflows/news_daily.yml` / `papers_weekly.yml` → 合并至 `daily-radar.yml`
- `generate_news_index.py` / `generate_academic_index.py` → 迁移至 `radar_index_generator.py`
- `news_md_to_html.py` / `academic_md_to_html.py` → 功能合并至 `radar_index_generator.py`

## 常用命令
```bash
# 手动运行新闻雷达
python3 news_radar.py

# 手动运行学术雷达
python3 academic_radar.py

# 重新生成归档主页
python3 radar_index_generator.py

# 完整本地运行
bash scripts/daily_update.sh

# 发送通知
python -m notify --type news
python -m notify --type papers
```

## 路径说明
- 输出写入 docs/news/ 和 docs/academic/
- config.py 中的路径已处理为绝对路径，可在任意目录下运行
- .env 文件包含 API 密钥，不在 git 中追踪
- 缓存在 paper_cache.json、cache/、docs/*/cache.json

## AI 模型配置
- 分析模型：deepseek-v4-flash（REASONING_EFFORT 控制推理深度）
- 草稿模型：deepseek-v4-pro（仅在评分 ≥8 且紧急度为 immediate 时调用）
- COT 提示可切换：config.py 中 ENABLE_COT_PROMPT

## 调度说明
- **launchd**（本地 Mac）：07:00 每天，通过 daily_update.sh
- **GitHub Actions**（云端 fallback）：UTC 22:00 每天
- 重叠运行是安全的（MD5 去重缓存）
