#!/usr/bin/env python3
"""解析最新报告（资讯或论文），整理成简报推送到钉钉（对齐 HTML 页面信息）"""

import os
import sys
import time
import hmac
import hashlib
import base64
import urllib.parse
import re
from pathlib import Path

import requests

# -------------------- 钉钉签名与发送 --------------------
def generate_sign(secret: str) -> tuple:
    ts = str(round(time.time() * 1000))
    to_sign = f"{ts}\n{secret}".encode()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac.new(secret.encode(), to_sign, hashlib.sha256).digest()))
    return ts, sign

def send_dingtalk(webhook: str, secret: str, title: str, text: str) -> bool:
    ts, sign = generate_sign(secret)
    url = f"{webhook}&timestamp={ts}&sign={sign}"
    try:
        r = requests.post(url, json={"msgtype": "markdown", "markdown": {"title": title, "text": text}}, timeout=10)
        return r.json().get("errcode") == 0
    except Exception as e:
        print(f"发送失败: {e}")
        return False

# -------------------- MD 解析 --------------------
def extract_field(line: str, field_name: str) -> str:
    """提取 Markdown 列表项中的字段值"""
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        val = m.group(1).strip()
        # 移除残留的加粗标记
        return re.sub(r"\*+", "", val).strip()
    return ""

def parse_items(report_path: str, min_score: float = 4.0) -> list[dict]:
    """提取评分 >= min_score 的所有条目"""
    content = Path(report_path).read_text(encoding="utf-8")
    items = []
    cur = {}
    in_draft = False
    draft_lines = []

    for line in content.split("\n"):
        s = line.strip()
        # 检测新条目：以 "### " 开头，并且不是 "### 高相关" 等标题
        if s.startswith("### ") and not s.startswith("### 高相关") and not s.startswith("### 中相关"):
            # 保存上一个条目
            if cur.get("title"):
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                items.append(cur)
                draft_lines = []
            cur = {"title": s[4:].strip()}
            in_draft = False
            continue

        # 采集草稿段落（在 "✍️ 自动生成书稿草稿" 之后）
        if "✍️ 自动生成书稿草稿" in s or "自动生成书稿草稿" in s:
            in_draft = True
            continue
        if in_draft:
            draft_lines.append(s)
            # 如果遇到下一个条目或分隔线，结束草稿区域
            if s.startswith("###") or s.startswith("---"):
                in_draft = False
                cur["draft"] = "\n".join(draft_lines[:-1]).strip()
                draft_lines = []
            continue

        # 提取各个字段（仅在当前条目下）
        if not cur.get("score"):
            cur["score"] = extract_field(s, "最终评分")
        if not cur.get("urgency"):
            cur["urgency"] = extract_field(s, "紧迫度")
        if not cur.get("summary"):
            cur["summary"] = extract_field(s, "核心发现")
        if not cur.get("url"):
            cur["url"] = extract_field(s, "链接")
        if not cur.get("implications"):
            cur["implications"] = extract_field(s, "与本书关联")
        if not cur.get("chapter"):
            cur["chapter"] = extract_field(s, "目标章节")

    # 处理最后一个条目
    if cur.get("title"):
        if draft_lines:
            cur["draft"] = "\n".join(draft_lines).strip()
        items.append(cur)

    # 过滤并保留评分 >= min_score 的条目
    result = []
    for it in items:
        score_str = it.get("score", "0").split("/")[0]
        try:
            score = float(score_str)
        except ValueError:
            continue
        if score >= min_score:
            it["score_num"] = score
            result.append(it)
    return result

