# 基于 ArkClaw 的智能审批方案

> 类型：PPT | 状态：已深化 | 日期：2026-06-08

## 选题背景

以来伊份 BPM 审批场景为蓝本，设计基于 ArkClaw 的智能审批系统。核心思路：用 ArkClaw 作为审批助手的"大脑"，连接飞书电子表格（规则管理）、BPM 系统（流程引擎）、OCR 能力（附件解析），实现从规则配置到单据审核的全链路智能化。

## 核心内容

### 设计文档
- `01-打透观点/智能审批系统-用户体验流与信息处理流-设计文档.md` — 完整设计（v1.1）

### PPT 输出（在线预览 · 支持 ← → 键盘切换）
- [📺 Deck 播放模式](https://gabyzheng.github.io/content-system/02-%E9%80%89%E9%A2%98%E5%86%85%E5%AE%B9/PPT/02-%E5%9F%BA%E4%BA%8EArkClaw%E7%9A%84%E5%AE%A1%E6%A0%B8%E6%96%B9%E6%A1%88/07-%E5%B7%B2%E5%8F%91%E5%B8%83/index.html) — 左右键切换页面，底部导航栏
- [P01 · 用户体验流](https://gabyzheng.github.io/content-system/02-%E9%80%89%E9%A2%98%E5%86%85%E5%AE%B9/PPT/02-%E5%9F%BA%E4%BA%8EArkClaw%E7%9A%84%E5%AE%A1%E6%A0%B8%E6%96%B9%E6%A1%88/07-%E5%B7%B2%E5%8F%91%E5%B8%83/P01_%E7%94%A8%E6%88%B7%E4%BD%93%E9%AA%8C%E6%B5%81.html) — 用户视角：规则管理 + 单据审核
- [P02 · 信息处理流](https://gabyzheng.github.io/content-system/02-%E9%80%89%E9%A2%98%E5%86%85%E5%AE%B9/PPT/02-%E5%9F%BA%E4%BA%8EArkClaw%E7%9A%84%E5%AE%A1%E6%A0%B8%E6%96%B9%E6%A1%88/07-%E5%B7%B2%E5%8F%91%E5%B8%83/P02_%E4%BF%A1%E6%81%AF%E5%A4%84%E7%90%86%E6%B5%81.html) — ArkClaw 后台：配置→校验→OCR→AI→推送→回调

## 关键设计

- **规则存储**：飞书电子表格（Sheet1 总览 JSON + Sheet2~N 按流程命名）
- **规则分类**：表单校验 / 附件校验 / 交叉校验
- **规则状态**：有效 / 失效 / 待验证（默认）
- **执行动作**：人工复核 / 驳回
- **审核流程**：每 30 分钟拉取 → OCR → 规则匹配 → AI 建议 → 飞书卡片 → 用户操作
- **异常覆盖**：规则管理 9 种 + 单据审核 17 种

## 相关项目

- 来伊份 BPM 项目：`projects/laiyifen-bpm/`
