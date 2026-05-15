#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推送历史追踪
============
记录每次推送的摘要信息，方便回溯和调试。

存储位置：notify_push_history.json（项目根目录）
保留策略：最近 90 天 + 最多 500 条记录
"""

import json
import time
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta


class PushHistory:
    """
    推送历史记录器。

    用法：
        ph = PushHistory()
        ph.record(type="news", channels=["dingtalk"], items_count=5, dry_run=False)
        recent = ph.recent(days=7)
    """

    MAX_RECORDS = 500
    MAX_AGE_DAYS = 90

    def __init__(self, history_path: Path = None):
        self.history_path = history_path or Path("notify_push_history.json")
        self._records: list = []
        self._load()

    def record(
        self,
        report_type: str,
        channels: List[str],
        total_items: int,
        pushed_items: int,
        dry_run: bool = False,
        success_channels: List[str] = None,
        errors: dict = None,
    ):
        """
        记录一次推送。

        参数：
          report_type      — "news" / "papers"
          channels         — 使用的通道列表
          total_items      — 报告中总条目数
          pushed_items     — 实际推送的条目数
          dry_run          — 是否为演习
          success_channels — 发送成功的通道列表
          errors           — {channel_name: error_message}
        """
        tz_cst = timezone(timedelta(hours=8))
        now = datetime.now(tz_cst)

        entry = {
            "timestamp": now.isoformat(),
            "report_type": report_type,
            "channels": channels,
            "total_items": total_items,
            "pushed_items": pushed_items,
            "dry_run": dry_run,
            "success_channels": success_channels or [],
            "errors": errors or {},
        }

        self._records.append(entry)

        # 限制条数
        if len(self._records) > self.MAX_RECORDS:
            self._records = self._records[-self.MAX_RECORDS:]

        self._save()

    def recent(self, days: int = 7) -> list:
        """获取最近 N 天的推送记录"""
        cutoff = datetime.now(timezone(timedelta(hours=8))) - timedelta(days=days)
        result = []
        for r in self._records:
            try:
                ts = datetime.fromisoformat(r["timestamp"])
                if ts >= cutoff:
                    result.append(r)
            except (ValueError, KeyError):
                continue
        return result

    def last_push(self, report_type: str = None) -> Optional[dict]:
        """获取最近一次推送记录（可按类型筛选）"""
        for r in reversed(self._records):
            if report_type is None or r.get("report_type") == report_type:
                return r
        return None

    def stats(self) -> dict:
        """获取推送统计摘要"""
        total = len(self._records)
        success_count = sum(
            1 for r in self._records if r.get("success_channels")
        )
        dry_runs = sum(1 for r in self._records if r.get("dry_run"))

        # 按通道统计
        channel_stats = {}
        for r in self._records:
            for ch in r.get("success_channels", []):
                channel_stats[ch] = channel_stats.get(ch, 0) + 1

        return {
            "total_pushes": total,
            "successful_pushes": success_count,
            "dry_runs": dry_runs,
            "by_channel": channel_stats,
        }

    def _load(self):
        """从文件加载"""
        if self.history_path.exists():
            try:
                with open(self.history_path, encoding="utf-8") as f:
                    self._records = json.load(f)
                # 清理过期
                self._purge_old()
            except (json.JSONDecodeError, IOError):
                self._records = []
        else:
            self._records = []

    def _save(self):
        """保存到文件"""
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)

    def _purge_old(self):
        """清理超过 MAX_AGE_DAYS 的记录"""
        cutoff = datetime.now(timezone(timedelta(hours=8))) - timedelta(
            days=self.MAX_AGE_DAYS
        )
        self._records = [
            r
            for r in self._records
            if datetime.fromisoformat(r.get("timestamp", "2000-01-01")) >= cutoff
        ]
