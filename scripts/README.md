# Renegade AI · 雷达自动化部署指南

## 架构

```
本地 Mac（launchd 07:00）
 ┣━ scripts/daily_update.sh
 ┃  ┣━ python3 news_radar.py         ← 每日新闻扫描
 ┃  ┣━ python3 academic_radar.py      ← 每周一学术扫描
 ┃  ┣━ python3 radar_index_generator.py  ← 索引生成 + git push
 ┃  ┗━ 日志 → logs/update_*.log
 ┗━ 自动 git push → GitHub

Cowork 定时任务 08:00（可选的 fallback）
 ┗━ python3 radar_index_generator.py  ← 本地推送失败时的兜底
```

## 安装

### 1. 安装 Python 依赖（如果还没装过）

```bash
cd /Users/Ethan/Documents/GitHub/renegade-ai-Updater
pip install openai feedparser python-dotenv requests lxml
```

### 2. 安装 launchd 定时任务（每天 07:00 执行）

```bash
# 加载任务
launchctl load ~/Library/LaunchAgents/com.renegadeai.radar-update.plist

# 如果文件不在 LaunchAgents 目录，先复制过去
cp scripts/com.renegadeai.radar-update.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.renegadeai.radar-update.plist
```

### 3. 验证

```bash
# 查看任务是否已加载
launchctl list | grep renegadeai

# 手动立即执行一次测试
bash scripts/daily_update.sh
```

### 4. 卸载

```bash
launchctl unload ~/Library/LaunchAgents/com.renegadeai.radar-update.plist
```

## 日志

- 每次运行：`logs/update_YYYY-MM-DD_HH-MM-SS.log`
- launchd 标准输出：`logs/launchd_stdout.log`
- launchd 错误输出：`logs/launchd_stderr.log`
- 旧日志自动保留 30 天

## 说明

- 新闻雷达：**每天**自动扫描 24 个 RSS 源
- 学术雷达：**每周一**自动扫描 arXiv + Semantic Scholar
- 索引页：扫描完成后自动生成并推送到 GitHub
- Cowork 定时任务已改为 fallback 角色
