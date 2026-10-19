# State

## 当前线上
- https://gooddesign.qiuyiwu.com/ 已恢复压缩包原版馆首页与交互。
- 主机yongle-nanjing；nginx静态+Node原API（loopback 3187）；systemd gooddesign。
- 2026-10-12 实查 release：20260911T030604Z-evidence-stand2；公开根目录 current/public。
- 发布脚本scripts/deploy.sh；构建scripts/build_original.py；构建结果original-app/。
- 旧site/及001简化门户已被替代，不再用于生产构建。
- 私有配置/etc/gooddesign.env；企业需求/var/lib/gooddesign/inquiries.jsonl，独立于release。
- 证书沿用Let's Encrypt自动续期；release与nginx配置备份位于服务器backups/。

## 实测
原首页哈希一致；560项目与560知识页保留；教师工具补齐。线上基础模型SSE真实回答通过，企业表单校验通过，独立测试验证需求持久化。详见原版线上验收.json、原版浏览器验收.md。

## 边界
深度模型未单独调用测试；学习看板仍主要为本机原型；企业需求无自动通知后台；原知识引用为启发式匹配，尚未升级为完整检索体系。未全量复核内容事实或全交互回归。

## 下一步
围绕03-平台规划/信息架构与平台定位-v2.md讨论项目主数据与10个知识包样本。

## 2026-09-07 产业Demo
/industry-demo/ 已发布；connect有入口。五步交互、三方向预置研究、文本下载；并非实时自动联网调研。源码extensions/public/industry-demo，构建叠加保留。

## 2026-09-07 用户反馈后的恢复
用户认为原版更好。已恢复设计系统改版前的原站，保留双环Demo。004设计系统及平台新外框退出生产，只保留本地草案；构建与部署亦恢复原版路径，防止再次覆盖。后续以原版视觉和节奏为准做局部改进。

## 2026-09-07 005 企业课题工作台
- release 20260907T102228Z；新增 /industry-demo/workspace.html 和 /knowledge-data/project-index.json。
- 560条项目索引、96条描述缺失、3条未审核机制样本；不是完整知识库。
- 工作台支持本机多课题、问题修改、案例选择、方向编辑、验证记录和JSON导出。无云端账户或自动TRIZ。
- 本地浏览器保存/重载/切换/导出通过；线上HTTP与健康接口200、原首页哈希一致。线上浏览器工具两次超时，未完成线上视觉复验。

## 2026-09-07 双环价值研究
新增 /industry-demo/research.html 与 shuanghuan-research.json，六项目证据与验证建议；产业Demo添加入口。release 20260907T102519Z-research，基于线上20260907T102228Z复制，仅更新研究页、数据和入口，保留其他线上内容。六条来源位置与哈希本地校验通过，线上六条原文引用校验通过。浏览器工具超时，视觉与筛选点击未验收。研究非企业确认，非实时生成。

## 2026-09-07 研究方向进入课题工作台
release 20260907T103032Z-research-workspace。六张研究卡新增课题入口，工作台可选择研究方向并创建含证据、对照方案和验证计划的新课题，保留原记录。tests/test_research_workspace.cjs 验证六方向创建、来源、保存及原记录保留通过。服务器本机经HTTPS nginx验证四个文件字节一致，API健康通过，原首页未修改。公网访问本轮超时，未完成外网与浏览器验收；首次公网校验已回滚，随后以服务器HTTPS核验通过发布。

## 2026-09-07 现场研究 Agent
/industry-demo/live.html 提供问题输入、现场约束、六条证据展开、在线SSE、停止、重算、预置样例及简报下载。默认标准模型，75秒前端超时；深度模型55秒测试未返回，标准通道25秒完成一次真实简短约束分析（非全长流程性能保证）。程序测试输入/上下文限制/分片解析/模式区分通过；服务器HTTPS核验通过，浏览器工具超时未完成视觉验收。预加载资料与在线生成明确区分，不宣称实时联网。在线输出未经工程复核。007详见specs。

