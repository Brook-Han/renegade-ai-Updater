# 新闻索引页与学术索引页设计风格对齐分析报告

## 执行摘要

经过对 `docs/news/index.html`、`docs/academic/index.html`、`docs/index.html`（主页）以及两个生成脚本（`generate_news_index.py`、`generate_academic_index.py`）的逐行比对，发现两页之间存在 **11 类核心不对齐问题**，涵盖设计令牌、布局结构、组件实现、交互细节和工程架构五个维度。以下按优先级排序，提供可执行的修复方案。

---

## 一、设计令牌 (Design Tokens) 不对齐

### 问题描述
两页使用不同的颜色值和字体比例，破坏视觉一致性。

| Token | 新闻页 (v5.4) | 学术页 (v5.3) | 主页 (v5.4) | 建议统一值 |
|-------|---------------|---------------|-------------|-----------|
| `--bg` | `#0c0c18` | `#08080e` | `#0c0c18` | `#0c0c18` |
| `--card` | `#1a1a2e` | `#13131f` | `#1a1a2e` | `#1a1a2e` |
| `--accent` | `#ff5c45` | `#e8503a` | `#ff5c45` | `#ff5c45` |
| `--accent2` | `#d4a85c` | `#c9a040` | `#d4af5c` | `#d4af5c` |
| `--accent3` | `#5ba3e6` | `#4a8fcf` | `#5ba3e6` | `#5ba3e6` |
| `--text-muted` | `#a8a8d0` | `#6868a0` | `#a8a8d0` | `#a8a8d0` |
| `--border-bright` | `#3a3a5a` | `#2e2e50` | `#3a3a5a` | `#3a3a5a` |
| 基础字号 | `1rem` | 未显式设置 | `1rem` | `1rem` |
| 小字号比例 | `.72rem` | `.62rem` / `.58rem` | `.72rem` | `.72rem` |

### 影响
- 学术页整体更"暗"、更"灰"，与新闻页和主页形成视觉断层
- 悬停状态、标签颜色在不同页面跳转时产生"闪烁"感

### 修复方案
**选项 A（推荐）**：将学术页 CSS 完整替换为新闻页/主页的 v5.4 Design Tokens，确保三页完全一致。

**选项 B**：提取共享 CSS 到 `docs/assets/style.css`，两页通过 `<link>` 引用，从根本上消除复制粘贴导致的漂移。

---

## 二、Hero 区域结构缺失（新闻页）

### 问题描述
新闻页 **完全缺失** `hero-strip` 结构。对比三页：

- **主页**：完整的 `hero-strip` → `hero-left`（标题+描述+标签）+ `hero-right`（统计数字）
- **学术页**：完整的 `hero-strip` → 同上结构
- **新闻页**：`hero-strip` 被注释为空（第 418-419 行），然后在 `<main>` 内部用简陋的 `hero-eyebrow` + `<h1>` + `hero-desc` 拼凑（第 433-442 行）

```html
<!-- 新闻页实际结构（错误） -->
<main class="main">
  <div class="hero-eyebrow">§ News Archive</div>  <!-- 应在 hero-strip 内 -->
  <h1>NEWS ARCHIVE</h1>                            <!-- 缺少 hero-title 类 -->
  <div class="hero-desc">...</div>                  <!-- 在 main 内，非 hero 区域 -->
  <div class="controls-bar">...</div>               <!-- 重复！ -->
```

### 影响
- 新闻页顶部视觉层次断裂，用户进入后无法获得与学术页一致的"归档页"认知
- 统计数字（报告总数、天数）完全缺失，信息密度下降
- 品牌一致性受损

### 修复方案
在 `generate_news_index.py` 或模板中，参照学术页和主页的 `hero-strip` 结构重建：

```html
<div class="hero-strip">
  <div class="hero-left">
    <div class="hero-eyebrow">§ News Archive</div>
    <h1 class="hero-title">NEWS<br><span>ARCHIVE</span></h1>
    <p class="hero-desc">News signal extracted from the noise — ranked by relevance to cognitive friction and civilizational diagnosis.</p>
    <div class="hero-tags">
      <span class="hero-tag" id="tagTotal">— REPORTS</span>
      <span class="hero-tag" id="tagDays">— DAYS</span>
      <span class="hero-tag">TOP 3 LATEST · TOP 1 ARCHIVE</span>
      <span class="hero-tag">SCORE / 10</span>
    </div>
  </div>
  <div class="hero-right">
    <div class="stat-block"><span class="n" id="statTotal">—</span><span class="l">Reports</span></div>
    <div class="stat-divider"></div>
    <div class="stat-block"><span class="n" id="statDays">—</span><span class="l">Days</span></div>
  </div>
</div>
```

---

## 三、Controls Bar 重复（新闻页）

### 问题描述
新闻页存在 **两个** `controls-bar`：

1. 第一个在 `</nav>` 之后（第 422-429 行）
2. 第二个在 `<main>` 内部（第 439-442 行）

