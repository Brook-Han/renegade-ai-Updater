#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renegade AI 通知系统 · 统一 CLI
================================
替代旧版 dingtalk.py 和 notify_dingtalk.py。

用法：
  python -m notify --type news                    # 推送最新新闻
  python -m notify --type papers                  # 推送最新论文
  python -m notify --type news --dry-run          # 预览不发送
  python -m notify --type news --channels dingtalk,telegram
  python -m notify --type news --min-score 5.0 --top-n 3
  python -m notify --file path/to/report.md       # 指定文件
  python -m notify --history                      # 查看推送历史
  python -m notify --status                       # 查看通道状态
"""

import os
import sys
import re
import argparse
from pathlib import Path
from typing import List

from .channels import get_channel, PushItem, PushResult
from .parser import ReportParser
from .dedup import DedupCache
from .builder import MessageBuilder
from .history import PushHistory


# ── 环境变量解析 ──────────────────────────────────────────────

def _get_enabled_channels() -> List[str]:
    """从环境变量读取启用的通道列表"""
    env_val = os.getenv("NOTIFY_ENABLED_CHANNELS", "dingtalk")
    return [c.strip() for c in env_val.split(",") if c.strip()]


def _get_base_url() -> str:
    """获取报告页面基础 URL"""
    return (
        os.getenv("REPORT_BASE_URL", "")
        or os.getenv("NOTIFY_REPORT_BASE_URL", "")
    ).rstrip("/")


# ── 报告文件查找 ──────────────────────────────────────────────

def _find_latest_report(report_type: str) -> Path:
    """
    自动查找最新的报告文件。
    搜索路径：docs/{type}/ 目录。
    """
    search_patterns = [
        f"docs/{report_type}/*_report_*.md",
        f"docs/{report_type}/*.md",
    ]

    all_files = []
    for pattern in search_patterns:
        all_files.extend(Path().glob(pattern))

    if not all_files:
        # 兼容 academic → papers 映射
        alt_type = "academic" if report_type == "papers" else report_type
        for pattern in [
            f"docs/{alt_type}/*_report_*.md",
            f"docs/{alt_type}/*.md",
        ]:
            all_files.extend(Path().glob(pattern))

    if not all_files:
        return None

    # 按修改时间排序，取最新
    return sorted(all_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def _build_report_url(report_file: Path, base_url: str) -> str:
    """构建报告的公开访问 URL"""
    # 处理 docs/ 子目录结构
    try:
        if "docs" in report_file.parts:
            idx = report_file.parts.index("docs")
            relative = Path(*report_file.parts[idx + 1:]).with_suffix(".html")
        else:
            relative = report_file.with_suffix(".html").name
    except (ValueError, IndexError):
        relative = report_file.with_suffix(".html").name

    url = f"{base_url}/{relative}"
    if not url.startswith("http"):
        url = f"https://{url}"
    return url


def _extract_date(filename: str) -> str:
    """从文件名提取日期"""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return match.group(1) if match else ""

# ── 主流程 ────────────────────────────────────────────────────

def run(args: argparse.Namespace) -> int:
    """
    执行通知推送流程。
    返回 0 表示成功，1 表示失败。
    """

    report_type = "papers" if args.type in ("papers", "academic") else "news"
    min_score = args.min_score
    top_n = args.top_n
    dry_run = args.dry_run
    channel_names = [
        c.strip().lower()
        for c in (args.channels or _get_enabled_channels())
    ]

    # ── 1. 查找报告 ──────────────────────────────────────────
    if args.file:
        report_file = Path(args.file)
        if not report_file.exists():
            print(f"❌ 文件不存在: {report_file}")
            return 1
    else:
        report_file = _find_latest_report(report_type)
        if not report_file:
            print(f"⚠️ 未找到 {report_type} 报告文件")
            return 0

    print(f"📄 报告文件: {report_file}")

    # ── 2. 解析报告 ──────────────────────────────────────────
    parser = ReportParser()
    try:
        all_items = parser.parse(str(report_file), min_score=min_score)
    except Exception as e:
        print(f"❌ 解析报告失败: {e}")
        return 1

    if not all_items:
        print(f"⚠️ 无评分 ≥{min_score} 的条目，跳过推送")
        return 0

    print(f"📊 解析到 {len(all_items)} 条评分 ≥{min_score} 的内容")

    # ── 3. 去重 ──────────────────────────────────────────────
    dedup = DedupCache()
    fresh_items = dedup.filter(all_items)
    skipped = len(all_items) - len(fresh_items)
    if skipped:
        print(f"🔄 去重过滤: 跳过已推送 {skipped} 条")

    if not fresh_items:
        print("✨ 所有条目均已推送过，无需重复发送")
        return 0

    # ── 4. 排序 + TOP N ───────────────────────────────────────
    top_items = parser.top(fresh_items, n=top_n)
    print(f"🏆 精选 TOP {len(top_items)} 条准备推送")

    # ── 5. 构建消息 ──────────────────────────────────────────
    base_url = _get_base_url()
    report_url = _build_report_url(report_file, base_url) if base_url else ""
    date_str = _extract_date(report_file.name)

    builder = MessageBuilder()
    markdown_content = builder.build_markdown(
        top_items, report_type, report_url, len(all_items), date_str
    )
    html_content = builder.build_telegram_html(
        top_items, report_type, report_url, len(all_items), date_str
    )

    # ── 6. Dry-run 模式 ───────────────────────────────────────
    if dry_run:
        print("\n" + "=" * 60)
        print("🔍 DRY-RUN 模式 — 以下为预览，不会实际发送")
        print("=" * 60)
        print(f"\n通道: {', '.join(channel_names)}")
        print(f"标题: Renegade AI {report_type}简报 (TOP{len(top_items)}/{len(all_items)})")
        print(f"{'─' * 60}")
        print(markdown_content)
        print(f"{'─' * 60}")
        print("✅ Dry-run 完成")

        # 记录到历史（标记 dry_run）
        history = PushHistory()
        history.record(
            report_type=report_type,
            channels=channel_names,
            total_items=len(all_items),
            pushed_items=len(top_items),
            dry_run=True,
        )
        return 0

    # ── 7. 推送 ───────────────────────────────────────────────
    results: List[PushResult] = []
    success_channels = []
    errors = {}

    for ch_name in channel_names:
        channel = get_channel(ch_name)
        if channel is None:
            print(f"⚠️ 未知通道: {ch_name}，已跳过")
            errors[ch_name] = "未知通道类型"
            continue

        if not channel.is_ready():
            print(f"⏭️ {ch_name}: 未配置，跳过 (状态: {channel.state.value})")
            errors[ch_name] = f"通道未就绪: {channel.state.value}"
            continue

        # 选择合适的内容格式
        if ch_name == "telegram":
            content = html_content
        else:
            content = markdown_content

        title = f"Renegade AI {report_type}简报 (TOP{len(top_items)}/{len(all_items)})"
        result = channel.send(title, content, top_items)
        results.append(result)

        if result.success:
            print(f"✅ {ch_name}: 推送成功 ({result.items_count} 条)")
            success_channels.append(ch_name)
        else:
            print(f"❌ {ch_name}: 推送失败 — {result.error_message}")
            errors[ch_name] = result.error_message

    # ── 8. 标记已推送 + 记录历史 ──────────────────────────────
    if success_channels:
        dedup.mark_pushed(top_items)

    history = PushHistory()
    history.record(
        report_type=report_type,
        channels=channel_names,
        total_items=len(all_items),
        pushed_items=len(top_items),
        dry_run=False,
        success_channels=success_channels,
        errors=errors,
    )

    # ── 9. 摘要 ───────────────────────────────────────────────
    print(f"\n{'─' * 40}")
    if success_channels:
        print(f"✅ 推送完成 | 通道: {', '.join(success_channels)} | "
              f"日期: {date_str} | TOP: {len(top_items)}/{len(all_items)}")
        return 0
    else:
        print(f"❌ 所有通道推送失败")
        return 1


def cmd_history() -> int:
    """查看推送历史"""
    history = PushHistory()
    stats = history.stats()

    print("📊 推送统计")
    print(f"  总推送次数: {stats['total_pushes']}")
    print(f"  成功次数:   {stats['successful_pushes']}")
    print(f"  演习次数:   {stats['dry_runs']}")
    if stats["by_channel"]:
        print("  按通道:")
        for ch, count in stats["by_channel"].items():
            print(f"    - {ch}: {count} 次")

    recent = history.recent(days=7)
    if recent:
        print(f"\n📋 最近 7 天推送记录 ({len(recent)} 条):")
        for r in recent[:10]:
            ts = r.get("timestamp", "")[:16]
            rt = r.get("report_type", "?")
            sc = ", ".join(r.get("success_channels", [])) or "失败"
            dry = " [DRY-RUN]" if r.get("dry_run") else ""
            print(f"  {ts} | {rt:6s} | {sc}{dry} | "
                  f"{r.get('pushed_items', 0)}/{r.get('total_items', 0)} 条")
    return 0


def cmd_status() -> int:
    """查看通道状态"""
    print("🔍 通知通道状态:\n")
    for ch_name in ["dingtalk", "telegram"]:
        channel = get_channel(ch_name)
        if channel is None:
            print(f"  ❓ {ch_name}: 模块未安装")
            continue
        status = channel.get_status()
        icon = "✅" if status["state"] == "ready" else "⏭️"
        print(f"  {icon} {ch_name}: {status['state']}")
        if status["last_error"]:
            print(f"     上次错误: {status['last_error']}")
    return 0


# ── 入口 ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🔔 Renegade AI 通知系统 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python -m notify --type news
  python -m notify --type papers --dry-run
  python -m notify --type news --channels dingtalk,telegram
  python -m notify --file docs/news/news_report_2026-05-15.md
  python -m notify --history
  python -m notify --status
        """,
    )

    parser.add_argument(
        "--type", choices=["news", "papers", "academic"],
        default="news", help="报告类型"
    )
    parser.add_argument(
        "--file", default=None, help="直接指定 .md 报告文件路径"
    )
    parser.add_argument(
        "--channels", default=None,
        help="要使用的通知通道，逗号分隔 (如: dingtalk,telegram)"
    )
    parser.add_argument(
        "--min-score", type=float, default=4.0, help="最低评分阈值"
    )
    parser.add_argument(
        "--top-n", type=int, default=5, help="推送前 N 条"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="预览模式：显示消息内容但不实际发送"
    )
    parser.add_argument(
        "--history", action="store_true", help="查看推送历史"
    )
    parser.add_argument(
        "--status", action="store_true", help="查看通道状态"
    )

    args = parser.parse_args()

    if args.history:
        return cmd_history()
    if args.status:
        return cmd_status()

    return run(args)


if __name__ == "__main__":
    sys.exit(main())
