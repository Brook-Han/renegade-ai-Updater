#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram 通知通道
=================
通过 Telegram Bot API 发送消息到指定聊天。

配置环境变量：
  NOTIFY_TELEGRAM_BOT_TOKEN  — Bot Token（从 @BotFather 获取）
  NOTIFY_TELEGRAM_CHAT_ID    — 目标 Chat ID（可以是个人或群组）

获取 Chat ID：
  1. 在 Telegram 搜索 @userinfobot，发送 /start，获取你的 ID
  2. 或者给自己的 Bot 发一条消息，然后访问：
     https://api.telegram.org/bot<TOKEN>/getUpdates

特性：
  - HTML 格式（粗体、链接、斜体）
  - 链接预览
  - 静默发送（disable_notification）
  - 失败重试
"""

import os
import time
from typing import List

import requests

from . import BaseChannel, PushItem, PushResult


class TelegramChannel(BaseChannel):
    name = "telegram"

    def __init__(self):
        super().__init__()

    def _validate_config(self) -> bool:
        """检查 Bot Token 和 Chat ID 是否配置"""
        token = os.getenv("NOTIFY_TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("NOTIFY_TELEGRAM_CHAT_ID", "")
        return bool(token and chat_id)

    def _send(self, title: str, content: str, items: List[PushItem]) -> PushResult:
        """
        通过 Telegram Bot API 发送消息。
        使用 HTML parse_mode 以获得更好格式。
        """
        token = os.getenv("NOTIFY_TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("NOTIFY_TELEGRAM_CHAT_ID", "")

        # 是否静默发送（不弹出通知声音）
        silent = os.getenv("NOTIFY_TELEGRAM_SILENT", "false").lower() in (
            "true", "1", "yes"
        )

        # 构建 HTML 消息
        from ..builder import MessageBuilder
        mb = MessageBuilder()
        html_content = content  # builder 已在外部生成

        url = f"https://api.telegram.org/bot{token}/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": html_content,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
            "disable_notification": silent,
        }

        last_error = ""
        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, timeout=15)
                result = r.json()

                if result.get("ok"):
                    msg_id = str(result.get("result", {}).get("message_id", ""))
                    return PushResult(
                        channel_name="telegram",
                        success=True,
                        items_count=len(items),
                        message_id=msg_id,
                    )

                err_desc = result.get("description", "未知错误")
                err_code = result.get("error_code", -1)

                # 429 Too Many Requests → 退避
                if err_code == 429:
                    retry_after = result.get("parameters", {}).get(
                        "retry_after", 2 ** attempt
                    )
                    time.sleep(int(retry_after) + 1)
                    last_error = f"频率限制(429)，第{attempt+1}次重试"
                    continue

                return PushResult(
                    channel_name="telegram",
                    success=False,
                    items_count=0,
                    error_message=f"[{err_code}] {err_desc}",
                )

            except requests.exceptions.Timeout:
                last_error = f"请求超时（第{attempt+1}次）"
                time.sleep(2 ** attempt)
            except Exception as e:
                return PushResult(
                    channel_name="telegram",
                    success=False,
                    items_count=0,
                    error_message=str(e),
                )

        return PushResult(
            channel_name="telegram",
            success=False,
            items_count=0,
            error_message=last_error or "重试耗尽",
        )
