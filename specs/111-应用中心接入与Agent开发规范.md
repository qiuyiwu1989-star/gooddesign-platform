# 111: 应用中心接入与 Agent 开发规范

## 要什么

把应用中心从入口页升级为受治理的应用注册中心。规范必须先按节奏回答“为什么、给谁、算什么、共享什么、如何接入、最后怎样工程化”，再落到 Manifest、Schema、MCP 与 SDK。

## 推理顺序

### 第一步：先定义应用中心的任务

应用中心不是导航页，也不是把六个链接排成卡片。它要回答：一个真实用户或 Agent，如何根据当前任务，进入正确应用，并知道这个应用能形成什么、依据是什么、边界是什么。

因此它的核心对象不是“页面”，而是“可执行任务”。

### 第二步：再区分使用者

- 公众与教师：需要阅读、看展、学习。
- 企业与研究人员：需要定义问题、组织证据、形成研究任务。
- 开发者与 Agent：需要读取能力、项目、方法、证据和输出契约。
- 政府与园区：需要把区域产业问题转成可研究任务。

不同使用者不能用同一种入口说明，也不能共用同一权限。

### 第三步：定义什么才算一个应用

一个应用不是一条路由。它必须同时有：

1. 稳定身份与当前状态。
2. 面向的人群和任务。
3. 输入与输出。
4. 可调用的项目、方法、MCP 或引擎能力。
5. 真实案例与证据边界。
6. 权限与发布门禁。

缺少这些，只能算页面入口，不能登记为应用中心应用。

### 第四步：定义共享底座

项目库、方法库、研究版本和 GDRP 输出是所有应用共享的底座。应用不得复制第二套事实，也不得把本地整理内容写成源事实。

共享底座提供：

- 项目证据：读取、检索、版本定位。
- 方法能力：方法 ID、版本、适用边界。
- 研究输出：GDRP research-pack、report、manifest。
- 权限边界：公开、登录、试点、租户隔离分别声明。

### 第五步：定义 Agent 怎样接入

Agent 不应先读代码或安装 SDK。正确顺序是：

1. 读取应用注册表。
2. 读取目标应用 Manifest。
3. 调用 `inno_capabilities` 获取真实工具。
4. 通过只读 MCP 检索项目、方法和证据。
5. 在当前客户端保存研究过程。
6. 按 GDRP Schema 校验研究包。
7. 提交独立评审；没有真实确认不得升格状态。

### 第六步：最后才决定 SDK

SDK 是稳定接口的封装，不是规范本身。先做 Agent App Kit：Manifest、应用 Skill、MCP 示例、GDRP Schema 与最小脚手架。等应用 Manifest、MCP 参数和 GDRP 输出稳定后，再封装 Python / TypeScript SDK。

## 不做什么

- 不新增生产路由、应用详情页、用户体系、租户数据库或模型调用。
- 不改变现有六应用的名称、公开路由、案例内容、事实和研究状态。
- 不把 SDK 当成规范本身。
- 不让 Agent 写入 approved、confirmed、engineering_validated、expert_reviewed、recommendations、public 或 training_authorized。

## 核心契约

### 应用 Manifest

每个应用必须声明：

- `id / title / kind / category / status`
- `audience / task / summary`
- `route.catalog / route.detail / route.runtime`
- `inputs / outputs`
- `capabilities.mcp_tools / capabilities.engine / capabilities.writes`
- `permissions.public_read / requires_login / tenant_isolation / mcp_access`
- `evidence.case_ids / must_show_boundary / forbidden_claims`
- `release.requires`

状态只允许 `planned / pilot / live / deprecated`；展示标签可以保留“已有内容”等中文口径，但系统状态必须统一。

### 接入顺序

1. 读取应用注册表和应用 Manifest。
2. 调用 `inno_capabilities`，不猜工具或版本。
3. 使用只读 MCP 检索项目、方法和证据。
4. 在客户端保存研究过程；远程不写源档案。
5. 按 GDRP Schema 校验研究包。
6. 提交独立评审；未获真实确认不得升格状态。

## 验收清单

- [x] `extensions/application-center/apps.json` 六个应用全部升级为 `gd-app-0.1`。
- [x] 新增 `application.schema.json`，字段、状态、权限和禁写声明可校验。
- [x] 新增构建脚本生成 `output/inno-preview/gooddesign-site/inno/apps/registry.json`。
- [x] 注册表保持六个应用、真实案例映射、只读 MCP 边界和现有路由。
- [x] 应用中心页面继续读取原字段，现有 096/101/103/109 回归通过。
- [x] 不部署生产，不提交 Git。

## 实现约束

沿用现有 `apps.json` / `cases.json` 作为公开内容真源；新增字段只描述接入契约。构建产物不得包含密钥、私有路径、内部会议或未确认事实。

## 状态

done：gd-app-0.1、应用 Schema、注册表构建与本地验收通过，未部署生产。
