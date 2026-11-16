# GoodDesign UI

好设计长期使用的产品设计系统。以造物云离线 V2.3 为稳定底座，以 Apple 级精致度作为排版、材质、圆角、反馈和无障碍的质量要求。

当前版本：1.0.1 / 096视觉重构，已接入生产。完整规范见 `03-平台规划/好设计平台设计系统-v3.md` 与 `03-平台规划/网站信息架构-v2.md`。模型关系图与应用工作台采用096真实任务结构，不再使用三等宽卡片作为默认表达。

## 快速使用

```html
<link rel="stylesheet" href="../method-workbench/vendor/tokens.css">
<link rel="stylesheet" href="../method-workbench/vendor/design-system.css">
<link rel="stylesheet" href="gooddesign.css">
```

根节点使用 `data-theme="light"` 或 `dark`，产品场景使用 `data-zw-mode="product"`。不要在线引入另一套主题或组件库。

本地预览：在项目根目录启动静态 HTTP 服务，访问 `/extensions/design-system/`。直接打开文件也可查看，但统一以 HTTP 验收结果为准。

## 分层与所有权

| 层 | 文件 | 规则 |
|---|---|---|
| 造物云稳定底座 | `extensions/method-workbench/vendor/` | 只读复用，不为好设计页面修改 |
| GoodDesign UI 核心 | `gooddesign.css` | 产品令牌、组件与模式，集中评审 |
| 真实组件样板 | `index.html`、`preview.js` | 展示标准用法和完整状态，不接生产数据 |
| 页面组合 | 各业务页面 | 只写页面布局，不私改核心品牌令牌 |

业务数据、研究判断和模型调用不属于设计系统。组件接收真实状态，不自行推断事实、评分、专家审核或工程可行性。

## 稳定契约

以下内容变更必须按破坏性变更评审：

- `data-theme`、`data-zw-mode` 和主题令牌名称。
- `gd-button`、`gd-field`、`gd-project`、`gd-method`、`gd-route`、`gd-badge`、`gd-drawer` 等公开类名。
- 路线选择的 `data-route`、`aria-pressed` 和详情同步关系。
- 证据抽屉的原生 dialog、Escape 关闭和焦点返回行为。
- 保存反馈的内容性质、待审核/待确认状态与错误保留输入行为。

允许在补丁版本中修正对比度、布局溢出、错误状态、无障碍和文案清晰度。新增兼容组件或页面模式进入次版本。删除或重命名公开契约、改变令牌语义、改变交互绑定进入主版本评审。

## 精致度标准

- 中文正文 400，UI 主力 500，标题与关键强调 600，不使用 800 以上中文字重。
- 按钮使用胶囊形，输入框使用 12px，卡片 18-20px，大面板与浮层 28px 连续圆角。
- 深度依靠发丝边界、轻薄材质和柔和阴影，不用多层厚重玻璃。
- 动效只表达反馈与状态变化，并尊重减少动态偏好。
- 任何可点击目标至少 44×44px，任何关键状态不能只靠颜色表达。
- 项目封面、方法图标和研究引文使用真实资产，不用装饰性假数据撑页面。

## 变更门禁

每次核心变更必须同时完成：

1. 设计核对：层级、字体、间距、圆角、材质和内容优先级一致。
2. 契约核对：公开类名、令牌、ARIA、数据绑定和旧用法未静默破坏。
3. 状态核对：默认、hover、active、focus、disabled、空、载入、错误和成功。
4. 浏览器核对：1440、1280、1024、768、390、360px，无全页横向溢出。
5. 交互核对：键盘、Escape、主题、保存、刷新和错误保留输入按组件覆盖。
6. 内容核对：来源、AI、待确认、冲突、未知和历史版本未混淆。
7. 证据核对：保留实际测试输出和最终截图，不以“样式已修改”代替验收。

基础回归：

```sh
python3 -m unittest tests.test_design_system_069 -v
```

## 版本与发布

- `0.1.x`：候选阶段，允许在样板中校准组件，但仍须保留兼容说明和测试证据。
- `0.x` 次版本：新增兼容组件、页面模板和状态，不改变已有语义。
- `1.0`：首个真实生产页面完成设计、代码、无障碍和浏览器验收后再评估。
- 主版本：处理破坏性令牌、类名、交互或数据绑定变更，附迁移指南。

每次变更记录：版本、日期、变更内容、兼容性、实际验收、涉及页面和回滚方式。生产采纳按页面独立发布，不随核心样式提交自动上线。

## 页面采纳顺序