## 现场分析与课题交接
新增案例纳入/排除、真实执行事件记录、条件变动后旧分析失效。完整在线输出或明确预置样例可保存为本机课题，携带问题、约束、证据快照、分析模式与原始分析；试验结果保持为空。工作台按task参数打开对应课题。程序验证证据排除确实影响请求，输入与SSE、课题保存及六方向回归通过；服务器HTTPS核验，公网HTML可访问；浏览器控制仍超时，视觉验收未完成。
最终发布：20260907T112650Z-handoff-verified。首次传输中断后重新逐文件传输；live.html/live.js/workspace.js三个文件服务器HTTPS SHA256与本地一致，确认新功能实际发布。

## 2026-09-07 连续研究与轮次对照
release 20260907T113828Z-rounds。在线研究将上一轮待审核结论纳入上下文（最多8条历史），要求说明保留/改变/撤回；前后原文并列，全部轮次可JSON导出并随课题保存。工作台保存后可通过resume返回在线研究，加载本机问题/约束/证据与轮次，续研另存课题保留旧记录。修复预置样例修改条件后的保存失效检查，简报来源仅列本轮纳入项目。程序测试涵盖续研上下文、证据排除、保存、恢复与旧结果失效；服务器HTTPS四文件SHA256与本地一致。未完成浏览器视觉验收，也未重跑多轮真实模型质量评审。

## 2026-09-07 创新设计大模型定义页上线
仅增补 /model/，release 20260907T124101Z-model-definition，基于线上 rounds 版本复制，服务器 HTTPS 内容哈希验证通过。构建脚本已纳入此页。详见 00-项目管理/创新设计大模型定义页-发布记录.md。

## 定义页 V1.1 产品架构
已更新 /model/，release 20260907T130112Z-model-v11。新增产品架构与试点规划，公网与服务器HTTPS文件一致；浏览器视觉复验超时。

## 2026-09-09 双环现场演示收口
release 20260909T1020Z-shuanghuan-demo-ready，基于线上20260907T130112Z-model-v11仅替换 industry-demo/index.html、live.html、live.css、live.js、demo-guide.html。新增 /industry-demo/demo-guide.html 现场路线页，产业Demo与现场Agent导航加入入口。live.js 在在线模型失败或超时时记录失败并自动载入明确标注的预置研究，避免现场停在错误状态；不伪装为实时生成。node语法、tests/test_live_demo.cjs、tests/test_research_workspace.cjs通过；服务器本机HTTPS确认demo-guide内容、live.js兜底文案和/api/health正常。公网curl本轮仍出现超时，属于外网链路检查未完成；服务器current指向新release且五个文件SHA256与本地构建一致。

## 2026-09-09 双环用户体验流程调整
release 20260909T1056Z-shuanghuan-ux-flow，基于上一双环现场演示版本仅替换 industry-demo/index.html、live.html、live.css、demo-guide.html。demo-guide 从内部演示路线改为企业用户旅程：确认企业与问题、看见证据与取舍、加入约束并研究、沉淀为创新课题；保留明天演示路径和一句话讲法。live.html 左侧工作流程改为用户路径，产业Demo入口文案改为“企业创新体验流程：从问题到课题”。node语法与tests/test_live_demo.cjs通过；服务器本机HTTPS和公网HEAD均确认demo-guide 200，/api/health正常。

## 2026-09-10 双环交互设计原因页
release 20260910T0958Z-shuanghuan-ux-reason，基于上一双环用户体验流程版本仅替换 industry-demo/demo-guide.html 和 live.css。demo-guide 进一步改为从企业用户疑问出发解释交互设计原因：信任、相关、可控、落地；新增“演示时的体验节奏”四段卡片，说明开场、证据、交互、收束各讲什么。构建通过，tests/test_live_demo.cjs通过；公网与服务器本机HTTPS均确认页面200与关键文案生效，/api/health正常。

