# 好设计平台

原版网站已上线：[好设计馆](https://gooddesign.qiuyiwu.com/)。以用户提供压缩包为基线，保留既有视觉、页面与交互，后续在此基础上迭代。

- 当前信息结构与定位：[信息架构与平台定位-v2](03-平台规划/信息架构与平台定位-v2.md)
- 运行状态：[STATE.md](STATE.md)；待办：[TASKS.md](TASKS.md)
- 原版迁移：[spec 002](specs/002-original-migration.md)
- 原快照：99-历史项目快照/（本地保留，不含入公开网站）
- 发布构建：original-app/；旧site/是已替代的简化版本。
- 日常发布：`scripts/deploy.sh`（仅发布已提交且推送的 `original-app/`）。
- 历史重建：`python3 scripts/build_original.py` 依赖本地忽略的历史快照；GitHub 克隆后可直接运行仓库内的 `original-app/`。
- 后端配置保存在服务器私有文件，企业需求独立持久化。原始资料、会议、内部方案不发布。

网站包含560个项目档案、知识页、数字馆、互动展项、教育课例、教师工作台、助手与企业入口。现有知识与教学内容成熟度不一，后续以来源、审核和复用验证推进。

## 2026-09-07 用户反馈后的恢复
用户认为原版更好。已恢复设计系统改版前的原站，保留双环Demo。004设计系统及平台新外框退出生产，只保留本地草案；构建与部署亦恢复原版路径，防止再次覆盖。后续以原版视觉和节奏为准做局部改进。


## 代码与服务器统一位置

- GitHub（私有）：https://github.com/qiuyiwu1989-star/gooddesign-platform
- 活跃本地仓库：`/Volumes/邱懿武/邱懿武认知大脑/好设计平台`
- 分支：`main`。代码先提交、推送，再从提交生成发布包。
- 服务器：南京腾讯云 `146.56.239.22`，SSH `yongle-nanjing`。
- 线上地址：https://gooddesign.qiuyiwu.com/
- 服务目录：`/var/www/gooddesign.qiuyiwu.com/`，`current` 指向某个 `releases/` 版本。
- 运维位置及操作：[deploy/README.md](deploy/README.md)。

## 克隆后运行

```sh
cd original-app
HOST=127.0.0.1 PORT=3187 node server.js
```

模型功能需要运行环境配置。服务器密钥和企业提交数据独立保管，不随仓库同步。
`extensions/` 为增量开发源文件；`original-app/` 为完整可运行发布版本，提交前同步相应修改。
当前版本包括本地馆/教育扩展，生产发布版本单独记录；创建仓库并不自动发布页面。