1. 用一个真实 `/inno/` 页面验证核心令牌和公共组件。
2. 用一个项目档案验证长文、目录、证据和内容状态。
3. 用 ML-025 研究工作台验证路线、反馈和待确认补充。
4. 用资料后台验证高密度文件与审核队列。
5. 再评估其他页面，不做无验收的全局换肤。

每一步都保留旧页面回滚能力，并单独验证路由、权限、数据版本和研究内容未改变。

## 当前真实页面样板

`portal.html` 是项目库首页的首次真实采纳，使用560项目与当前研究状态，保留搜索、筛选、分页和URL恢复。

```sh
python3 scripts/preview_gooddesign_portal.py --port 8891
```

访问 `http://127.0.0.1:8891/extensions/design-system/portal.html`。静态回归：

```sh
python3 -m unittest tests.test_design_system_069 tests.test_gooddesign_portal_069 -v
```

该预览只读公开目录字段，不开放私有原件，不修改生产。

## 全站迁移预览

071已完成旧站1165页、方法库67页和5个动态公共页的统一迁移，共1237静态页，另接动态档案、资料后台、方法工作台和企业研究闭环。

```sh
python3 scripts/build_gooddesign_site.py
python3 scripts/preview_gooddesign_site.py --port 8892
```

全站走查：`http://127.0.0.1:8892/site-index.html`。资料后台8893、方法工作台8894、企业闭环8895。验收报告见 `00-项目管理/071-全站GoodDesignUI迁移验收.md`。

## 品牌与“小好”

GoodDesign 的统一导航、底部、主题和“小好”由 `scripts/gooddesign_chrome.py` 单源生成。品牌 Logo 与 IP 资产位于本目录的 `brand-logo.svg`、`ip-xiaohao.svg`，交互在 `chrome.js`。超链接不使用箭头，动作以明确文字表达。

“小好”只提供真实导览，不调用模型或修改资料。工作区调用时必须传入当前 `project`，不得回退到默认项目。R50 方法页的精修资源为 `method-detail.css`，验收见 `00-项目管理/072-全站导航品牌与IP助理验收.md`。

## 奖项图标

`awards/` 提供统一细线几何家族：金奖单菱形、银奖双圆环横线、铜奖六边形中心短线、创意奖三个相连节点、提名奖开放圆环中心点、菁英奖四个有序节点。旧星芒、灯泡、书签、桂冠方案已废弃。`portal.js` 按 `project.award` 映射，并保留文字标签。验收见 `00-项目管理/073-奖项系列图标验收.md`。

## 需求研究工作台

074 将需求板块重新定义为研究任务工作台：真实问题 → 参考资料 → 研究路线 → 核对计划。源文件为 `needs-workspace.html/css/js`，全站构建后访问 `http://127.0.0.1:8892/inno/needs-v2/`。当前仅本地候选，不替换生产 `/inno/needs/`。

桌面采用步骤、任务、判断三层，移动端自然单列。未知、待确认补充和模板路线必须明确，不调用模型，不推断迁移可行、客户确认或工程有效性。草稿保存在当前浏览器；导出 JSON 不修改源项目。研究交接通过原生对话框预览、全选和系统复制快捷键完成，不依赖剪贴板授权。

```sh
python3 -m unittest tests.test_needs_workspace_074 -v
```

21项浏览器检查与全量507项固定环境回归通过，验收见 `00-项目管理/074-需求研究工作流重构验收.md`。

## 数据可视化

075 将 `/inno/report/` 重构为真实数据图表优先，生成器为 `scripts/data_report_page.py`，样式和交互位于 `extensions/project-portal/data-report.css/js`。预览：`http://127.0.0.1:8892/inno/report/`。

- 560项目的奖项与年份分布，点击接项目库筛选。
- 98案来源、已知字段和结构化记录的证据密度，点击接真实档案。
- 研究覆盖、质量状态、评分分布与64方法分类，质量状态可过滤清单。
- 所有聚合从安全快照计算，不硬编码年度，不把数量、Agent校准或字段覆盖冒充专家质量。

```sh
python3 -m unittest tests.test_data_report_075 -v
python3 tests/browser/data_report_075.py
```

36项浏览器检查与全量514项固定环境回归通过，验收见 `00-项目管理/075-数据总览可视化重构验收.md`。统一主题脚本每页只能加载一次，SVG数据链接须同时验证鼠标和键盘激活。

## 企业创新工作台

076 将旧产业演示重新定义为 `/inno/loop/` 研究任务工作台，预览：`http://127.0.0.1:8895/`。页面复用ML024三任务与真实API，不新建演示状态或第二套后端。

