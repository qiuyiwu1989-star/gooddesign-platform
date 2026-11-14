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

022布局修正：reader/library/assessment共用toc-reader与同一正文网格；侧栏资料/评估入口同步aria-current。研究工具的宽屏布局保留。

023文档结构：后续建档先读项目文档文件结构规范-v1.md及模板/项目文档标准模板-v1；三份阅读文档+数据/来源/版本。嫦娥项目文件目录.md映射现有文件，不搬真源；新模板尚未接入专用构建，不能宣称复制即生成站点。

024素材管道：project_pipeline.py bootstrap/scan/watch/fetch/read/search/retry建立私有项目库及分层来源读取，入口为素材清洗管道使用说明-v1.md。运行库04-知识库/项目库与01-原始资料/项目投递箱均不入Git。机器转换不等于核读/事实确认；人工改过的MD不覆盖，生成稿进待合并。ingest修订与深研版本分开；MCP协议服务未实现，不能把internal_local标签当成远程ACL。

025独立项目入口：OpenDesign项目区/创新设计平台为符号链接导航，唯一活跃代码仍在好设计平台，禁止复制为第二份工作副本。deploy/innovation-project.json及03-平台规划/独立项目区与域名迁移方案-20261020.md记录建议/实际边界；opendesign.cc/innovation/及候选域名尚未上线。

026入口已由用户确认为opendesign.cc/inno/（取代025暂定/innovation/，未曾部署）；网站结构见网站信息架构-v1.md。主导航首页/好设计奖/项目库/好设计馆/科技教育/企业创新，三阅读视图共享项目ID；底层引擎与MCP不占用OpenDesign已有接口。

027预览：extensions/inno/与build_inno_preview.py构建output/inno-preview/inno（忽略入Git），独立8775预览。只导出原站公开字段/封面及嫦娥读者HTML，普通案例未评分，嫦娥不改事实；不可复制私有原件/快照。馆/教育/企业为入口页并标明原站外链，无新增API；生产发布仍未执行。

028AI推演：用户明确允许标记的推理补充。AI推演.json独立存储、绑定0.4.2证据并纳入capture；dossier_reasoning.py校验/展示4条应用假设，类型/前提/边界/验证明确。页面5.1.0/内容0.5.0，事实/原子/55自评不变。真实合作、许可、专利/参数/收益等不由AI猜填；规范见AI解读与推演规范-v1.md。

029机制与回流：机制解读.json独立保存六项AI解读，dossier_mechanisms.py校验冻结证据与来源；关联探索.json只索引AI推演四设想，暂无目标建档或验证。设计思路聚焦原项目机制，具体应用/规则试读移入应用与价值的折叠关联探索。页面5.2.1/内容0.6.1，0.6.0为来源索引修正前中间记录；55自评不变。机制知识与关联回流规范-v1.md定义未来审核回流流程，当前不宣称流程已自动运行。

030今日接续：2026-10-21工作计划在00-项目管理/2026-10-21-工作计划.md；本轮仅重启8775预览和列计划，后续工作尚未实施，先等待用户走查反馈再依优先级推进。

031后台核对：2026-10-21恢复project_pipeline.py watch本地监听。网页上传/深研调度/语义审核后台尚未实现，方案在03-平台规划/研究入库后台-现状与建设方案-20261021.md；不要把562已转换来源当作全库深研，或把心跳文件当永久服务。

032论文资产：私有库2025-00/论文原文管理/论文原件清单.json与管理HTML链接原件/清洗文档。A01 HTML、A03十页PDF已入管线，A04既有PDF去重；A02下载受限仍待全文。核读标签与获取状态独立，不能因机器抽取把A03升为全文已核读。见00-项目管理/032-论文原件归档结果.md。

033文件后台：scripts/file_admin.py及extensions/file-admin/服务127.0.0.1:8776，接现有私有库/投递箱；Host/Origin/CSRF校验、异步任务、上传/URL/筛选/下载/文本及PDF图像预览。双击scripts/启动资料后台.command。不得暴露公网或混入8775公开构建。嫦娥48文件含23来源说明，四论文原件齐备（A02七页扫描PDF需OCR，研究核读仍摘要）；下载状态不提升事实/评分。说明在extensions/file-admin/README.md。

034专利资产：私有库2025-00/专利原文管理/专利原件清单.json关联P01—P06六PDF（47页，四扫描待OCR）及四检索网页。8776新增专利分类、公开号和项目关联提示；并非获奖项目正式完整成果清单，不升格现权属/法律状态/实际装机。原文下载/翻页与解读核读分开，事实和55自评不变。

035图片素材：archive_case_images.py从已存网页及论文/专利PDF归档图片，私有索引2025-00/图片素材/图片清单.json记录出处/页码/提取方法/去重。当前144项（59网页候选、45PDF嵌图、6附图页、34扫描页），143可预览，1原图损坏保留字节，另1失败链接。8776新增图片分类/子类型/缩略图和PNG预览；有效本地上传图自动分类。衍生页不称独立插图，候选语义/再发布授权未确认。

036归属治理：project_ownership.py过滤实时管线/文件API/下载范围；project_pipeline新快照冻结归属，旧未登记版本标historical_unfiltered。私有2025-00/资料归属.json当前v2：172项目资料、9公共参考、9移交2015-02、6配图待确认。curate_change_ownership.py为单次人工规则纠错，不能当全库自动分类；不覆盖已有归属。项目检索按原题录补关键词/年份/奖项，筛选不自动切项目。六阶段规范见项目归属与清洗提炼管线-v0.1.md，自动字段提炼/审核尚未接通，先完善嫦娥不开展下一项目深研。

037私有交接：build_case_handoff.py按当前归属导出output/handoff/（忽略Git）；check_case_handoff.py验证完整性/引用/读取。交付包标准只读示例非MCP服务；割胶图谱另列应用试验，公共/移交/待确认原件不入包；保留必要外部参考题录。完整历史snapshot未交付，不据随包manifest宣称历史链可验。

038管线v1：先读项目档案标准-v1/可运行档案管线-v1.md。research_workflow.py负责OCR/证据候选/审核/不可覆盖发布，file_admin统一投递监听；archive_mcp.py为已实现本机stdio只读八工具，v0.1草案保留。原人工底稿0.6.1不覆盖；管线research-000001为独立序列，复杂字段可人工/Agent提交，规则覆盖有限，OCR不升格核读，发布不升55分。依赖固定在requirements-research-pipeline.txt和外置盘.runtime；旧启动入口转统一脚本。

039方法库：04-知识库/创新方法库为v0.1结构规范与空目录（0方法）；方法卡区分原典/改编/AI解释，输入、步骤、知识调用、产物、边界及评估逐项定义。属于引擎资源，保留三板块架构；未接方法MCP/自动调度，应用运行记录不混入源项目事实。

040三方法：创新方法库已登记IM-PD/FA/CA-001三张1.0.0平台改编卡、16步骤；innovation_methods.py分层读/校验，run_method_case_demo.py做固定模拟需求SDK检索与本轮编写分析的重放，不冒充通用LLM推理或研发团队实际方法史。/methods/四视图及固定重放，方法MCP新增三工具合计11；应用记录在忽略的output/innovation-runs。结构/证据/交接/查询指纹与硬约束可校验，企业目标效果仍未验证。

041工作区减负：workspace_ui.py统一8776的档案/资料/创新研究入口；/dossier/仍读人工底稿，研究发布版另列。文件/审核/记录分视图，文件分页/原文优先，研究三视图/三阶段/原位证据。HTML仅可信应用模板使用逐响应nonce；原始HTML仍附件下载，禁止放宽为unsafe-inline或通用私有静态文件服务。历史运行不覆写，当前阅读层6.0.0，不改变数据评分或推理能力边界。

