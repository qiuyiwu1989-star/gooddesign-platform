# 123 产业创新 Agent 真实后端（20261114-123-fix1）

展厅 Agent 从"动画演示"升级为"真实研究"：模型起草 + 真实检索 + 确定性校验，SSE 实时推流。用户决策：自建 Python 编排（不托管火山方舟/Coze，不引 LangChain）。

## 架构

```
输入地名 → 模型调用1：产业画像+客户画像（结构化 JSON，标"模型生成·待核"）
        → 模型调用2：需求结构化（引擎语言 proposed/hard=null）
        → 模型调用3：检索词提议（源语汇短词，不含事实）
        → 真实检索：innovation_knowledge 逐字召回（103 研究版，项目必须真实存在）
        → 模型调用4：双侧映射（transfer 契约：link/diff 必填，非候选项目丢弃并记录）
        → 确定性校验 → SSE 推流 → UI 渲染报告
```

核心纪律（与 098/108 一致）：模型只起草提议，确定性层才有写入权；映射非真实候选一律丢弃并如实记录；模型失败如实报告不补造；推荐永远为空。

## 实现

- `scripts/expo_agent_server.py`：stdlib HTTP 服务，端口 18792，`GET /api/run?place=X` 出 SSE（log/stage/blk/pack/done/error 事件），`/api/health` 健康检查。模型经 OpenAI 兼容端点 chat completions（`/etc/innovation-expo.env`，root:www-data 640，由 ubuntu 组读取，密钥不入仓库）。2026-11-14 起通道为阿里云百炼 compatible-mode + deepseek-v4.1-flash-1017（原火山方舟配置备份 .bak-20261114）；实测召回与关联数优于原通道。
- 部署：`innovation-expo.service`（WorkingDirectory=运行时 release，与 dossier 同库：04-知识库/项目库 568 项）。nginx `/expo/api/` → 18792（limit_req 6r/m burst 3，SSE 关缓冲；limit_req_zone 在 conf.d/expo-agent.conf，server 上下文不允许）。
- UI（v4）：`extensions/expo/agent-template.html` 统一事件处理器——真实 SSE 与静态数据包回放共用一套 renderBlk/finishReport；API 不可达自动降级静态包（离线展厅照常工作）。
- 发布：20261114-123-fix1（static/methods/runtime 三 base，mcp 保持 118）。

## 实测（线上真实调用）

- 玉环：47s 完整流程；模型产出"中国阀门之都"等画像、8 条需求；首轮板块词检索 0 候选（如实报告不补造）；加检索词提议后真实召回 4-8 个候选项目，输出 7 条机制关联（差异同列）；3 方向全标研究假设；0 推荐。
- 嘉善：真实召回 2 候选，6 条机制关联。
- 降级：本地无 API 时自动走静态数据包，16 条日志全流程完成。
- 诚实记录：映射调用曾 ReadTimeout（45s 上限），如实记录"机制关联为空"；已提至 100s 并压缩上下文后通过。
- 未验证项：本机 Chromium 当时全域出站被重置（baidu 同挂），线上 UI 的 EventSource 路径未做浏览器端验证；SSE 事件流、blk 负载与静态降级路径均已验证。

## 已知边界

- 需求与画像为模型生成（标"待核"），金融/合规倾向较强时提示词需继续校准向产品技术需求。
- 逐字检索召回受词表限制（110 基线），候选少时映射也少；候选为 0 时如实显示空。
- 每次运行约 1-2 分钟与若干模型调用费用；限速 6r/m 每 IP。
