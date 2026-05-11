#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔔 钉钉机器人推送脚本（Renegade AI 专用版）

✨ 功能：
  ✅ 支持钉钉加签验证（HMAC-SHA256），更安全
  ✅ 自动解析 Markdown 报告，提取高价值条目
  ✅ 智能筛选：只推送评分 ≥4.0 的前 5 条内容
  ✅ 格式精美：Markdown 排版 + 链接 + 摘要 + 章节标记

📋 用法：
    # 推送新闻报告
    python dingtalk.py --type news
    
    # 推送论文报告  
    python dingtalk.py --type papers
    
    # 指定具体文件推送
    python dingtalk.py --file reports/news/news_report_2026-05-11_143022.md

🔐 所需环境变量：
    - DINGTALK_WEBHOOK: 机器人 Webhook URL
    - DINGTALK_SECRET: 加签密钥（钉钉机器人安全设置中获取）
    - REPORT_BASE_URL: 报告页面基础 URL（如: https://brook-han.github.io/renegade-ai-Updater/reports）

作者：Brooks Han
版本：v1.1 (2026-05-11)
"""

import os
import sys
import time
import hmac
import hashlib
import base64
import urllib.parse
import re
from pathlib import Path
from typing import Optional, List, Dict

import requests

# ──────────────────────────────────────────────────────────────
# 🔐 钉钉签名与发送
# ──────────────────────────────────────────────────────────────

def generate_sign(secret: str) -> tuple:
    """
    生成钉钉机器人签名所需的时间戳和签名（加签模式）
    
    参数:
        secret: 钉钉机器人的加签密钥
    
    返回:
        (时间戳字符串, 签名字符串)
    """
    ts = str(round(time.time() * 1000))  # 当前毫秒时间戳
    to_sign = f"{ts}\n{secret}".encode()  # 待签名字符串
    # HMAC-SHA256 + Base64 + URL 编码
    sign = urllib.parse.quote_plus(
        base64.b64encode(
            hmac.new(secret.encode(), to_sign, hashlib.sha256).digest()
        ).decode()
    )
    return ts, sign


def send_dingtalk(webhook: str, secret: str, title: str, text: str) -> bool:
    """
    发送钉钉 Markdown 消息
    
    参数:
        webhook: 机器人 Webhook 地址
        secret: 加签密钥
        title: 消息标题
        text: Markdown 格式内容
    
    返回:
        bool: True 表示发送成功
    """
    try:
        ts, sign = generate_sign(secret)
        # 拼接带签名的完整 URL
        url = f"{webhook}&timestamp={ts}&sign={sign}"
        
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            }
        }
        
        r = requests.post(url, json=payload, timeout=15)
        result = r.json()
        
        if result.get("errcode") == 0:
            print(f"✅ 钉钉推送成功: {title}")
            return True
        else:
            print(f"❌ 钉钉返回错误: {result}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 钉钉请求超时")
        return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


# ──────────────────────────────────────────────────────────────
# 📄 Markdown 报告解析
# ──────────────────────────────────────────────────────────────

def extract_field(line: str, field_name: str) -> str:
    """从一行中提取 "- **字段名**: 值" 格式的内容"""
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        return re.sub(r"\*+", "", m.group(1)).strip()
    return ""


def parse_items(report_path: str, min_score: float = 4.0) -> List[Dict]:
    """
    解析 Markdown 报告，提取条目信息
    
    参数:
        report_path: .md 文件路径
        min_score: 最低评分阈值
    
    返回:
        符合条件的条目列表
    """
    content = Path(report_path).read_text(encoding="utf-8")
    items = []
    cur = {}
    in_draft = False
    draft_lines = []

    for line in content.split("\n"):
        s = line.strip()
        
        # 新条目标志：### 开头且不是章节标题
        if s.startswith("### ") and not any(x in s for x in ["高相关", "中相关", "低相关", "紧急"]):
            if cur.get("title"):
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                items.append(cur)
                draft_lines = []
            cur = {"title": s[4:].strip()}
            in_draft = False
            continue
        
        # 草稿区域检测
        if "✍️" in s and ("草稿" in s or "draft" in s.lower()):
            in_draft = True
            continue
        if in_draft:
            if s.startswith("###") or s.startswith("---"):
                in_draft = False
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                draft_lines = []
                continue
            draft_lines.append(s)
            continue
        
        # 提取字段（只提取一次）
        if not cur.get("score"):
            cur["score"] = extract_field(s, "最终评分") or extract_field(s, "相关度")
        if not cur.get("urgency"):
            cur["urgency"] = extract_field(s, "紧迫度")
        if not cur.get("summary"):
            cur["summary"] = extract_field(s, "核心发现") or extract_field(s, "事件摘要")
        if not cur.get("url"):
            cur["url"] = extract_field(s, "链接")
        if not cur.get("implications"):
            cur["implications"] = extract_field(s, "与本书关联") or extract_field(s, "理论关联")
        if not cur.get("chapter"):
            cur["chapter"] = extract_field(s, "目标章节")

    # 处理最后一个条目
    if cur.get("title"):
        if draft_lines:
            cur["draft"] = "\n".join(draft_lines).strip()
        items.append(cur)

    # 过滤 + 转换评分
    result = []
    for it in items:
        score_str = str(it.get("score", "0")).split("/")[0]
        try:
            score = float(score_str)
        except ValueError:
            continue
        if score >= min_score:
            it["score_num"] = score
            result.append(it)
    
    return result


# ──────────────────────────────────────────────────────────────
# 📝 构造钉钉消息（TOP 5 精选）
# ──────────────────────────────────────────────────────────────

def build_brief(top_items: List[Dict], report_type: str, report_url: str, total: int, date_str: str) -> str:
    """生成钉钉 Markdown 消息内容"""
    
    # 标题前缀
    if report_type == "papers":
        title_prefix = "📚 **Renegade AI 学术简报**"
        emoji = "🎓"
    else:
        title_prefix = "📰 **Renegade AI 资讯简报**"
        emoji = "🗞️"
    
    lines = [
        f"## {title_prefix}",
        f"**{date_str}** · 共分析 {total} 条 | 精选 {len(top_items)} 条高价值内容",
        "",
    ]
    
    # 遍历 TOP 条目
    for idx, it in enumerate(top_items, 1):
        title = it.get("title", "")[:80]
        score = f"{it.get('score_num', 0):.1f}/10"
        url = it.get("url", "#")
        chapter = it.get("chapter", "")
        summary = it.get("summary", "")
        implications = it.get("implications", "")
        
        lines.append(f"### {idx}. {title}")
        lines.append(f"- ⭐ 评分：{score} [↗ 原文]({url})")
        
        if chapter and chapter not in ("N/A", ""):
            lines.append(f"- 📍 {chapter}")
        if summary and summary not in ("N/A", ""):
            # 截断 + 省略号
            summary_clean = summary[:150] + ("..." if len(summary) > 150 else "")
            lines.append(f"- 📝 {summary_clean}")
        if implications and implications not in ("N/A", ""):
            lines.append(f"- 🔗 {implications[:120]}...")
        
        # 如果有草稿，添加标记
        if it.get("draft"):
            lines.append("- ✍️ 已生成书稿草稿")
        
        lines.append("")  # 空行分隔
    
    # 页脚 + 完整报告链接
    lines.append("---")
    lines.append(f"> {emoji} [📄 查看完整报告（含全部条目 + 书稿草稿）]({report_url})")
    lines.append(f"> 🤖 自动推送 · Renegade AI v5.3")
    
    msg = "\n".join(lines)
    
    # 安全截断（钉钉限制 4000 字符）
    if len(msg) > 3800:
        msg = msg[:3800] + "\n\n> ⚠️ 内容过长已截断，请点击查看完整报告。"
    
    return msg


# ──────────────────────────────────────────────────────────────
# 🚀 主入口
# ──────────────────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="🔔 推送 Renegade AI 报告到钉钉")
    parser.add_argument("--type", choices=["news", "papers", "academic"], 
                       default="news", help="报告类型")
    parser.add_argument("--file", default=None, help="直接指定 .md 文件路径")
    parser.add_argument("--min-score", type=float, default=4.0, help="最低评分阈值")
    parser.add_argument("--top-n", type=int, default=5, help="推送前 N 条")
    args = parser.parse_args()
    
    # 🔐 读取环境变量
    webhook = os.getenv("DINGTALK_WEBHOOK")
    secret = os.getenv("DINGTALK_SECRET")
    base_url = os.getenv("REPORT_BASE_URL", "").rstrip("/")
    
    if not webhook or not secret:
        print("❌ 缺少环境变量: DINGTALK_WEBHOOK 或 DINGTALK_SECRET")
        print("💡 GitHub Actions 中请在 Settings → Secrets 中配置")
        sys.exit(1)
    
    if not base_url:
        print("❌ 缺少环境变量: REPORT_BASE_URL")
        print("💡 示例: https://brook-han.github.io/renegade-ai-Updater/reports")
        sys.exit(1)
    
    # 📁 确定报告文件
    if args.file and Path(args.file).exists():
        latest_md = Path(args.file)
        print(f"📄 使用指定文件: {latest_md}")
    else:
        # 自动查找最新报告
        report_type = "academic" if args.type == "papers" else args.type
        pattern = f"reports/{report_type}/*_report_*.md"
        report_files = sorted(Path().glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not report_files:
            print(f"⚠️ 未找到 {args.type} 报告文件")
            sys.exit(0)
        
        latest_md = report_files[0]
        print(f"📄 自动选择: {latest_md}")
    
    # 📊 解析条目
    items = parse_items(str(latest_md), min_score=args.min_score)
    if not items:
        print(f"⚠️ 无评分 ≥{args.min_score} 的条目，跳过推送")
        sys.exit(0)
    
    # 🏆 排序 + 取 TOP N
    items.sort(key=lambda x: x["score_num"], reverse=True)
    top_n = items[:args.top_n]
    
    # 🔗 构造报告 URL
    html_file = latest_md.with_suffix(".html").name
    # 处理子目录情况：reports/news/xxx.html → news/xxx.html
    relative_path = latest_md.relative_to(Path("reports")).with_suffix(".html")
    report_url = f"{base_url}/{relative_path}"
    
    # 📅 提取日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', latest_md.name)
    date_str = date_match.group(1) if date_match else "Unknown"
    for it in top_n:
        it["date"] = date_str
    
    # 📝 生成消息
    msg = build_brief(top_n, args.type, report_url, len(items), date_str)
    title = f"Renegade AI {args.type}简报 (TOP{len(top_n)}/{len(items)})"
    
    # 📤 发送
    print(f"📤 推送 {len(top_n)} 条内容到钉钉...")
    ok = send_dingtalk(webhook, secret, title, msg)
    
    if ok:
        print(f"✅ 推送成功 | 日期:{date_str} | 类型:{args.type} | TOP:{len(top_n)}")
        sys.exit(0)
    else:
        print("❌ 推送失败")
        sys.exit(1)


if __name__ == "__main__":
    main()