## 2026-09-10 双环产业创新流水线Demo
release 20260910T1016Z-shuanghuan-pipeline-demo，基于上一双环交互设计原因版本仅替换 industry-demo/index.html、app.js、style.css。/industry-demo/ 从链接列表和表单向导改为现场交互流水线：左侧01-05步骤轨道，中间当前环节舞台，右侧研究流水线事件与当前输出；流程为识别企业、调研画像、提出问题、匹配融合、生成报告。新增自动演示按钮，保留企业名称校验、三条研究方向、项目证据、报告下载/打印与边界说明。新增 tests/test_industry_pipeline.cjs，验证五步推进、证据融合和报告阶段；tests/test_live_demo.cjs、tests/test_research_workspace.cjs通过。公网与服务器本机HTTPS均确认/industry-demo/ 200与关键文案生效，/api/health正常。

## 2026-09-10 双环视觉统一与内容增强
release 20260910T1038Z-shuanghuan-visual-pipeline，基于上一双环流水线版本仅替换 industry-demo/index.html、app.js、style.css。/industry-demo/ 视觉统一到好设计馆原站语言：纸色背景、深蓝夜航 hero、金色强调、宋体标题、Noto Sans 正文、品牌 logo 导航。自动演示流程内容增强：识别企业卡、调研画像图、潜在问题卡、匹配融合图、指标标签和报告摘要卡。保留企业校验、自动演示、报告下载/打印、工作台和现场 Agent 入口。node 语法、tests/test_industry_pipeline.cjs、tests/test_live_demo.cjs、tests/test_research_workspace.cjs 通过；本地浏览器验证自动演示可到达 05 报告并恢复“自动演示”按钮；公网与服务器本机 HTTPS 确认 /industry-demo/ 200 与关键文案生效，/api/health 正常。

## 2026-09-10 双环内容加厚与网页报告
release 20260910T062330Z-shuanghuan-rich-demo，基于上一双环视觉流水线版本仅替换 industry-demo/index.html、app.js、style.css、data.json。自动演示节奏改为首步约 1.8 秒、后续每步约 6.5 秒，并在每步加入“模拟深度研究处理中”的分项加载动画。调研画像扩充为公开事实、能力标签、资料来源、画像摘要四块；企业研究问题扩充为 6 个问题，每个问题标注来源与提出原因；匹配环节新增迁移依据、需补数据、评价指标与项目证据；报告生成环节新增网页报告预览、HTML 下载、文本下载和打印入口。node 语法、tests/test_industry_pipeline.cjs、tests/test_live_demo.cjs、tests/test_research_workspace.cjs 通过；本地静态检查和公网 HTTPS 检查确认 /industry-demo/、app.js、data.json 生效，/api/health 正常。

## 2026-09-10 产业演示四页面关系与节点式工作台
release 20260910T064453Z-industry-node-workspace，基于上一双环内容加厚版本仅替换 industry-demo 的演示页面、脚本、样式和研究数据文件。重新定义四页面关系：/industry-demo/ 是面向现场的产业演示看台，research.html 是证据看台，live.html 是现场研究 Agent，workspace.html 是创新工作台。research.html 从独立长列表改为证据对象看台，展示项目档案、原文摘录、来源位置、平台分析、适用边界、最小验证和需补资料，并提供“带入现场 Agent”和“生成课题节点”入口。live.html 统一为好设计馆视觉风格，并明确其处于证据看台和工作台之间；支持 evidence 参数从证据页带入单条证据和对应问题。workspace.html 从表单章节改为节点式创新工作台，包含企业画像、问题定义、证据匹配、方法取舍、验证计划、成果沉淀六个节点，中间为节点画布，右侧为节点检查器。node 语法、tests/test_industry_pipeline.cjs、tests/test_live_demo.cjs、tests/test_research_workspace.cjs 通过；本地浏览器检查确认工作台节点画布和证据看台动态渲染正常；公网 HTTPS 检查确认 research.html、live.html、workspace.html、live.js 生效，/api/health 正常。