- 研究概览、需求与条件、路线与证据、验证计划、反馈与回流五视图。
- 桌面任务导航、当前工作、研究判断三层，手机自然单列。
- 补充与反馈真实保存，保持待审核和精确版本绑定，支持失败重试、刷新恢复与任务隔离。
- 候选资料不冒充已匹配证据，研究行动不授权实体试验，导出不调用模型。

```sh
python3 -m unittest tests.test_enterprise_workbench_076 -v
python3 tests/browser/enterprise_workbench_076.py
```

45项隔离数据库浏览器检查与全量519项固定环境回归通过，验收见 `00-项目管理/076-企业创新工作台产品重构验收.md`。浏览器验收只写SQLite临时副本，不污染真实研究记录。

## MCP接入中心

077 将 `/inno/mcp/` 重构为接入与工具管理页，预览：`http://127.0.0.1:8892/inno/mcp/`。生成器为 `scripts/innovation_gateway_page.py`，交互为 `mcp-guide.js`，布局为 `mcp-center.css`。

- 远程只读服务地址、JSON/TOML配置预览与复制。
- 发现、深读、组包三类8项真实工具，支持搜索、分组筛选与参数展开。
- 检索、读取、核证、组包的调用顺序，保留任务描述复制与排障。
- 密钥只用于本次复制，预览只用占位符，不进存储、URL或请求；pagehide清空。
- 复制拒绝时使用原生对话框全选，不伪造成功；无虚假在线状态。

```sh
python3 -m unittest tests.test_mcp_center_077 -v
python3 tests/browser/mcp_center_077.py
```

5项静态测试、34项浏览器检查与全量524项固定环境回归通过，验收见 `00-项目管理/077-MCP接入中心布局重构验收.md`。

## 小好AI Agent角色

078 将通用机器人改为原创研究搭子：薄荷绿圆润身体、深色描边、探索笔记本与珊瑚色点缀。角色表达亲和、好奇和严谨，不把IP包装成模型能力。

- `ip-xiaohao.svg`：默认挥手，导航与找项目，使用 `?v=078` 防旧缓存。
- `ip-xiaohao-method.svg`：读方法，使用打开的书。
- `ip-xiaohao-evidence.svg`：核证据，使用放大镜。

```sh
python3 -m unittest tests.test_ip_xiaohao_078 -v
python3 tests/browser/ip_xiaohao_078.py
```

5项静态测试、19项浏览器检查与全量529项固定环境回归通过，验收见 `00-项目管理/078-小好AI-Agent-IP角色验收.md`。动态档案与资料页必须同时加载 `gooddesign_links()`，只替换导航HTML会导致SVG按原尺寸放大。

## 首页细节精修基线

080形成0.1.1本地候选。首屏采用探索导语与真实精选项目，项目统计独立且动态计算；筛选区去厚面板，项目卡显式重置旧核心`min-height`。清除按钮只在有筛选时启用，目录失败可真实重试，搜索焦点、按钮下压、分页禁用和空结果恢复完整。

```sh
python3 -m unittest tests.test_home_refinement_080 tests.test_gooddesign_portal_069 -v
python3 tests/browser/home_refinement_080.py
```

86项首页浏览器检查、9项专项与旧首页测试、546项全量回归通过。前后截图和报告在`output/design-080`，验收见`00-项目管理/080-首页设计细节与交互精修验收.md`。该基线只在`/inno/`生效，其他页面逐项评审后采纳，不自动全局换肤。

## 小好 Copilot 入口

081将入口移出导航DOM并固定右下角，避免导航毛玻璃改变fixed参照。桌面显示头像与名称，移动端为48px圆形；导览面板锚定入口上方。`replace_chrome`同时清理旧trigger/dialog，1238页各一个实例。ARIA、Escape、焦点返回、深浅主题与项目深链完整。

```sh
python3 -m unittest tests.test_xiaohao_copilot_081 tests.test_ip_xiaohao_078 -v
python3 tests/browser/xiaohao_copilot_081.py
```

43项专项、19项旧角色与552项全量测试通过。截图与报告在`output/design-081`，验收见`00-项目管理/081-小好右下角Copilot入口验收.md`。Copilot外观不代表模型对话或自动研究能力。

## 需求研究动态案例

082在`/inno/needs-v2/`增加12动作/五阶段动态演示，使用079真实来源，明确标注模拟与0次模型调用。`needs-live-demo.js`按事件索引驱动计划、当前动作、日志、证据和完成数，不使用虚假联网或打字机效果。支持暂停、继续、重播、关闭，减少动态直接完整显示，原需求草稿与导出逻辑不变。

