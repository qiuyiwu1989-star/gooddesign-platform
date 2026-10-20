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

## 项目档案本地预览

嫦娥标杆位于`04-知识库/标杆案例/2025-00-嫦娥钻取采样/`。运行`python3 scripts/build_benchmark_dossier.py`重建；该目录启动HTTP服务（本机8773）后打开`档案.html?v=4.0.0`。默认阅读项目档案，资料解读与评估独立查看，研究工具在页尾。解释真源为`阅读内容.json`，原始研究/正文/原子数据真源保持分层；版本治理见标准目录。此页面尚未发布生产。

018本地阅读更新为`档案.html?v=4.1.0`。可从`#reader-experience`看设计经验，从`#reader-versions`看版本分类。标准见`04-知识库/项目档案标准-v1/标杆与匹配规范-v0.1.md`；`匹配调用样例.json`为人工需求的固定版本上下文示例，不是在线引擎。

019本地预览：`档案.html?v=4.2.0#reader-engine-audit`查看12维审计；`#reader-research-depth`查看来源工况与派生统计。补证、规则与局限见`创新引擎审计与工况匹配-v0.2.md`。本轮未部署生产。

020：`项目图谱.html`演示嫦娥经验如何关联割胶任务，`档案.html?v=4.3.0`顶端可进入。`python3 scripts/build_benchmark_dossier.py`会一并重建；`build_project_graph_demo.py`可单独生成。应用数据是`割胶机器人-迁移试读.json`，与源项目事实隔离；源内容固定0.4.0。
