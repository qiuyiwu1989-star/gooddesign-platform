# 120 去 /inno/ 路径改造（20261113-120-fix1）

117 阶段二主体：好设计馆主域名下，用户页面从 /inno/* 迁到根路径，旧路径全部 301，技术路径不动。

## URL 结构

| 页面 | 新路径 | 旧路径（301） |
| --- | --- | --- |
| 好设计馆 | /（116 已完成）与 /museum/ | /inno/museum/ |
| 项目库 | /projects/ | /inno/、/inno/projects/ |
| 方法库 | /methods/（含 /methods/methods/Rxx.html） | /inno/methods/ |
| 应用中心/案例 | /apps/、/cases/ | /inno/apps/、/inno/cases/ |
| 需求研究 | /needs/（服务 needs-v2 内容） | /inno/needs/、/inno/needs-v2/ |
| 数据总览 | /report/ | /inno/report/ |
| 关于/模型/指南/MCP | /about/、/model/、/guide/、/mcp/ | /inno/ 同名 |
| 档案 | /dossier/ | /inno/dossier/ |
| 画布 | /canvas/（API 在 /api/rc/） | /inno/canvas/ |
| 登录/登出 | /login/、/logout/ | /inno/login/、/inno/logout/ |
| 企业工作台 | /loop/ | /inno/loop/ |
| 资料管理 | /admin/ | /inno/admin/ |
| 研究工作区 | /innovation/（此前线上 404，本轮修复路由） | 无 |

不动：/inno/portal/（资产）、/inno/legacy/（旧页）、/inno/api/ 与 /inno/mcp/api（MCP 客户端）、/inno/canvas/api/（画布 API 兼容）。

## 实现分层

- **nginx**：deploy/nginx-inno-root.conf（根路径静态 exact + 运行时反代 + @root_login）；haoshejiguan.com server 级 rewrite 21 条做 /inno/ 页面 301（负向断言保护 /inno/canvas/api/）；deploy/nginx-method-library.conf 改为 /methods/ 直出；旧 inno-readonly.conf 保留服务技术路径。配置备份 .bak-20261113。
- **chrome**：gooddesign_chrome 导航/底部/助手动作全换根路径，品牌首页指 /（好设计馆）。
- **页面生成器**：app_center/data_report/info_pages/gateway_page/model_explorer/model_official/project_portal/needs_research/build_method_reader/workspace_ui 的页内链接统一迁移；档案"整理与查看研究版本"指 /projects/。
- **鉴权**：innovation_auth Cookie Path=/inno → Path=/（否则根路径下不带 Cookie 登录失效）；登录表单 action=/login/；safe_next 接受任意站内相对路径，默认 /loop/；@root_login 302 到 /login/?next=。
- **画布前端**：/canvas/ 下 RC_API 走 /api/rc/（原有分支逻辑正好适配）。
- **canonical**：1248 页 canonical 同步到根路径；审计器 ROUTE_MAP 与新结构同构，P0=0/P1=0 保持。

## 踩到的坑

- /projects/ 上线首小时"研究整理版"显示"-"：portal.js 用相对路径 fetch('catalog.json')，在 /inno/ 下碰巧正确，迁到 /projects/ 后 404。改绝对路径 /inno/catalog.json，以 120-fix1 发布。相对路径取数在路径改造中必然踩雷，迁移类任务必须检查全部 fetch/相对 API。
- nginx proxy_pass 带不带尾斜杠决定路径是否保留（/innovation/ 必须保留前缀）；运行时同时挂载 /x 与 /api/x，/inno/api/ 的既有映射依赖这一点。
- needs-research.conf 原先揭示 /inno/needs/ 实际服务 needs-v2 内容，/needs/ 保持同语义。

## 验证

- 733 项全量回归通过（9 个路径断言随结构更新）；审计 P0=0/P1=0。
- 线上：14 条根路径 200；/inno/、/inno/methods/R50、/inno/dossier 301 正确且保留查询串；canvas 匿名 302→/login/?next=/canvas/；登录 POST 200 非 403；MCP 无凭证 401；技术路径（portal CSS、legacy、mcp/api）不受影响；旧域 opendesign.cc 301 链终态落在新根路径 200。
- 桌面 1440 与移动 390 浏览器截图通过（移动截图为工具设备切换合成假象，布局已确认）。

## 未做

- 运行时 opendesign_readonly PREFIX 仍为 /inno（运行时页面内部链接经 301 跳转，一次跳跃可接受；下一轮可翻转为 ''）。
- 档案维护工作区（/inno/ 下鉴权区）保持原路径；cos 迁移与磁盘（1.1G 可用）仍待办；未提交 Git。

## 追记（2026-11-13 fix2 与浏览器套件收口）

- Playwright chromium 安装完成后补齐脚本化浏览器回归：chrome_isolation_086(34)、design_refinement_096、dossier_reading_094(41)、data_report_075(36)、archive_reading_100(165) 全部通过。本地浏览器环境 = preview_gooddesign_site.py:8892（已同步根路径映射）+ research-100/previews:56061。
- 套件暴露的滞后问题已修：apps.json 应用路由全部迁根路径（registry/schema 同步，catalog const 改 /apps/）；portal.js 项目卡改 /dossier/、catalog.json 改绝对路径；075/094/096 三个浏览器套件断言随结构更新；/apps/ 改 alias 前缀使 registry.json 与 application.schema.json 可达。
- 访问级别变化（有意）：/inno/apps/registry.json 原来落在鉴权 catchall（302 登录），120 后经 rewrite 到 /apps/registry.json 公开可读，符合 111 规范"Agent 可读"的设计意图。
- 069/080/111 单测断言同步绝对路径与新 catalog 常量。733 项全量回归 + 5 个浏览器套件全绿。
- 发布 20261113-120-fix2（static/methods/runtime，mcp 保持 118），回滚材料 release-backups/20261113-120-fix2。
