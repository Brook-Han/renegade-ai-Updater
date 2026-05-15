#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚠️ 已废弃 — 请使用 python -m notify 或 python dingtalk.py
=============================================================
此文件保留兼容旧版 news_daily.yml / papers_weekly.yml，
实际逻辑已迁移到 notify/ 模块。

迁移后即可删除此文件。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from notify.cli import main

if __name__ == "__main__":
    sys.exit(main())
