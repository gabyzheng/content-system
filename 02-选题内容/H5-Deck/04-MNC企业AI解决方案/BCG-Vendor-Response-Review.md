# BCG Vendor Response Review — Trae Work

> Review 日期：2026-07-01
> 对照源：Trae Enterprise 官方文档（docs.trae.ai/enterprise）+ 内部安全合规资料 + 产品知识

---

## 逐条问题清单

### Q1 — 支持的模型
**当前回复**：Trae Work is model-agnostic...can provide access to ByteDance/Volcano Engine model capabilities...

**问题**：回复说"Trae Work is model-agnostic"，但从 Trae Enterprise 官方文档来看，产品层面的模型管理描述是：

> "Supports unified management of TRAE built-in models and enterprise built-in models. TRAE built-in models are provided by TRAE and are ready to use out of the box; enterprise built-in models are configured and managed by your enterprise itself." [来源：docs.trae.ai/enterprise]

官方文档的定位是"支持 TRAE 内置模型 + 企业自建模型"，不是"model-agnostic"。model-agnostic 的表述可能让 BCG 产生"可以任意接入任何模型"的预期，但实际产品层面的内置模型是 TRAE 预集成的豆包家族。

**建议**：改为 "Trae Work supports TRAE built-in models (Doubao family covering text, multimodal understanding, generation, reasoning and speech) as well as enterprise-managed custom models, configurable through the enterprise console to meet model selection and data governance requirements." 

---

### Q8 — 关键限制
**当前回复**：None. The product complies with applicable national compliance requirements.

**问题**：回复"None"过于绝对。任何产品都有局限性。结合官方文档和实际产品能力，至少应如实说明：

1. Trae Enterprise 当前支持的是 Teams Plan，企业级功能相对轻量（官方文档原文："TRAE Enterprise offers the Teams plan"）[来源：docs.trae.ai/enterprise]
2. 部分安全能力（如 CMK 客户管理密钥）官方文档已明确"尚未确认"（Q49 回复中你自己也写了"Customer-managed encryption keys have not yet been confirmed"）
3. Microsoft Purview DLP 兼容性也未确认（Q69）

如果 Q8 回复"None"但 Q49 和 Q69 又承认某些能力未确认，BCG 会发现前后矛盾。

**建议**：改为 "Key considerations include: (1) The current enterprise offering is based on the Teams plan, with certain advanced enterprise features under development; (2) customer-managed encryption key (CMK) support and Microsoft Purview DLP compatibility have not yet been confirmed for the current scope; (3) some deployment models (e.g., full on-premises) require further evaluation. The product complies with applicable national compliance requirements."

---

### Q20 — 数据本地化限制在中国大陆
**当前回复**：We have an overseas version to support overseas use.

**问题**：BCG 问的是"Can data residency be restricted to Mainland China?"，问的是**是否能限制数据仅存储在中国大陆**。你的回复"我们有海外版本支持海外使用"答非所问——这是回答"能不能在海外用"，而不是"能不能限制在中国大陆"。

从 Trae Enterprise 官方文档：

> "Enterprise data and service infrastructure are deployed and stored based on the account's geographic region. Data isolation mechanisms are implemented to support compliance with applicable local data protection and regulatory requirements." [来源：docs.trae.ai/enterprise]

官方文档明确说明数据按账户所在地理区域部署，暗示支持中国大陆区域部署。但"海外版本"的存在并不直接回答"中国大陆数据驻留"问题。

**建议**：改为 "Yes. For accounts registered in Mainland China, enterprise data and service infrastructure are deployed and stored within the region. Data isolation mechanisms are implemented to support compliance with applicable local data protection and regulatory requirements. For accounts registered in other regions, data residency follows the respective region's infrastructure."

---

### Q16 — 第三方依赖
**当前回复**：No restrictions.

**问题**：回复过于简略且不准确。BCG 问的是"What dependencies does the provider have on third-party AI models, infrastructure providers, or technology partners?"（供应商对第三方 AI 模型、基础设施提供商、技术合作伙伴有哪些依赖？）

回复"No restrictions"是回答"有没有限制条件"，而不是回答"有哪些依赖"。BCG 需要了解的是 Trae Work 依赖哪些第三方技术栈（如火山引擎云基础设施、特定模型提供商等），以便评估供应链风险。

**建议**：改为 "Trae Work is built on Volcano Engine's cloud infrastructure and natively integrates with ByteDance/Volcano Engine models (Doubao family). Enterprise customers can also configure custom models through the enterprise console. Key dependencies include Volcano Engine's IaaS/PaaS layer for compute, storage and network, and the underlying model inference services. A detailed dependency list can be provided during due diligence."

---

### Q18 — 日志和审计记录的保留
**当前回复**：Records relating to prompts, outputs, model interactions, operational logs and audit trails are retained only on the Trae Work side.

**问题**：回复只说了"日志保留在 Trae Work 侧"，但没有回答 BCG 问题中的三个核心点：(1) 保留什么？(2) 保留多久？(3) BCG 能否控制或修改保留期？

