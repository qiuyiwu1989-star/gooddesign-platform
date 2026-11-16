# 116 好设计馆独立域名接入（haoshejiguan.com）

用户已将 haoshejiguan.com 的 @、www、泛解析三条 A 记录指向 146.56.239.22（2026-11-12 18:31）。本次把它接入为好设计馆的独立域名。

## 方案

- `/` 直接服务好设计馆（museum），不做跳转：域名即馆。
- `/inno/` 全量镜像主项目区路由（复用 inno-readonly.conf 与 method-library.conf 两个 snippet）：馆内绝对链接与 `<base href="/inno/legacy/">` 资产在本域名下原样可用；档案、MCP、画布试点的鉴权逻辑原样继承（匿名访问 /inno/canvas/ 仍 302 登录）。
- 配置文件入库：deploy/nginx-haoshejiguan.com.conf，安装到 /etc/nginx/sites-available/ 并软链启用。

## 过程与坑

1. 先装仅 80 端口的引导配置（证书不存在时 nginx -t 会因 443 块引用证书失败），webroot 方式申请证书。
2. certbot 因服务器存在两个 ACME 账号要求显式 `--account`，选 acme-v02 生产目录下账号签发成功，有效期 2026-11-12 至 2027-02-10，certbot.timer 自动续期。
3. `location = /` 用 alias 指到文件会被追加 index 指令变成 `index.htmlindex.html` 报 500；改 root + try_files 修复。
4. 未遇 ICP 拦截：域名 HTTP 直连返回本机 nginx 响应。

## 验证

- `https://haoshejiguan.com/` 稳定 200（29533B，与 /inno/museum/ 同字节），www 同；HTTP 301 到 HTTPS。
- /inno/、/inno/museum/、/inno/dossier/?project=2025-00 均 200；/inno/canvas/ 匿名 302 登录。
- 浏览器桌面 1440 与移动 390 截图通过（移动首截为工具设备切换过渡假象，重截单列正常），截图 output/design-116。

## 未做

- 泛解析存在的 *.haoshejiguan.com 未配（通配证书需 DNS-01，暂无必要）。
- 站内链接仍指向各功能绝对路径 /inno/，跨域返回 opendesign.cc 的场景未强制统一；是否把 haoshejiguan.com 提升为平台主域名单独决策。
- 未提交 Git。
