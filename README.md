# 好设计平台

[平台首页](https://gooddesign.qiuyiwu.com/) · [设计系统](https://gooddesign.qiuyiwu.com/design-system.html)

五入口：项目库、好设计馆、科技教育、智能助手、企业创新。原馆页面迁至museum.html，原有项目和工具地址保留。

当前建设：[设计系统v1](03-平台规划/好设计设计系统-v1.md)、[五板块结构](03-平台规划/五大板块结构定义-v1.md)。

- 来源快照：99-历史项目快照/，本地只读保留。
- 新功能源码：extensions/public/；平台模板：scripts/platform_design.py。
- 构建：python3 scripts/build_original.py；验收：python3 scripts/check_design.py。
- 发布：scripts/deploy.sh，自动检查、版本切换与回滚；运行细节见STATE.md。
- original-app/是发布构建，site/是已替代的早期简化版。
- 密钥与企业数据不入公开目录，线上模型沿用原服务。

设计系统覆盖公共外框和新组件，原课件/展项内部逐步迁移。资料覆盖与事实核验分开，所有新分析仍需证据和审核。
