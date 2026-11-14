---
title: GoodDesign 多 Agent 共享背景页
version: 2026-11-12
audience: agents, developers, product collaborators
production_release: 20261112-115
local_focus: application-center, agent-access, reasoning-canvas, research-engine
---

# GoodDesign 多 Agent 共享背景页

这份页面给后续 Agent、开发者、产品和研究协作者使用。它不是营销介绍，而是当前项目的工作背景、系统边界、接入规则和下一步约定。

## 1. 项目一句话

好设计平台以真实获奖项目档案为核心，把项目证据、设计方法、研究流程和真实应用连接起来，让公众能理解好设计，让企业能把真实经验转成可研究、可验证的创新任务。

核心原则：

1. 应用可以很多，事实只能一份。
2. 能力可以扩展，权限必须逐级打开。
3. Agent 可以参与研究和开发，但不能虚构状态、证据、专家审核或工程验证。
4. 研究可以暂时不推荐，`recommendations=[]` 是合法结果。

## 2. 当前生产与本地状态

- 用户当前指定真实环境：`https://haoshejiguan.com/`；项目区为 `/inno/`。仓库 nginx 配置将根路径服务为好设计馆，并复用项目区路由。
- 115部署验收记录的目标是 `https://opendesign.cc/inno/canvas/`，release `20261112-115`；不同域名是否同版需逐路由核实，不由首页200推断。
- 应用中心控制台与应用注册规范已随 112 上线；线上 registry 是否公开仍由 111 线决定。
- 推理画布本地 113/114 已完成状态、角色与报告；115 已部署为受保护试点 `/inno/canvas/`，登录后浏览器走招待完成。
- 服务器发布前仍需先处理根分区空间；不要直接覆盖生产 release。
- 当前工作区存在多个并行会话改动，提交时只添加本会话明确文件，禁止 `git add -A`。

## 3. 应用中心的正确推理顺序

讨论应用中心时按这个顺序，不要直接跳到页面或 SDK：

### 第一步：定义任务

应用中心不是导航页。它要帮助用户或 Agent 按真实任务进入正确应用，并理解这个应用能形成什么、依据是什么、边界是什么。

### 第二步：区分使用者

- 公众与教师：阅读、看展、学习。
- 企业与研究人员：定义问题、组织证据、推进验证。
- 开发者与 Agent：读取能力、项目、方法、证据和输出契约。
- 政府与园区：把区域产业问题转成可研究任务。

### 第三步：定义什么才算应用

一个应用不是一条路由。它必须同时具备：

1. 稳定身份与状态。
2. 面向人群和任务。
3. 输入与输出。
4. 可调用的项目、方法、MCP 或引擎能力。
5. 真实案例与证据边界。
6. 权限与发布门禁。

### 第四步：定义共享底座

项目库、方法库、研究版本和 GDRP 输出是所有应用共享的底座。应用不得复制第二套事实，也不得把本地整理内容写成源事实。

### 第五步：定义 Agent 接入

Agent 不先读代码，也不先安装 SDK。正确顺序是：

1. 读取应用注册表。
2. 读取目标应用 Manifest。
3. 调用 `inno_capabilities`。
4. 通过只读 MCP 检索项目、方法和证据。
5. 在当前客户端保存研究过程。
6. 按 GDRP Schema 校验研究包。
7. 提交独立评审；未获真实确认不得升格状态。

### 第六步：最后才决定 SDK

SDK 是稳定接口的封装，不是规范本身。先做 Agent App Kit：Manifest、应用 Skill、MCP 示例、GDRP Schema 与最小脚手架。接口稳定后再封装 Python / TypeScript SDK。

## 4. 应用注册契约

当前本地已把六个应用升级为 `gd-app-0.1` Manifest：

- 好设计馆：内容体验应用。
- 科技教育：学习应用。
- 需求研究：研究入口。
- 企业创新工作台：研究工作台试点。
- Agent 与 MCP 接入：开发者连接器。
- 区域产业赋能：区域应用规划。

每个应用都必须声明：

- `id / title / kind / category / status`
- `audience / task / summary`
- `route.catalog / route.detail / route.runtime`
- `inputs / outputs`
- `capabilities.mcp_tools / capabilities.engine / capabilities.writes`
- `permissions.public_read / requires_login / tenant_isolation / mcp_access`
- `evidence.case_ids / must_show_boundary / forbidden_claims`
- `release.requires`

状态只允许：`planned / pilot / live / deprecated`。

关键文件：

- `extensions/application-center/apps.json`
- `extensions/application-center/application.schema.json`
- `scripts/build_application_registry.py`
- 本地构建输出：`output/inno-preview/gooddesign-site/inno/apps/registry.json`

## 5. MCP 与 Agent 边界

