# 124 地方产业 Deep Research 方案调研（2026-11-14）

目标：输入一个地方 → 真深度调研 → 产出"地方产业 × 好设计"研究报告（HTML 交付，格式后定）。
约束（不可让渡）：真实检索（560 项目库）、契约校验（事实与判断分离）、诚实标注、火山方舟已有账号、可私有化部署。

## 候选方案对比

### 方案一：GPT Researcher 改造集成（assafelovic/gpt-researcher，约 28k★，Apache-2.0，Python）

- 架构：planner 拆子问题 → 并行 execution agent 抓取 → aggregator 写成带引用报告（2000+ 词），导出 Markdown/PDF/Word。
- 数据源：网页搜索（Tavily/SerpAPI 等）、**本地文档**（DOC_PATH）、**MCP**（`RETRIEVER=mcp` 或 `tavily+mcp` 混合策略）。
- 模型：OpenAI 兼容端点可配，火山方舟可用。
- 契合点：MCP 混合检索 = 网页（地方产业事实）+ 我们的 8 个只读工具（获奖项目库），正好是我们需要的混合结构；报告导出链完整。
- 风险：网页搜索需额外 API key（Tavily 等，费用与依赖）；其引用纪律与我们的契约不一致，输出必须再过我们的校验层；自带 FastAPI+NextJS 偏重，报告模板需替换。
- 结论：**适合做 1-2 天的对照原型**，验证报告质量天花板，不作为主线。

### 方案二：在 123 骨架上深化为真 Deep Research（推荐主线）

- 已有：模型起草（火山方舟）→ 真实检索（innovation_knowledge）→ 契约校验（transfer/禁写字段）→ SSE 推流 → 报告视图。
- 关键增量三件套：
  1. **联网搜索**：火山方舟 chat completions 自带 `web_search` 工具（模型可调官方搜索），无需 Tavily；地方产业事实由"模型联网搜索 + 引用源"补齐，全部标"公开资料·待核"。
  2. **planner 多子问题循环**：把单一画像调用改为 planner（拆 5-8 个研究子问题）→ 每子问题分别联网搜索+库内检索 → 汇总统稿。
  3. **证据账本**：每条引入事实带来源 URL 与检索记录（对齐 100 线 sources/claims 纪律），为后续 GDRP 化做准备。
- 优势：纪律完全内生（模型永远只起草）；与 GDRP/引擎同构；无新重依赖；SSE 演示体验无缝延续。
- 代价：planner/executor 循环自己写（约 2-3 天工作量），效果需迭代。

### 方案三：smolagents / HF Open Deep Research 改造

- CodeAgent 循环 + 搜索工具链现成，GAIA 55%；可换 LiteLLM 模型（火山方舟）与自定义 Tool（我们的项目库检索）。
- 问题：以"代码执行"为中心，与我们确定性校验哲学不合；联网工具默认 Google 系（国内不可用需替换）；改造后纪律仍需自己加。
- 结论：不如方案二贴合，不做主线。

### 方案四：火山方舟深度思考/托管 Deep Research

- 深度思考是模型思维链特性，不等于带搜索的研究代理；托管 Deep Research 应用的数据与循环在平台侧，禁写纪律嵌不进去，HTML 定制弱。
- 结论：只用其模型 API 与 web_search 工具，不用其托管形态。

## 推荐

**主线方案二（123 骨架深化），支线方案一做对照原型。** 阶段：

1. **阶段 A（联网真实调研）**：expo_agent_server 增加 web_search 工具调用，画像/需求改为"联网搜索+引用源"；保留库内真实检索与契约。
2. **阶段 B（planner 多步循环）**：子问题拆解→并行研究→综述，证据账本落 SQLite。
3. **阶段 C（报告交付）**：HTML 报告格式由用户定稿后，对接现有渲染层（可复用 GDRP 模板纪律：未知、待核、附录引用齐全）。
4. 支线：GPT Researcher pip 模式挂我们 MCP 跑一次玉环，对比报告质量与引用可靠性，反哺主线提示词。

## 参考来源

- [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher)（planner-executor、MCP 混合检索、报告导出）
- [GPT Researcher MCP 配置文档](https://docs.gptr.dev/docs/gpt-researcher/retrievers/mcp-configs)（RETRIEVER=mcp / 混合策略）
- [火山方舟深度思考文档](https://www.volcengine.com/docs/ark/deep-thinking)（模型思维链）
- [smolagents open_deep_research 复现](https://github.com/huqianghui/open_deep_research_by_smolagents)（GAIA 55%）
- [Four Open-Source Deep Research Agents, Tested Honestly](https://www.digitalapplied.com/blog/open-source-deep-research-agents-2026-guide)（2026 横向评测）