042整理引导：资料管理为文件/整理入档/任务进度。workflow.js以三步组织选资料、对照原文决定、预览后保存研究版本；采用是用户逐项决定，不自动审核。publish可选expected_candidate_ids在库锁内校验预览集合，旧调用仍兼容；展示底稿不自动覆盖。研究入口更名应用案例，当前固定模拟企业场景，方法/原始事实不改。操作见042-资料整理操作说明.md。

043资料管家方向：正常流程改为资料投放→Agent持续整理→合格内容自动研究入档→人工处理例外。本轮仅新增/api/automation与后台状态概览，读取活进程/巡检/当前项目队列；semantic_agent_connected与automatic_publication均false。完整能力与准入见043-资料管家与自动入档方案.md及specs/043，不把OCR/规则监听称完整Agent，不自动通过历史候选。

044十小时：用户2026-10-22 01:18授权十小时其他项目深研与管家建设，续接读specs/044及00-项目管理/044-十小时执行与验收.md，自动跟进ID automation，先按最近一次10点验收、09:45冻结，最迟11:18停新增。archive_steward.py为SQLite持久增量/租约/有限重试/自动准入与选批发布；深读来自外部Agent提交，尚无内置LLM。API/后台概览真实显示，2015-02/2017-01首次research-000001已发布55项更新，初始研究未完成。新项目steward_dossier_ui.py读研究版，嫦娥仍人工标杆。切勿把2019-s10 FAST馈源舱混成整台FAST；多项目评分未评，第一版通用导出说明中沿用55的文本需以后续有实质新增的版本更正，旧版不可覆盖。

044b续接：Steward0.2新增持久fetch与含清洗指纹任务键；source_reclean.py生成不可覆盖HTML边界修订并可从中断恢复，图片表格不假装HTML可还原。蛟龙表1原图/逐行验证数据已保存（CORE-LAB-TABLE-1/0.1.0），正文与表的72/82mm和8.4/10min差异未裁决。两例当前research-000004/000003，具体数量及复兴一手论文新任务66—69见044执行文档末尾。评分/专家状态未升级，后台无内置LLM。

044c：资料管家0.3.0的pause/resume为全库设置，已运行任务先结束；retry仅failed且项目相符，旧失败状态保存在SQLite controls表，不对冲突/待Agent强行重试。POST /api/steward-control沿用防跨站检查。复兴两篇2020论文进入research-000004，论文索引与私有批次见044执行文档；日期/统计差异不强行统一，质量未评。当前8776服务会话53565；重启前先暂停并确认持久/旧任务均空闲。

044d：Store.submit(fetch)及页面/api/fetch共用Steward持久下载，任务列表合并jobs.json历史与steward-N编号，只允许failed重试；相同项目URL跨标题/处理器复用旧任务。新下载不写旧jobs.json。archive_case_images.run可限制source_ids并支持关联PDF；复兴23工程图+2shared装饰原件，22网页下载失败留痕。当前8776会话78183。深度Agent/评分边界不变；下步八模块阅读综述、具体缺口及任务范围治理。

044e：research_reader_notes.py冻结八模块AI导读，路径研究工作区/阅读导读/research-N/语义版本，校验档案哈希和本模块记录引用，JSON/MD/manifest原子落盘；新研究版不自动继承旧稿。steward_dossier_ui默认短导读+折叠事实/缺口，仍三视图同目录。MCP概览可固定revision并附导读，来源数量声明当前规模；不是新事实/评分或专家结论。当前两例research000004+导读0.1.1，8776会话6754。后续打包应包含配套导读，不把它混成事实字段。

044f：steward_scope.py以scope_holds+controls可逆保留非项目未完成任务，后台15秒巡检、处理前核对，不抢运行中任务、不重放完成项。同篇文献显示关联但不互相提升核读。复兴research000005为42记录/85有值事实/14AI，新增P02 CN102611346B 28页原件仅封面+摘要/部分权利要求选读，当前法律状态未知；配导读0.1.0（按研究版独立序列）。当前8776会话86117。规则仍有7旧pending编号，下一步不能把引用的对比专利当当前文献编号，需按已索引身份收紧并保留重复处理审计。

044g：RULE_METHOD为conservative_rules_v2_identity，indexed_document识别主/关联格式；indexed_identifier只允许声明或已发布的本件编号。Steward0.5.0严格关闭已发布同值旧DOC占位，reviewer_kind=rule和resolution保存证明版本，不删除/升分，真实差异/人工决定不动。已关闭7项、仍6项其他编号待核。单项目维护失败写settings并提示，不挡其他队列。当前8776会话79836，管家恢复；两例事实版本/导读未变。后续优先核对原始好设计奖范围并构建通用交付包。

044h研究交付：build_research_handoff.py导出任意已有研究项目的固定版本+绑定导读，归属只允许project，冻结证据块原字节留存；research_handoff_check.py与read示例离线运行。只有单快照和前序manifest身份对照，不称历史全链；Hash防损坏非签名或事实认证。阶段包/原件全部私有output/handoff。新研究深挖继续后须重建包，不将旧包当最新版本。

044i限定选录：source_excerpt.py创建共享原件的项目连续原文选录，保留父件/冻结块/选择范围；research_workflow.evidence沿父件复核，禁止标题/用途/编者说明成为事实引文，嵌套选录同样限制。交付保存selection_text及父件元数据；shared父原件不随包，不能声称离线包已完整核验父件。Steward0.5.1。两例当前蛟龙research000005、复兴000007，各导读0.1.0，源背景/算法/专利/正式获奖名单的边界以044执行文档末尾为准；质量仍未评。

044j研究评估：research_assessment.py将六维AI判断与机器证据检查分开、绑定research版不可覆盖，质量总分/专家状态不提升。safe_read另做当前证据复检；MCP概览review_detail默认false仅摘要，true可深入，工具仍11个。评估/导读/研究事实版本独立；新数据不能沿用旧评估。当前报告0.1.0绑蛟龙000005/复兴000007。cgd公开目录已可用匿名网页会话+X-Requested-With检索，官方条目详情和整届shared响应在044j，未入结构化事实；优先按项目单行核对再发布，勿把createTime/participant当获奖年份/个人名单。

044k官方目录：source_json_row.py只投影data.rows中唯一id且名称/matchYear与项目一致的原行，保留父响应/行哈希；research_workflow和研究评估验证父件成员关系，交付不混整届其他条目。Steward0.5.2。MCP gd_read_evidence含supporting_evidence，可用chunks_sha256选择研究版已有修订，禁止任意路径/越权。当前蛟龙000006、复兴000008各导读评估0.1.0；图片索引按范围交付，旧清单缺sha从来源身份补齐不丢人工标签。第三例FAST须先核2019馈源舱对象，别混2017索驱动系统与整台FAST。

044l：Steward0.5.3新增record_asset_review，仅可信本地Agent可用，核当前project归属/原件SHA/清单视觉状态后持久登记asset_reviews，保留旧任务结果，仅关闭本图awaiting_agent任务；非事实/全文/工程/权利审核，不关冲突或运行任务。3张044k已视觉整理图片闭环。第三例2019-s10 FAST馈源舱已核2019银奖，research000001为25记录/40有值事实/6AI，导读/六维评估各0.1.0；不得混2017索驱动或整台FAST。2018综述/2020测量论文/2025设备介绍的对象与时间分开，2020精度试验非恶劣天气验证；A02均值/Rms统计口径待澄清，DOI原印刷连接号与canonical_doi检索形式分开。8776会话5259，暂停已恢复；MDPI403三次失败不绕过，尚无FAST专利清单。

044m：Steward0.5.4；research_workflow.doi_tokens按完整印刷token读取，保留EN DASH、不把未知Unicode截成前缀。reconcile_identifiers兼容有理由/时间的human或agent明确驳回，检查原件/归属与任务原件身份，全部异常解决才移出需判断；有已发布Agent研究才completed，否则仍awaiting_agent。FAST现research000003为32记录/55有值事实/10AI，导读0.1.0/评估0.1.1；P01 CN206110736U为地面建造/停靠/维护相关配套，非已确认获奖成果。000002曾将公告专利权人误映原申请人，000003明确撤回、旧版保留；纠错前阶段包隔离勿交付。服务81363已恢复，专利现权属/法律/采用与同日发明案未确认。

