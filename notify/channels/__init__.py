#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知通道抽象基类
================
所有通知通道（钉钉、Telegram、邮件等）继承此基类。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ChannelState(Enum):
    UNCONFIGURED = "unconfigured"   # 缺少必要配置
    READY = "ready"                 # 已就绪
    DISABLED = "disabled"           # 被用户显式禁用
    ERROR = "error"                 # 上次发送失败


@dataclass
class PushItem:
    """一条待推送的内容条目"""
    title: str
    score: float
    url: str
    summary: str = ""
    implications: str = ""
    chapter: str = ""
    urgency: str = ""
    draft: str = ""                # 书稿草稿文本
    fingerprint: str = ""          # 去重指纹（MD5）
    item_id: str = ""              # 唯一标识


@dataclass
class PushResult:
    """单次推送结果"""
    channel_name: str
    success: bool
    items_count: int
    error_message: str = ""
    message_id: str = ""           # 平台返回的消息 ID


class BaseChannel(ABC):
    """
    通知通道抽象基类。

    子类需要实现：
      - name: 通道名称（如 "dingtalk"）
      - _validate_config(): 检查配置是否完整
      - _send(title, content, items): 实际发送逻辑
    """

    name: str = "base"

    def __init__(self):
        self.state = ChannelState.UNCONFIGURED
        self.last_error: str = ""

    # ── 子类必须覆盖 ──────────────────────────────────────────

    @abstractmethod
    def _validate_config(self) -> bool:
        """检查环境变量是否完整。返回 True 表示配置就绪。"""
        ...

    @abstractmethod
    def _send(self, title: str, content: str, items: List[PushItem]) -> PushResult:
        """
        执行实际发送。
        参数：
          title   — 消息标题
          content — 已格式化的消息内容（Markdown 或 HTML）
          items   — 原始条目列表（供 ActionCard 等类型使用）
        返回 PushResult。
        """
        ...

    # ── 公共接口 ──────────────────────────────────────────────

    def is_ready(self) -> bool:
        """检查通道是否可用"""
        if self.state == ChannelState.DISABLED:
            return False
        if self.state == ChannelState.UNCONFIGURED:
            if self._validate_config():
                self.state = ChannelState.READY
            else:
                return False
        return self.state == ChannelState.READY

    def send(self, title: str, content: str, items: List[PushItem]) -> PushResult:
        """发送通知（含状态检查）"""
        if not self.is_ready():
            return PushResult(
                channel_name=self.name,
                success=False,
                items_count=0,
                error_message=f"通道未就绪: {self.state.value}"
            )

        try:
            result = self._send(title, content, items)
            if result.success:
                self.state = ChannelState.READY
            else:
                self.state = ChannelState.ERROR
                self.last_error = result.error_message
            return result
        except Exception as e:
            self.state = ChannelState.ERROR
            self.last_error = str(e)
            return PushResult(
                channel_name=self.name,
                success=False,
                items_count=0,
                error_message=str(e)
            )

    def disable(self):
        """显式禁用此通道"""
        self.state = ChannelState.DISABLED

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "last_error": self.last_error,
        }


def get_channel(name: str) -> Optional[BaseChannel]:
    """
    工厂函数：根据名称返回通道实例。
    支持：dingtalk, telegram
    """
    name = name.strip().lower()
    if name == "dingtalk":
        from .dingtalk import DingTalkChannel
        return DingTalkChannel()
    elif name in ("telegram", "tg"):
        from .telegram import TelegramChannel
        return TelegramChannel()
    return None
