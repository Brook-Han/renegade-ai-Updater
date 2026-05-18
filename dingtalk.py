#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔔 钉钉推送脚本 — 向后兼容包装
================================
此文件保留用于兼容现有 GitHub Actions 工作流。
实际逻辑已迁移到 notify/ 模块。

用法（与旧版完全兼容）：
    python dingtalk.py --type news
    python dingtalk.py --type papers
    python dingtalk.py --file path/to/report.md

新增功能（通过 notify 模块）：
    python dingtalk.py --type news --dry-run        # 预览
    python dingtalk.py --type news --channels dingtalk,telegram
    python dingtalk.py --history                    # 查看推送历史
    python dingtalk.py --status                     # 查看通道状态

版本：v2.0 (2026-05-15) — 重构为 notify/ 模块包装
"""

import sys
import os
from dotenv import load_dotenv

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 加载 .env 环境变量（本地运行必须）
load_dotenv()

from notify.cli import main

if __name__ == "__main__":
    sys.exit(main())