## 2026-09-10 双环演示暂停、深报告与控制台工作台
release 20260910T070647Z-demo-pause-report-console，基于上一产业节点工作台版本仅替换 industry-demo/index.html、app.js、style.css、data.json、workspace.html、workspace.js、workspace.css。自动演示按钮从“停止演示”改为可暂停/继续：播放中显示“暂停演示”，暂停后显示“继续演示”，并保留当前步骤供现场讲解。最终报告标题改为“双环传动精密传动创新机会研究报告”，网页版报告增加 KPI、融合矩阵、项目证据、双环问题来源、建议推进路线和边界说明。双环问题池移除平台级“好设计项目库如何服务企业研发”，替换为“机器人减速器机会如何分层”。创新工作台进一步改为控制台布局：顶部 sticky 控制条、创新控制台节点导航、中间节点画布、右侧当前节点处理面板，更接近节点工具/看板式演示体验。node 语法、tests/test_industry_pipeline.cjs、tests/test_live_demo.cjs、tests/test_research_workspace.cjs 通过；本地浏览器检查确认控制台式工作台渲染正常；公网 HTTPS 检查确认暂停/继续、报告标题、问题替换和控制台工作台生效，/api/health 正常。

## 2026-09-10 现场Agent定义与大屏画布工作台
release 20260910T072015Z-agent-workspace-canvas，基于上一暂停/深报告/控制台版本仅替换 industry-demo/live.html、live.js、live.css、workspace.html、workspace.js、workspace.css。live.html 重新定义现场 Agent 为“研究转译器”，说明其职责是把企业现场问题、现场补充约束和好设计证据转成可审计、可保存、可继续推进的研究轮次；新增 INPUT/EVIDENCE/JUDGEMENT/HANDOFF 四卡和现场问题、证据选择、研究输出三段状态图，live.js 让状态图随输入、证据勾选和生成状态变化。workspace.html/workspace.js/workspace.css 将创新工作台升级为大屏画布控制台：顶部保留课题、证据、保存、导出工具，新增放大、缩小、复位画布；中间节点画布支持拖动空白处平移、拖动节点调整位置、缩放视图，并用边线标注企业画像、问题定义、证据匹配、方法取舍、验证计划、成果沉淀之间的逻辑关系；右侧继续作为当前节点处理面板。node 语法、tests/test_industry_pipeline.cjs、tests/test_live_demo.cjs、tests/test_research_workspace.cjs 通过；公网和服务器本机 HTTPS 确认 live.html、workspace.html 200，/api/health 正常，服务器 current 指向该 release。

## 2026-09-10 人机协作节点工作台
release 20260910T073604Z-human-ai-node-workspace，基于上一现场Agent定义与大屏画布工作台版本仅替换 industry-demo/workspace.html、workspace.js、workspace.css。workspace.html 将标题与定位改为“产品创新的人机协作工作台”，新增左侧节点库，强调流程、方法、证据、Agent 和产出都可以作为节点编排。workspace.js 将原六个表单章节映射为 11 个画布节点：企业输入、问题定义、机会分析、TRIZ矛盾、案例类比、证据看台、现场Agent、方案生成、验证计划、研究报告、知识沉淀；节点类型分为 human、method、evidence、agent、validation、output，点击节点切换右侧协作面板，拖动节点和缩放/平移画布能力保留。workspace.css 改为三栏控制台布局：左侧节点库、中间大屏画布、右侧协作面板，并用不同色条区分节点类型、用高亮边线表达当前相关路径。node 语法、tests/test_research_workspace.cjs、tests/test_live_demo.cjs、tests/test_industry_pipeline.cjs 通过；公网 HTTPS 确认 workspace.html 200 与关键文案/节点模型/CSS 生效，/api/health 正常。

## 2026-09-10 全屏创新工作台
release 20260910T074842Z-fullscreen-innovation-workbench，基于上一人机协作节点工作台版本仅替换 industry-demo/workspace.html、workspace.js、workspace.css。workspace.html 从普通网页布局改为全屏应用：顶部系统栏、命令栏、左侧节点库、中间产品创新编排画布、右侧协作面板。workspace.css 为创新工作台单独定义工具型 UI 规范，不再强绑好设计馆原页面样式；采用深色系统栏、灰蓝点阵画布、玻璃控制条、类型化节点色条和高亮路径，目标是现场大屏可演示。workspace.js 保留保存、导出、证据生成课题、拖动节点、画布平移与缩放能力，新增“聚焦流程”和“演示模式”：演示模式会按企业输入、问题定义、方法、证据、Agent、验证、报告、知识沉淀顺序自动聚焦节点。node 语法、tests/test_research_workspace.cjs、tests/test_live_demo.cjs、tests/test_industry_pipeline.cjs 通过；公网 HTTPS 确认 workspace.html 200，workspace-fullscreen、产品创新编排画布、演示模式、togglePlay、workbench-app 等关键内容生效，/api/health 正常。