学术页和主页均只有一个 controls-bar，位于 hero-strip 和 main 之间。

### 影响
- 视觉冗余，移动端高度占用翻倍
- 两个搜索框 ID 相同（`id="searchInput"`），导致 JavaScript 行为不可预测

### 修复方案
删除新闻页 `<main>` 内部的第二个 controls-bar，保留 hero-strip 和 main 之间的唯一一个。

---

## 四、Score Bar 实现方式不一致

### 问题描述
三页使用三种不同的分数条实现：

| 页面 | 实现方式 | 代码示例 |
|------|---------|---------|
| **主页** | 5 个 `<span class="bar">` 元素，部分 `.filled` | `<div class="score-bar"><span class="bar filled"></span>...` |
| **新闻页** | 单个 `<div class="score-bar-fill">` 宽度百分比 | `<div class="score-bar-fill mid" style="width:77%">` |
| **学术页** | **完全缺失** score-bar | 仅显示数字 |

### 影响
- 同一设计系统内出现三种进度条实现，维护成本极高
- 学术页缺少视觉化的分数暗示，信息传达效率低

### 修复方案
统一采用 **主页的 5-bar 实现**（最精细，支持动画）：

```html
<div class="score-bar">
  <span class="bar filled"></span>
  <span class="bar filled"></span>
  <span class="bar filled"></span>
  <span class="bar"></span>
  <span class="bar"></span>
</div>
```

在生成脚本中根据分数计算 filled 数量：
- 0-2: 1 bar
- 2-4: 2 bars
- 4-6: 3 bars
- 6-8: 4 bars
- 8-10: 5 bars

---

## 五、Type Tag 样式不一致

### 问题描述

| 页面 | 标签类名 | 样式 |
|------|---------|------|
| **主页** | `type-tag news` / `type-tag academic` | 有背景色、边框、专属颜色 |
| **新闻页** | `type-tag news` | 同主页 |
| **学术页** | `type-tag`（无子类） | 默认 accent 色，无专属样式 |

学术页的 `type-tag` 缺少 `.academic` 子类样式定义，虽然 CSS 中定义了 `.type-tag.academic`，但 HTML 中未使用。

### 修复方案
在学术页生成脚本中，为 type-tag 添加 `academic` 子类：

```html
<span class="type-tag academic">PAPER</span>
```

并确保 CSS 中 `.type-tag.academic` 的样式与新闻页的 `.type-tag.news` 形成对称（使用 accent 色而非 accent3）。

---

## 六、版本号不一致

### 问题描述
- 新闻页：`RENEGADE AI v5.4`
- 学术页：`RENEGADE AI v5.3`
- 主页：`RENEGADE AI v5.4`

### 修复方案
统一为 **v5.4**，并在 `generate_academic_index.py` 中更新。

---

## 七、模板架构差异

### 问题描述

| 页面 | 模板方式 | 风险 |
|------|---------|------|
| **新闻页** | 依赖外部文件 `news_template_v54.html` | 文件不存在时生成失败 |
| **学术页** | 内联模板 `get_html_template()` | 与生成逻辑耦合，无法复用 |

实际检查：`news_template_v54.html` **不存在**于项目目录中，但新闻页仍能生成，说明当前文件是之前生成的静态文件，而非最新脚本输出。

### 修复方案
**推荐统一为内联模板**：将新闻页也改为与学术页相同的内联模板模式，或反之提取共享模板。考虑到两页结构高度相似（仅 hero 文案、标签文案、filter 按钮不同），建议：

1. 创建共享模板函数，接收参数：`page_type` ('news' | 'academic'), `hero_title`, `hero_desc`, `filter_buttons`, `status_messages`
2. 两页生成脚本调用同一模板函数

---

## 八、Footer 缺失（新闻页）

### 问题描述
学术页有 `<footer>` 元素（第 504-507 行）：

```html
<footer>
  <span>Renegade AI v5.3 · Brooks Han</span>
  <a href="https://github.com/Brook-Han/renegade-ai-Updater" target="_blank">GitHub ↗</a>
</footer>
```

新闻页完全缺失 footer。

### 修复方案
在新闻页模板中添加相同 footer，更新版本号为 v5.4。

---

## 九、Status Bar 消息不对齐

### 问题描述
两页 status bar 的轮播消息不同：

- **新闻页**：包含 `RENEGADE_SEED_STATUS: GERMINATING` 等通用消息
- **学术页**：包含 `ACADEMIC_PIPELINE: NOMINAL` 等学术专属消息

虽然差异化有一定合理性，但消息格式和风格应统一。

### 修复方案
统一消息格式，或按页面类型注入 2-3 条专属消息 + 共享消息。

---

## 十、Accessibility 支持差异

### 问题描述
新闻页（继承自 v5.4 主页）包含：
- `:focus-visible` 样式
- `@media(prefers-reduced-motion:reduce)` 媒体查询
- `aria-label`, `aria-pressed` 属性

