#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推送去重缓存
============
避免同一条内容被重复推送到用户手机。
基于 MD5 指纹 + 时间窗口机制。

工作原理：
  1. 每次推送前，计算待推条目的指纹
  2. 与缓存中已推送指纹比对，排除重复
  3. 推送成功后，将新指纹写入缓存
  4. 超过去重窗口（默认 3 天）的旧记录自动清理

存储位置：notify_push_cache.json（项目根目录）
"""

import json
import time
from pathlib import Path
from typing import List, Set
from .channels import PushItem


class DedupCache:
    """
    推送去重缓存。

    用法：
        dc = DedupCache()
        fresh = dc.filter(items)          # 过滤掉已推送的
        ...
        dc.mark_pushed(fresh)             # 推送成功后标记
    """

    def __init__(self, cache_path: Path = None, window_days: int = 3):
        """
        参数：
          cache_path  — 缓存文件路径，默认项目根目录
          window_days — 去重窗口（天），超过此时间的记录自动清理
        """
        self.cache_path = cache_path or Path("notify_push_cache.json")
        self.window_days = window_days
        self._records: dict = {}  # {fingerprint: pushed_at_timestamp}
        self._load()

    def filter(self, items: List[PushItem]) -> List[PushItem]:
        """
        过滤掉已在窗口内推送过的条目。
        返回未推送的条目列表。
        """
        self._cleanup()
        fresh = []
        for item in items:
            fp = item.fingerprint
            if not fp:
                fresh.append(item)
                continue
            if fp not in self._records:
                fresh.append(item)
        return fresh

    def mark_pushed(self, items: List[PushItem]):
        """将条目标记为已推送"""
        now = time.time()
        for item in items:
            if item.fingerprint:
                self._records[item.fingerprint] = now
        self._save()

    def get_push_count(self) -> int:
        """返回当前去重窗口内的已推送数量"""
        self._cleanup()
        return len(self._records)

    def _cleanup(self):
        """清理过期记录"""
        cutoff = time.time() - (self.window_days * 86400)
        expired = [fp for fp, ts in self._records.items() if ts < cutoff]
        for fp in expired:
            del self._records[fp]

    def _load(self):
        """从文件加载缓存"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    self._records = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._records = {}
        else:
            self._records = {}

    def _save(self):
        """保存缓存到文件"""
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._records, f, ensure_ascii=False, indent=2)