## 2026-09-10 工作台画布可见性与方法节点深化
release 20260910T080951Z-canvas-methods-visible，基于上一全屏创新工作台版本仅替换 industry-demo/workspace.html、workspace.js、workspace.css。针对现场截图中画布中部空白、节点偏到边缘的问题，重排 canvasNodes 坐标并将默认视角改为 zoom=.78、pan={x:62,y:92}，让节点打开即在中间画布首屏可见；复位按钮同步回到该可见视角。workspace.html 给 workspace.css 和 workspace.js 加版本参数 v=20260910-canvas-methods，避免浏览器沿用旧资源。方法节点从原来的机会分析/TRIZ扩展为机会分析、功能拆解、TRIZ矛盾、跨域类比、五大构成评估，并在右侧协作面板增加“节点运行”说明；产出链路保留现场Agent、方案生成Agent、验证计划、研究报告、知识沉淀。workspace.css 缩小画布总宽和节点宽度，增强节点状态点与类型色条，让中间区域更像可拖动、可编排的创新方法画布。node 语法、tests/test_research_workspace.cjs、tests/test_live_demo.cjs、tests/test_industry_pipeline.cjs 通过；本地浏览器确认 13 个节点在画布中可见，公网 HTTPS 确认版本化资源、功能拆解/跨域类比/五大构成评估、width:1640px 等关键内容生效，/api/health 正常。

## 2026-09-10 浅色自适应创新画布

release `20260910T082854Z-light-canvas-fit`。基于上一版全屏创新工作台，仅替换 `industry-demo/workspace.html`、`workspace.js`、`workspace.css`。定位中间画布“只露一小部分”的主要原因是 `workspace.html` 使用 `main.node-canvas`，被全站 `style.css` 的 `main{max-width;margin;padding}` 规则影响，导致画布按普通页面容器布局；本版在 `workspace.css` 明确重置 `.node-canvas` 与 `main.node-canvas` 的 `max-width/margin/padding`，并新增 `fitFlow()`，根据 `#canvas-viewport` 实际尺寸自动计算初始 zoom/pan，复位和聚焦流程也走同一套自适应逻辑。默认主题改为浅色 `theme-light`，增加“深色模式/浅色模式”切换；画布增加“双环演示案例”浮层；节点保留企业输入、问题定义、机会分析、功能拆解、TRIZ 矛盾、跨域类比、五大构成评估、好设计证据、现场 Agent、方案生成 Agent、验证计划、研究报告、知识沉淀，并在右侧面板强化“节点运行”。HTML/JS/CSS 使用 `v=20260910-light-canvas-fit` 强制刷新缓存。

验证：`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_research_workspace.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_industry_pipeline.cjs`、`python3 scripts/build_original.py` 均通过。本地浏览器 DOM/布局读取确认页面为 `workspace-fullscreen theme-light`，画布中 13 个节点全部生成，缩放下限已从 `.54` 调整为 `.38` 以适配较窄视口。公网确认 `workspace.html` 返回 200，引用 `workspace.js?v=20260910-light-canvas-fit`，JS 包含 `fitFlow()`/`toggleTheme()`，CSS 包含 `main.node-canvas` 修复和 `theme-light` 样式，`/api/health` 返回 `ok:true`。

## 2026-09-10 故事化方法选择工作台

release `20260910T084509Z-story-method-flow`。基于浅色自适应创新画布版本，仅替换 `industry-demo/workspace.html`、`workspace.js`、`workspace.css`。本版按用户反馈把“方法节点”从一股脑堆叠改为“问题触发的方法路由”：主线变为识别企业、提出问题、选择方法、匹配证据、生成方案、沉淀报告 6 步；画布中的方法选择器根据双环机器人关节平台化问题，只点亮功能拆解、TRIZ 矛盾、案例类比三条方法链。机会分析与五大构成评估保留为备选/暂不展开节点，分别用于商业场景扩展和报告收束检查，避免现场演示时主线被方法库淹没。左侧节点库新增 6 段故事线按钮，节点卡显示故事编号与泳道，右侧协作面板新增“为什么到这里”，方法取舍面板新增问题信号、选择逻辑、本轮点亮方法、暂不展开方法，强调人机协作中的判断依据与边界。

