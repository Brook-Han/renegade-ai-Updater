#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息构建器
==========
将解析后的 PushItem 列表构建为各通道的格式化消息。

支持格式：
  - markdown  — 通用 Markdown（钉钉 Markdown 消息、Telegram）
  - actioncard — 钉钉 ActionCard（独立的标题 + Markdown 内容，支持单条独立跳转）
  - html       — Telegram HTML（parse_mode=HTML）
"""

from typing import List, Optional
from .channels import PushItem


class MessageBuilder:
    """
    消息构建器。

    用法：
        mb = MessageBuilder()
        md = mb.build_markdown(items, "news", report_url, total, date_str)
        # 或
        cards = mb.build_actioncard(items, report_url)
    """

    # ── 通用 Markdown ─────────────────────────────────────────

    def build_markdown(
        self,
        items: List[PushItem],
        report_type: str,
        report_url: str,
        total_count: int,
        date_str: str = "",
    ) -> str:
        """
        构建通用 Markdown 消息（兼容钉钉和 Telegram）。

        参数：
          items       — 待推送条目（已排序，已截断 top N）
          report_type — "news" / "papers"
          report_url  — 完整报告页面 URL
          total_count — 报告中总条目数
          date_str    — 日期字符串（如 2026-05-15）
        """
        is_papers = report_type in ("papers", "academic")

        if is_papers:
            header = "📚 **Renegade AI 学术简报**"
            footer_emoji = "🎓"
        else:
            header = "📰 **Renegade AI 资讯简报**"
            footer_emoji = "🗞️"

        lines = [
            f"## {header}",
            f"**{date_str}** · 共分析 {total_count} 条 | 精选 {len(items)} 条高价值内容",
            "",
        ]

        for idx, item in enumerate(items, 1):
            title = item.title[:80]
            score_str = f"{item.score:.1f}/10"

            lines.append(f"### {title}")
            lines.append(f"- ⭐ 评分：{score_str} [↗ 原文]({item.url})")

            if item.chapter and item.chapter not in ("N/A", ""):
                lines.append(f"- 📍 {item.chapter}")

            if item.summary and item.summary not in ("N/A", ""):
                summary_clean = self._truncate(item.summary, 250)
                lines.append(f"- 📝 {summary_clean}")

            if item.implications and item.implications not in ("N/A", ""):
                lines.append(f"- 🔗 {self._truncate(item.implications, 120)}")

            if item.draft:
                lines.append("- ✍️ 已生成书稿草稿")

            lines.append("")

        # 页脚
        lines.append("---")
        lines.append(
            f"> {footer_emoji} [📄 查看完整报告（含全部条目 + 书稿草稿）]({report_url})"
        )
        lines.append("> 🤖 自动推送 · Renegade AI v5.3 · notify v2.0")

        msg = "\n".join(lines)

        # 安全截断（4000 字节约为钉钉限制）
        if len(msg) > 3800:
            msg = msg[:3800] + "\n\n> ⚠️ 内容过长已截断，请点击查看完整报告。"

        return msg

    # ── 钉钉 ActionCard ────────────────────────────────────────

    def build_actioncard(
        self,
        items: List[PushItem],
        report_url: str,
    ) -> dict:
        """
        构建钉钉 ActionCard 消息体。

        ActionCard 在手机端比纯 Markdown 体验更好：
        - 每条内容独立展示
        - 底部有跳转按钮
        - 支持单条独立跳转（btnOrientation=1 时每条一个按钮）

        返回钉钉 API 的 payload dict。
        """
        if not items:
            return {}

        # 标题：取第一条的标题 + 总数
        title = f"Renegade AI · TOP{len(items)} 精选"

        # Markdown 正文
        lines = []
        for idx, item in enumerate(items, 1):
            score_str = f"{item.score:.1f}/10"
            lines.append(f"### {idx}. {item.title[:60]}")
            lines.append(f"> ⭐ {score_str}")
            if item.summary:
                lines.append(f"> {self._truncate(item.summary, 120)}")
            lines.append("")

        text = "\n".join(lines)

        # 按钮：单条跳转模式
        btns = []
        for idx, item in enumerate(items, 1):
            if item.url:
                btns.append({
                    "title": f"#{idx} 原文",
                    "actionURL": item.url,
                })

        # 加上查看完整报告的按钮
        btns.append({
            "title": "📄 完整报告",
            "actionURL": report_url,
        })

        payload = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": title,
                "text": text,
                "btnOrientation": "1",  # 竖向排列
                "btns": btns[:6],       # 钉钉 ActionCard 最多 5 个按钮
            },
        }

        return payload

    # ── 钉钉 FeedCard（原生卡片体验）─────────────────────────

    def build_feedcard(
        self,
        items: List[PushItem],
        report_url: str,
        report_type: str = "news",
        date_str: str = "",
    ) -> dict:
        """
        构建钉钉 FeedCard 消息体。

        FeedCard 是手机端体验最好的格式：
        - 每条内容渲染为一张可点击的独立卡片
        - 标题 + 评分摘要直接展示
        - 点击卡片跳转原文（无需点小链接）
        - 最后一张卡片链接到完整报告

        返回钉钉 API 的 payload dict。
        """
        if not items:
            return {}

        is_papers = report_type in ("papers", "academic")
        emoji = "🎓" if is_papers else "🗞️"

        links = []
        for idx, item in enumerate(items, 1):
            # 卡片标题：序号 + 评分 + 标题（钉钉 FeedCard 标题最长 100 字符）
            score_str = f"{item.score:.1f}"
            card_title = f"#{idx} ⭐{score_str} {item.title}"
            if len(card_title) > 100:
                card_title = card_title[:97] + "..."

            link = {
                "title": card_title,
                "messageURL": item.url if item.url else report_url,
            }
            links.append(link)

        # 最后一张卡片：完整报告入口
        label = "学术简报" if is_papers else "资讯简报"
        links.append({
            "title": f"{emoji} 📄 查看完整{label}（含书稿草稿）",
            "messageURL": report_url,
        })

        return {
            "msgtype": "feedCard",
            "feedCard": {
                "links": links,
            },
        }

    # ── Telegram HTML ──────────────────────────────────────────

    def build_telegram_html(
        self,
        items: List[PushItem],
        report_type: str,
        report_url: str,
        total_count: int,
        date_str: str = "",
    ) -> str:
        """
        构建 Telegram HTML 消息（parse_mode=HTML）。

        Telegram 支持有限的 HTML 标签：<b>, <i>, <u>, <s>, <a>, <code>, <pre>
        """
        is_papers = report_type in ("papers", "academic")
        emoji = "🎓" if is_papers else "🗞️"
        label = "学术简报" if is_papers else "资讯简报"

        lines = [
            f"<b>{emoji} Renegade AI {label}</b>",
            f"<i>{date_str} · 共分析 {total_count} 条 | 精选 {len(items)} 条</i>",
            "",
        ]

        for idx, item in enumerate(items, 1):
            score_str = f"{item.score:.1f}/10"
            # 标题 + 链接
            if item.url:
                lines.append(
                    f"<b>{idx}. <a href=\"{item.url}\">{self._escape_html(item.title[:80])}</a></b>"
                )
            else:
                lines.append(f"<b>{idx}. {self._escape_html(item.title[:80])}</b>")

            lines.append(f"⭐ {score_str}")

            if item.chapter and item.chapter not in ("N/A", ""):
                lines.append(f"📍 {self._escape_html(item.chapter)}")

            if item.summary and item.summary not in ("N/A", ""):
                lines.append(
                    f"📝 {self._escape_html(self._truncate(item.summary, 200))}"
                )

            if item.draft:
                lines.append("✍️ 已生成书稿草稿")

            lines.append("")

        # 页脚
        lines.append(
            f"<a href=\"{report_url}\">📄 查看完整报告（含全部条目 + 书稿草稿）</a>"
        )
        lines.append("<i>🤖 自动推送 · Renegade AI v5.3 · notify v2.0</i>")

        return "\n".join(lines)

    # ── 工具方法 ──────────────────────────────────────────────

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        """截断文本，添加省略号"""
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."

    @staticmethod
    def _escape_html(text: str) -> str:
        """转义 HTML 特殊字符"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