学术页（v5.3）**完全缺失**这些无障碍支持。

### 修复方案
将新闻页的 accessibility CSS 和 ARIA 属性完整移植到学术页。

---

## 十一、动画与交互细节差异

### 问题描述

| 属性 | 新闻页/主页 | 学术页 |
|------|-----------|--------|
| 卡片入场动画 | `fadeUp .4s` | `fadeUp .55s` |
| 卡片悬停阴影 | 多层 box-shadow + 边框发光 | 仅背景色变化 |
| 卡片悬停渐变 | `::before` 渐变层 | 无 |
| 链接悬停 gap 动画 | `gap: 4px → 6px` | 无 |
| 主题按钮旋转 | `transform:rotate(180deg)` | 无 |
| 滚动条样式 | 完整自定义 | 基础自定义 |

### 修复方案
统一采用新闻页/主页的 v5.4 动画系统，学术页需要补充：
- `.radar-card::before` 渐变层
- 悬停 box-shadow 多层效果
- 链接 `gap` 过渡动画
- 主题按钮旋转效果

---

## 修复优先级矩阵

| 优先级 | 问题 | 工作量 | 影响 |
|--------|------|--------|------|
| **P0** | Design Tokens 统一 | 中 | 全局视觉一致性 |
| **P0** | Hero 区域重建（新闻页） | 中 | 页面结构完整性 |
| **P0** | Controls Bar 去重 | 低 | 功能正确性 |
| **P1** | Score Bar 统一 | 中 | 组件一致性 |
| **P1** | Type Tag 子类修复 | 低 | 组件一致性 |
| **P1** | 版本号统一 | 低 | 品牌一致性 |
| **P1** | Footer 补全 | 低 | 页面完整性 |
| **P2** | 模板架构统一 | 高 | 长期维护性 |
| **P2** | Accessibility 补全 | 中 | 合规与体验 |
| **P2** | 动画系统统一 | 中 | 交互一致性 |
| **P3** | Status Bar 消息优化 | 低 | 细节打磨 |

---

## 推荐实施路径

### 阶段一：紧急修复（1-2 小时）
1. 统一 Design Tokens（复制新闻页 CSS 到学术页）
2. 修复新闻页 Hero 区域和 Controls Bar 重复
3. 统一版本号为 v5.4

### 阶段二：组件对齐（2-3 小时）
4. 统一 Score Bar 实现
5. 修复 Type Tag 子类
6. 补全 Footer 和 Accessibility

### 阶段三：架构重构（4-6 小时）
7. 提取共享模板/组件系统
8. 统一动画和交互细节
9. 建立视觉回归测试（可选）

---

## 附录：关键代码差异对照

### A. Hero 区域（新闻页 vs 学术页）

```diff
- <!-- 新闻页：缺失 hero-strip -->
- <main class="main">
-   <div class="hero-eyebrow">§ News Archive</div>
-   <h1>NEWS ARCHIVE</h1>
-   <div class="hero-desc">...</div>
-   <div class="controls-bar">...</div>  <!-- 重复！ -->

+ <!-- 学术页：正确结构 -->
+ <div class="hero-strip">
+   <div class="hero-left">
+     <div class="hero-eyebrow">§ Academic Archive</div>
+     <h1 class="hero-title">ACADEMIC<br><span>ARCHIVE</span></h1>
+     <p class="hero-desc">...</p>
+     <div class="hero-tags">...</div>
+   </div>
+   <div class="hero-right">
+     <div class="stat-block">...</div>
+   </div>
+ </div>
```

### B. Score Bar（三页对比）

```diff
  <!-- 主页 -->
  <div class="radar-score">
    7.7<span>/10</span>
    <div class="score-bar">
      <span class="bar filled"></span>
      <span class="bar filled"></span>
      <span class="bar filled"></span>
      <span class="bar filled"></span>
      <span class="bar"></span>
    </div>
  </div>

  <!-- 新闻页 -->
  <div class="radar-score">7.7<span>/10</span></div>
  <div class="score-bar"><div class="score-bar-fill mid" style="width:77%"></div></div>

  <!-- 学术页 -->
  <div class="radar-score">9.3<span>/10</span></div>
- <!-- 完全缺失 score-bar -->
```

### C. Design Tokens 差异

```diff
  :root {
-   --bg:           #08080e;   /* 学术页 */
+   --bg:           #0c0c18;   /* 新闻页/主页 */
-   --card:         #13131f;   /* 学术页 */
+   --card:         #1a1a2e;   /* 新闻页/主页 */
-   --accent:       #e8503a;   /* 学术页 */
+   --accent:       #ff5c45;   /* 新闻页/主页 */
-   --text-muted:   #6868a0;   /* 学术页 */
+   --text-muted:   #a8a8d0;   /* 新闻页/主页 */
  }
```

---

*报告生成时间：2026-06-09*  
*基于文件：docs/news/index.html, docs/academic/index.html, docs/index.html, generate_news_index.py, generate_academic_index.py*