验证：`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_research_workspace.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_industry_pipeline.cjs`、`python3 scripts/build_original.py` 均通过。本地浏览器确认 14 个节点全部在画布视口内，故事按钮 6 个，已选择方法为功能拆解、TRIZ 矛盾、案例类比，备选方法为机会分析、五大构成评估。公网确认 `workspace.html` 200，引用 `workspace.js?v=20260910-story-method-flow`，JS 包含 `method-router`/`storySteps`，CSS 包含 `story-rail`/`method-router`/`method-card`，`/api/health` 返回 `ok:true`。

## 2026-09-10 ComfyUI 式可编排节点工作台

release `20260910T085959Z-comfy-node-edit`。基于故事化方法选择工作台，仅替换 `industry-demo/workspace.html`、`workspace.js`、`workspace.css`。本版把工作台从固定流程图改为可编排节点画布：`canvasNodes` 增加 visible/locked 状态，默认画布只显示 12 个双环演示主线与已触发方法节点，机会分析、五大构成评估默认收在左侧模板库，不再一股脑铺到画布上。顶部新增“移除节点”“复原节点”，左侧新增节点数量与 NODE TEMPLATES，模板卡区分“已在画布 · 点击聚焦”和“点击添加到画布”。选中非锁定节点后可从画布移除，节点不会丢失，会回到模板库；点击模板可添加回画布；复原节点会恢复双环演示默认节点组合和初始坐标。边线、自动聚焦和自适应缩放均只计算当前可见节点，避免隐藏节点影响画布视图。主线关键节点暂时锁定，避免现场误删导致演示断链。

验证：`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_research_workspace.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_industry_pipeline.cjs`、`python3 scripts/build_original.py` 均通过。本地浏览器验证默认画布 12 个节点，机会分析和五大构成评估在模板库；移除“功能拆解”后画布为 11 个节点且模板卡变为“点击添加到画布”；添加“机会分析”后画布回到 12 个节点；复原后回到默认组合，功能拆解恢复，机会分析重新收回模板库。公网确认 `workspace.html` 200，引用 `workspace.js?v=20260910-comfy-node-edit`，JS 包含 `addNode`/`removeActiveNode`/`restoreDefaultNodes`，CSS 包含 `node-count`/`template-bank`/`template-card`，`/api/health` 返回 `ok:true`。

## 2026-09-10 创新工作台 V2 稳定演示版

release `20260910T091233Z-workbench-v2`。基于 ComfyUI 式可编排节点工作台，仅替换 `industry-demo/workspace.html`、`workspace.js`、`workspace.css`。本版先修复截图暴露的选中节点 UI 错误：补充强制的 `.theme-light .node-card.active` 状态，确保浅色主题下选中节点为深色底、白色可读文字，不再出现白字浅底。交互上把演示模式从“轮流聚焦既有节点”改为“逐步添加/点亮推理节点”：第一步画布只显示双环企业画像，随后依次出现问题定义、方法选择器、三条已触发方法、好设计证据、现场 Agent、方案生成与验证计划、报告和知识沉淀；暂停后保留当前画布状态，继续后进入下一阶段。右侧节点检查器新增“模拟运行、接受输出、标记待复核、生成下游节点”四个节点级动作，把节点从静态说明卡推进为可推理、可复核、可生成下游的交互单元。顶部文案把“复原节点”改为“复原画布”，与“复位视图”区分。

验证：`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_research_workspace.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_industry_pipeline.cjs`、`python3 scripts/build_original.py` 均通过。本地浏览器验证默认画布 12 个节点，选中节点 computed style 为 `rgb(23, 32, 51)` 深色背景和白色文字；右侧 4 个节点动作按钮出现；演示模式第一步只显示 1 个节点，第二步显示 2 个节点，暂停后按钮变为“继续演示”并保持当前节点数。公网确认 `workspace.html` 200，引用 `workspace.js?v=20260910-workbench-v2`，JS 包含 `demoStages`/`applyDemoStage`/节点动作绑定，CSS 包含 `v2 node state model` 与 `node-mini-actions`，`/api/health` 返回 `ok:true`。

