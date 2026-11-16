# 项目档案治理 v1：MVA、sources 与 claims

日期：2026-11-05  
规范：specs/100  
状态：本地试点，未改变现有研究真源和生产页面

## 1. 一份真源，三种用途

当前 `研究工作区/版本/research-*/档案.json` 仍是研究真源。本目录定义的 MVA 是由当前版本生成的治理投影，不能手改，也不与原档案并列维护另一套事实。

- **MVA**：把项目身份、来源、事实 claims、平台条目、质量状态和缺口放在同一版本边界内。
- **sources**：描述资料资产及其读取、归属、原件与衍生件关系。
- **claims**：只承载 `content_nature=source_statement` 的已知项目陈述。
- **平台条目**：`platform_metadata` 与 `platform_analysis` 单独保存，不计入项目事实。
- **人读／维护视图**：后续都从 MVA 与原研究真源生成，不分别填写数字。

## 2. MVA 不等于完成研究

`mva_ready=true` 只表示当前投影通过结构、引用和冻结证据检查，不表示：

- 原文陈述为真；
- 全文已由人核读；
- 原件性质已经人工确认；
- 项目研究已经完整；
- Agent 评估仍然有效；
- 专家审核或工程验证已经完成。

上述状态分别记录。默认 `human_read=false`、`expert_reviewed=false`、`engineering_validated=false`、`official_ingestion=false`、`semantic_review=false`、`quality_score=null`，只有真实记录才能改变。

## 3. 来源资产规则

1. `original` 是登记角色，不自动等于已确认原件；自动投影的 `original_verified` 恒为 `false`。
2. `readable`、`chunks` 是衍生资产，不能与原文件重复计为独立证据。
3. 原文件与可读件指纹相同只形成警告，不增加独立证据数量，也不据此自动删除文件。
4. 项目关系必须保留判断依据；项目直接来源、相关技术、共享参考和未解决归属不得混算。
5. 读取范围保留机器抽取、OCR、摘要、题录、未读等真实状态，机器可读不升级为人工核读。
6. 文件路径必须位于项目目录内，禁止绝对路径、`..` 和符号链接越界。

## 4. Claim 规则

1. 每条 claim 绑定 `project_id + research_revision + record_id + field`。
2. `claim_id` 是身份指纹，不随展示文案变化；研究版本变化后必须重新绑定档案指纹。
3. 每条已知事实至少有一条完整冻结证据：来源、原文件指纹、块编号、块指纹、逐字引文、引文指纹和读取范围。
4. 引文必须存在于指定证据块，且来源仍属于当前项目。
5. `platform_metadata`、`platform_analysis`、AI 解读与假设不得进入事实 claims。
6. 未知、未研究、冲突、待复评不生成已知 claim，不用空字符串或 0 代替。
7. 纯展示修订不改变 claim；事实、证据或边界变化必须建立新研究版本。

## 5. 门禁与输出

`archive_governance.py` 提供：

- `audit`：只读检查当前版本，输出 blockers、warnings 和指标，不写项目库。
- `build`：生成 MVA；若有 blocker，拒绝写入。
- `write`：写入 `研究工作区/治理/mva/<research-N>.json`，同路径同内容可重复，不同内容禁止覆盖。

门禁失败不会被包装成“已完成 MVA”。审计产物可以记录问题，但不能命名为已验收档案。

## 6. 文件

- `mva.schema.json`：MVA 总体结构。
- `source-asset.schema.json`：来源资产结构。
- `claim.schema.json`：事实 claim 与冻结证据结构。
- `scripts/archive_governance.py`：投影、校验、审计与不可覆盖写入。
- `tests/test_archive_governance_100.py`：规范、正反例和真实项目试点检查。
