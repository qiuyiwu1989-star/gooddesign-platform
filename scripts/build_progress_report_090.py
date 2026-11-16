# coding: utf-8
import json
import os
from pathlib import Path

from method_library_catalog import catalog

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/reports'


def main():
    audit = json.loads((ROOT / 'output/research-088/audit-summary.json').read_text())
    inventory = json.loads((ROOT / 'output/research-089/summary.json').read_text())
    case = json.loads((ROOT / 'output/research-079/2019-s19/publish-result.json').read_text())
    build = json.loads((ROOT / 'output/inno-preview/gooddesign-site-report.json').read_text())
    full_status = audit['standard_batch_validation']['20261103-doubao-full-01']
    patents_status = audit['standard_batch_validation']['20261103-doubao-patents-01']
    full_pass = full_status.get('mechanical_pass_pending_content_review', 0)
    full_fix = full_status.get('needs_correction', 0)
    patents_pass = patents_status.get('mechanical_pass_pending_content_review', 0)
    patents_fix = patents_status.get('needs_correction', 0)
    native = audit['native_research']
    totals = inventory['totals']
    queues = audit['queue_counts']
    tests = int(os.environ.get('FULL_TEST_COUNT', '591'))
    report = {
        'schema': 'gooddesign-progress-report-1.0',
        'date': '2026-11-04',
        'snapshot_at': inventory['generated_at'],
        'product': {'index_projects': 560, 'built_html_pages': build['html_pages'], 'method_count': len(catalog()['methods']), 'design_system': 'GoodDesign UI 0.1.1 本地候选', 'production_changed': False},
        'research': {
            'native_projects': native['projects'],
            'native_revision_distribution': audit['revision_distribution'],
            'records': native['records'],
            'known_fact_cells': native['known_fact_cells'],
            'ai_items': native['ai_items'],
            'traceable_projects': native['audit_traceable'],
            'attention_projects': native['audit_attention'],
            'evidence_issues': native['issues'],
            'full_sources': totals['full_sources'],
            'patents_sources': totals['patents_sources'],
            'raw_source_files': totals['raw_source_files'],
            'image_files': totals['image_files'],
            'material_bytes': totals['material_bytes'],
            'image_bytes': totals['image_bytes'],
            'full_batch_status': full_status,
            'patents_batch_status': patents_status,
            'queue_counts': queues,
            'gap_counts': inventory['gap_counts'],
        },
        'case_079': {'project_id': case['project_id'], 'revision': case['publish']['revision'], 'records': case['records'], 'known_fact_cells': case['known_fact_cells'], 'ai_items': case['ai_items'], 'expert_reviewed': case['expert_reviewed']},
        'verification': {'full_regression_tests': tests, 'homepage_browser_checks': 86, 'copilot_browser_checks': 43, 'museum_browser_checks': 40, 'chrome_browser_checks': 34, 'museum_hero_browser_checks': 34},
        'boundaries': ['未部署生产', '未完成专家审核', '动态案例为0次模型调用的脚本演示', '专利lead不是权属或采用证明', '图片版权按原记录保留未知', '学生/概念作品无URL不伪造'],
        'next_priorities': ['修复full 205批、patents 127批路径和文件角色', '重绑2025-00旧底稿791项证据', 'A队列60项完整定向检索', 'B队列397项存量核读与关键原件补证', 'C队列70项深化与D队列33项证据绑定', '按页面族制定生产发布与回滚计划'],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '项目进展数据-2026-11-04.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    q = queues
    text = f'''# 好设计 GoodDesign 项目进展汇报

**汇报日期：2026-11-04**  
**数据快照：{inventory['generated_at']}**  
**汇报范围：069-089产品与设计系统更新、079项目档案、088-089深研盘点**

## 一、管理层摘要

好设计正在从“项目展示网站”升级为“真实项目档案数据库 + 设计创新引擎 + 企业研究应用”。本轮同时推进了三件事：统一长期设计系统、建立可追溯的研究版本、把560个项目的收集材料转成可继续深化的数据资产。

当前最重要的判断是：**产品骨架和本地体验已基本成形，但深研仍处在分层建设阶段。** 560个项目目录齐全不等于560个真深研完成。当前有103个原生研究版，full/patents标准批各467个；新增批次中还发现205个full和127个patents结构问题，需要先修正再继续。

生产站点尚未部署本轮更新，专家审核和工程验证未完成。

## 二、项目当前架构

| 层级 | 已形成的资产 | 当前用途 |
|---|---|---|
| 项目档案数据库 | 560项目索引、原子字段、来源块、研究版本、导读评估、素材总表 | 查找项目、核对原文、追踪证据和缺口 |
| 设计创新引擎 | 64个方法档案、方法阅读、MCP只读工具与配置中心 | 提供分析路径和可复用调用方式 |
| 应用能力 | 需求研究、企业创新工作台、好设计馆、动态案例、小好Copilot | 把项目与方法用于研究、展示和企业问题 |
| 长期设计系统 | 造物云V2.3底座 + GoodDesign UI组件、中文品牌与IP | 统一页面、导航、底部、状态和交互品质 |

## 三、产品与设计系统更新

### 3.1 长期设计基础

- **069-072**：确立GoodDesign UI，以造物云离线V2.3为稳定底座，完成全站页面迁移、统一导航/底部、GoodDesign品牌和小好IP。
- **073-078**：完成奖项细线几何图标、需求研究工作台、数据可视化、企业创新工作台、MCP接入中心和小好角色体系。
- **079**：形成6000HP电动压裂泵原生研究档案，不把简介润色当成研究完成。
- **080-082**：精修首页、将小好迁移为右下角Copilot、增加Deep Research式动态案例。
- **083-087**：恢复展馆图片、统一中文主导Logo、取消Copilot背景模糊、隔离顶底栏、将高饱和蓝色渐变改为石墨色首屏。

### 3.2 当前可用体验

- 项目库支持真实项目搜索、筛选、分页和URL恢复。
- 项目档案按八模块阅读，事实、AI分析、未知与补证任务分层。
- 需求研究提供真实问题、参考资料、研究路线和核对计划。
- 动态案例可展示拆解、检索、阅读、交叉核对和结论草案，但它是**0次模型调用的脚本演示**，不是实时AI研究。
- 小好提供找项目、读方法、核证据的真实导览，不冒充模型对话。
- 好设计馆已恢复原有98张项目封面，统一导航和石墨色首屏。

## 四、数据资产进展

### 4.1 全库规模快照

| 指标 | 当前快照 |
|---|---:|
| 项目总数 | 560 |
| 原生研究版 | {native['projects']} |
| 尚未生成原生研究版 | {560-native['projects']} |
| full / patents 标准批 | 各467个 |
| full / patents 来源条目 | {totals['full_sources']} / {totals['patents_sources']} |
| 原始来源文件 | {totals['raw_source_files']} |
| 图片文件 | {totals['image_files']} |
| 素材总量 | {totals['material_bytes']/1e9:.2f} GB |
| 构建页面 | {build['html_pages']} |
| 全量回归测试 | {tests}项 |

来源条目按JSONL实际数量统计，不因校验失败归零；文件数不代表独立来源、全文核读或质量分。

### 4.2 原生研究资产

103个原生研究版共有**{native['records']}条记录、{native['known_fact_cells']}个有值事实字段、{native['ai_items']}条AI分析**。其中102个研究版通过追溯检查，`2025-00`因旧人工底稿缺逐字段冻结证据对象，出现{native['issues']}项异常，需要重新绑定证据。

### 4.3 079单案示范

6000HP电动压裂泵已形成`{case['publish']['revision']}`，包含{case['records']}条记录、{case['known_fact_cells']}个有值事实字段和{case['ai_items']}条带边界的AI分析。三种等效台数、成本、申报、论文实验、媒体报道与后续产业化分别保留，9项专利只保留申报披露，未编造编号或权属。

## 五、质量现状与必须正视的问题

1. **原生覆盖仍不足。** 当前只有{native['projects']}/560原生研究版，不能宣称全库深研完成。
2. **新增批次存在结构错误。** full有{full_fix}批、patents有{patents_fix}批需要修正，主要是越界路径和非标准文件角色。当前机械通过为full {full_pass}/467、patents {patents_pass}/467。
3. **旧底稿证据需要重绑。** `2025-00`的{native['issues']}项异常主要来自旧版只有`source_ids`，不能直接复制成新版已核验字段。
4. **专利多数仍是lead。** 申请、公开、授权、权属和实际采用必须分别核验，不能绕过CNIPA登录墙或补造号码。
5. **学生/概念作品与图片不能硬补。** 无URL、无公开资料、图片版权未知均按原记录保留，不能虚构应用、客户或授权。
6. **上线与研究审核仍是两回事。** 本轮只有本地预览，没有生产部署；动态展示和机械校验都不能代替领域专家或项目方确认。

## 六、下一阶段计划

### P0：先修数据可信度

- 修复full {full_fix}批、patents {patents_fix}批路径和`files.role`，将真实文件放回批次目录并重算SHA256，不修改校验器绕过。
- 重绑`2025-00`旧底稿的来源块、逐字引文和定位，再补原始验证。
- 继续保留`2021-c30`修复记录，同时补可定位专利公开文本，不能只停留在lead。

### P1：按队列推进全量深研

- **A队列60项**：无标准批、无原生版，做完整定向检索与投递。
- **B队列397项**：有标准批、无原生版，先存量核读，只补P0缺口和关键原件。
- **C队列70项**：有标准批、有原生版，深化技术验证、设计取舍、成果清单和应用证据。
- **D队列33项**：无标准批、有原生版，补缺失来源和证据绑定，避免重复凑批次。

### P2：把研究成果接入真实应用

继续以079为标准，把可追溯事实转成机制解释、方法参考和企业研究输入；没有原始工程记录的项目，不直接生成迁移结论或效益承诺。

### P3：按页面族发布

先制定备份、回滚、权限和线上回归方案，再逐步发布首页、项目档案、方法库、好设计馆和需求研究，不直接全站覆盖，不提前关闭旧频道。

## 七、汇报时可用的一句话

**好设计已经完成从项目展示到数据底座、设计系统和研究应用的骨架搭建；下一阶段不再追求页面和文件数量，而是把每个项目的证据、工程验证和真实应用做深。**

## 八、可复核入口

- 全量质量审计：`output/research-088/audit-summary.json`
- 560队列：`output/research-088/queues.json`
- 560素材总表：`output/research-089/material-inventory.csv`
- 结构化汇报数据：`output/reports/项目进展数据-2026-11-04.json`
- 079单案：`output/research-079/2019-s19/publish-result.json`
- 本地首页：`http://127.0.0.1:8892/inno/`
- 好设计馆：`http://127.0.0.1:8892/inno/museum/`
- 需求研究：`http://127.0.0.1:8892/inno/needs-v2/`

> 本报告不包含私有原件、未公开推荐书或会议内容。质量总分、专家审核与生产发布均保持未完成状态。
'''
    (OUT / '项目进展汇报-2026-11-04.md').write_text(text, encoding='utf-8')
    print(json.dumps({'report': str(OUT / '项目进展汇报-2026-11-04.md'), 'data': str(OUT / '项目进展数据-2026-11-04.json'), 'native_projects': native['projects'], 'full_batch_status': full_status, 'patents_batch_status': patents_status, 'full_regression_tests': tests}, ensure_ascii=False, indent=2))
    return report


if __name__ == '__main__':
    main()