044n：check_pipeline_e2e.py用外置盘隔离虚构样本库走真实HTTP/监听/持久暂停重启/固定外部Agent证据/自动发布/冲突/MCP/离线包，19项实测；不是通用LLM或真实项目研究。file_admin.py支持显式--library/--inbox，默认库不变、始终loopback。自动状态合并旧任务与持久任务，计任务而非资料；failed_records/needs_judgment明确失败/判断，awaiting_agent/scope_hold另列，GET只读。README旧下载桥接描述已纠正。运行说明在00-项目管理/044-管线运行与验收说明.md；实际8776会话82576恢复，无内置语义模型。

044o：Steward0.5.5；OCR登记现在同步实际chunks_sha256，duplicate也核原件/衍生manifest/当前chunks与document路径。repair_ocr_pointer仅显式修复可验证的OCR前旧指纹，未知差异报错；ocr(...,rebuild=True)新建vision-v2保留旧件用于没有可验证历史清单的老OCR，重复幂等。实际6源重跑新OCR、3源修元指纹，所有旧研究字节不变。真实4项目295登记来源原件/现行块、18研究版与当前OCR清单预检无错误，人工标杆另过结构检查；不当完整度/真实性评分。8776会话68451已恢复。阶段包044o-交付索引.json仍非最终09:45交付。

044p：蛟龙新增科技部/声学所2013验收报道及崔维成/宋婷婷2019《科技导报》研制回顾HTML A04（DOI...2019.16.012，文件名20191613不作DOI编号）。任务157发布26事实+4AI→research000007，53记录/127有值/20AI；导读与评估各0.1.0重新绑定。模型布局/样机/海试改动与历史用户补证，工程曾验收不等于本库专家审核；101潜次时间口径不合并为当前统计。3新源与全部步骤已入管家，原始报告/完整名单/专利实际采用仍缺；阶段索引044p非最终包。

044q：收口验收全量296测试、最新19项真实隔离HTTP/重启/MCP、298来源/19研究版预检已过。运行说明与开发恢复交接分开；下一步私有代码bundle/资料库一致性归档及实际恢复验证。项目应用包和含共享/待定资料的内部恢复包用途不同，不能公开；09:45最终交付仍待。

044q恢复实测：output/handoff/044q-私有开发恢复-20261022-082449，代码8a72629/14794资料文件；离线clone/解压全SHA/SQLite/恢复3例MCP与4档案HTTP通过，原后台恢复。测试副本位于output/research-batches/044q/restored-code；不交付可变副本，不把复用本机Python当新机安装验收。最终09:45项目包索引待下一轮。

044r已于09:45前准备交付：output/handoff/044-最终验收-20261022/验收入口.html及交付索引.json，说明00-项目管理/044-最终验收交付.md。4项目测试包/原件/数据已重建与校验，后台8776继续运行。合计10失败/9需判断/43待Agent/9归属暂停明确保留，不能说全部任务完成。后续不扩研究范围，只核交付/响应用户；授权最迟11:18结束，暂停本对话automation（不是产品资料管家）。

044s（09:19）：验收冻结复检四ZIP/现研究版/恢复文件指纹、四档案HTTP及管家状态均一致；报告output/research-batches/044s/验收冻结复检.json。STATE顶部和TASKS当前项已指向最终交付，不再按历史“待建设”重复重做。无新研究/评分/公网部署，不重复最终通知。


044t：2026-10-22 10:50自动开发续接automation已PAUSED并复核，产品8776/资料管家继续运行。当前阶段已收口，研究/测试包保持冻结，未完成任务见044最终说明；不要因旧心跳提示自行重启开发，待用户新指令。

045：所有/dossier/项目沿用嫦娥视觉规范，dossier_layout.py复用dossier_reader_ui和render_reader_dossier的阅读CSS；steward_dossier_ui映射动态数据，workspace_ui共享上下文。新档案不得再造research-reader独立主题；未评不画分数、AI/未知/机器核读边界保留。规范03-平台规划/项目档案统一阅读规范-v1.md；4项目真实样式/三视图/移动交互与相关Python测试通过。研究/评分/044包未变，自动续接仍暂停。

046：用户新授权3 Agent并行开发，semantic_agent/semantic_service接真实Codex模型（只读/工具禁用/结构输出/OS已启用本机代理）；风险/矛盾批次needs_review不自动入档，日限3新/变更文本，旧库不隐式重跑。控制/回执持久，按attempt/status/resultSHA幂等；启动恢复ready交接与expired running，不能用展示最近100判队列。innovation_knowledge保留旧引用和AI侧链边界，innovation_application支持真实reasoner与规则模式分别标注；MCP14只读。蛟龙000008仅2项独立复核新增，指南/评估重冻、质量不自动升分。入口/状态/未完项见046-Agent开发与验收.md；044历史包不重写，开发automation不自动恢复。

049部署：用户授权OpenDesign /inno/受保护只读快照，独立innovation-readonly服务及私有/var/lib/innovation-design/library；当前源码scripts/opendesign_readonly.py包装既有Handler，不启动watcher，禁止写入。nginx专用Basic Auth凭据不入Git；MCP v1.30.0通过授权SSH stdio实测14工具/8案，不冒称HTTP MCP。云端单向快照、本地仍处理真源；发布更新先读049部署与验收，勿启用云端Agent或公开原件。

050金奖任务：scripts/gold_research_task.py管理98金奖候选、10维检索和SQLite资料采集。实际检索记录与查询计划分开；新件通过project_pipeline.fetch/ingest(initial_scope="pending")在第一入库快照冻结待核范围，重复不得改已有归属。任务区04-知识库/历史素材登记/金奖全量采集任务，采集进程有时间/数量上限且无模型/事实发布；不能声称全网已穷尽或无人值守Deep Research已建成。接续先读050操作文档并核worker.json/PID，不重复开worker、不自动云同步。

051全金奖深化：用户2026-10-23新授权10小时，截止11:23:41 Asia/Seoul，规范见specs/051-十小时全金奖标杆深化.md。gold_source_triage只读关联建议、gold_deep_research只生成实际模型待审草稿、gold_benchmark_audit只读验收；都不能关键词自动认定项目归属或专业审核。6新案真实研究版/导读/评估已发布，后续按原件独立复核和native propose/review/publish；仅明确自身文件提交，其他方法库会话并行不得收编覆盖。单项目正式名单选录保留parent/位置，相关论文/专利不推采用，下载/草稿/发布/标杆分开统计。

051最新续授权（2026-10-23）：用户取消原十小时停止点，要求连续十小时以上，先98金奖逐项达到可验收标杆档案，再继续其他项目。原11:23:41停新增/暂停automation规则已被替代；现有heartbeat已更新持续续接。gold_deep_research移除默认旧截止，显式传入deadline仍受限，单批98上限/连续3故障停止保留。旧运行进程可能仍持旧截止，需实际检查后安全续开，不能凭代码更新说进程已热更新。

ML-002: method_quality_gate.py screens declared records only; expert_certified remains false. No source truth or reviewer identity certification. Continue with six-method contracts and independent evaluation; frozen library unchanged.

ML-003: method_engine_mcp.py is a separate local stdio pilot using SDK1.30/jsonschema4.26. Rule tools and quota-consuming real-model tools are distinct. Frozen v0.1 content unchanged; v0.2 contracts are frozen technical snapshots, not expert approval. Read ML-003 state before continuation; do not rerun frozen overlay builder or publish pending-review drafts.

ML-004：方法工作台原型位于extensions/method-workbench，用户要求造物云设计系统，当前离线V2.3。交互与示例真实边界见该目录README；未接模型或MCP，不部署、不覆写ML-003冻结交付。

