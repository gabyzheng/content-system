# AI PPT JSON 工作流 — 深度指南

> 源文档：[Aime 邪修：无需设计师，高复杂度 PPT 生成自由](https://bytedance.larkoffice.com/wiki/HEqQwV3UTiawvCkPuT1cdOqjnmf)
>
> 本文档是你未来做 PPT 时的操作手册。每次做新 PPT 时按这个流程走。

---

## 一、协作原则

### 1.0 互动规则

1. **信息缺失时主动追问** — 你不说清楚客户是谁、受众是谁，我不会硬编。我会直接问。
2. **你犹豫时我提供建议** — 你对叙事顺序、页数、版式不确定？我会给出具体方案和理由，你来决策。
3. **不替你决策，但帮你缩小决策空间** — 永远给你选项 + 我的推荐 + 理由，最终拍板是你。
4. **每一步都等你确认再进入下一步** — 不跳过，不假设你同意。

### 1.1 分工哲学

| 你负责 | AI 负责 |
|--------|---------|
| 判断、洞察、结构、表达 | 版式、插图、视觉层级 |
| 对客户/受众的深度理解 | 将设计意图翻译为可渲染的 JSON |
| 内容质量与逻辑自洽 | 风格一致性、视觉专业性 |
| 最终决策与微调 | 批量产出、快速迭代 |

**一句话：你管内容对不对，AI 管好不好看。**

### 1.2 JSON 的本质

> JSON 不是技术格式。JSON 是"设计意图的结构化表达"。

理解这个认知转变非常重要。你写的 JSON 不是在"编程"，而是在用结构化语言描述一页 PPT 应该长什么样——它包含什么信息、视觉焦点在哪、文字怎么排、用什么图、避免什么。**JSON 写得越细，图片模型出图越稳。**

### 1.3 为什么不用 HTML/SVG 方案

HTML/SVG 生成的 PPT 千篇一律、可视化效果差、审美疲劳严重。图片模型（nano banana / gpt2）生成的视觉效果远优于模板化方案。

---

## 二、两类 JSON 的分工

| | 总览 JSON | 逐页 JSON |
|---|---|---|
| **用途** | 快速生成总图，通篇预览全 deck | 喂给图片模型逐页生成高清 PPT |
| **颗粒度** | 页面级：title + core_message | 元素级：layout + elements + illustration_prompt |
| **时机** | 拆页完成后立即输出 | 总览确认叙事逻辑后逐页输出 |
| **产出** | 一张全览图，可快速判断结构 | 每页一张 4K 高清图 |
| **修改成本** | 低，改结构只需改 JSON | 高，改内容需重新出图 |

**流程：总览 JSON → 你审 → 调整 → 确认 → 逐页 JSON → 你喂 gpt2 → 逐页出图**

---

## 三、完整四步工作流

### 第 1 步：打透观点（最重要的一步）

**不做这一步，后面全是浪费。**

这一步的目标不是"让 AI 写内容"，而是**借 AI 逼自己把观点压实**。你和 AI 来回交互，逐步形成有价值的原始内容和故事线。

核心问题清单：
1. 这次沟通对象是谁？角色、层级、决策权？
2. 他们最关心什么？不关心什么？（不是所有信息都要放进去）
3. 这套 PPT 的主结论是什么？（一句话能说清楚）
4. 哪些观点必须讲？哪些可以删？（删比加更难，但更重要）
5. 最合理的叙事顺序？（不是信息罗列，是说服路径）
6. 有哪些输入材料？（会议纪要、客户关注点、行业最佳实践、竞品分析）

#### 起手 Prompt（直接复制使用）

```
你不要先做 PPT。
先作为有业务理解和技术判断的咨询顾问，结合我给到的输入，和我一起把这次沟通打透。

背景：
- 客户/受众：[填写]
- 沟通对象角色：[填写]
- 当前核心问题：[填写]
- 我希望推动的方向：[填写]
- 我已有观点：[填写]

请你输出：
1. 本次沟通最核心的一句话结论
2. 受众最可能关心的 5 个问题（按优先级排序）
3. 本方案最容易讲偏的 3 个坑
4. 最合理的叙事顺序（从什么开始，到哪结束，中间的逻辑链条）
5. 应该拆成几页，每页承担什么叙事任务

要求：
- 不空泛，不讲废话
- 站在沟通视角，不是知识罗列视角
- 结论先行
- 每页只能有一个核心判断
```

#### 这一步的判断标准

- ✅ 你能清晰说出这套 PPT 的"一句话结论"
- ✅ 你知道哪些内容要删、哪些要保留
- ✅ 你对叙事顺序有明确的逻辑判断
- ❌ 感觉"内容都挺好，都放进去吧" → 没打透，继续讨论

---

### 第 2 步：拆页设计（内容结构 → 页面结构）

这一步的关键是**每页只承载一个核心判断**。一页塞太多 = 像思维导图不像 PPT。

不要直接让 AI 堆文案。先让它做**页面级设计说明**——这一页讲什么、不讲什么、用什么视觉手段。

#### 拆页 Prompt

```
基于刚才确定的叙事，请拆成 [N] 页。

每一页输出：
- page_id：P01, P02, ...
- 页面标题：对客展示的标题
- 唯一核心结论：这一页只讲这一个判断
- 受众关心什么：这一页对受众的价值是什么
- 适合的版式结构：左文右图 / 上标题中图示 / 三列卡片 / 时间线 / ...
- 适合的图示类型：信息图 / 话题图谱 / 对比表 / 流程图 / 数据图 / ...
- 文案层级规划：主标题(≤15字) / 副标题(≤30字) / 要点(≤3条,每条≤25字) / 注释
- 这一页最应避免的错误：空泛、术语堆砌、无视觉焦点、大段文字等

要求：
- 每页只能有一个核心判断
- 不要堆大段文字
- 蓝色简约咨询风格
- 16:9 比例
```

#### 拆页质量检查

- ✅ 每页核心判断互不重叠
- ✅ 页面之间有清晰的叙事推进
- ✅ 版式选择服务于内容（不是随便套模板）
- ❌ 两页讲同一个东西 → 合并或删一页
- ❌ 一页塞了 3 个以上判断 → 拆分

---

### 第 3 步：输出 JSON（核心产出）

#### 3.1 总览 JSON

拆页确认后立刻输出。用于快速生成全览图，检查整体结构。

**结构模板：**

```json
{
  "deck_name": "方案标题",
  "theme": "blue_minimal_consulting",
  "aspect_ratio": "16:9",
  "resolution": "3840x2160",
  "slides": [
    {
      "page_id": "P01",
      "title": "页面标题",
      "core_message": "一页一个核心判断，一句话说清楚"
    }
  ]
}
```

**用途：** 拿这个 JSON 生成一张总览图 → 看全篇叙事逻辑 → 调整 page 顺序 / 增删页面 → 确认后进入逐页 JSON。

#### 3.2 逐页 JSON

总览确认后，逐页输出精细 JSON。**这是喂给 gpt2 的最终格式。**

**完整结构模板：**

```json
{
  "page_id": "P03",
  "title": "页面标题（≤15字）",
  "subtitle": "副标题（≤30字，可选）",
  "core_message": "核心信息，一句话。这决定了整页的视觉焦点和叙事方向。",
  "layout": {
    "type": "left_text_right_map",
    "visual_focus": "right_topic_map",
    "density": "medium",
    "whitespace": "generous"
  },
  "elements": [
    {
      "type": "headline_block",
      "position": "top_left",
      "content": {
        "title": "主标题",
        "subtitle": "副标题"
      }
    },
    {
      "type": "three_point_argument",
      "position": "left_center",
      "content": [
        "论点 1（≤25字）",
        "论点 2（≤25字）",
        "论点 3（≤25字）"
      ]
    },
    {
      "type": "topic_map",
      "position": "right_large",
      "content": {
        "center": "中心概念",
        "branches": ["分支1", "分支2", "分支3", "分支4", "分支5"]
      }
    },
    {
      "type": "bottom_note",
      "position": "bottom_full",
      "content": "底部结论或注释（≤50字）"
    }
  ],
  "illustration_prompt": "英文插图提示词，用英文写，描述视觉风格和图示内容",
  "style_rules": {
    "tone": "calm_executive",
    "avoid": ["too much glow", "cyberpunk feeling", "long paragraphs", "crowded labels"]
  }
}
```

#### 3.3 逐页 JSON 的质量标准

JSON 里必须回答这些问题（否则就是写得太泛）：

| 维度 | 检查项 | 不合格示例 | 合格示例 |
|------|--------|-----------|---------|
| **内容** | 这一页讲什么、不讲什么 | 堆了 5 个观点 | 1 个核心判断 + 支撑点 |
| **视觉** | 视觉中心是什么 | 没有 visual_focus | `"visual_focus": "right_topic_map"` |
| **层级** | 文字层级清晰吗 | 全是 body text | 标题→副标题→要点→注释 |
| **图示** | 图在服务什么观点 | 纯装饰图 | 话题图谱服务于"用户问题空间"概念 |
| **审美** | 避免什么错误 | 没写 | `"avoid": ["long paragraphs", "crowded labels"]` |

#### 3.4 常用版式类型

```
left_text_right_map        — 左文右图（论证+图示）
left_text_right_chart      — 左文右数据图
top_title_center_visual    — 上标题 + 居中大图
three_column_cards         — 三列卡片（并列关系）
two_column_compare         — 双列对比（对比关系）
timeline_horizontal        — 横向时间线（过程/路径）
full_bleed_visual          — 全幅视觉（冲击力）
quote_centered             — 居中引用（金句页）
title_only                 — 纯标题（章节过渡页）
grid_icons                 — 图标网格（能力/特性展示）
```

#### 3.5 常用元素类型

```
headline_block       — 标题区（title + subtitle）
three_point_argument — 三点并列论证
topic_map            — 话题/概念图谱（中心辐射）
comparison_table     — 对比表（A vs B）
icon_grid            — 图标+文字网格
data_chart           — 数据图表（柱/折/饼）
flow_diagram         — 流程图（步骤/阶段）
quote_block          — 引用块
bottom_note          — 底部结论/注释
callout_card         — 高亮卡片（重点信息）
stat_big_number      — 大字数据展示
image_with_caption   — 配图+说明
```

---

### 第 4 步：JSON → gpt2 → 逐页出图

你拿到逐页 JSON 后，逐页喂给 gpt2（或其他图片模型），生成高清 PNG。

**注意事项：**
- 每页独立生成，保证高清
- 同一套 deck 保持 style_rules 一致
- 出图后如有内容调整，只改那页 JSON 重新生成
- illustration_prompt 用英文写，模型对英文理解更好

---

## 四、生成 JSON 的统一 Prompt

```
现在把第 [1-N] 页输出为可直接给图片模型使用的 JSON。

要求：
- 整体风格：蓝色简约、专业咨询风、16:9、4K 输出
- 避免大段文字堆积
- 每页有明确视觉中心
- 版式要有留白，不能像 Word
- 插图要服务观点，不是装饰
- 每页要包含：
  - page_id, title, subtitle, core_message
  - layout（type, visual_focus, density, whitespace）
  - elements（每个元素写清 type, position, content, 字数控制）
  - illustration_prompt（英文）
  - style_rules（tone, avoid）
- 不要出现不适合直接对客展示的内部口吻
```

---

## 五、真实案例参考（GEO 方案）

### 总览 JSON 示例

```json
{
  "deck_name": "某消费行业 GEO 体系化建设咨询方案",
  "theme": "blue_minimal_consulting",
  "aspect_ratio": "16:9",
  "resolution": "3840x2160",
  "slides": [
    { "page_id": "P01", "title": "从工具试用走向体系建设", "core_message": "GEO 不应被理解为单一工具采购，而应被定义为品牌在对话式入口中的新经营能力。" },
    { "page_id": "P02", "title": "为什么现在必须做 GEO", "core_message": "用户搜索行为正在向问答、推荐、生成式对话迁移，品牌入口正在被重构。" },
    { "page_id": "P03", "title": "GEO 不只是品牌词优化", "core_message": "大量对话行为围绕节日、材料、搭配、场景、礼赠、风格等非品牌词展开。" },
    { "page_id": "P04", "title": "数字消费者与热词嗅探如何形成闭环", "core_message": "一端生成潜在话题，一端验证真实热度，帮助企业更快进入高价值问题空间。" },
    { "page_id": "P05", "title": "工具只是底座，不是全部答案", "core_message": "真正有效的 GEO 建设必须同时覆盖内容、知识、实验、组织、反馈与运营机制。" },
    { "page_id": "P06", "title": "伙伴在体系中的角色", "core_message": "伙伴不应只提供工具，而要参与方法、数据、实验与运营协同。" },
    { "page_id": "P07", "title": "建议的合作路径", "core_message": "先做诊断与优先级判断，再做试点闭环，最后形成可复制的 GEO 运营体系。" },
    { "page_id": "P08", "title": "合作后的预期展望", "core_message": "目标不是多一个工具，而是让品牌逐步具备持续占领对话入口的能力。" }
  ]
}
```

### 逐页 JSON 示例（P03）

```json
{
  "page_id": "P03",
  "title": "GEO 不只是品牌词优化",
  "subtitle": "品牌真正需要经营的是用户问题空间，而不仅是品牌名称本身",
  "core_message": "消费者在生成式对话中提出的问题，往往先于品牌发生；谁先进入问题空间，谁更可能进入决策空间。",
  "layout": {
    "type": "left_text_right_map",
    "visual_focus": "right_topic_map",
    "density": "medium",
    "whitespace": "generous"
  },
  "elements": [
    {
      "type": "headline_block",
      "position": "top_left",
      "content": {
        "title": "很多高价值流量，起点根本不是品牌词",
        "subtitle": "而是节日、礼赠、材质、搭配、年龄段、使用场景、风格偏好等真实问题"
      }
    },
    {
      "type": "three_point_argument",
      "position": "left_center",
      "content": [
        "对话式搜索首先承接的是意图，不是品牌忠诚。",
        "用户在表达需求时，往往使用场景语言，而不是商品语言。",
        "品牌若只优化品牌词，容易错失大规模前置需求入口。"
      ]
    },
    {
      "type": "topic_map",
      "position": "right_large",
      "content": {
        "center": "消费者问题空间",
        "branches": ["节日送礼", "宝石材质", "搭配建议", "纪念日场景", "预算区间", "风格偏好", "年龄阶段", "情绪表达"]
      }
    },
    {
      "type": "bottom_note",
      "position": "bottom_full",
      "content": "GEO 体系建设不能只交给 SEO 或投放思路处理，而需要内容、商品、品牌、数据和 AI 方法协同。"
    }
  ],
  "illustration_prompt": "professional blue consulting infographic, clean topic map radiating from center, luxury consumer intent themes, minimal icons, soft depth, strong whitespace, executive presentation quality, 16:9, 4k",
  "style_rules": {
    "tone": "calm_executive",
    "avoid": ["too much glow", "cyberpunk feeling", "long paragraphs", "crowded labels"]
  }
}
```

---

## 六、常见翻车及预防

| 翻车表现 | 根因 | 预防措施 |
|----------|------|---------|
| 好看但内容空洞 | 跳过第 1 步，直接做 PPT | 第 1 步不打透，绝不下笔 |
| 像思维导图不像 PPT | 没拆页，一页塞太多 | 每页一个核心判断 |
| 视觉效果差 | JSON 只写"蓝色科技风" | elements 写清位置、内容、字数；illustration_prompt 用英文写具体 |
| 生成结果千篇一律 | 用 HTML/SVG 模板方案 | 坚持用图片模型 |
| 改一页全盘重来 | JSON 和图片耦合在一起 | 逐页独立 JSON + 逐页独立出图 |
| 内部口吻暴露给客户 | JSON 里写了"给客户看"之类 | 所有 content 字段写对客语言 |

---

## 七、风格固化与复用

当你形成自己稳定的风格后，将以下内容固化为 Few-shot 参考：

1. **总览 JSON 模板**（deck 级别的固定结构）
2. **逐页 JSON 模板**（页面级别的固定结构）
3. **常用版式对应的 elements 配置**（如"左文右图"的标准 element 组合）
4. **style_rules 常量**（tone、color palette、avoid 清单）
5. **illustration_prompt 前缀**（固定的风格描述前缀）

这样每次做新 PPT 时，只需改内容字段，结构不变，大幅提速。

---

## 八、Mira GPT Image 2 配图模式（新增）

### 8.1 适用场景

逐页 JSON 生成后，通过 Mira API 调用 GPT Image 2 严格按 JSON 的 `illustration_prompt` 逐页生成配图。

### 8.2 技术参数

| 项目 | 值 |
|------|-----|
| API 端点 | `https://mira.bytedance.com/mira/api/v1/chat/completion` |
| 认证方式 | `mira_session` cookie（从浏览器 DevTools → Console → `document.cookie` 获取） |
| 模型参数 | `summaryAgent: "gpt-image-2"` |
| 输出分辨率 | 1672×941（16:9，固定值，不可调） |
| 单张成本 | ~$0.013 |
| 生成速度 | ~60s/张 |
| 建议间隔 | 30s 以上，避免限流 |

### 8.3 调用流程

```
1. 创建 Session
   POST /mira/api/v1/chat/create
   → 获取 sessionId

2. 发送生图请求
   POST /mira/api/v1/chat/completion
   Body: {
     "sessionId": "...",
     "content": "{illustration_prompt 原文}",
     "messageType": 1,
     "summaryAgent": "gpt-image-2",
     "dataSources": ["manus"],
     "comprehensive": 1,
     "config": {"online": false, "mode": "quick", "tool_list": []}
   }
   → SSE 流式返回，从 result 字段提取图片 URL

3. 下载图片
   GET {图片URL}（需带 mira_session cookie）
   → 保存为 JPEG
```

### 8.4 与 Seedream 5.0 的对比

| 维度 | Mira GPT Image 2 | Seedream 5.0 |
|------|-----------------|--------------|
| 分辨率 | 1672×941 | 2848×1600 (2K) |
| 调用方式 | Mira API (cookie) | ARK API (API Key) |
| 成本 | Mira 额度 | ARK 额度 |
| 风格控制 | 英文 prompt 效果好 | 中英文均可 |
| 适用场景 | PPT 单页配图（supporting visual） | 需要更高分辨率的场景 |

### 8.5 批量生成脚本模板

```python
# 核心逻辑：逐页读取 JSON → 提取 illustration_prompt → 调 Mira API → 下载
# 每页间隔 30s，支持断点续跑（已存在的文件跳过）
# 完整脚本参考：阿迪达斯选题实际执行记录
```

### 8.6 图片品质与模板选择

Mira 图片走字节 ImageX 服务，URL 中的 `~tplv-{template}` 后缀决定图片处理方式。

| 模板后缀 | 文件大小 (16:9) | 说明 |
|----------|:---:|------|
| `~tplv-xobrcjvdq7-image-jpeg.jpeg` | ~82KB | 默认压缩版，带水印 |
| `~tplv-xobrcjvdq7-image.image` | ~332KB | **高品质版（推荐）**，4x 体积 |

**规则：始终使用 `~tplv-xobrcjvdq7-image.image` 模板。** 下载时把 URL 中的模板后缀替换即可。

```bash
# 从 SSE 拿到原始 URL 后，替换模板后缀再下载
HQ_URL=$(echo "$ORIG_URL" | sed 's/~tplv-[^?]*/~tplv-xobrcjvdq7-image.image/')
curl -H "Cookie: $COOKIE" "$HQ_URL" -o output.jpeg
```

关于水印：水印是 ImageX 模板在服务端渲染时叠加的，无法通过 API 参数去除。下载按钮的 `&filename=...&download=1` 参数仅触发浏览器下载行为（Content-Disposition header），不改变图片内容。

### 8.7 超时与防重复生成

**核心原则：每次生图请求必须设置超时，超时后不得自动重试。**

```python
# 生图请求超时设置
TIMEOUT = 120  # 秒，GPT Image 2 通常 20-90s 完成

# 超时后的处理逻辑：
# 1. 不要自动重试 — 可能图片已在生成中，重试会导致重复
# 2. 检查 SSE 响应是否已返回部分数据
# 3. 如果确实无响应，收集超时页面列表
```

**超时报告机制：**
- 批量生成完成后，汇总所有超时/失败的页面
- 向主人报告：「以下 N 页超时/失败：P03, P07, P12...」
- 由主人决定是否重新生成这些页面
- 主人发起重试时，脚本只跑指定的失败页面（断点续跑）

防重复机制：
- 每页生成前检查目标文件是否已存在且 > 1KB（80 字节 = 失败下载）
- 已存在的有效文件自动跳过（断点续跑）
- 单次请求超时后不自动重试，需人工确认

### 8.8 文件命名规则

**命名格式：`P{page_id}-{title}.jpeg`**

- `page_id`：两位数字，如 `01`, `02`, `03`
- `title`：从对应 JSON 的 `title` 字段提取，空格替换为 `-`，特殊字符（`·`、`：`、`/` 等）保留
- 示例：`P01-知识引擎-·-驱动品牌知识智能化.jpeg`

```python
# 从 JSON 提取 page_id 和 title 生成文件名
def get_filename(json_path):
    with open(json_path) as f:
        data = json.load(f)
    page_id = str(data['page_id']).zfill(2)  # "1" → "01"
    title = data['title'].replace(' ', '-')   # 空格 → 连字符
    return f"P{page_id}-{title}.jpeg"
```

产出路径：
1. 生成时保存到 `05-配图/mira-gpt-image2/`
2. 确认后复制到 `07-已发布/` 供主人检查

### 8.9 注意事项

- cookie 有效期有限，过期需重新从浏览器获取
- GPT Image 2 不支持指定分辨率，1672×941 是固定输出
- 图片 URL 含签名，有时效性，需及时下载
- 批量生成建议分批次跑（每批 10-12 页），避免 OOM
- 产出目录：`05-配图/mira-gpt-image2/`
- 确认后复制到 `07-已发布/` 供最终使用
- **始终使用 `image.image` 模板，不要用默认的 `image-jpeg.jpeg`**

---

## 九、总结

这套方法的本质是**把脑力花在刀刃上**：
- 你的时间 → 判断、洞察、结构、表达
- AI 的时间 → 版式、插图、视觉层级、批量产出

**AI 是放大器。你观点浅，它把空话包装得更像样；你结构乱，它把混乱排得更精致。但如果你真的理解得深，AI 会把你从低价值美工劳动中解放出来。**
