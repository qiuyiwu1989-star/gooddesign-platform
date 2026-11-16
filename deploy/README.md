# 好设计代码与部署位置

## 2026-11-06 主项目区当前发布

`opendesign.cc/inno/` 当前为112：应用中心控制台版上线。静态站、方法库、档案运行均为`20261106-112`，整体回滚`20261105-097`（运行回滚`20261105-097-fix1`）。本轮运行时仅更新`scripts/app_center_096.py`，静态仅`inno/apps/index.html`及两个注册规范JSON；阅读区重构由档案治理线进行中、未纳入。打包与激活脚本为`scripts/package_inno_release_112.py`、`scripts/activate_inno_release_112.py`，流程同097三段式。根分区经瘦身约4.1G可用（55个旧release已备份至本地归档后删除），后续发布仍需先确认空间。

核对日期：2026-10-12。

| 项目 | 统一位置 |
|---|---|
| GitHub | https://github.com/qiuyiwu1989-star/gooddesign-platform （私有，main） |
| 本地活跃仓库 | /Volumes/邱懿武/邱懿武认知大脑/好设计平台 |
| 主机 | yongle-nanjing / ubuntu@146.56.239.22 |
| 服务基目录 | /var/www/gooddesign.qiuyiwu.com |
| 当前网站文件 | /var/www/gooddesign.qiuyiwu.com/current/public |
| 发布版本 | /var/www/gooddesign.qiuyiwu.com/releases/ |
| 回滚记录 | /var/www/gooddesign.qiuyiwu.com/backups/ |
| API 服务 | gooddesign.service，127.0.0.1:3187 |
| 服务入口 | /var/www/gooddesign.qiuyiwu.com/current/server.js |
| 企业提交数据 | /var/lib/gooddesign/inquiries.jsonl |
| 私有配置 | /etc/gooddesign.env |
| nginx | /etc/nginx/sites-available/gooddesign.qiuyiwu.com |

## 2026-10-12 收编

服务器实查 current 指向 `20260911T030604Z-evidence-stand2`；服务为 active。
本地与线上存在版本差异，历史线上版本无法可靠倒推出 Git SHA，不虚构对应关系。
本次建立 GitHub 代码基线及固定发布入口，未覆盖生产页面。
服务器基目录已符合项目独立目录要求，无须搬动运行文件。

## 日常流程

1. 修改 extensions、scripts 与规划文件，按需同步 original-app。
2. 验证、审阅差异，显式提交文件并 `git push origin main`。
3. 执行 `scripts/deploy.sh`，将已推送提交中的 original-app 发布为新版本。
4. 检查首页、API 与修改的实际交互。发布版本的 REVISION 记录 Git SHA。

发布脚本拒绝未提交的受控文件改动，以及未进入 main 的提交。
不在生产 current 中直接编辑代码，不把服务器私有配置和企业数据回拉到代码仓库。
历史快照与原始资料只在移动硬盘保留。旧的全量重建流程需要这些本地资料。

## 回滚

查找 backups/<版本>.previous 指向的旧版本，原子切换 current 后重启 gooddesign。
需要确认没有其他发布正在进行。nginx 与 systemd 配置本次保持不变。

## 2026-11-12 好设计馆独立域名

`haoshejiguan.com`（含 www）已接入：`/` 直出好设计馆 museum 页，`/inno/` 镜像主项目区全部路由（复用现有 snippet，鉴权继承）。配置 `deploy/nginx-haoshejiguan.com.conf`，证书 Let's Encrypt 至 2027-02-10。泛解析未配。详见 `specs/116`。

## 2026-11-12 主域切换与118发布

平台主域名为 `haoshejiguan.com`；`opendesign.cc/inno/` 页面 301、API 308 永久跳转（配置 `deploy/nginx-opendesign.cc.conf`，备份 `.bak-20261112`）。当前发布 `20261112-118`（static/methods/runtime/mcp 四 base），回滚见 `release-backups/20261112-118`。打包/激活：`scripts/package_inno_release_118.py`、`scripts/activate_inno_release_118.py`。构建后上线前必须 `scripts/site_audit_118.py` 达到 P0=0 P1=0。

## 2026-11-12 119发布

当前发布 `20261112-119`（static/methods/runtime；mcp 保持 20261112-118）。方法页密度、档案孤立符号、CSS 版本化与 canonical 上线。打包/激活：`scripts/package_inno_release_119.py`、`scripts/activate_inno_release_119.py`（支持空 mcp 清单）。

## 2026-11-13 120 去 /inno/ 路径改造

当前发布 `20261113-120-fix1`（static/methods/runtime；mcp 保持 20261112-118）。页面全部走根路径（/projects/、/methods/、/apps/、/needs/、/report/、/dossier/、/canvas/、/login/ 等），旧 /inno/ 页面 301。路由三层：`deploy/nginx-inno-root.conf` + `inno-readonly.conf`（技术路径）+ `nginx-method-library.conf`；nginx 备份 `.bak-20261113`。打包/激活：`scripts/package_inno_release_120.py`、`scripts/activate_inno_release_120.py`（fix1 同名后缀）。

## 展厅演示应用

`https://haoshejiguan.com/expo/` 嘉善展厅演示（121）：单文件离线 HTML，服务器路径 `/var/www/expo/jiashan/index.html`（独立目录，不属于 release）。更新：本地 `scripts/build_expo_jiashan.py` 重建（先删 output 旧文件）后 scp 覆盖服务器文件即可，无需发 release。

## expo agent 模型配置

`/etc/innovation-expo.env`（root:www-data 640）：2026-11-14 起为阿里云百炼 compatible-mode（deepseek-v4.1-flash-1017），原火山方舟配置备份 `.bak-20261114`。密钥只存在服务器该文件，不进仓库与文档。
