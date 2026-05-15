#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renegade AI 通知模块 v2.0
=========================
可插拔多通道通知系统，替代旧版 dingtalk.py / notify_dingtalk.py。

架构：
  channels/          — 通知通道实现（钉钉 ActionCard、Telegram Bot 等）
  parser.py          — Markdown 报告结构化解析器
  dedup.py           — 推送去重缓存（避免重复推送同一内容）
  builder.py         — 消息构建器（评分排序 + 格式化）
  history.py         — 推送历史追踪
  cli.py             — 统一命令行入口

用法：
  python -m notify --type news                    # 推送最新新闻报告
  python -m notify --type papers                  # 推送最新论文报告
  python -m notify --type news --dry-run          # 预览不发送
  python -m notify --type news --channels dingtalk,telegram
"""

__version__ = "2.0.0"
__author__ = "Brooks Han"
