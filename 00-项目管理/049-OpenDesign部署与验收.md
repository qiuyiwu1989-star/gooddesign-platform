# 049 OpenDesign部署与验收

2026-10-22。用户授权部署当前项目库，已发布受保护只读快照。

- 资料入口：https://opendesign.cc/inno/
- 嫦娥：https://opendesign.cc/inno/dossier/?project=2025-00
- 其他研究项目：2015-02、2017-01、2019-s10、2021-00、2021-01、2021-02、2025-02，替换project参数。
- 560题录、8研究版本；并非560完成档案，也不是8例均专家审核。

## 运行与范围
南京yongle-nanjing，独立systemd innovation-readonly，监听127.0.0.1:18776。代码/阅读依赖在/var/www/innovation-design/releases/20261022-049，current链接；私有资料在/var/lib/innovation-design/library，不在主站Web根。nginx仅新增/inno/专用include，不覆盖OpenDesign首页、设计包与既有MCP。

所有/inno/子资源经HTTPS Basic Auth，使用现有qiuyiwu账户与原有密码。专用/etc/nginx/inno.htpasswd从既有凭据复制，不把密码写进项目或交付说明。后续原账户密码变化需同步该专用文件。验收临时账户已删除。

这是单向发布快照，不自动同步本机更改。云端不启动watcher、OCR或模型任务，拒绝POST/PUT/PATCH/DELETE；本机8776仍承担上传/清洗/发布。API读取必要运行状态可能创建云端内部缓存/状态文件，不代表开放用户编辑。未搬本机.file-admin任务、模型日志和凭据，也未恢复旧automation。

## MCP
云端安装mcp==1.30.0，与现有FastMCP兼容。最初安装的2.x不兼容，验收发现后已固定v1，未修改现有MCP实现。远程通过授权SSH传输stdio，可用deploy/innovation-mcp-ssh.example.json；客户端须已有可用的yongle-nanjing SSH配置及密钥权限。无匿名HTTP MCP入口，不占用OpenDesign原/mcp/http。

## 验收
5项新增本地测试通过：子路径改写、外链与证据不变、写入动词拒绝、不启动watcher、nginx鉴权边界。

实际服务器HTTPS：匿名首页/API/脚本/档案/附件401；登录8档案、项目列表、脚本、资料与研究API200；560项目；真实原件下载200；写请求403；OpenDesign主站200。服务active，健康表明cloud_read_only=true、watcher_running=false。初次阅读漏字段字典已补齐；已包含标准、方法库、标杆档案和既有联动报告依赖。

真实SDK经SSH：发现14工具，8项目研究版本/记录数读取全部通过；与本机核对一致。

真实公网浏览器：嫦娥与混联机器人三视图切换、390px无横向溢出；资料管理可加载560项目选项；页面脚本错误与/inno/资源失败均为空。修复部署提示条inline-style CSP冲突，保持nonce策略。

产物与实际HTTP/MCP报告：output/deploy-049/（私有，不入Git）。首次传输release/library SHA验证通过，后补依赖与提示条修订另列最终文件指纹，不能把初次打包SHA视为最后完整release指纹。

## 回滚与后续
nginx原配置备份/var/lib/innovation-design/nginx-backup-049.conf。如需撤回，恢复该配置，nginx -t后reload；停用innovation-readonly，保留私有资料。首次发布此前无current版本；未来更新创建新release并原子切current，禁止覆盖用户研究数据。

后续：全库进度总览和MCP调用策略文档仍未交付；云端写入/同步/多用户权限与HTTP MCP需独立实施，当前不宣称完成。