当前 MCP 是远程只读知识与证据入口。它提供项目、方法、证据和研究上下文组装能力，但不提供：

- 源档案写入。
- 远程研究历史保存。
- 模型自动调用。
- 工程验证或专家审核。

Agent 和 Host 不得写入或伪造以下状态：

- `approved`
- `confirmed`
- `customer_confirmed`
- `engineering_validated`
- `expert_reviewed`
- `recommendations`
- `public`
- `training_authorized`

## 6. 引擎与输出标准

### GD-CRE 引擎

`specs/098` 定义创新研究引擎 V1；`specs/108` 已实现确定性骨架 GD-CRE-0.1。

引擎输出包括：

- ProblemBrief
- FunctionModel
- CaseRetrieval
- TransferMap
- ConceptSet
- ComparisonRecord
- ValidationPlan
- ResearchRun

当前 `model_assisted` 不开放；割胶基线是 15 需求、7 功能、28 选项、4 组合、60 个未知判断、`recommendations=[]`。

### GDRP 研究包

`specs/099` 定义研究输出物标准。每次研究任务应交付：

```text
research-pack.json
report.html
report.md
manifest.json
```

HTML、Markdown、图示和汇报页必须由同一个 `research-pack.json` 生成，不能各自维护不同事实。

## 7. 推理画布

推理画布是企业创新工作台的人侧交互层，不是自动化流水线。

它的节奏是：

```text
发问 → 查证 → 拆问题 → 发散 → 质疑 → 取舍 → 立约
```

原则：

- 节点是人的思考动作，不是机器任务。
- AI 只在节点内有角色，节点之间由人驱动。
- 被毙掉的方向保留痕迹。
- 改主意是一等公民，重开节点会让下游待复核。
- 每条路线必须写验证方法和放弃条件。
- 审计对象是人的判断依据，不是机器运行日志。

## 8. 应用中心视觉当前版本

应用中心本地 109 版采用三栏桌面控制台：

- 左侧：场景、状态与共享底座。
- 中间：应用产品卡。
- 右侧：固定应用详情。

规则：

- 页面与公共导航内容宽可扩展至 1680px。
- 2000px 屏幕不允许出现大面积无意义空白。
- 产品卡使用低饱和色调、细边框、标题层级、摘要和交付物标签。
- 不使用大渐变地图、浅色圆点、通栏顶部色线、全宽胶囊假按钮或伪造产品截图。
- 移动端降为场景横滑、搜索、状态和应用卡横滑。

## 9. 当前协作红线

- 不公开密钥、私有原件、内部会议或未确认推荐书。
- 不把 AI 解读写成事实。
- 不把研究整理版写成专家审核。
- 不把候选方向写成工程方案。
- 不把未验证的区域规划写成已有成果。
- 不覆盖历史研究包；修订必须新建版本。
- 发布前必须有备份、构建产物检查、健康检查和回滚路径。

## 10. Agent 快速接班入口

新 Agent 进入项目时，先读：

1. `AGENTS.md`
2. `TASKS.md`
3. `STATE.md`
4. `DECISIONS.md`
5. `specs/111-应用中心接入与Agent开发规范.md`
6. `specs/109-应用中心桌面控制台视觉.md`
7. `specs/098-创新研究引擎算法V1-割胶机器人样板.md`
8. `specs/099-创新研究输出物标准.md`
9. `specs/104-企业创新工作台-产品定义.md`
10. `specs/107-企业创新工作台-开发任务拆解.md`
11. `specs/113-推理画布受保护试点第一阶段.md`
12. `specs/114-推理画布受保护试点第二阶段.md`
13. `specs/115-推理画布受保护试点部署.md`

常用本地命令：

```bash
python3 scripts/build_gooddesign_site.py
python3 scripts/build_application_registry.py
python3 scripts/preview_gooddesign_site.py --port 8892
python3 -m unittest tests.test_application_registry_111
```

## 11. 当前建议的下一步

1. 推理画布 113 已完成本机状态服务与 GDRP JSON 导出；114 已完成本地三角色视图与 GDRP 人读报告。
2. RC-16 已有115受保护试点部署记录；继续核新域名登录后画布、账号隔离、桌面移动及回滚，不重复部署。
3. 110 暴露的检索质量问题已由 123 完成确定性修复：匹配体空白归一化（自召回 95.3%→100%，基线 15 个换行未中全闭合）与 build_queries 源语汇标注/零召回预警；语义召回与扩库仍另立任务。
4. 为每个应用补一份由 Manifest 生成的 `APP_SKILL.md`。
5. 为 Agent 增加最小示例：读取注册表、调用 capabilities、组装研究上下文、校验 GDRP。
6. 等 Manifest、MCP 参数和 GDRP 输出稳定后，再决定 Python / TypeScript SDK。