## 2026-09-10 cocreation-v1
release `20260910T100130Z-cocreation-v1`。基于 `20260910T091233Z-workbench-v2` 继续增强创新工作台的人机共创能力，仅替换 `industry-demo/workspace.html`、`workspace.js`、`workspace.css`，并补回 release 根目录服务文件以保持 `gooddesign.service` 正常运行。本版在画布底部新增“现场共创”输入区，演示者或企业现场人员可以把人的约束、想法、反驳接入当前选中节点；系统会生成 `human co-created` 动态节点，自动连接到当前节点，并在右侧协作面板标注为“现场共创节点”。复原画布时会清空这些临时共创节点与对应边线，回到双环默认演示主线。

验证：`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_research_workspace.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_industry_pipeline.cjs`、`python3 scripts/build_original.py` 均通过。公网确认 `workspace.html` 200，引用 `workspace.css?v=20260910-cocreation-v1` 与 `workspace.js?v=20260910-cocreation-v1`；HTML 包含 `co-create-dock`/“现场共创”，JS 包含 `function coCreate`/`human co-created`/`canvasNodes.splice(initialNodeCount)`/`edges.splice(initialEdgeCount)`，CSS 包含 `.co-create-dock` 与 `.node-card.co-created`；`/api/health` 返回 200 `ok:true`，`gooddesign.service` 为 active。

## 2026-09-11 shared-demo-fix
release `20260911T014841Z-shared-demo-fix`。针对用户反馈“共享链接在其他电脑上适配，演示卡住不能动”，更新 `industry-demo/index.html`、`app.js`、`style.css`、`live.html`、`live.js`、`live.css`、`workspace.html`、`workspace.js`、`workspace.css`。修复点：1）产业演示第一步在双环主体默认成立时不再强制等待手动勾选，点击“推进下一步”会自动确认共享演示范围，避免现场卡住；2）现场 Agent 在线研究增加 12 秒首段内容安全兜底，模型或网络慢时自动切到预置研究，整体请求上限从 75 秒降到 45 秒；3）`live.html?shared=1` 或 `?demo=1` 会直接进入共享演示模式，不依赖本机历史记录；4）`workspace.html?task=...` 在其他电脑没有本机 localStorage 课题记录时，自动载入双环演示样例并提示，而不是跳到无关本机记录；5）给 index/live/workspace 的关键 CSS/JS 引用增加 `v=20260911-shared-demo-fix` 缓存版本，减少共享电脑加载旧脚本导致的按钮失效。

验证：`node --check extensions/public/industry-demo/app.js`、`node --check extensions/public/industry-demo/live.js`、`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_industry_pipeline.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_research_workspace.cjs`、`python3 scripts/build_original.py` 均通过。额外 VM 验证 `validateStep()` 在默认双环名称且未勾选时会自动勾选并返回 true。公网确认 `/industry-demo/`、`/industry-demo/live.html`、`/industry-demo/live.html?shared=1`、`/industry-demo/workspace.html?task=shared-test` 均返回 200；公网脚本确认包含“共享演示模式确认”、12 秒安全演示兜底、共享课题链接 fallback；`/api/health` 返回 200 `ok:true`。公网 curl 偶发首包超时后重试成功，页面逻辑已做兜底以避免现场卡住。

## 2026-09-11 scroll-fix
release `20260911T015454Z-scroll-fix`。针对用户反馈“为什么还是不能上下滚动浏览”，定位根因是 `workspace.css` 中 `html,body{height:100%;margin:0;overflow:hidden}` 为全屏创新工作台准备，但被 `live.html`、`index.html`、`research.html`、`demo-guide.html` 等普通页面共同引用，导致这些页面在其他电脑和共享链接中被锁住滚动。本版从非工作台页面移除 `workspace.css` 引用，只保留 `workspace.html` 加载工作台样式；同时将工作台 CSS 的锁滚动规则改为 `body.workspace-fullscreen{height:100%;margin:0;overflow:hidden}`，避免未来误伤普通页面。index/live/workspace 资源版本更新为 `v=20260911-scroll-fix`。

