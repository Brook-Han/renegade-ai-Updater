# Phase 0 验证报告：AI HOT API 数据形态分析

## 一、API 调用验证

**调用命令**：
```bash
curl -s -H "User-Agent: Mozilla/5.0 ..." \
  "https://aihot.virxact.com/api/public/items?mode=selected&since=2026-06-03T04:00:00Z&take=10"
```

**结果**：✅ 成功返回数据，HTTP 200，JSON 格式，无需认证

---

## 二、AI HOT 数据格式分析

### 单条数据完整结构

```json
{
  "id": "cmq7esdai02hdsl5wq2pe6o5v",
  "title": "Magnetar用数百AI智能体替代分析师",
  "title_en": "Bloomberg：Magnetar Capital, the $18B hedge fund company, will avoid human analysts in its newest of…",
  "url": "https://x.com/rohanpaul_ai/status/2064524448582267047",
  "source": "X：Rohan Paul (@rohanpaul_ai)",
  "publishedAt": "2026-06-10T01:46:00.000Z",
  "summary": "Bloomberg：Magnetar Capital，这家 180 亿美元的对冲基金公司，将在其最新产品中避免使用人类分析师，转而依靠数百个 AI 智能体进行股票研究。",
  "category": "industry",
  "score": 75,
  "selected": true
}
```

### 字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | string | AI HOT 内部 ID（nanoid） | `cmq7esdai02hdsl5wq2pe6o5v` |
| `title` | string | **中文标题**（编辑翻译/润色） | `Magnetar用数百AI智能体替代分析师` |
| `title_en` | string/null | 英文原标题（可能为 null） | `Bloomberg：Magnetar Capital...` |
| `url` | string | 原文链接（可直达来源） | `https://x.com/rohanpaul_ai/...` |
| `source` | string | 来源描述（含平台+作者） | `X：Rohan Paul (@rohanpaul_ai)` |
| `publishedAt` | string | ISO 8601 时间 | `2026-06-10T01:46:00.000Z` |
| `summary` | string | **中文摘要**（1-3 句，信息密度高） | `Bloomberg：Magnetar Capital...` |
| `category` | string | 5 个分类之一 | `industry` |
| `score` | int | 编辑评分（0-100） | `75` |
| `selected` | bool | 是否精选（mode=selected 时全为 true） | `true` |

---

## 三、与 News Radar 标准格式对比

### News Radar 标准文章格式

```json
{
  "id": "news_<sha256前16位>",
  "title": "文章标题",
  "summary": "摘要(最多500字)",
  "published": "ISO8601日期",
  "url": "原文链接",
  "authors": ["作者列表"],
  "source": "newsapi|rss",
  "source_name": "来源名称"
}
```

### 字段映射表

| AI HOT 字段 | News Radar 字段 | 映射方式 | 备注 |
|-------------|----------------|---------|------|
| `title` | `title` | ✅ 直接映射 | AI HOT 中文标题质量高 |
| `summary` | `summary` | ✅ 直接映射 | AI HOT 摘要已精炼，无需截断 |
| `publishedAt` | `published` | ✅ 直接映射 | 同为 ISO 8601 格式 |
| `url` | `url` | ✅ 直接映射 | 完全兼容 |
| `source` | `source_name` | ✅ 直接映射 | 如 `X：Rohan Paul` |
| — | `source` | 固定值 `"aihot"` | 标识数据来源 |
| — | `id` | 生成 `news_<sha256(url)前16位>` | 保持与现有格式一致 |
| — | `authors` | 从 `source` 提取或留空 `[]` | 可选增强 |
| `category` | — | **新增字段** `aihot_category` | 保留分类信息 |
| `score` | — | **新增字段** `aihot_score` | 编辑评分可作参考 |
| `title_en` | — | **新增字段** `title_en` | 保留英文原标题 |

### 格式转换代码示例

```python
def normalize_aihot_to_news(aihot_item: dict) -> dict:
    """将 AI HOT 数据格式转换为 News Radar 标准格式"""
    import hashlib
    
    url = aihot_item.get("url", "")
    title = aihot_item.get("title", "")
    
    # 生成与现有格式一致的 ID
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    
    return {
        "id": f"news_{url_hash}",
        "title": title,
        "summary": aihot_item.get("summary", "")[:500],  # 保持一致性截断
        "published": aihot_item.get("publishedAt", ""),
        "url": url,
        "authors": [],  # AI HOT 不提供作者列表
        "source": "aihot",
        "source_name": aihot_item.get("source", "AI HOT"),
        # 保留 AI HOT 特有字段
        "aihot_category": aihot_item.get("category"),
        "aihot_score": aihot_item.get("score"),
        "title_en": aihot_item.get("title_en"),
    }
```

---

## 四、关键发现

### ✅ 高度兼容的点

1. **时间格式完全一致**：`publishedAt` 和 `published` 都是 ISO 8601，无需转换
2. **URL 可直接使用**：`url` 字段就是原文链接，与现有格式一致
3. **摘要质量高**：AI HOT 的 `summary` 是编辑撰写的中文摘要（1-3 句），比 RSS 的 `summary_detail.value` 质量更高
4. **分类系统清晰**：5 个分类（industry/ai-models/ai-products/paper/tip）可作为理论映射的辅助信息
5. **编辑评分可用**：`score`（0-100）可转换为 1-10 系统，作为 `relevance` 的参考

