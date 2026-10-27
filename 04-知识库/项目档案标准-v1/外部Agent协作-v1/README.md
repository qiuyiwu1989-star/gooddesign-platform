# 外部Agent资料收集与入档协作 v1

入口文件：给收集Agent的任务书.md（转发它）；项目派单索引.csv（560个真实项目及投递路径）；模板/（复制字段）；接收加工流程.md（主Agent执行）。空目录代表可投递，绝不代表已收集完成。

## 唯一落点

```
04-知识库/项目库/<真实项目ID>/
├── 01-项目档案.md、02-资料与解读.md、03-档案评估.md   # 正式，收集Agent不改
├── 来源/、数据/、研究工作区/、版本/、资料归属.json     # 正式，收集Agent不改
└── 04-深研素材/
    ├── 01…09、原始信息/、04-图片素材/               # 豆包已有包原样保留
    └── 外部投递/
        └── <日期-Agent-主题-序号>/                  # 每次新建，禁止覆盖
            ├── batch.json
            ├── sources.jsonl
            ├── claims.jsonl
            ├── queries.jsonl
            ├── 交接说明.md
            ├── 原件/
            ├── 可读件/
            └── 图片/
```

JSONL一行一个JSON对象，不使用代码围栏。路径一律相对批次根，如原件/SRC001.pdf，禁止绝对路径、../、符号链接；SHA256对实际字节计算。批次ID只能3–96位英文字母、数字、短横线；同主题另一轮另起序号。多个Agent不能共写一个批次。

## 字段约定

sources 的files例子：
```
[{"path":"原件/SRC001.pdf","role":"original","sha256":"实际64位SHA256"},
 {"path":"可读件/SRC001.txt","role":"readable","sha256":"实际64位SHA256"}]
```
下载原件保存原字节，不把整理Markdown叫原始网页全文；转换记录写工具/方式、页码范围、OCR未核状态。read_scope只能metadata/abstract/excerpt/fulltext/ocr_unchecked/unread；fulltext须有原件+可读件，是否真全文仍由接收方核读。摘要、摘录可以交，但不得改成fulltext。

access_status：downloaded/link_only/blocked/failed。获取失败允许files为空，作为线索保留。source_type记录来源性质，不是“真实性等级”。公开来源也不自动获得图片/全文再发布权。

project_relation：project_source（原文明确对应项目对象，但仍待主Agent确认）、related_technology（同团队/同路线等）、shared_reference（多项目背景）、unresolved（未确定）；必须写relation_basis。采用/权属/奖项归属不能由相关性推定。

候选事实 kind=source_statement 时必须有 evidence，例如：
```
[{"source_id":"SRC001","readable_path":"可读件/SRC001.txt",
  "quote":"从可读文件原样复制的完整句段，不改字和单位",
  "locator":"PDF第5页，3.2节，第2段"}]
```
kind=ai_analysis要明确假设和限制，不能借事实标签入库；kind=lead可以没有引文。数值的对象、单位、工况、测试/仿真/预测身份分别写清，未知用null或“未知”。八模块：身份与范围、需求与系统、设计思路、指标与验证、专利与论文、历程与故事、应用与价值、质量与维护。无需为每个模块编满内容。

queries只录实际执行，outcome只能found/no_result/blocked/failed。无结果、访问受限也是可用交付，但不可叫全文已读。sources引用去重后计数，重复URL、同原件不同文本版本、项目来源登记条目与独立来源数分别统计。

## 本机初始化与机械核验

在好设计平台根目录：
```
.runtime/pipeline/bin/python scripts/agent_intake.py init 2025-04 20261027-doubao-patents-01 --agent Doubao --topic 专利及项目关联
.runtime/pipeline/bin/python scripts/agent_intake.py validate "04-知识库/项目库/2025-04/04-深研素材/外部投递/20261027-doubao-patents-01"
```
初始化不会代填研究成果，空draft不能通过。提交前batch.status改submitted。validate只读、不会导入正式库或联网验证事实；mechanical_pass_pending_content_review只是结构通过，后面仍须核读。失败修本批次，不修改其他批次。不会Python的Agent可手动依样创建；只有Markdown能力的先交可读表格，交接标明待格式转换。

## 豆包现有33包

原目录不搬、不覆写，已做初步数量/抽查，报告在output/research-051/incoming-doubao-2025。将其视作legacy待核素材，不逼迫重做264文件。主Agent后续映射来源/阅读范围、纠错与选取候选；收集Agent可引用现有文件为线索，不能把旧摘要复制为新取得原文或重复计新增。

原件私有；正式页面/MCP只经主Agent按现行审核流程发布。浏览器/外部Agent不能访问本盘时，用同结构压缩包交用户转存，没有自动上传服务。磁盘离线应停写，需暂存时仅按用户指定待归位区标记，不静默另建副本。