验证：`node --check extensions/public/industry-demo/app.js`、`node --check extensions/public/industry-demo/live.js`、`node --check extensions/public/industry-demo/workspace.js`、`node tests/test_industry_pipeline.cjs`、`node tests/test_live_demo.cjs`、`node tests/test_research_workspace.cjs`、`python3 scripts/build_original.py` 均通过。公网确认 `/industry-demo/live.html` 不再包含 `workspace.css`，只加载 `live.css?v=20260911-scroll-fix` 与 `live.js?v=20260911-scroll-fix`；`/industry-demo/` 不再包含 `workspace.css`，加载 `style.css?v=20260911-scroll-fix` 与 `app.js?v=20260911-scroll-fix`；`workspace.css` 中全局锁滚动已改为只作用于 `body.workspace-fullscreen`；`/api/health` 返回 200 `ok:true`。

## 2026-10-12 GitHub 与部署位置统一
私有仓库 qiuyiwu1989-star/gooddesign-platform；本地活跃仓库仍在移动硬盘好设计平台。服务器统一 /var/www/gooddesign.qiuyiwu.com，运行时数据 /var/lib/gooddesign，配置 /etc/gooddesign.env。发布脚本改为已推送 Git 提交打包与 REVISION 记录，本次未部署网站。详见 deploy/README.md。

## 2026-10-19 档案规范与首个标杆（011）
知识库新增规范v1.1及2025-00嫦娥钻取采样公开资料深研档案，HTML本地8773预览。20来源、20关键陈述、6专利候选；结构检查、检索与移动端浏览器通过。D2候选，未获专家或项目方确认；未改动original-app或生产发布。

## 012 主档案v2.0
本地8773/档案.html已更新为主档案正文，新增字段/标签及来源反查；源为主档案结构.json。12维度49字段22标签，保留011证据台账。检查通过，资料和专业审核仍待补；生产未更改。

## 2026-10-19 013 结构化档案v3
本地8773/档案.html默认八板块；233原子字段、17实体、72条本例记录、939个单元值。保留v2完整正文；通用/领域与P0/P1筛选、字段定义反查、逐值证据和下载可用。类型/引用/锚点与浏览器验收通过；仍属公开资料研究基线，专业审核未完成。无生产部署。

## 2026-10-19 015 数据库治理基线
本地8773档案页在第八板块展示六维质量和版本。研究内容0.1.0保留既有20来源基线；0.1.1补S21、两陈述/两事件及部分修订，现为21来源/22陈述/75记录/974槽位。质量自评46.25/100，取值登记547/974（56.2%），均非专业审定。10测试、引用/类型、版本哈希、390px/打印媒体/下载检查通过；生产及original-app未改动，MCP尚为契约。

## 2026-10-19 016 内容0.2.0
本地8773档案页继续原布局，指标验证增加可展开的10行对照子表。23来源/30陈述/92原子记录/1202槽位，论文4条中全文2/摘要2。自评50/100、登记覆盖706/1202；旧版本未覆写，16测试/版本完整性/浏览器通过。内部原始PDF位于01-原始资料/论文，未入公开站点；生产未改。

## 2026-10-19 017 读者版档案
本地8773/档案.html?v=4.0.0默认项目档案，资料与解读、档案评估分别查看。八模块统计可复算，内部字段及来源索引后置。92记录/23来源/706已填字段不变，自评50/100；解释内容0.2.1已留档。20测试、结构检查、四版快照校验与浏览器验收通过，未改生产。

## 2026-10-19 018 单案标杆试行
8773/档案.html?v=4.1.0保留八板块；设计思路可展开三条可借鉴经验和七个人工需求规则试读。评估页可看标杆缺口与独立版本分类，档案内容0.3.0。调用样例JSON按内容快照读取、附来源和限制，未接入AI或MCP。27测试及浏览器检查通过；生产未更改。
