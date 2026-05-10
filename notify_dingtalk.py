#!/usr/bin/env python3
"""
钉钉机器人推送脚本（只推送评分最高的前 5 条）
用途：将每天/每周生成的 AI 报告中的高价值内容推送到钉钉群
用法：
    python notify_dingtalk.py --type news      # 推送新闻报告
    python notify_dingtalk.py --type papers    # 推送论文报告
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

import requests

# ==================== 钉钉签名与发送 ====================

def generate_sign(secret: str) -> tuple:
    """
    生成钉钉机器人签名所需的时间戳和签名
    参数：secret – 钉钉机器人的加签密钥
    返回：(时间戳字符串, 签名字符串)
    """
    ts = str(round(time.time() * 1000))                     # 当前毫秒时间戳
    to_sign = f"{ts}\n{secret}".encode()                    # 待签名字符串
    # 计算 HMAC-SHA256 签名并进行 Base64 编码和 URL 编码
    sign = urllib.parse.quote_plus(
        base64.b64encode(hmac.new(secret.encode(), to_sign, hashlib.sha256).digest())
    )
    return ts, sign

def send_dingtalk(webhook: str, secret: str, title: str, text: str) -> bool:
    """
    发送钉钉消息（Markdown 格式）
    参数：
        webhook – 钉钉机器人的 Webhook 地址
        secret   – 加签密钥
        title    – 消息标题（在钉钉中会显示）
        text     – Markdown 格式的消息内容
    返回：True 表示发送成功，False 表示失败
    """
    ts, sign = generate_sign(secret)
    url = f"{webhook}&timestamp={ts}&sign={sign}"          # 拼接完整请求 URL
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": text
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        result = r.json()
        if result.get("errcode") == 0:
            return True
        else:
            # 打印钉钉返回的错误信息，方便排查
            print(f"❌ 钉钉返回错误：{result}")
            return False
    except Exception as e:
        print(f"❌ 发送请求异常：{e}")
        return False

# ==================== Markdown 报告解析 ====================

def extract_field(line: str, field_name: str) -> str:
    """
    从一行文本中提取类似 "- **字段名**: 值" 的内容
    参数：
        line       – 一行文本
        field_name – 要提取的字段名（如 "最终评分"）
    返回：提取到的值，如果没找到则返回空字符串
    """
    # 正则匹配：以 - 开头，然后是任意数量的 *，接着字段名，再任意数量的 *，然后是冒号和内容
    pattern = rf"-\s*\*+\s*{re.escape(field_name)}\s*\*+\s*:\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        # 去掉可能残留的加粗标记 *
        return re.sub(r"\*+", "", m.group(1)).strip()
    return ""

def parse_items(report_path: str, min_score: float = 4.0) -> list[dict]:
    """
    解析 Markdown 报告文件，提取所有条目（卡片）的信息
    参数：
        report_path – .md 文件的路径
        min_score   – 最低评分阈值（低于此评分的条目会被过滤）
    返回：列表，每个元素是一个字典，包含标题、评分、链接、摘要等字段
    """
    content = Path(report_path).read_text(encoding="utf-8")
    items = []          # 存储所有解析出的条目
    cur = {}            # 当前正在解析的条目
    in_draft = False    # 是否正在读取草稿内容
    draft_lines = []    # 暂存草稿的行

    for line in content.split("\n"):
        s = line.strip()
        # 新条目标志：以 "### " 开头，并且不是 "### 高相关" 等章节标题
        if s.startswith("### ") and not s.startswith("### 高相关") and not s.startswith("### 中相关"):
            # 保存上一个条目
            if cur.get("title"):
                if draft_lines:
                    cur["draft"] = "\n".join(draft_lines).strip()
                items.append(cur)
                draft_lines = []
            # 开始新条目
            cur = {"title": s[4:].strip()}   # 去掉 "### " 得到标题
            in_draft = False
            continue

        # 检测草稿区域的开始（包含 "✍️ 自动生成书稿草稿" 的行）
        if "✍️ 自动生成书稿草稿" in s:
            in_draft = True
            continue
        if in_draft:
            draft_lines.append(s)
            # 草稿区域结束的标志：遇到下一个条目或分隔线
            if s.startswith("###") or s.startswith("---"):
                in_draft = False
                cur["draft"] = "\n".join(draft_lines[:-1]).strip()
                draft_lines = []
            continue

        # 提取各个字段（只在当前条目中提取一次）
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

    # 过滤掉评分低于 min_score 的条目，并转换评分为数字
    result = []
    for it in items:
        score_str = it.get("score", "0").split("/")[0]   # 例如 "8.5/10" → "8.5"
        try:
            score = float(score_str)
        except ValueError:
            continue
        if score >= min_score:
            it["score_num"] = score          # 存入数字评分，方便排序
            result.append(it)
    return result

# ==================== 构造钉钉消息（只取评分最高的前5条）====================

def build_brief(top_items: list[dict], report_type: str, report_url: str, total: int) -> str:
    """
    根据评分最高的若干条目生成钉钉 Markdown 消息
    参数：
        top_items   – 得分最高的条目列表（已按评分降序排序）
        report_type – "news" 或 "papers"
        report_url  – 完整报告页面的 URL
        total       – 报告中所有条目的总数（用于显示）
    返回：Markdown 格式的消息字符串
    """
    # 消息标题前缀
    if report_type == "papers":
        title_prefix = "📚 **Renegade AI 每周论文简报**"
    else:
        title_prefix = "📰 **Renegade AI 每日资讯简报**"

    lines = [
        f"## {title_prefix}",
        f"**{top_items[0]['date']}** · 总条目 {total} | 展示评分最高 {len(top_items)} 条",
        ""
    ]

    # 遍历前5条（调用时已经只传了5条）
    for idx, it in enumerate(top_items, 1):
        title = it.get("title", "")[:100]                # 限制标题最长100字符
        score = f"{it.get('score_num', 0):.1f}/10"
        url = it.get("url", "#")
        chapter = it.get("chapter", "")
        summary = it.get("summary", "")
        implications = it.get("implications", "")

        lines.append(f"### {idx}. {title}")
        lines.append(f"- ⭐ 评分：{score} [原文]({url})")
        if chapter and chapter != "N/A":
            lines.append(f"- 📍 {chapter}")
        if summary and summary != "N/A":
            lines.append(f"- 📝 {summary[:200]}")        # 摘要最多显示200字符
        if implications and implications != "N/A":
            lines.append(f"- 🔗 {implications}")
        lines.append("")                                 # 空行分隔

    # 附加完整报告链接
    lines.append(f"> 📄 [查看完整报告（含书稿草稿）]({report_url})")
    msg = "\n".join(lines)

    # 最终安全截断：如果消息长度超过 4000 字符，强行截断（一般不会发生，因为只有5条）
    if len(msg) > 4000:
        msg = msg[:4000] + "\n\n> ⚠️ 消息过长已截断，请查看完整报告。"
    return msg

# ==================== 主入口 ====================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="推送 Renegade AI 报告到钉钉")
    parser.add_argument("--type", choices=["news", "papers"], default="news",
                        help="报告类型：news 或 papers")
    parser.add_argument("--file", default=None,
                        help="直接指定要推送的 .md 报告文件路径（可选）")
    args = parser.parse_args()

    # 读取环境变量
    webhook = os.getenv("DINGTALK_WEBHOOK")
    secret = os.getenv("DINGTALK_SECRET")
    if not webhook or not secret:
        sys.exit("❌ 缺少钉钉环境变量 DINGTALK_WEBHOOK 或 DINGTALK_SECRET")

    base_url = os.getenv("REPORT_BASE_URL", "").rstrip("/")
    if not base_url:
        sys.exit("❌ 缺少 REPORT_BASE_URL 环境变量")

    # 根据是否传入 --file 来决定使用哪个报告文件
    if args.file:
        # 直接使用工作流传入的文件路径
        latest_md = Path(args.file)
        if not latest_md.exists():
            print(f"❌ 指定的文件不存在: {latest_md}")
            sys.exit(1)
        print(f"📄 解析: {latest_md}")
    else:
        # 原来的自动查找逻辑
        pattern = f"reports/{args.type}_report_multi_*.md"
        report_files = sorted(Path().glob(pattern))
        if not report_files:
            print(f"⚠️ 未找到任何 {args.type} 报告文件")
            sys.exit(0)
        latest_md = report_files[-1]
        print(f"📄 解析: {latest_md}")

    # 解析所有满足最低评分的条目
    items = parse_items(str(latest_md), min_score=4.0)
    if not items:
        print("⚠️ 没有符合评分标准的条目（低于 4.0 分）")
        sys.exit(0)

    # 按评分降序排序，只取前5条
    items.sort(key=lambda x: x["score_num"], reverse=True)
    top5 = items[:5]

    # 构造完整报告的 HTML 链接
    html_file = latest_md.with_suffix(".html").name
    report_url = f"{base_url}/{html_file}"
    if not report_url.startswith("http"):
        report_url = f"https://{report_url}"

    # 从文件名中提取日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', latest_md.name)
    if date_match:
        date_str = date_match.group(1)
        for it in top5:
            it["date"] = date_str

    # 生成钉钉消息
    msg = build_brief(top5, args.type, report_url, len(items))
    title = f"Renegade AI {args.type}简报 (TOP5/{len(items)})"

    # 发送
    ok = send_dingtalk(webhook, secret, title, msg)
    if ok:
        print("✅ 推送成功")
    else:
        print("❌ 推送失败")
        sys.exit(1)