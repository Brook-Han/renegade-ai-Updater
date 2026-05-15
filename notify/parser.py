#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 报告结构化解析器
==========================
替代旧版逐行正则匹配，使用分块 + 状态机方式解析报告。

支持的字段：
  - 标题 (### 开头)
  - 最终评分 / 相关度
  - 紧迫度
  - 核心发现 / 事件摘要
  - 链接
  - 与本书关联 / 理论关联
  - 目标章节
  - 草稿（✍️ 标记区域）
"""

import re
import hashlib
from pathlib import Path
from typing import List, Optional
from .channels import PushItem


class ReportParser:
    """
    报告解析器。
    用法：
        parser = ReportParser()
        items = parser.parse("docs/news/news_report_2026-05-15.md", min_score=4.0)
        top5 = parser.top(items, n=5)
    """

    # 字段名 → 统一键名 映射（解决新旧格式差异）
    FIELD_MAP = {
        "最终评分": "score",
        "相关度": "score",
        "紧迫度": "urgency",
        "核心发现": "summary",
        "事件摘要": "summary",
        "链接": "url",
        "原文链接": "url",
        "与本书关联": "implications",
        "理论关联": "implications",
        "目标章节": "chapter",
        "案例价值": "case_value",
    }

    # 非条目标题（章节标题）
    SECTION_HEADERS = {
        "高相关", "中相关", "低相关", "紧急",
        "High Relevance", "Medium Relevance", "Low Relevance",
        "推荐阅读", "学术速递", "资讯精选",
        "附录", "Appendix",
    }

    def __init__(self):
        pass

    def parse(self, report_path: str, min_score: float = 4.0) -> List[PushItem]:
        """
        解析一份 Markdown 报告，返回符合评分阈值的条目列表。

        参数：
          report_path — .md 文件路径
          min_score   — 最低评分阈值（含）
        返回：
          List[PushItem]
        """
        content = Path(report_path).read_text(encoding="utf-8")
        blocks = self._split_blocks(content)
        items = []

        for block in blocks:
            item = self._parse_block(block)
            if item and item.score >= min_score:
                items.append(item)

        return items

    def top(self, items: List[PushItem], n: int = 5) -> List[PushItem]:
        """按评分降序取前 N 条"""
        return sorted(items, key=lambda x: x.score, reverse=True)[:n]

    # ── 内部分块 ─────────────────────────────────────────────

    def _split_blocks(self, content: str) -> List[str]:
        """
        按 ### 标题将报告拆分为块。
        每个块以 ### 开头（或为第一个块的前导文本）。
        """
        lines = content.split("\n")
        blocks = []
        current = []

        for line in lines:
            stripped = line.strip()
            # 遇到新标题时，保存当前块
            if stripped.startswith("### ") and current:
                blocks.append("\n".join(current))
                current = [line]
            else:
                current.append(line)

        if current:
            blocks.append("\n".join(current))

        return blocks

    def _parse_block(self, block: str) -> Optional[PushItem]:
        """
        解析单个内容块。
        返回 PushItem 或 None（如果是章节标题块）。
        """
        lines = block.split("\n")
        if not lines:
            return None

        title_line = lines[0].strip()

        # 跳过非条目标题
        if not title_line.startswith("### "):
            return None

        raw_title = title_line[4:].strip()

        # 去除标题自带序号（如 "1. ", "12. "），避免钉钉渲染时双重编号
        raw_title = re.sub(r'^\d+\.\s+', '', raw_title)

        # 判断是否为章节标题
        for sh in self.SECTION_HEADERS:
            if sh.lower() in raw_title.lower():
                return None

        item_data = {"title": raw_title}

        # 状态机遍历剩余行
        in_draft = False
        draft_lines = []
        current_field = None

        for line in lines[1:]:
            s = line.strip()

            # 草稿区域检测
            if ("✍️" in s and ("草稿" in s or "draft" in s.lower())):
                in_draft = True
                draft_lines = []
                continue

            if in_draft:
                # 草稿结束条件
                if s.startswith("###") or s.startswith("---"):
                    in_draft = False
                    item_data["draft"] = "\n".join(draft_lines).strip()
                    continue
                draft_lines.append(s)
                continue

            # 提取字段行：- **字段名**: 值
            field_match = re.match(
                r"-\s*\*+\s*(.+?)\s*\*+\s*:\s*(.+)", s
            )
            if field_match:
                raw_field = field_match.group(1).strip()
                raw_value = re.sub(r"\*+", "", field_match.group(2)).strip()

                # 映射到统一键名
                unified_key = self.FIELD_MAP.get(raw_field)
                if unified_key and unified_key not in item_data:
                    item_data[unified_key] = raw_value
                continue

            # 链接提取（可能以 [原文](url) 格式出现）
            link_match = re.search(r'\[.*?\]\((https?://[^\s)]+)\)', s)
            if link_match and "url" not in item_data:
                item_data["url"] = link_match.group(1)

        # 处理末尾草稿
        if in_draft and draft_lines:
            item_data["draft"] = "\n".join(draft_lines).strip()

        # 清洗 URL（去除可能嵌套的 Markdown 链接语法）
        url_raw = item_data.get("url", "")
        url_clean = self._clean_url(url_raw)

        # 评分解析
        score_str = item_data.get("score", "0")
        score_num = self._parse_score(score_str)

        # 生成指纹（用于去重）
        fp = self._fingerprint(item_data["title"], url_clean)

        return PushItem(
            title=item_data["title"],
            score=score_num,
            url=url_clean,
            summary=item_data.get("summary", ""),
            implications=item_data.get("implications", ""),
            chapter=item_data.get("chapter", ""),
            urgency=item_data.get("urgency", ""),
            draft=item_data.get("draft", ""),
            fingerprint=fp,
            item_id=fp[:12],
        )

    @staticmethod
    def _clean_url(raw: str) -> str:
        """
        清洗 URL，去除嵌套 Markdown 链接语法和空白。
        输入可能为：
          - 纯 URL: https://example.com
          - 嵌套 Markdown: [https://arxiv.org/...](https://arxiv.org/...)
          - 带括号: [https://example.com]
        输出：纯 URL。
        """
        raw = raw.strip()
        if not raw:
            return ""
        # 去除外层方括号
        if raw.startswith("[") and raw.endswith("]") and "(" not in raw:
            raw = raw[1:-1]
        # 提取 Markdown 链接中的实际 URL：[text](url) → url
        md_link = re.match(r'\[.*?\]\((https?://[^\s)]+)\)', raw)
        if md_link:
            return md_link.group(1)
        # 如果本身就是纯 URL，直接返回
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw
        return raw

    @staticmethod
    def _parse_score(raw: str) -> float:
        """解析评分字符串：'8.5/10' → 8.5, '7' → 7.0"""
        try:
            return float(str(raw).split("/")[0].strip())
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _fingerprint(title: str, url: str) -> str:
        """生成条目指纹（MD5）"""
        content = f"{title}|{url}".encode("utf-8", errors="ignore")
        return hashlib.md5(content).hexdigest()
