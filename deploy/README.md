# 好设计代码与部署位置

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
