# 推理画布（reasoning-canvas）

企业创新工作台的人机交互层原型：七个思考节点（发问、查证、拆问题、发散、质疑、取舍、立约），AI 在节点内有角色，节点之间由人驱动。产品定义 specs/104，功能描述 specs/106，任务拆解 specs/107。

## 本机预览

纯静态（无检索能力）：

```sh
python3 scripts/preview_reasoning_canvas.py --port 8977
```

带真实检索、引擎候选、工作区状态与 GDRP 导出（RC-03/05/08/11，须仓库运行时与私有项目库）：

```sh
.runtime/pipeline/bin/python3 scripts/reasoning_canvas_server.py --port 8978
```

访问 `http://127.0.0.1:8978/extensions/reasoning-canvas/`。API：`/api/rc/search_methods`（64 方法目录）、`/api/rc/search_projects`（560 项目目录）、`/api/rc/engine_candidates`（GD-CRE-0.1 割胶冻结样例）、`/api/rc/state`、`/api/rc/revisions`、`/api/rc/gdrp`。仅 loopback；只有 `/api/rc/state` 接受画布状态写入。

## 边界

- 查证节点的真实检索经本机桥接调用项目库只读工具；每次检索留痕（查询词、域、命中数）并进入导出档案；服务未启动时前端如实提示，不伪装结果。
- 发散节点的引擎候选来自 GD-CRE-0.1 冻结样例（run-20261105T140200Z，review_pending）只读投影，不重算；候选经人「确认写入」才进入思考痕迹，未确认不进导出。
- 画布工作区使用 SQLite 追加不可覆盖修订；localStorage 只是服务不可达时的降级层。导出研究包先过 GDRP Schema，签署不等于客户确认、专家评审或工程验证。
- 未调用在线模型；重置需确认。视觉复用 GoodDesign UI 令牌，不私改品牌令牌；vendor 底座只读。
- 本目录不接入构建与发布链，未部署生产。

## 文件

| 文件 | 职责 |
|---|---|
| index.html | 页面骨架，引用 vendor 令牌、gooddesign.css 与页面样式 |
| data.js | 割胶案例真实研究材料（只搬运，不发明） |
| state.js | 状态结构、localStorage 持久化、全部状态变更动作、Markdown 导出 |
| reasoning-canvas.js | 视图渲染与事件绑定，不直接改状态 |
| reasoning-canvas.css | 页面布局样式，只用 GoodDesign UI 令牌 |

## 回归

```sh
python3 -m unittest tests.test_reasoning_canvas_rc01 -v
.runtime/pipeline/bin/python3 -m unittest tests.test_reasoning_canvas_rc03 tests.test_reasoning_canvas_rc08 -v
```
