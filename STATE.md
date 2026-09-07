# State

## 当前线上
- https://gooddesign.qiuyiwu.com/ 已恢复压缩包原版馆首页与交互。
- 主机yongle-nanjing；nginx静态+Node原API（loopback 3187）；systemd gooddesign。
- release：20260907T102228Z；current指向该release，公开根目录current/public。
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