从 Trae Enterprise 官方文档：企业管理员可以查询管理员操作日志（"Supports querying administrator operation logs to facilitate internal audits and issue tracing"），但文档中未明确说明用户级别的 prompt/output 日志保留期。

**建议**：补充保留期和 BCG 控制权信息。如果当前无法给出具体保留期，应如实说明："Retention periods for prompts, outputs, model interactions, operational logs and audit trails should be confirmed for the selected deployment. Enterprise administrators can query admin operation logs through the console. BCG's ability to control or modify retention periods should be documented in the data processing terms."

---

### Q55 — 安全认证
**当前回复**：Independent certifications, assessments, audits or attestations depend on the selected entity, region and deployment stack. For overseas enterprise offerings, SOC 2-related materials may be available...

**问题**：回复中"may be available"语气太弱，且未区分 Trae Work 和底层火山引擎基础设施。BCG 这类咨询公司的尽职调查通常需要**具体可验证的认证**。如果你知道火山引擎已获得的认证（如 ISO 27001、SOC 2、等保等），应明确列出，并区分"平台层认证"和"应用层认证"。

从内部资料（亿滋安全合规调研）可知火山引擎有完整的合规认证体系。应该把这个信息用上。

**建议**：区分两层回答：
- 基础设施层（火山引擎云）：列出已有认证（ISO 27001、SOC 2、等保三级等——需要你确认具体有哪些）
- 应用层（Trae Work）：说明当前认证状态和路线图

---

### Q48 — 项目间数据隔离
**当前回复**：Yes. Data can be segregated between projects or cases through workspace/project-level permissions, knowledge base separation, connector scoping and administrative policies.

**问题**：回复正确，但可以更强。Trae Enterprise 官方文档明确支持"Enterprise document sets"（企业文档集）和"Enterprise agents"（企业级 Agent），这些是天然的项目级隔离机制。可以引用官方文档作为支撑。

**建议**：补充引用："Yes. Data segregation between projects is supported through workspace/project-level permissions, enterprise document sets, knowledge base separation, connector scoping and administrative policies. BCG can define project boundaries and user groups during onboarding." [来源：docs.trae.ai/enterprise]

---

### Q69 — Microsoft Purview DLP 兼容性
**当前回复**：Microsoft Purview DLP compatibility has not yet been confirmed for the proposed scope...

**问题**：回复本身没有大问题（诚实承认未确认），但可以补充说明 Trae Work 自身的内置数据保护能力作为替代方案，避免 BCG 认为"完全没有 DLP 能力"。

Trae Enterprise 官方文档提到：
> "Supports protecting code assets by prohibiting AI from accessing code repositories that contain sensitive information, core algorithms, or non-open-source projects." [来源：docs.trae.ai/enterprise]

虽然这是代码层面的访问控制而非通用 DLP，但至少说明产品有数据保护意识。

**建议**：在现有回复后补充："While Microsoft Purview DLP compatibility is under evaluation, Trae Work provides built-in data protection mechanisms including: content security policies, permission-based access control, project-level data segregation, and audit logging. These can be assessed against BCG's DLP requirements during technical validation."

---

## 其他观察（非问题，建议关注）

### 回复风格一致性
整体回复风格偏"法律/合规话术"，很多地方用了"should be confirmed during due diligence"、"depends on"、"can be discussed"等模糊措辞。这在 BCG 的 vendor assessment 中可能被认为是"回避问题"。建议：
- 凡是能给出确定回答的，给出确定回答
- 凡是确实需要部署确认的，明确说明"什么条件下可以确定"
- 避免通篇"should be discussed contractually"——BCG 知道这些需要合同约定，他们问的是**你的立场是什么**

### 关键缺失
- 没有提到 Trae Work 与 Trae IDE/Trae Plugin 的关系（BCG 采购的是 Trae Work 还是 Trae Enterprise？这会影响后续安全评估范围）
- 没有明确 Trae Work 的部署架构是 SaaS only 还是支持 hybrid
- 没有提及数据加密的具体标准（AES-256? TLS 1.3?）

---

## 总结

| 问题编号 | 严重程度 | 问题类型 |
|---------|---------|---------|
| Q20 | 🔴 高 | **答非所问** — 问数据驻留，回答海外版本 |
| Q16 | 🔴 高 | **理解偏差** — 问依赖关系，回答限制条件 |
| Q8 | 🟡 中 | **前后矛盾** — Q8 说无限制，Q49/Q69 承认有限制 |
| Q1 | 🟡 中 | **措辞不精确** — "model-agnostic"与实际产品定位不符 |
| Q18 | 🟡 中 | **不完整** — 缺少保留期和控制权 |
| Q55 | 🟡 中 | **语气太弱** — 应区分平台层/应用层认证 |
| Q48 | 🟢 低 | **可增强** — 补充官方文档引用 |
| Q69 | 🟢 低 | **可增强** — 补充内置替代方案 |