ML-005：割胶实验在output/rubber-tapping-pilot；scripts/*rubber*.py为本任务脚本。private保留案例摘录、数据库，不公开、不打包。需求与方案为研究稿；后台语义调用失败，实际执行模式是Host Agent+方法MCP，不称全自动模型生成；不改源案例事实或旧契约。

ML-006：extensions/method-workbench/app与method_workbench_server/bridge.py为本机8786新工作台。完整60档案、需求版本和真实MCP题录/计划接入，持久数据output/method-workbench-private，不入Git。只建立计划，未接网页节点生成/提交；旧报告不自动绑定改后需求。勿改ML-003核心冻结文件；交付见00-项目管理/ML-006-工作台交付.md。

ML-007取代上条执行边界：method_workbench_execution.py独立持久worker接真实逐节点生成/编辑/校验/提交；一次生成最多一次模型调用，无自动重试。正式工作台六研究产物已提交，来源为两模型草稿（R48有Host修订）加四Host适配稿，R17模型超时保留。质量门禁仍blocked/非专家认证；数据三SQLite，原模型审计仍在旧私有目录，不修改冻结核心或旧自动化。见ML-007交付。

ML-008：R17由method_workbench_morphology.py逐功能生成并绑定输入指纹，完整后才汇总及走原MCP门禁。新增增量MCP入口20工具，旧18工具入口不变。证据按块预览/确认加入、同内容去重。真实试验7/14片段，F08日志429并限时退出，无新任务重试；原ML007第三步也记录429，不可把超时归因于长输出。试验库不替换原六产物，见ML-008交付。提示词/片段语义变更需升级VERSION。

ML-009：method_workbench_review.py只读投影已提交产物，候选配对枚举不等于实际物理接口，未审查不等于冲突，声明相容不等于验证。输入SHA/原判断/未知保留至报告；不评分、不自动推荐，不变更冻结核心。

ML-010：工作台产品品牌为好设计，保留现有设计系统技术资产；需求四步引导和核对摘要不等于模型自动理解。用户原话与未来模型推测须分开，未知可跳过，不自动收费运行。

ML-011：/library展示层改为extensions/method-reader，build_method_reader.py从冻结档案构建，不覆写冻结库。公开Markdown/JSON附件限白名单；60正文默认展开，图示只反映档案结构。MCP配置/写入规范独立页，原18与可选20工具分清；file://原冻结页保持原样。

055：用户新授权方法库长任务，复用ML-011展示层；method_reader_visuals.py由pilot独占，root整合/文档渲染/浏览器，quality只读MCP核验与量规。冻结内容不改，不收编其他会话核心变更，技术测试不自动认80分。

ML-012 In progress（本会话）：新增R49—R52研究增补库，原冻结60不改；method_library_catalog.py聚合64，build_method_reader/工作台接聚合；新增独立method_engine_library_mcp.py22工具入口（原18/20不变）。055的method_reader_visuals.py不修改，新图标由method_supplement_visuals.py代理。后续测试用目录计数，不能硬编码60。待校验与交付。

ML-012完成：64条聚合包含R49—R52四增补研究稿；FBS limited_excerpt_only须保留页首补证提示。method_engine_library_mcp.py是可选22工具入口，新增2只读增补内容工具；原18/20和固定六契约不变。新档案指纹在增补目录，构建前需一致；详ML-012交付。

ML-013：方法阅读版已上线opendesign.cc/methods/，现有/inno/Basic Auth账号文件，独立gooddesign-methods release/current。只读静态604文件，非云端方法执行或HTTP MCP；更新先读ML-013交付，使用新release，原生产案例库/主站不得覆写。

ML-013访问规则更新：用户拒绝浏览器原生登录方式，/methods/已免登录公开只读；勿重新加Basic Auth。原/inno/访问权限不变。

ML-014：64份逐法第一轮研究在02-研究/ML-014-逐法深度研究，研究总索引.json绑定报告SHA和核读范围；不是64部原典全文或专家认证。R10来源身份、WB版本/术语差异等后续整合先看总论与逐法证据。10组局部教学不冒全方法执行；线上正文未因这批研究自动更新。

ML-013正式URL更新为https://opendesign.cc/inno/methods/，旧/methods/301；公开方法子路由优先于/inno/默认代理，勿重新加登录。案例服务独立include，不由方法库工作流改权限。

ML-015：/inno/站点外壳统一用scripts/inno_site_chrome.py，变量源extensions/inno/system.css，资源URL/inno/portal/system.css；项目/方法页不能另造全站导航或品牌色。案例部署需带新module和system.css；方法发布保留共用CSS依赖。网站架构见03-平台规划/inno网站架构与设计系统-v1.md；线上纯换外壳，不混入055/ML014待审内容。

- ML-016（2026-10-27）：/inno/needs/已上线，统一外壳、浏览器多草稿、项目/方法参考及真实MCP参数交接；无云端保存或模型推理。详见00-项目管理/ML-016-需求研究上线交付.md。

- ML-017（2026-10-27）：64项第二轮深化档案见02-研究/ML-017-方法深化第二轮/README.md；80 URL取得尝试及选段核读、R33/R38两项局部数学复算；非64部全文或工程/专家认证，线上及原执行契约未改。

065外部Agent资料投递：先读04-知识库/项目档案标准-v1/外部Agent协作-v1/README.md及给收集Agent的任务书.md；只写指定项目04-深研素材/外部投递/唯一批次，不改正式来源/数据/研究工作区/版本/评分。scripts/agent_intake.py机械核验不等语义审核或自动入档；保现有豆包素材，root按接收流程加工。

- ML-018（2026-10-27）：64项逐法深化已分为七批任务卡，入口00-项目管理/ML-018-逐法深化任务/任务总表.md；首项MD-001/R48待启动，非已委派外部人员或已完成研究。独立复核、现场输入缺口保留。

- ML-018多Agent已于2026-10-27按用户授权启动：needs_deepening负责001/002，function_deepening负责003/004，validation_deepening负责005/006/007；成果只写02-研究/方法深化执行/各任务目录。主Agent负责共享教学输入绑定、交叉Agent复核与集成；57项仍待启动。初始化脚本已阻止覆盖执行进度。

- ML-018第二批（2026-10-27）：用户授权继续，MD008—016九项已分配原三Agent，入口02-研究/方法深化执行/批次02-集成/启动与验收.md。首批交叉审查出现保真门禁缺口，须独立版本修订/重绑复测，不标审核通过；后续48项待启动。

- ML018继续（2026-10-27）：第二批9包交付且主Agent核指纹，交叉复核进行；首批v0.1.1新目录修订已指派并按R08→R48→R14→R17→验证链重绑；第三批MD017—029共13项分三Agent组内排队，后续35项待启动。不得把已分配写成完成。

- ML019（2026-10-27）：方法卡片全称改右上A—G角标，64icon统一2.6线宽；生产20261027-ML019-cards，详细HTML未改；移动/筛选验收通过，见ML-019-方法卡片视觉调整.md。研究Agent任务继续。

- ML018第四批（2026-10-27）：前三批29作者包已核文件指纹；首批7修订版待独立复测，第三批13待交叉审，第二批发现项新版本修订已分配；第四批MD030—037八项组内排队，后续27项待启动。入口批次04-集成/启动与验收.md。

- ML018第五批（2026-10-27）：前四批37作者稿已核文件指纹，第五批MD038—049十二项已分配，后15项待启动。优先第二批修订复测/第四批交叉审/第三批发现项修订；R35未收敛等限制明确保留。

- ML020（2026-10-27）：用户最新要求去掉A—G字母，线上已移除卡片角标/筛选和详细页前缀，保留分类与图标。生产20261027-ML020-no-letters。

- ML018本轮收口（2026-10-27）：64项作者包、42修订包及独立Agent复核已归档，入口02-研究/方法深化执行/README.md；本轮列定来源P2/机械缺口已新版本复测，源全文/专业/客户/现场缺口保留。线上正文/现有六执行契约未改，不称64通用求解器或专家认证。任务07线上发布仍未勾选。

- ML021（2026-10-27启动）：用户要求全部方法正文再深化至高质量后才转上线；三Agent按19/24/21全覆盖，质量门槛见specs/ML-021-内容质量深化与上线候选验收.md。新稿只写02-研究/ML-021-内容质量深化，各项审计后实改、互审。不可把ML018技术复核/64文件存在当正文通过；暂不发布。

ML-024规划：企业创新研究闭环按specs/ML-024-企业创新研究闭环.md及00-项目管理/ML-024-企业创新研究闭环/执行计划与验收.md；root独占共享契约/路由/状态，Agent各写认领目录，作者与独立验收分离。当前仅计划完成，未实施；技术/语义/领域/发布分开验收。

ML024更新：三任务本机闭环已实现；72模块/6旧网关回归、真实SDK/浏览器、24原稿/48有限遮盲AI评审及独立对账已完成。旧planned说明由本条更新；客户确认/完整经验取舍/领域效果/生产发布仍待。新轮不得覆旧原稿/评分，证据返回须核原件/chunk/quote及native真实字段。

ML025：缺口补充以clarification独立pending版本保存，禁止自动升级为confirmed需求或改方案。侧栏展示候选资料，不因可读取认匹配。

069 GoodDesign UI：长期设计系统以03-平台规划/好设计平台设计系统-v3.md、extensions/design-system/README.md及specs/069为准。造物云离线V2.3为稳定底座，Apple级精致度是质量要求，不再另起风格。vendor只读，GoodDesign核心集中维护，页面不得私改品牌令牌；公开类名/ARIA/数据绑定按语义化版本管理。当前0.1候选，真实样板与5项测试、6宽度及18项浏览器检查已过，未改生产。新页面按贡献门禁采纳，首个生产页验收后再评估1.0，禁止全局换肤。

069首次真实采纳：extensions/design-system/portal.html为/inno/项目库首页本地新版，scripts/preview_gooddesign_portal.py在8891只读公开目录字段。560真实项目/98封面、搜索筛选、研究状态、分页与URL恢复完整，8项Python与33项浏览器检查通过，未部署。后续复用GoodDesign核心，不在页面另造主题。

071全站UI迁移：GoodDesign UI已应用于旧站1165页、方法库67页及5个动态公共页，合计1237静态页，并接档案/资料后台/方法工作台/企业闭环。统一资产scripts/gooddesign_assets.py、构建build_gooddesign_site.py、预览preview_gooddesign_site.py，走查8892/site-index.html。1237/1237双宽度零溢出/加载/资产错误，494回归通过；详00-项目管理/071验收。仅本地，禁止未经页面族发布计划与线上回归直接全站部署。

072导航品牌IP：统一组件scripts/gooddesign_chrome.py，品牌为GoodDesign，Logo/小好SVG在extensions/design-system，导航含主题切换和小好真实导览，超链接不得用箭头。1237页均一个标准导航/底部；R50用method-detail.css精修。工作区必须传project，保留feedback/print等旧功能节点。17类浏览器与498回归通过，详00-项目管理/072验收。生产未改。

073奖项图标：按用户“太丑”反馈废弃星芒/灯泡/书签/桂冠，改成统一细线几何家族。金奖单菱形、银奖双圆环横线、铜奖六边形短线、创意三节点、提名开放圆环中心点、菁英四有序节点。portal.js按project.award映射且保留文字标签，禁止把其他类别统称铜奖或用图标制造评分排名。构建复制到/inno/portal/awards，详00-项目管理/073验收。

074需求研究：新版本地原型/inno/needs-v2/，源文件extensions/design-system/needs-workspace.*。产品定义是真实问题→参考资料→研究路线→核对计划，不是四步表单或AI推荐；桌面三层、移动单列。未知与pending clarification保留，model_calls=0，不改源项目/生产数据。复制采用预览+全选+系统快捷键，不依赖剪贴板授权。21项浏览器检查与507回归通过，详074验收；未提交Git、未部署生产。

075数据总览：本地/inno/report/已重构为真实图表优先。scripts/data_report_page.py从catalog和data-report安全快照计算奖项/年份/证据/质量/方法分布，不硬编码年度等聚合。图表可筛选和进入真实档案，未评不画0，数量不冒充质量。原生SVG需保留键盘激活，移动端图表局部滚动。replace_chrome必须移除旧chrome.js再插统一脚本，每页只能加载一次。36浏览器检查与514回归通过，详075验收；未部署生产。

076企业创新：/inno/loop/从产业Demo重新定义为研究任务工作台。复用innovation_loop_server.bundle和原反馈/补充接口，前端为extensions/enterprise-workbench，服务器只白名单提供两个静态资源。五视图概览/需求/路线/验证/反馈，桌面三层、移动单列；三任务/六经验真实数据，不另造后端或自动演示。补充和反馈必须保持pending、精确版本绑定、错误保留、失败同身份重试和任务隔离。验收使用SQLite临时副本，禁止污染真实记录。45浏览器检查与519回归通过，详076验收；生产未改。

077 MCP接入：/inno/mcp/重构为配置与工具管理页。innovation_gateway_page.py目录严格为远程8只读工具，发现3/深读4/组包1，不混本机10工具或写/历史工具。密钥预览只用占位符，不存存储/URL/请求；TOML走GOODDESIGN_MCP_TOKEN，复制拒绝时原生对话框全选，不伪报成功。mcp-center.css须纳入build_gooddesign_site。34浏览器检查与524回归通过，详077验收；生产未改。

078小好AI Agent：角色为原创薄荷绿研究搭子，不再使用通用机器人。主资产ip-xiaohao.svg，读方法/核证据独立动作SVG，统一深色描边与珊瑚色笔记本；主图URL带?v=078防旧缓存。导览只提供找项目/读方法/核证据真实链接，不冒模型对话。动态档案/资料页必须同时加载gooddesign_links，否则SVG会按原尺寸放大；不得只替换HTML。5静态测试、19浏览器检查与529回归通过，详078验收；生产未改。

070主项目区：用户明确opendesign.cc/inno/为好设计唯一主要项目区，gooddesign.qiuyiwu.com转为旧站资产来源，不再长期平行运营。迁移先读specs/070；不得现在直接关站、改DNS或复制私有资产。展馆/教育/教师/互动/助手/企业服务逐项映射和真实验收，保持项目ID、权限与深链，完成301和只读回滚准备后才可安排旧频道退役。

079项目档案：2019-s19宏华6000HP电动压裂泵已由豆包投递线索加工为原生研究版research-000001，45记录/180有值事实/42有边界AI，导读和六维评估各0.1.0绑定数据指纹。scripts/build_case_079.py重复构建须保持no_changes；三种等效台数、成本与申报/媒体范围不得合并，9项专利无清单不得补编号，pending/404/失败PDF不得作原文。动态档案统一底部、无链接箭头，深色卡用ui-surface。540测试和33浏览器检查通过；质量未评、非专家审核、未部署。详079验收。

080首页精修：GoodDesign UI 0.1.1本地候选，沿用造物云V2.3及用户参考图，保留560项目/搜索/筛选/分页/URL。首屏为探索入口+真实精选，统计独立且研究数动态计算，筛选去厚卡，项目封面显式清旧min-height，清除/错误/空/焦点/禁用真实可用。86浏览器检查、9专项与旧首页测试、546全量回归通过；不自动扩全站、未提交Git或部署。详080验收。

081小好Copilot：入口必须移出gd-nav DOM后固定右下，避免导航backdrop-filter改变fixed参照。桌面头像+名称、移动48px圆形，面板锚定入口上方；replace_chrome同步清理旧trigger/dialog，1238页各一个。aria-haspopup/controls/expanded与焦点返回真实同步，不冒模型对话。43专项、19旧角色、86首页、33档案浏览器检查与552全量测试通过；未部署。详081验收。

082需求动态案例：/inno/needs-v2/新增Deep Research式模拟播放，12动作/五阶段/四真实079来源，显著标0次模型调用，非实时Agent/工程结论。needs-live-demo.js以事件索引驱动当前动作/日志/进度，暂停不重复、重播归零、关闭清timer，减少动态直接完整显示；不改needs-workspace草稿/导出。11静态、39浏览器、558全量测试通过；未部署。详082验收。

083好设计馆：图片404根因是/inno/museum别名导致相对资源错误解析，不是原图丢失。build_gooddesign_site生成真实inno/museum/index.html，base=/复用旧站98封面和品牌资产，预览不再映射根首页；移除旧馆nav与旧copilot脚本，保留链接回退。主导航新增museum且正确高亮，导航标签nowrap，1023px以下两行局部滚动。40展馆浏览器检查与563全量测试通过；未部署。详083验收。

084中文品牌：brand-logo.svg由G改为中文“好”主体+珊瑚探索光点，系统中文无衬线、无外部依赖；导航/页脚统一strong好设计、small GoodDesign，中文20px、英文10px，资源?v=084防旧缓存。旧互动正文品牌文案不纳入共享chrome判定。40品牌浏览器检查与568全量测试通过；未部署。详084验收。

085小好清晰背景：dialog.gd-assistant::backdrop统一background:transparent、backdrop-filter:none及-webkit前缀，打开时不再灰化/模糊其他区域；保留showModal、ARIA、Escape和焦点返回。12专项、43旧角色与570全量测试通过；未部署。详085验收。

086顶底栏统一：replace_chrome只移除带旧brand的导航，不能见nav就删，功能steps保留；旧copilot脚本清理。footer仅替换旧页面底部，gd-live-*功能footer保留；共享底部按data-gd-chrome计1，不要求组件footer总数为1。gd-links/gd-footer-links用类选择器清除旧nav背景/定位/高度/边框，categories/award/laureates归museum高亮。34专项与575全量测试通过；未部署。详086验收。

087展馆首屏：museum-hero.css在旧内联样式后加载，foyer/page-hero由饱和蓝紫渐变改为#15151c/#1d1d27/#27232f石墨色，系统无衬线、#F59A82珊瑚提示、正文rgba(236,238,255,.76)，移除径向光晕。仅inno/museum与categories生效，文案/图片/URL不变。34专项与580全量测试通过；未部署。详087验收。

088全量深研分层：560目录齐全≠真深研完成，原生版103，标准full/patents各467。A60无批无版、B397有批无版、C70有批有版、D33无批有版，队列output/research-088闭合。2021-c30已将无登记来源的两候选降lead并过校验，2025-00旧底稿791项缺冻结evidence须重绑。后续新增文件出现越界路径与非法role，当前full 262通过/205待修、patents 340通过/127待修，必须修本批而非改校验器。豆包按088任务书检索，主Agent核读入档，不自动升分。6专项与586全量测试通过；未部署。

089素材总表：build_material_inventory_089只读生成output/research-089 CSV/JSON/summary，560行与索引一致，含字节/原始文件/JSONL来源/图片/原生版/缺口及快照时间。来源条目不因校验失败归零，full/patents分开；文件数不是独立来源或质量分。持续写入时重建，不将快照当永久真值。5专项与591全量测试通过；未部署。

090项目汇报：build_progress_report_090使用最新088/089快照生成output/reports/项目进展汇报-2026-11-04.md及数据JSON。汇报需区分560目录与103原生版、full 205/patents 127结构错误、2025-00证据重绑、0模型演示、未部署/未专家审核；计划按异常修复、A60/B397/C70/D33和页面族发布。5专项与596全量测试通过；未部署。

091 HTML汇报：build_progress_report_page_091从090 JSON生成output/reports/项目进展汇报-2026-11-04.html，preview_progress_report_091在8896仅本机只读服务，证据路径白名单。首屏管理层摘要+KPI+18.4%原生覆盖，架构/队列/风险/P0-P3完整，统一导航/底部/小好与打印，不另写数字。5静态、32浏览器、601全量测试通过；未部署。

092知识资产卡片：汇报页数据资产区改为四层关系流与8张真实资产卡，支持全部/项目档案/来源素材/方法应用筛选及原生dialog详情、证据深链、Escape/外部关闭和焦点返回；打印展开全部并恢复原筛选，移动关系流为两列。090 JSON新增method_count，从method_library_catalog动态聚合64项，不硬编码。修复091打印媒体缺闭合括号导致卡片样式失效的问题。5静态、56浏览器、32旧页面浏览器与606全量测试通过，截图output/design-092；未部署。

093主项目区生产发布：093e+fix1已上线opendesign.cc/inno/。静态站/方法/档案/MCP独立release，current路径与回滚材料以STATE和093验收为准。需求主入口V2，展馆与legacy公开，loop授权并独立SQLite，103原生研究版同步；私有API/原件和MCP未授权401。激活必须解析current真实路径后复制，排除符号链接/private-sources，不覆盖旧library。612测试、58线上浏览器、1777路由及隔离写入通过；COS无凭据未使用，旧站未关闭，未提交Git。

094档案核心阅读：20261104-094-fix1已上线。核心四模块overview/technical/innovation/validation默认展开，其他模块按需展开且不再单开手风琴；动态已知记录默认展开，原文、待补和AI仍分层。render_reader_dossier模板必须保持完整f-string，禁止占位符入页面；移动表格局部滚动且无全页溢出。opendesign_readonly.single_chrome强制清理重复导航/底部，不能只靠条件避免追加。研究事实/版本/评分不变。6专项、618全量、线上41浏览器及5项目计数通过，回滚093e-fix1。

095统一封版已上线：静态站20261104-095，档案运行20261104-095-authfix2，回滚094-fix1。/about项目介绍、/model大模型定义、/guide使用指南、/apps应用中心及5个真实案例已上线；导航含应用中心，关于/MCP/资料管理辅助，needs-v2/projects/learn重定向。引用为桌面预览+移动底部面板+打印来源列表。统一登录为innovation-auth签名Cookie，Origin null仅接受Sec-Fetch-Site same-origin，表单错误返回登录页；ubuntu加入www-data组以读取既有640账号文件，MCP仍Bearer。626测试、80页面、9登录检查通过，未提交Git。

096模型与应用中心视觉重构已上线：静态站与档案均为20261104-096，回滚095-authfix2。首页模型区废弃三等宽卡片，改079证据/方法/研究/应用四层可切换路径；应用中心改任务/详情/案例三层联动。模型标题不掉了了，深色标题显式浅色，移动自然堆叠。630测试、线上29浏览器通过，长期规则见设计系统v3第23节。

097全站设计统一与模型V2.0已上线：静态站/方法库20261105-097，档案20261105-097-fix1，整体回滚096。gooddesign_chrome为唯一公共导航/底部真源，body直接子级选择器隔离旧样式，桌面导航65px；所有静态/动态页必须main#main，无main旧页自动建正文容器。模型页是官方领域智能系统介绍，三层两环一网络，不得宣称自主训练基础大模型。635测试、线上52浏览器及11关键页通过。服务器根分区仅约91MB可用，后续发布先处理空间；硬链接克隆时覆盖文件须先解除链接。

098引擎算法草案：specs/098以割胶RUBBER-20261026/r1为V1固定样例，确定性骨架+设计案例推理+可选模型辅助。15需求/7功能/28选项/4组合/60未知判断，recommendations=[]不得改写成唯一推荐；hard=null、proposed、unknown均不得升格。先实现无模型S0—S10及负例，混合召回后评估；Host/模型不能写approved、hard、pass、engineering_validated、expert_reviewed或公共事实。草案未实施/未客户验收，生产仍097。

099输出物标准：GDRP规范见specs/099及04-知识库/项目档案标准-v1/创新研究输出物标准-v1。每次任务交research-pack.json+report.html+report.md+manifest.json，统一骨架加product/engineering/ai4s领域模块；HTML/MD由JSON生成，不另写事实。无推荐是合法完成，未知和权限不可因结构完整而省略。割胶示例Schema与文件指纹通过，生产未改。

101应用中心应用化视觉：specs/101将/inno/apps/升级为共享底座地图+应用Dock+产品详情面板，展示人群/任务/状态/交付物/案例路径/边界与阶段规划；应用图标用文字系统，不虚构新能力或模型进度。移动地图和Dock横向滚动且页面禁横向溢出，保留096筛选/案例联动契约。7项专项与回归、桌面/移动/深色浏览器通过，截图output/design-101；未部署生产。

102报告模板：GDRP的人读报告模板结构见specs/102，割胶填充示例为上述标准目录templates/report.html（与099的examples/report.html摘要并存，不替代）。三层阅读、九章骨架；模板只搬运research-pack字段，recommendations=[]、60格未知、模型失败、审核状态必须原样可见；正文禁出现破折号字符。渲染器scripts/build_gdrp_report.py已实现：Schema先验、逐字段渲染、无项目名只显示ID、输出断言无破折号；--md/--manifest可出四件套，源pack副本随目录交付。产物examples/report-rendered.html不入099 manifest，割胶四件套在output/gdrp/RUBBER-20261026-r1（gitignore）且指纹可目录内复核。桌面1440/移动390验证截图在output/design-100（模板）与output/design-102（渲染版），生产未改。

103应用中心产品货架：specs/103在101基础上将/inno/apps/改为三组场景+真实搜索+状态组合筛选+六色产品卡；卡片含人群任务/摘要/交付物/入口，详情为随应用换色的应用主页。只用现有apps/cases真源，不加评分、进度、头像或假截图。096/101/103共10项回归与桌面/移动/深色浏览器通过，截图output/design-103；未部署生产。

109应用中心桌面控制台：specs/109替代103的浅卡模板，改为左侧场景/状态导航、中间产品卡货架、右侧固定应用详情三栏；页面与公共导航内容宽至1680px，2000px不再半屏空白。去掉大渐变地图和浅色圆点，保留低饱和色调、真实搜索与组合筛选。096/101/103/109共13项回归，2000/1440/390/深色浏览器通过，截图output/design-109；未部署生产。

111应用中心接入与Agent开发：specs/111定义gd-app-0.1 Manifest和Agent App Kit顺序。apps.json六应用升级为身份/类别/状态/路由/输入输出/能力/权限/证据边界/发布门禁；application.schema.json校验，build_application_registry.py生成gd-app-registry-0.1。构建输出/inno/apps/registry.json和application.schema.json，MCP边界仍远程只读，Agent不得写approved/confirmed/engineering_validated/recommendations等禁写字段。096/101/103/109/111共17项回归通过；未部署生产。

113推理画布受保护试点第一阶段：reasoning_canvas_server.py新增本机SQLite工作区状态与GDRP端点，canvas_gdrp_mapper.py将画布裁决/毙掉/优先级/取舍/签署/检索留痕/引擎确认映射到gdrp-0.1；状态追加不可覆盖revision，base_revision冲突409，localStorage仅降级。浏览器保存r1、刷新恢复、下载GDRP且Schema 0错误；18项RC01/03/08回归通过。未做用户系统、未接模型、未部署生产。

ML-026方法资产与Skill：规范见specs/ML-026。档案/契约/评测分别版本化，Skill为生成视图而非第二真源；S0可读/S1引导/S2契约执行，评测、专家和工程状态独立。统一MCP按method_id+version调用，不建64个方法工具。先六契约轻量Skill及R48/R17/R42评测，再验证R02/R22/R52/WB01类型模板；当前仅规范未实施。

ML-027运行反馈与版本：规范见specs/ML-027。原始MethodRun/StepRun/ArtifactRevision/Review/Feedback/Outcome追加保存，统计为可重建投影；反馈不得自动改公共方法、事实、评分或授权。ChangeProposal经固定回归、留出任务和独立审核才发布，旧Run绑定旧版。先本机私有Learning Store与R42计划≠实测回归，不改旧18/20/22工具、数据库或生产。

100项目档案治理：执行specs/100及04-知识库/项目档案标准-v1/档案治理-v1。MVA由scripts/archive_governance.py从当前研究真源生成，禁止手改或另立事实；claims只含source_statement，platform_metadata/analysis单列。研究MODULE_ENTITIES与展示DISPLAY_MODULE_ENTITIES分离，历史导读不得因展示归位失效。9个试点MVA共510条可追溯事实；2025-00四批98字段同值重绑至research-000008，109条可追溯事实、剩余367项，未通过门禁不得写MVA。表格粘连数值与未归属来源不得放行，专利题录不等于权属或采用证明。完整阅读版正文只呈现项目内容，内部工作文案只在评估区；引用按来源与引文去重为注号，原文集中在资料页，H01/H02直接展开且旧深链保留。知识图谱由scripts/archive_knowledge_graph.py从当前真源生成，默认项目→主题→记录，点选展示来源与逐字证据，不得把筛选当数据修订；评估区使用同口径可追溯环图、内容构成和主题卡片。备份验收在../本地备份归档/好设计平台/2026-11-05-档案治理前-备份验收.json，同一卷不等于异地灾备。首批预览output/research-100/previews，41项相关Python、26项图谱浏览器检查与720项全量Python回归通过；未部署，生产现112。


ML-028方法能力地图：specs/ML-028及04-知识库/创新方法库/能力地图-v0.1定义28类能力与64方法×S0—S10候选路由，机器JSON和人工矩阵由scripts/build_method_capability_map.py从目录真源生成。S2仅六契约，S0为研究_only专题，其余S1；dossier输入输出与引擎逻辑产物分离，S10由运行版本系统承担，不用方法档案冒充。7项地图测试及16项原引擎回归通过；未语义全审、未接生产路由、未部署。

108引擎确定性骨架GD-CRE-0.1：实现见specs/108，算法以098为准、输出物以099为准。五模块：innovation_engine_v1（S0/S1/S2/S10编排、禁写字段递归扫描、不可覆盖冻结、CLI）、innovation_retrieval_v1（S3/S4真实库只读检索，候选一律unknown）、innovation_transfer_v1（S5映射8字段契约）、innovation_concepts_v1（S6/S7，O0基线与C0全O0）、innovation_validation_v1（S8/S9，G0-G4门禁、判据保留hard原值、推荐必返空）。模式rule_only/host_agent；model_assisted拒绝并记录，V1无模型后端。Host提议文件是待审核输入不是事实。割胶基线15/7/28/4/60全unknown、recommendations=[]由13项测试锁定；判据hard从需求派生，GDRP示例判据hard=true系098禁升格规则前的写法，指纹锁定不改，以引擎为准。冻结产物output/engine-runs/（gitignore），渲染视图在冻结后生成不入引擎manifest。686项全量通过；未做model_assisted与混合召回，未部署、未提交Git，生产仍097。


ML-029方法页标准与三类标杆：方法页标准-v1及specs/ML-029定义资产包和四层质量证据；标杆方法-v0.1含R17契约工具、R02框架编排、R52定性/定量三类共31文件，由build_method_benchmarks生成。R17历史28证据回放7/28/4通过；0.3.0-candidate.1阻断未知相容性候选但未冻结。R02教学重定义、R52 EVPI20/EVSI6/净值3及零价值例通过。48项相关回归通过；R17专属性模型实验因无Codex CLI为0次且blocked，不得宣称研究增量。详ML-029验收，未改冻结资产或生产。

110检索质量评估V1：规范见specs/110。scripts/retrieval_eval_v1.py四指标只读评估器（普查/机械自召回/词表差距/引擎触达），评估集tests/fixtures/retrieval_eval_v1/paraphrase_set.json为人工评估数据非研究事实，基线报告output/retrieval-eval-v1/生成即冻结不可覆盖。基线：103/578项目可检索、1068节点、三维齐全21项目；自召回95.3%且未中全因json.dumps换行转义（046模块缺口，未修）；逐字对照16/16而人工改写0/16；功能抽象词全库零触达。model_assisted前须先做匹配体归一化与查询词源语汇化（均为确定性修复）；语义召回只能扩召回不能新增事实；扩库优先于扩算法。7项专项通过、报告两次运行逐字节一致；未部署，生产仍097。

112服务器瘦身与发布：规范见specs/112。发布用scripts/package_inno_release_112.py与activate_inno_release_112.py（仿097三段式：静态全量+方法库+运行时overlay，硬链接克隆，symlink切换，健康检查失败自动回滚）。发布前必须与线上release做全量SHA比对确认变更范围，打包变换（legacy页base注入）会制造假差异，须比对打包后产物。服务器备份流必须单独校验（tar列目录+计数）通过后才可删除源，禁止与curl等stdout混入同一流。根分区现4.1G可用；docker镜像8.9G与/var/www/html旧站媒体3.9G未动，媒体进COS是长期方案。生产20261106-112。

116好设计馆独立域名：haoshejiguan.com配置在deploy/nginx-haoshejiguan.com.conf并入库，`/`以root+try_files直出gooddesign-site current的museum页（alias指文件会被index追加成index.htmlindex.html报500，禁止该写法），`/inno/`全量include inno-readonly与method-library两snippet镜像主项目区。新域名先装仅80端口引导配置申请证书（certbot多账号须显式--account，用acme-v02目录），再装443完整配置。证书/etc/letsencrypt/live/haoshejiguan.com至2027-02-10自动续期。

117主域切换与视觉统一：规范见specs/117三阶段。阶段一已完成：opendesign.cc的/inno/*全部301（API为308）到haoshejiguan.com，实现方式是摘除其server块的两个inno snippet include再加跳转location，snippet只留在haoshejiguan.com；opendesign.cc主站配置已入库deploy/nginx-opendesign.cc.conf，服务器备份.bak-20261112。阶段二把去/inno/路径与全站视觉统一合并为一次静态重建一次发布，目标结构/projects//methods//apps//needs//report//dossier//canvas/，旧/inno/*一律301保护。阶段三MCP客户端口径随重建收口。

2026-11-12协作入口：先读AGENT-CONTEXT.md及00-项目管理/20261112-协作环境同步.md。用户指定真实环境haoshejiguan.com，活跃代码仍外置盘好设计平台；空系统盘目录不建第二副本。

118全站审计与发布：规范见specs/118。构建后必须跑scripts/site_audit_118.py且P0=0/P1=0；审计器含base href解析、动态路由白名单、JS赋值href白名单（JS_ASSIGNED_HREF）、文本级旧域名扫描。innovation-mcp有独立release树/var/www/innovation-mcp（ExecStart按其current解析），发布须四base（static/methods/runtime/mcp）同步，见scripts/activate_inno_release_118.py。auth登录Origin白名单在scripts/innovation_auth.py，新增域名必须同步加入否则登录403；登录POST路径是/inno/login/不是/inno/auth/*。contributing.html由build_method_reader.py重新生成，改extensions/method-reader/下同名文件无效。本机Playwright浏览器未装时浏览器套件不可跑，用桌面浏览器工具人工验证并如实记录。

119方法页密度与发版细节：规范见specs/119。grid的gap会同时作用行列，hero类多行卡片必须column-gap/row-gap分离。给标签加id的正则必须包含闭合符>（workspace_ui.py:31的<main\b(?![^>]*\bid=)不匹配>导致全档案页多出可见>，同类错误写替换时先想残留）。portal四CSS与方法库CSS/JS链接统一带?v=内容sha前8位（gooddesign_assets.css_version与build_method_reader.page），发版后禁止依赖浏览器缓存刷新。全站页面经build_gooddesign_site.decorate注入canonical（CANONICAL_BASE=https://haoshejiguan.com，museum指向主域根）。深浅色域规则在视觉规范v2第13节：chrome恒浅色，深色展厅仅museum family。

120去inno路径改造：规范见specs/120。URL结构：页面根路径（/projects//methods//apps//needs//report//dossier//canvas//login/等），旧/inno/页面由haoshejiguan.com的server级rewrite 301（/inno/canvas/api负向断言保护）；技术路径/inno/portal|legacy|api|mcp/api不动。路由分三层：deploy/nginx-inno-root.conf（根路径）+inno-readonly.conf（技术路径）+method-library.conf（/methods/直出）。登录Cookie Path=/（innovation_auth.py），改路径前缀必须同步cookie作用域。fetch相对路径在路径改造中必踩雷（portal.js的catalog.json教训），迁移时先全量grep fetch/相对API。nginx proxy_pass尾斜杠决定路径前缀去留。/needs/服务的是needs-v2内容不是needs。运行时PREFIX仍为/inno未翻转。

120-fix2浏览器套件：本地脚本化浏览器回归环境=preview_gooddesign_site.py:8892（静态+动态dossier，已含根路径映射）+research-100/previews:56061；Playwright浏览器在~/Library/Caches/ms-playwright，系统python3运行tests/browser/。apps.json路由变更必须同步application.schema.json的catalog/detail/runtime正则并重建registry（build_gooddesign_site含此步）。/apps/用alias前缀而非精确location（registry.json等子资源需可达）。

121嘉善展厅演示：场景=大屏投影非触摸+演讲者翻页，叙事=产业×好设计创新×创新设计大模型的关联。scripts/build_expo_jiashan.py从catalog真源生成单文件离线HTML（封面/二维码base64内联零外部依赖），产物不可覆盖须先删再建。产业画像与机会方向是builder顶部策展常量，换场地改数据复用。项目事实只从catalog读，机会方向必须标"研究假设·未经验证"，迁移点只写"一种解/可类比"。

122新旧馆整合：规范见specs/122。/museum/hall|zones|x-ray|playground|laureates|assistant|connect|award为博物馆系干净地址（nginx regex location直出build根文件，zones映射categories.html）。展品互链改写必须在构建期build_gooddesign_site.decorate的MUSEUM_LINK_MAP做，禁止直接改original-app源文件（旧渠道共用同一文件，005身份校验会挂）。/inno/legacy/仅作资产与atom/project技术路径，旧馆首页已301到/。

123产业Agent真实后端：规范见specs/123。expo_agent_server.py（18792，innovation-expo.service）架构=模型起草+真实检索+契约校验，模型配置/etc/innovation-expo.env（勿读/etc/gooddesign.env，600拒绝过）。SSE事件log/stage/blk/pack/done/error，UI统一handleEvent回放与真实共用。映射项目必须来自innovation_knowledge真实召回，模型自选项目过validate_matches丢弃并记录。检索词由模型提议短词（源语汇化），板块长词召回必零。nginx limit_req_zone只能放http上下文（conf.d/expo-agent.conf）。本地Chromium偶发全域出站被重置属工具侧，curl与线上服务为准。

123检索修复：ik.search匹配体经_norm归一化（去JSON转义空白与全部空白后casefold），跨行/排版差异不再丢命中，召回单调不减仍为逐字匹配；build_queries标注source_vocabulary，无query_hints功能附zero_recall_warning（110基线抽象词零触达，零结果不得解读为无相关知识）。修复后报告output/retrieval-eval-v1/post-fix-20261114.json：自召回100%（318/0未中），改写0%与抽象词零触达不变。语义召回与460不可检索项目扩库仍另立任务；割胶冻结run与110基线报告未重算。8专项+32相关回归+741全量通过；生产未改。