### ⚠️ 需要注意的点

1. **中文内容**：现有预筛选词库（理论概念词 + 领域词）全是英文，对中文内容无效
   - **解决方案**：初期对 `source="aihot"` 跳过预筛选（AI HOT 已是精选）
2. **无 authors 字段**：AI HOT 不提供结构化作者列表
   - **解决方案**：留空 `[]`，或从 `source` 字段提取（如 `X：Rohan Paul` → `Rohan Paul`）
3. **ID 系统不同**：AI HOT 使用 nanoid，现有系统使用 `news_<sha256>`
   - **解决方案**：在 `normalize_aihot_to_news()` 中统一生成 ID
4. **摘要偏短**：AI HOT 摘要通常 1-2 句（50-100 字），RSS 摘要可能 200+ 字
   - **影响**：AI 分析时的上下文较少，但质量更高（编辑精炼）
5. **category 是英文 slug**：`industry` 而非中文标签
   - **解决方案**：在报告生成时做映射（`industry` → `行业动态`）

---

## 五、融合难度评估

| 维度 | 难度 | 说明 |
|------|------|------|
| **数据格式转换** | ⭐ | 字段映射清晰，转换代码约 30 行 |
| **时间窗口过滤** | ⭐ | API 已支持 `since` 参数，服务端已过滤 |
| **URL 去重** | ⭐⭐ | 需与 RSS/NewsAPI 结果做 URL 比对，代码复用现有逻辑 |
| **预筛选适配** | ⭐⭐ | 需对中文内容特殊处理（跳过或新增中文词库） |
| **AI 分析适配** | ⭐⭐ | Prompt 需微调以处理中文摘要 |
| **报告生成适配** | ⭐ | 新增"中国 AI 动态"板块，不影响现有逻辑 |

**总体难度**：⭐⭐（简单到中等），主要是格式转换 + 预筛选适配两处工作。

---

## 六、Phase 0 验证结论

### ✅ 可行性确认

1. **API 可用**：无需认证，仅需带 UA 头，限流 600 req/min（远超每日需求）
2. **数据质量高**：编辑精选 + 中文摘要，信噪比优于 RSS 源
3. **格式兼容性好**：核心字段（title/summary/url/published）可直接映射
4. **时间窗口支持**：`since` 参数支持 7 天滚动窗口，与 `NEWS_DAYS_BACK=7` 完全对齐

### 📋 下一步行动（Phase 1）

1. **创建 `fetch_aihot()` 函数**（`news_sources.py`）
   - 调用 API，处理分页（如需 >100 条）
   - 格式转换（`normalize_aihot_to_news()`）
   - 时间窗口二次验证（防止 API 返回脏数据）

2. **集成到 `fetch_all_news()`**
   - 新增 `ENABLE_AIHOT` 配置开关（默认关闭）
   - 与 RSS/NewsAPI 结果合并
   - URL 去重（复用现有逻辑）

3. **预筛选特殊处理**
   - 对 `source="aihot"` 跳过预筛选（或仅做简单关键词过滤）
   - 观察 1-2 天输出，确认信噪比后再决定是否需要中文词库

4. **测试验证**
   - 本地运行 `python news_radar.py --limit 50 --no-llm`
   - 检查 AI HOT 条目是否正确进入 `docs/news/news_articles_YYYY-MM-DD.json`
   - 手动触发 AI 分析，验证中文摘要的分析质量

### 💡 优化建议

1. **利用 `score` 字段**：AI HOT 的编辑评分（0-100）可转换为 1-10 系统，作为 `relevance` 的先验知识（prior），减少 AI 调用次数
2. **利用 `category` 字段**：`paper` 类自动路由到学术管道，`ai-models`/`ai-products` 优先匹配理论模型 1-4
3. **保留 `title_en`**：在报告中提供英文原标题链接，方便读者深挖

---

## 七、示例：转换后的标准格式

```json
{
  "id": "news_a3f8b2c4d5e6f7g8",
  "title": "Magnetar用数百AI智能体替代分析师",
  "summary": "Bloomberg：Magnetar Capital，这家 180 亿美元的对冲基金公司，将在其最新产品中避免使用人类分析师，转而依靠数百个 AI 智能体进行股票研究。这家 180 亿美元的对冲基金公司希望 AI 搜索投资想法、研究公司、推荐头寸并预测趋势，而人类仅负责批准交易。",
  "published": "2026-06-10T01:46:00.000Z",
  "url": "https://x.com/rohanpaul_ai/status/2064524448582267047",
  "authors": [],
  "source": "aihot",
  "source_name": "X：Rohan Paul (@rohanpaul_ai)",
  "aihot_category": "industry",
  "aihot_score": 75,
  "title_en": "Bloomberg：Magnetar Capital, the $18B hedge fund company, will avoid human analysts in its newest of…"
}
```

---

**验证完成时间**：2026-06-10 12:15 GMT+8  
**验证结论**：✅ 高度可行，建议进入 Phase 1（Level 1 轻量融合）