```sh
python3 -m unittest tests.test_needs_live_demo_082 tests.test_needs_workspace_074 -v
python3 tests/browser/needs_live_demo_082.py
```

11项新旧静态测试、39项浏览器检查与558项全量测试通过。截图与报告在`output/design-082`，验收见`00-项目管理/082-需求研究DeepResearch动态案例验收.md`。真实Agent尚未接入，不能将播放进度解释为模型进度。

## 好设计馆资产与导航

083确认展馆图片404来自子路径相对资源解析，不是原图丢失。`build_gooddesign_site.py`生成真实`inno/museum/index.html`并设`base=/`，复用旧站98张封面与品牌资源；预览不再以根首页别名覆盖。旧馆顶栏和重复copilot移除，好设计馆加入统一主导航并正确高亮。导航标签保持单行，1023px以下使用两行局部滚动。

```sh
python3 -m unittest tests.test_museum_assets_083 -v
python3 tests/browser/museum_assets_083.py
```

40项展馆浏览器检查与563项全量测试通过，现存图片全部加载、0个404响应。截图与报告在`output/design-083`，验收见`00-项目管理/083-好设计馆图片恢复与主导航验收.md`。

## 中文主导品牌

084将`brand-logo.svg`从字母G改为中文“好”主体与珊瑚探索光点。导航/页脚统一中文好设计20px、GoodDesign 10px，资源使用`?v=084`防旧缓存。SVG使用系统中文无衬线，无新增依赖。共享导航、页脚、独立首页样板与动态档案同步。

```sh
python3 -m unittest tests.test_brand_chinese_084 -v
python3 tests/browser/brand_chinese_084.py
```

40项品牌浏览器检查与568项全量测试通过，截图与报告在`output/design-084`，验收见`00-项目管理/084-中文主导品牌Logo与字标验收.md`。

## Copilot 背景清晰

085将`dialog.gd-assistant::backdrop`设为透明且无模糊滤镜。打开小好时不再灰化或模糊其他区域，保留原生dialog、ARIA、Escape、焦点返回与项目深链。

```sh
python3 -m unittest tests.test_copilot_clear_backdrop_085 -v
python3 tests/browser/copilot_clear_backdrop_085.py
```

12项专项检查与570项全量测试通过，截图与报告在`output/design-085`，验收见`00-项目管理/085-小好打开时背景保持清晰验收.md`。

## 顶底栏统一隔离

086清理旧馆导航、旧footer和重复copilot，修正`gd-links/gd-footer-links`受旧通用nav样式污染的问题，并统一馆页面高亮。`replace_chrome`只移除带旧brand的导航，功能steps保留；`gd-live-*`组件footer保留，每页按`data-gd-chrome`计一个共享底部。

```sh
python3 -m unittest tests.test_chrome_isolation_086 -v
python3 tests/browser/chrome_isolation_086.py
```

34项专项检查与575项全量测试通过，截图与报告在`output/design-086`，验收见`00-项目管理/086-顶部与底部栏统一隔离验收.md`。

## 展馆首屏视觉品质

087将`foyer`和`page-hero`的蓝色渐变替换为低饱和石墨色，系统无衬线、珊瑚提示和清晰正文，移除径向光晕。`museum-hero.css`在旧内联样式后加载，仅馆首页与categories生效。

```sh
python3 -m unittest tests.test_museum_hero_087 -v
python3 tests/browser/museum_hero_087.py
```

34项专项检查与580项全量测试通过，截图与报告在`output/design-087`，验收见`00-项目管理/087-展馆首屏视觉品质精修验收.md`。

## 公共组件隔离与模型官方页

097统一公共导航、底部栏与`main#main`。`body > header.gd-nav`和`body > footer.gd-footer`是旧页面样式隔离基线，桌面导航65px；无`<main>`的旧页由`replace_chrome`自动建立正文容器，动态档案由`workspace_ui`补齐，不允许只保留失效的`href="#main"`。

模型官方页生成器为`scripts/model_official_097.py`，资源为`model-official.css/js`。三层架构和四种能力均有真实切换，使用真实项目图像和研究数据。模型被定义为领域智能系统，不宣称自主训练基础大模型。

```sh
python3 -m unittest tests.test_official_model_097 -v
python3 tests/browser/official_model_097.py
```

635项全量测试与52项线上浏览器检查通过，验收见`00-项目管理/097-全站设计统一与大模型官方介绍验收.md`。
