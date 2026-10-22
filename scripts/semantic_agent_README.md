# 046 受限语义深读适配器

`semantic_agent.py` 调用本机已登录的 Codex CLI 真实模型，不使用规则伪装深读。SQLite 保存队列、尝试次数、结果和显式重试审计；它只生成候选，不修改研究库或自动发布。

## 后台集成接口

```python
queue = SemanticQueue(library, state_dir=None)
queue.enqueue(project_id, source_ids, max_sources=3, max_calls=3, max_chars=24000)
queue.step(job_id=None)  # 放入单独 worker，不在 HTTP 请求线程里阻塞
queue.status(project_id)  # 按项目过滤；不要将无过滤状态暴露给页面
queue.get(job_id)
queue.bundle(job_id, project_id)  # 重新核验结果、原件与证据块
queue.pause(True)  # 运行中的一次先结束；不再领取新任务
queue.retry(job_id, project_id, actor)  # 显式增加一次调用预算，最多 3 次
```

每个新来源默认只获准一次模型调用。重复原件/文本/覆盖片段同身份不会再次调用。批次最多 3 个来源，每源最多 24000 个文字字符。排队、接收结果和交接时均核来源范围、原件及块哈希；候选再经 `research_workflow.add_candidate` 在内存副本中验证，不保存事实。

有风险或矛盾的任务（包括零候选）是 `needs_review`，必须留给人工/Agent 判断，不能自动提交。`ready` 也仅表示机械候选校验通过，不能认定事实真实；交给 Steward 后仍须经过它的敏感字段、冲突及发布门禁。`no_candidates` 不是原文完整审核成功。状态中覆盖范围是机器文本的已提供证据块，不含图表视觉核读认证。

## CLI

```sh
.runtime/pipeline/bin/python scripts/semantic_agent.py --project 2025-00 --source SOURCE_ID --step
.runtime/pipeline/bin/python scripts/semantic_agent.py --project 2025-00
```

模型执行采用 `read-only` sandbox、`--ephemeral`、严格 JSON schema，忽略用户插件/规则/项目文档，只保留用户选用的 model 设置和现有登录。关闭 shell、统一执行、apps、plugins、hooks、浏览器、computer use、图像与子 Agent 等能力，禁用 web search；若输出事件仍出现工具执行则拒收。源文只作为 JSON 数据输入，任何源文指令均明确禁止执行。当前适配标准 Codex 登录；定制 provider/MCP 配置不会自动继承。

超时（默认180秒、硬上限300秒）终止本次独立本地进程组，保留诊断。CLI 内部网络重连次数不代表本队列新授权调用；不能保证上游已产生请求完全不计费。中断租约到期只标需判断，不自动再次消耗模型；显式重试单独保存 attempt 目录。

## 本轮真实状态

2026-10-22，本机 `codex login status` 显示 ChatGPT 已登录，但真实 A01 调用 180 秒、使用当前配置 model 的 A03 调用 120 秒均网络流超时。无最终 JSON，无真实模型候选，本库未变。日志保存在私有 `output/agent-046/semantic/`，不能将登录状态或 12 项离线测试通过当成模型连接成功。
