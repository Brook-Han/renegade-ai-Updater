#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉通知通道 v2.1
=================
支持三种消息类型：
  1. Markdown   — 默认，完整内容：标题+评分+章节+摘要+关联+书稿标记（原版格式）
  2. ActionCard — 卡片样式 + 底部原文跳转按钮
  3. FeedCard   — 轻量模式，仅标题+链接（适合纯浏览）

配置环境变量：
  DINGTALK_WEBHOOK       — 机器人 Webhook URL
  DINGTALK_SECRET        — 加签密钥
  NOTIFY_DINGTALK_MSG_TYPE — markdown（默认）/ actioncard / feedcard
"""

import os
import time
import hmac
import hashlib
import base64
import urllib.parse
from typing import List

import requests

from . import BaseChannel, PushItem, PushResult


class DingTalkChannel(BaseChannel):
    name = "dingtalk"

    def __init__(self):
        super().__init__()

    def _validate_config(self) -> bool:
        webhook = os.getenv("DINGTALK_WEBHOOK", "") or os.getenv(
            "NOTIFY_DINGTALK_WEBHOOK", ""
        )
        secret = os.getenv("DINGTALK_SECRET", "") or os.getenv(
            "NOTIFY_DINGTALK_SECRET", ""
        )
        return bool(webhook and secret)

    def _send(self, title: str, content: str, items: List[PushItem]) -> PushResult:
        webhook = os.getenv("DINGTALK_WEBHOOK", "") or os.getenv(
            "NOTIFY_DINGTALK_WEBHOOK", ""
        )
        secret = os.getenv("DINGTALK_SECRET", "") or os.getenv(
            "NOTIFY_DINGTALK_SECRET", ""
        )
        msg_type = os.getenv("NOTIFY_DINGTALK_MSG_TYPE", "markdown").lower()

        from ..builder import MessageBuilder
        mb = MessageBuilder()
        report_url = os.getenv("REPORT_BASE_URL", "").rstrip("/")

        # ── 按类型构建 payload ────────────────────────────────
        if msg_type == "feedcard" and items:
            # 从 content 中提取 report_type 和 date_str
            # （cli.py 在构建 markdown 时已写入标题，这里从 items 推断）
            payload = mb.build_feedcard(
                items, report_url,
                report_type=self._guess_type(items),
                date_str="",
            )
            # FeedCard 没有独立的 title 字段
            title = f"Renegade AI · TOP{len(items)} 精选"

        elif msg_type == "actioncard" and items:
            payload = mb.build_actioncard(items, report_url)
            title = payload.get("actionCard", {}).get("title", title)

        else:
            # 兜底：Markdown
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content,
                },
            }

        # 签名 + 发送（含重试）
        ts, sign = self._generate_sign(secret)
        url = f"{webhook}&timestamp={ts}&sign={sign}"

        last_error = ""
        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, timeout=15)
                result = r.json()

                if result.get("errcode") == 0:
                    return PushResult(
                        channel_name="dingtalk",
                        success=True,
                        items_count=len(items),
                    )

                err_msg = result.get("errmsg", "未知错误")
                err_code = result.get("errcode", -1)

                if err_code == 90020:  # rate limited
                    wait = 2 ** attempt
                    time.sleep(wait)
                    last_error = f"频率限制，第{attempt+1}次重试: {err_msg}"
                    continue

                return PushResult(
                    channel_name="dingtalk",
                    success=False,
                    items_count=0,
                    error_message=f"[{err_code}] {err_msg}",
                )

            except requests.exceptions.Timeout:
                last_error = f"请求超时（第{attempt+1}次）"
                time.sleep(2 ** attempt)
            except Exception as e:
                return PushResult(
                    channel_name="dingtalk",
                    success=False,
                    items_count=0,
                    error_message=str(e),
                )

        return PushResult(
            channel_name="dingtalk",
            success=False,
            items_count=0,
            error_message=last_error or "重试耗尽",
        )

    @staticmethod
    def _guess_type(items: List[PushItem]) -> str:
        """从条目内容推断报告类型（papers 通常有 arXiv 链接）"""
        for item in items:
            if "arxiv" in item.url.lower():
                return "papers"
        return "news"

    @staticmethod
    def _generate_sign(secret: str) -> tuple:
        ts = str(round(time.time() * 1000))
        to_sign = f"{ts}\n{secret}".encode()
        sign = urllib.parse.quote_plus(
            base64.b64encode(
                hmac.new(secret.encode(), to_sign, hashlib.sha256).digest()
            ).decode()
        )
        return ts, sign