# -------------------- 构造钉钉消息 --------------------
def build_brief(items: list[dict], report_type: str, report_url: str) -> str:
    """生成对齐 HTML 页面的简报"""
    total = len(items)
    # 按评分为主、紧迫度辅助排序
    urgent = [i for i in items if i.get("urgency", "").strip().lower() == "immediate"]
    high = [i for i in items if i.get("score_num", 0) >= 6.5 and i not in urgent]
    medium = [i for i in items if 4.0 <= i.get("score_num", 0) < 6.5]

    title_prefix = "📚 **Renegade AI 每周论文简报**" if report_type == "papers" else "📰 **Renegade AI 每日资讯简报**"
    lines = [
        f"## {title_prefix}",
        f"**{items[0].get('date', '')}** · 总条目 {total} | 需紧急更新 {len(urgent)} | 高相关 {len(high)} | 其他关注 {len(medium)}",
        ""
    ]

    # 紧急更新
    if urgent:
        lines.append("### 🚨 需立即更新 (Immediate)")
        for it in urgent:
            lines.extend(_format_item(it))
        lines.append("")

    # 高相关
    if high:
        lines.append("### 🔥 高相关 (≥6.5)")
        for it in high:
            lines.extend(_format_item(it))
        lines.append("")

    # 中等关注（最多5条）
    if medium:
        lines.append("### 📌 其他关注 (4.0–6.4)")
        for it in medium[:5]:
            lines.extend(_format_item(it, brief=True))
        if len(medium) > 5:
            lines.append(f"\n> ⚡ 还有 {len(medium) - 5} 条，详见完整报告")
        lines.append("")

    lines.append(f"> 📄 [查看完整报告（含书稿草稿）]({report_url})")
    return "\n".join(lines)

def _format_item(it: dict, brief: bool = False) -> list[str]:
    """格式化单个条目，对齐 HTML 卡片信息"""
    title = it.get("title", "")[:150]
    score = f"{it.get('score_num', 0):.1f}/10"
    url = it.get("url", "#")
    chapter = it.get("chapter", "")
    summary = it.get("summary", "")
    implications = it.get("implications", "")

    block = []
    block.append(f"**{title}** [原文]({url})")
    block.append(f"- ⭐ 评分：{score}")
    if chapter and chapter != "N/A":
        block.append(f"- 📍 {chapter}")
    if summary and summary != "N/A":
        block.append(f"- 📝 {summary[:200]}")
    if implications and implications != "N/A":
        block.append(f"- 🔗 {implications}")
    block.append("")
    return block

# -------------------- 主入口 --------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["news", "papers"], default="news", help="报告类型")
    args = parser.parse_args()

    webhook = os.getenv("DINGTALK_WEBHOOK")
    secret = os.getenv("DINGTALK_SECRET")
    if not webhook or not secret:
        sys.exit("❌ 缺少钉钉环境变量")

    base_url = os.getenv("REPORT_BASE_URL", "").rstrip("/")
    if not base_url:
        sys.exit("❌ 缺少 REPORT_BASE_URL 环境变量")

    # 查找最新生成的报告 MD 文件（用于解析内容）
    pattern = f"reports/{args.type}_report_multi_*.md"
    report_files = sorted(Path().glob(pattern))
    if not report_files:
        print(f"⚠️ 未找到任何 {args.type} MD 报告")
        sys.exit(0)

    latest_md = report_files[-1]
    print(f"📄 解析: {latest_md}")

    # 解析 MD 获得条目
    items = parse_items(str(latest_md), min_score=4.0)
    if not items:
        print("⚠️ 没有符合评分标准的条目")
        sys.exit(0)

    # 构造对应的 HTML 文件名（与 MD 同名，扩展名 .html）
    html_file = latest_md.with_suffix(".html").name
    report_url = f"{base_url}/{html_file}"
    # 确保 URL 格式正确
    if not report_url.startswith("http"):
        report_url = f"https://{report_url}"  # 保险，但 base_url 应该已包含协议

    print(f"🔗 报告链接: {report_url}")

    # 添加日期字段（用于显示）
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', latest_md.name)
    if date_match:
        for it in items:
            it["date"] = date_match.group(1)

    msg = build_brief(items, args.type, report_url)
    title = f"Renegade AI {'论文' if args.type == 'papers' else '资讯'}简报 ({len(items)}条)"
    ok = send_dingtalk(webhook, secret, title, msg)
    print("✅ 推送成功" if ok else "❌ 推送失败")