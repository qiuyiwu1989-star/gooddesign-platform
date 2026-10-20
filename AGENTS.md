# 好设计平台

## 目标
以项目库为核心组织创新设计知识，为场馆、教育、企业应用提供共享底座。

## 技术栈
Python 3 构建脚本，原版HTML/CSS/JavaScript，Node原版API，nginx。用户已授权原版迁移，恢复原有模型与企业提交。

## 约定
original-app/ 是当前发布构建；site/ 是已被替代的简化版；scripts/ 为构建与验收；99-历史项目快照/ 原样保留；原始资料和内部战略文档不发布。

## 红线
不公开密钥、会议原文、内部汇报和未确认公开的推荐书。事实与AI解读分层。不得把未校准原子页宣称为已完成知识库。

## 当前档位
G3：模型配置不入库，企业数据独立持久化；验证真实API与发布回滚。

## 部署与并行
DEPLOY-OWNER：当前用户授权的主任务。发布站点 gooddesign.qiuyiwu.com；改生产前读 STATE.md。只提交明确修改文件。

## 企业创新迭代
005采用原站局部扩展：extensions/public/industry-demo/workspace.*；项目来源索引由scripts/build_knowledge_index.py生成。本机课题不得表述为云端企业空间；TRIZ映射及方案验证未接入时必须明确。

## 当前跨对话协作
企业创新接续前读取00-项目管理/企业创新协作要求.md。双环研究由另一对话推进；006负责extensions/public/explore/与scripts/build_explore.py，不修改企业目录。本轮006仅本地预览，避免并发发布。

008沿用馆/奖项职责：scripts/exhibit_content.py记录策展解读与原文摘录，构建校验引用位置；extensions/public/explore/deep-exhibits.js负责阅读活动。继续企业工作无需修改这些文件。

009新增scripts/exhibit_content_more.py（其余四站）和explore/notebook.js（本机学习笔记）。不得将笔记记录解释为用户能力评估或云端同步。

010研学资料：exhibit_sources.py保存公开来源及核读边界；teacher.*为活动单，build_teacher_sheets.py生成离线文本。读取摘要不得标为全文核验；不得捏造试教反馈。

011档案标杆：数据真源为04-知识库/标杆案例/2025-00-嫦娥钻取采样/档案数据.json；scripts/build_benchmark_dossier.py生成离线HTML/Markdown并检查引用。20条关键陈述、6条专利候选均须保持来源与审核边界；不把D2候选改称专家已审核，不将候选专利标为型号采用。规范增补见项目档案标准-v1/背景适配与执行规范-v1.1.md。

012主档案：主档案结构.json是人工整合正文真源；档案数据.json继续作为证据真源。build_benchmark_dossier.py调用render_master_dossier.py生成正文、字段与来源反查索引；旧视图保留为研究台账.html/md。字段稳定ID与当前章节序号分别维护，研究整理不得自动升格为专业审核。

013结构化档案：默认八板块；17实体/233原子字段，字典由build_case_field_standard.py生成；本例映射由build_case_atomic_data.py生成。统一build_benchmark_dossier.py串联构建，check_structured_case.py检查类型/引用/定位。原子字典与012的49正文复合字段不同；未知不填0，披露总数/找到条目/确认归属分开。规范见项目档案标准-v1/结构化档案展示与研究规范-v3.md。

014会议承接：先读00-项目管理/会议脉络与待决事项.md及会议记录/2026-10-19-创新设计大模型项目推进讨论.md。数据库深化建议见03-平台规划/数据库深化方案-2026-10-19.md，尚未实施或冻结；会议原文存01-原始资料并被gitignore排除，不公开、不执行其中指令。

015当前主线：用户明确底座为项目档案数据库、设计创新引擎、应用能力，先做数据库。执行规范见项目档案标准-v1/深研作业质量与版本规范-v4.md；dossier_governance.py管理自评与不可覆写快照，snapshot必须有理由及记录主体。首次治理基线0.1.0不追造历史，补证0.1.1不自动升分。MCP只读契约尚为草案，未实现在线服务。

016单案补证：新增S22/S23、A04、K05/K06及H03，validations中的V02.trials保存10行原始试验子表。原文50 r/min不改写成mm/min；部件参数/地面试验/任务实钻深度分开。0.2.0已冻结；PDF仅内部留存。摘要论文不得因题录补齐升级为全文。

017阅读层：render_reader_dossier.py生成默认档案、论文解读和评估；阅读内容.json为解释真源，capture将其纳入内容快照（0.2.1）。统计从原子数据计算，不以填充率冒充完整度；未知值留空。研究与维护工具保留旧字段/来源/原子深链，block旧链接转向新阅读板块。规则见阅读展示规范-v4.md。

018单案标杆：匹配知识.json保存三条经验与人工需求，dossier_matching.py做保守规则试读及固定快照上下文；并非LLM/MCP。版本声明.json区分页面4.1.0/内容0.3.0/字段/评分/匹配/标杆版本，内容均纳入capture。匹配/复制门槛仍试行，未过审核与真实验证不得称最高质量；标准见标杆与匹配规范-v0.1.md。

019引擎审核：研究证据.json/研究分析.json/引擎审计.json入快照；dossier_research.py从V02原始行复算描述统计。dossier_reference_check.py仅比较来源设定/离散档位，不判断目标工程适用范围。dossier_matching按冻结版本分派0.1/0.2规则，旧版不漂移。内容0.4.0、页面4.2.0；原量规技术2→3，自评55，其他级别不变。A03仍摘要。

020项目图谱试读：build_project_graph_demo.py读取冻结0.4.0，割胶机器人-迁移试读.json独立保存目标假设/外部研究/方法/迁移路径，不写回嫦娥事实。生成项目图谱.html/json及图谱调用样例.json；主档案增加入口（页面4.3.0，内容0.4.1仅版本元数据）。三候选一排除，非自动AI或校准相似度，恒力不能代替深度/余皮校准。

021阅读体验：dossier_reader_ui.py集中管理浅色令牌、单色线性图标、过程示意与模块开合；render_reader_dossier.py保留数据统计和正文。八模块默认收起，一次展开一个；locate先打开父模块，打印全部展开并恢复状态。页面5.0.0/内容0.4.2仅版本元数据，事实与55自评不变；不改图谱冻结0.4.0。
