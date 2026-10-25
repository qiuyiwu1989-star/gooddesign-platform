"""051: validate, render and read a research method library without changing runtime cards."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '04-知识库/创新方法库/建设工作区'
DEFAULT_OUTPUT = ROOT / '04-知识库/创新方法库/深度方法库-v0.1.0'
SECTIONS = {
    'identity': '身份与原典', 'problem': '解决什么问题', 'principle': '原理与框架',
    'applicability': '什么时候用', 'interpretation': '结果怎样判读',
    'example': '完整示例', 'pitfalls': '反例与常见误用', 'validation': '检查与验证',
    'adaptation': '平台适配说明', 'gaps': '尚待补证',
}
CATEGORIES = {
    'A': '问题发现与需求定义', 'B': '功能分析与概念生成', 'C': '技术发明与矛盾求解',
    'D': '机构架构与系统设计', 'E': '性能优化与工程实现', 'F': '方案决策与验证评价',
    'G': '全流程规划与创新管理',
}
KINDS = {'framework': '流程框架', 'method_family': '方法族', 'method': '具体方法',
         'tool': '工具', 'tool_family': '工具族', 'computational_method': '计算方法',
         'theory_method': '理论与方法', 'theory': '设计理论',
         'lineage_framework_topic': '谱系框架专题'}
MISSING_ACTIONS = {'ask_or_stop': '补齐必要输入后继续', 'mark_unknown': '标记未知并说明影响',
                   'concept_only': '仅形成条件性概念'}


def load(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def dump(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def valid_url(value):
    p = urlparse(str(value))
    return p.scheme in {'http', 'https'} and bool(p.netloc) and not p.username and not p.password


def text(value):
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def validate(d, known_ids=None):
    errors, warnings = [], []
    rid = d.get('research_id', '')
    if not re.fullmatch(r'(R\d{2}|WB\d{2})', rid):
        errors.append('研究ID格式不正确')
    for key in ['method_id', 'version', 'name', 'english_name', 'kind', 'category', 'summary',
                'content_status', 'execution_status', 'review_status', 'validation_status']:
        if not isinstance(d.get(key), str) or not d[key].strip():
            errors.append('缺少身份字段:' + key)
    if not re.fullmatch(r'\d+\.\d+\.\d+', d.get('version', '')):
        errors.append('版本必须为语义版本')
    if not re.fullmatch(r'IM-[A-Z]{2}-\d{3}', d.get('method_id', '')):
        errors.append('方法ID须使用统一三位序号')
    if d.get('category') not in {k+v for k, v in CATEGORIES.items()}:
        errors.append('主分类不在统一七类中')
    sections = d.get('sections', {})
    for key in SECTIONS:
        if not isinstance(sections.get(key), str) or not sections[key].strip():
            errors.append('缺少内容章节:' + key)
    chars = sum(len(x) for x in sections.values() if isinstance(x, str))
    if chars < 1600:
        warnings.append('方法主体不足1600字符，需内容深度复核')
    if d.get('validation_status') in {'validated', 'engineering_validated', 'passed'}:
        errors.append('本研究批次不得宣称工程验证通过')
    if not d.get('inputs') or not d.get('steps') or not d.get('outputs'):
        errors.append('缺少输入、操作或产物')
    if not d.get('evaluations'):
        errors.append('缺少反例/缺输入评估设计')
    sources = d.get('sources', [])
    source_ids = set()
    for s in sources:
        if s.get('source_id') in source_ids:
            errors.append('重复来源ID')
        source_ids.add(s.get('source_id'))
        for key in ['source_id', 'publisher', 'title', 'url', 'locator', 'read_scope', 'supports', 'evidence_note', 'rights']:
            if not s.get(key):
                errors.append('来源缺少字段:' + key)
        if not valid_url(s.get('url', '')):
            errors.append('来源URL不是合法HTTP(S)地址')
    if not sources:
        errors.append('没有来源')
    for i in d.get('inputs', []):
        if not all(i.get(k) for k in ['key', 'label', 'type', 'description', 'missing_action']):
            errors.append('输入声明不完整')
        if type(i.get('required')) is not bool:
            errors.append('required必须为布尔值')
    available = {i.get('key') for i in d.get('inputs', [])}
    if len(available) != len(d.get('inputs', [])):
        errors.append('重复输入key')
    done, produced = set(), set()
    for step in d.get('steps', []):
        sid = step.get('step_id')
        if not sid or sid in done:
            errors.append('步骤ID缺失或重复')
        if not set(step.get('depends_on', [])) <= done:
            errors.append('步骤依赖不存在、前向或成环:' + str(sid))
        if not set(step.get('input_refs', [])) <= available:
            errors.append('步骤输入未绑定:' + str(sid))
        if not set(step.get('source_refs', [])) <= source_ids:
            errors.append('步骤来源不存在:' + str(sid))
        for key in ['title', 'operation', 'decision', 'output_key', 'output_description', 'checks', 'stop_condition']:
            if not step.get(key):
                errors.append('步骤缺少' + key + ':' + str(sid))
        if not step.get('source_refs'):
            warnings.append('步骤尚未绑定原典/专业指南:' + str(sid))
        key = step.get('output_key')
        if key in available:
            errors.append('步骤产物覆盖输入或已有产物:' + str(key))
        available.add(key)
        produced.add(key)
        done.add(sid)
    if not {o.get('key') for o in d.get('outputs', [])} <= produced:
        errors.append('最终输出没有对应步骤产物')
    for relation in d.get('relations', []):
        target = relation.get('target_research_id')
        if known_ids is not None and target not in known_ids:
            errors.append('关联方法不存在:' + str(target))
        if not relation.get('binding') or not relation.get('condition'):
            errors.append('方法关系缺少衔接或条件')
    return {'research_id': rid, 'errors': errors, 'warnings': warnings,
            'text_characters': chars, 'steps': len(done), 'sources': len(sources),
            'status': 'failed' if errors else 'structure_passed_not_semantic_certification'}


def discover(work=WORK):
    return sorted(Path(work).glob('批次*/*/档案.json'))


def inspect(work=WORK, allow_unfinished_relations=False):
    paths = discover(work)
    records, read_errors = [], []
    for p in paths:
        try:
            records.append((p, load(p)))
        except (ValueError, OSError) as exc:
            read_errors.append({'file': str(p), 'error': str(exc)})
    known = {d.get('research_id') for _, d in records}
    expected = {f'R{i:02d}' for i in range(1, 49)} | {f'WB{i:02d}' for i in range(1, 13)}
    results = [validate(d, known | expected if allow_unfinished_relations else known) for _, d in records]
    duplicate_ids = [k for k, v in Counter(d.get('research_id') for _, d in records).items() if v > 1]
    duplicate_method_ids = [k for k, v in Counter(d.get('method_id') for _, d in records).items() if v > 1]
    return records, {'records': len(records), 'methods': sum(str(d.get('research_id', '')).startswith('R') for _, d in records),
                     'topics': sum(str(d.get('research_id', '')).startswith('WB') for _, d in records),
                     'read_errors': read_errors, 'duplicate_ids': duplicate_ids, 'results': results,
                     'duplicate_method_ids': duplicate_method_ids, 'unexpected_ids': sorted(known-expected),
                     'missing_methods': sorted({f'R{i:02d}' for i in range(1, 49)} - known),
                     'missing_topics': sorted({f'WB{i:02d}' for i in range(1, 13)} - known)}


def md_cell(value):
    return text(value).replace('|', '\\|').replace('\n', '<br>')


def markdown(d, operation=False):
    out = [f"# {d['name']}（{d['english_name']}）", '',
           f"{d['research_id']} · {d['method_id']} · {d['version']} · {d['kind']}", '', d['summary'], '',
           '状态：研究档案；平台操作适配；未专家审核；工程效果未验证。', '']
    sec = d['sections']
    for key in ['identity', 'problem', 'principle', 'applicability']:
        if not operation or key in {'identity', 'applicability'}:
            out += ['## ' + SECTIONS[key], '', sec[key], '']
    out += ['## 输入准备', '', '| 输入 | 类型/必需 | 内容与来源 | 缺失处置 |', '|---|---|---|---|']
    for i in d['inputs']:
        out.append('| ' + ' | '.join(md_cell(x) for x in [i['label'], i['type'] + (' / 必需' if i['required'] else ' / 可选'), i['description'], i['missing_action']]) + ' |')
    out += ['', '## 操作步骤', '']
    for s in d['steps']:
        out += [f"### {s['step_id']} {s['title']}", '',
                '**输入：** ' + '、'.join(s['input_refs']), '', '**动作：** ' + s['operation'], '',
                '**判断：** ' + s['decision'], '', '**产物：** ' + s['output_key'] + '；' + s['output_description'], '',
                '**检查：** ' + '；'.join(s['checks']), '', '**停止/返回：** ' + s['stop_condition'], '',
                '**知识查询：** ' + '；'.join(s.get('knowledge_queries', [])), '', '**依据：** ' + '、'.join(s.get('source_refs', [])), '']
    out += ['## 产物', '']
    for o in d['outputs']:
        out += [f"- **{o['key']} / {o['label']}**：" + '、'.join(o.get('required_fields', [])) + '。' + o.get('interpretation', '')]
    for key in ['interpretation', 'example', 'pitfalls', 'validation', 'adaptation', 'gaps']:
        out += ['', '## ' + SECTIONS[key], '', sec[key], '']
    out += ['## 方法关系', '']
    for r in d.get('relations', []):
        out += [f"- {r['relation']} → [{r['target_research_id']}](../{r['target_research_id']}/深度说明.md)：{r['binding']}；条件：{r['condition']}"]
    out += ['', '## 来源与核读范围', '']
    for s in d['sources']:
        out += [f"### {s['source_id']} {s['title']}", '', f"{s['publisher']} · [来源入口]({s['url']})", '',
                '**定位：** ' + s['locator'], '', '**核读范围：** ' + s['read_scope'], '',
                '**支持内容：** ' + '；'.join(s['supports']), '', '**核读释义：** ' + s['evidence_note'], '', '**权利：** ' + s['rights'], '']
    return '\n'.join(out) + '\n'


def structure_markdown(d):
    out = [f"# {d['name']}：方法结构", '',
           f"身份：{d['research_id']} / {d['method_id']} / {d['version']}", '',
           f"分类：{d['category']}；类型：{d['kind']}", '',
           '本文件定义检索与调用所需结构；完整解释见深度说明，逐步执行见操作指南。', '',
           '## 任务入口', '', d['sections']['applicability'], '', '## 输入契约', '']
    for i in d['inputs']:
        out += [f"- `{i['key']}`：{i['label']}；{i['type']}；必需={i['required']}；缺失={i['missing_action']}"]
    out += ['', '## 步骤与产物流', '', '| 步骤 | 依赖 | 输入 | 输出 |', '|---|---|---|---|']
    for s in d['steps']:
        out += ['| ' + ' | '.join(md_cell(x) for x in [s['step_id']+' '+s['title'], '、'.join(s['depends_on']) or '入口', '、'.join(s['input_refs']), s['output_key']]) + ' |']
    out += ['', '## 最终产物与判读', '']
    for o in d['outputs']:
        out += [f"- `{o['key']}`：{o['label']}；字段："+'、'.join(o['required_fields'])+'；'+o['interpretation']]
    out += ['', '## 引擎边界', '',
            '先按任务与适用条件筛选，再检查输入是否足够；步骤查询来源，产物按绑定关系交给下一方法。当前只提供内容与读取接口，未注册既有运行执行器。', '',
            '## 评估情境', '']
    for e in d['evaluations']:
        out += [f"- {e['scenario']} → {e['expected']}"]
    return '\n'.join(out)+'\n'


def build_registers(output, records, work=WORK):
    """Keep evidence, lineage and engine handoff separate from executable runtime."""
    sources, relations, gaps = [], [], ['# 证据缺口总表', '', '以下是各档案具体限制，不以结构验收代替原典核读或工程确认。', '']
    selection_path = Path(work)/'范围与分工.json'
    selection = load(selection_path) if selection_path.exists() else {}
    rationale = {r['research_id']: r['research'] for r in selection.get('methods', [])}
    inclusion = ['# 入库依据与类型边界', '', '本库覆盖约定的48项方法档案和12个闻邦椿谱系专题。并非宣称穷尽整个设计领域，也不是行业排名。标准、经典理论、专业机构指南与平台整合的依据强度不同；标准公开目录不能证明已经核读付费正文。', '']
    for _, d in records:
        rid = d['research_id']
        r = rationale.get(rid, {})
        inclusion += [f"## {rid} {d['name']}", '', '类型：'+d['kind']+'；研究选入依据标签：'+'、'.join(r.get('recognition_basis', ['闻邦椿谱系公开出处']))+'。', '',
                      '本轮直接出处：'+'；'.join(s['publisher']+' / '+s['title'] for s in d['sources'])+'。', '']
        for s in d['sources']:
            sources.append({'research_id': rid, 'method_name': d['name'], **s})
        relations.extend({'source_research_id': rid, **r} for r in d['relations'])
        gaps += [f"## {rid} {d['name']}", '', d['sections']['gaps'], '']
    dump(output/'来源总台账.json', {'source_entries': len(sources), 'unique_urls': len({s['url'] for s in sources}), 'sources': sources})
    dump(output/'方法关系.json', {'status': 'declared_content_relations_not_runtime_workflow', 'relations': relations})
    (output/'证据缺口总表.md').write_text('\n'.join(gaps))
    (output/'入库依据与类型边界.md').write_text('\n'.join(inclusion))
    guide = ['# 闻邦椿体系导览', '',
             '12个专题用于呈现体系及其方法族，不等于12个互不相关的独创算法。本文是平台导览，具体概念与原典核读范围以各档案为准。', '',
             '## 总体路线', '',
             '2013作者摘要的四阶段为3I调研→7D规划→1+3+X实施→3A检验，执行中允许返回。2016学校报道有5A用语，本版保留差异；未取得的全文不会靠名称补齐。', '',
             '```mermaid', 'flowchart LR', '  A[3I调研] --> B[7D总体规划]',
             '  B --> C[1+3+X综合实施]', '  C --> D[质量检验与评估]', '  D --> A',
             '  C --> E[功能优化]', '  C --> F[动态设计]', '  C --> G[智能设计]', '  C --> H[可视化设计]',
             '```', '',
             '结构性能、使用性能、制造性能是2013摘要中的主要性能分类；动态、智能、可视化属于设计方法方向，两者不混为同一层。当前智能设计专题主要讨论原体系中的工作参数、过程控制与监测，不自动等同今天的LLM。', '',
             '## 专题入口', '']
    for _, d in records:
        if d['research_id'].startswith('WB'):
            guide += [f"- [{d['research_id']} {d['name']}](档案/{d['research_id']}/深度说明.md)：{d['summary']}"]
    guide += ['', '## 方法数量与出处', '',
              '本人公开文章提供70多种方法、7类的历史自述。该历史说法与原论文具体图表、七个代表方向须分开核对，详见WB12；不把它们直接当成本库48项名单或平台七个任务分类。', '',
              '可公开取得的论文、只读到摘要的论文、只读到目录的书章分别记录。深度操作步骤包含平台编排，未把通用CAD、控制、模糊评价等技术全部归为闻邦椿独创。']
    (output/'闻邦椿体系导览.md').write_text('\n'.join(guide)+'\n')
    (output/'常用方法路线.md').write_text('''# 常用方法路线：选择示例

以下是平台编排的参考路线，不是某项标准的强制流程。中途出现输入缺口或证据冲突时，应返回；没有必要每项都调用。箭头仅说明内容交接，不代表运行引擎已自动连通。

## 新产品概念：从愿望到候选

[R48问题定义](档案/R48/方法结构.md)→[R08用户观察](档案/R08/方法结构.md)→[R14功能分析](档案/R14/方法结构.md)→[R17形态学](档案/R17/方法结构.md)→[R36概念筛选](档案/R36/方法结构.md)→[R44原型测试](档案/R44/方法结构.md)。

观察证据用于修订问题简报；功能模型提供组合维度；候选组合交给硬约束筛查；原型回答尚未证实的假设。若真实使用者与工况未知，停在调查与条件性概念，不能让筛选分数替代访谈。

## 既有机器异常：先找机制再求解

[R16根因分析](档案/R16/方法结构.md)→[R14功能与接口](档案/R14/方法结构.md)→[R22技术矛盾](档案/R22/方法结构.md)或[R23物理矛盾](档案/R23/方法结构.md)→[R27科学效应检索](档案/R27/方法结构.md)→[R32机构综合](档案/R32/方法结构.md)或[WB09深层动态设计](档案/WB09/方法结构.md)→[R42验证与确认](档案/R42/方法结构.md)。

故障现象、作用关系和关键工况支持问题建模；启发产生候选原理；专业模型检查连续运动或动态行为。原因没有证实，不能把一张根因图当实证结论；缺模型与求解工具时不宣称算过。

## 降本与可制造：必要功能优先

[R45价值工程](档案/R45/方法结构.md)→[R15 FAST](档案/R15/方法结构.md)→[R26功能裁剪](档案/R26/方法结构.md)→[R34 DFMA](档案/R34/方法结构.md)→[R40 FMEA](档案/R40/方法结构.md)→[R42验证与确认](档案/R42/方法结构.md)。

先识别功能与成本关系，再讨论由谁接替被删部件的功能，核查装配、维护和失效方式。采购价下降不能单独证明价值提高；必要功能、防护和维护要求未覆盖时不批准删除。

## 复杂机电系统：规划与接口协同

[WB02调研](档案/WB02/方法结构.md)→[WB03总体规划](档案/WB03/方法结构.md)→[WB04综合实施](档案/WB04/方法结构.md)，按对象选[R31 DSM](档案/R31/方法结构.md)、[R30公理化设计](档案/R30/方法结构.md)和[R47集合式并行工程](档案/R47/方法结构.md)，再交给[WB10评价](档案/WB10/方法结构.md)与[R42检验](档案/R42/方法结构.md)。

规划产生任务、方法与检验安排；架构活动明确依赖、耦合和候选可行域；评价使用可追溯证据。矩阵重排不是消除物理耦合，综合评分也不能掩盖硬约束；需求改变需回到规划。
''')
    categories = output/'分类'
    categories.mkdir(exist_ok=True)
    for code, name in CATEGORIES.items():
        out = [f'# {code} {name}', '', '按当前任务选择；分类是平台组织方式，不是行业唯一分类。一个方法可跨阶段使用，主分类不构成强制流程。', '']
        for _, d in records:
            if d['category'].startswith(code):
                out += [f"## [{d['research_id']} {d['name']}](../档案/{d['research_id']}/方法结构.md)", '', d['summary'], '',
                        '适用：'+d['sections']['applicability'], '']
        (categories/(code+'-'+name+'.md')).write_text('\n'.join(out))
    (output/'方法库结构规范.md').write_text('''# 方法库结构规范 v1

每个档案以 `档案.json` 为单一内容源，按版本生成方法结构、深度说明、操作指南和网页。原典、平台编排、教学示例分开说明。身份由 research_id、method_id、version 联合追踪；R14/R48复用原有方法身份，但不覆盖现有1.0.0执行卡。

## 每个方法的结构

1. 身份：中英文名、别名、谱系、方法类型、主分类和用途。
2. 深度解释：问题、原理、适用前提、判读、示例、误用、检查、适配与缺口。
3. 输入契约：键、类型、是否必需、来源要求及缺失处置。
4. 步骤契约：前序依赖、输入绑定、动作、分支判断、产物、检查、停止条件、来源及知识查询。
5. 输出契约：必须由步骤生成的产物、必含字段与解释边界。
6. 方法关系：前后置、组成、并行或替代，附产物绑定和适用条件。
7. 证据：作者、发布者、真实URL、定位、实际核读范围、所支持内容和权利说明。
8. 评估情境：正常/缺输入/不适用等预期行为；只是评估设计，不是已经通过测试。

## 分类与计数

A问题发现与需求定义；B功能分析与概念生成；C技术发明与矛盾求解；D机构架构与系统设计；E性能优化与工程实现；F方案决策与验证评价；G全流程规划与创新管理。

48个方法档案含框架、方法族、具体方法及平台整合项，不能说成48个独立标准。12个WB专题用于呈现闻邦椿体系层级，不另算12项原创方法。目录中的kind保留类型差异。

## 状态与版本

内容完成、来源核读、专家审核、工程验证、运行集成是不同维度。当前版本提供研究内容与读取接口，未完成专家审核及工程验证。标准摘要和书目目录的证据范围只到其公开内容，不冒称全文。

修订应保留change_log；正式集成必须另审输入输出契约、资源许可和真实任务表现。结构验收只检查字段及引用，不证明全部陈述正确。
''')
    (output/'引擎接入说明.md').write_text('''# 引擎接入说明：内容版接口

当前提供三层读取：目录搜索、完整方法、指定步骤及其来源。使用 `scripts/method_library_051.py search --query 关键词`；`read --id R17 --level steps --step-id R17-S01`。也支持method_id，如IM-ML-017。读取时核对目录记录的SHA256；此机制检查文件完整性，不认证外部来源。

## 后续推理应保留的三种匹配

任务→方法：先识别对象、阶段、问题类型、约束和已有材料；用适用条件和缺输入处置过滤，不能只因关键词相同就调用。

步骤→内容：步骤knowledge_queries说明需要的项目与知识证据，来源记录说明已读范围；匹配后要核查对象、工况、量纲与证据身份，不能照搬其他项目参数。引用回到具体source_id和定位。

产物→下一方法：按relations的binding与condition交接，检查上一方法输出实际包含下一方法的必需输入。当前绑定为说明性文本，未宣称已完成可自动执行的类型映射。

## 停止与返回

必要输入缺失时提问或只输出条件性概念；硬约束冲突时返回问题/方案；缺求解工具时不生成结果；来源未取得全文时不声称完成原算法。最终产物应附方法版本、输入版本、引用、未知及人工确认事项。

## 上线前验证

用真实任务验证方法推荐是否适用、每步证据是否充分、跨方法产物是否兼容，并测试缺输入、错误工况、许可受限与工具缺失。目录关键词检索目前不是语义推荐器，静态网页也不是运行执行器。保留旧的三张执行卡，待评审后逐项映射与集成。
''')


def render_md(value):
    try:
        from markdown_it import MarkdownIt
        return MarkdownIt('commonmark', {'html': False}).enable('table').render(value)
    except ImportError:
        return ''.join('<p>' + html.escape(p).replace('\n', '<br>') + '</p>' for p in value.split('\n\n'))


def page(title, main, detail=False):
    prefix = '../' if detail else ''
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + html.escape(title) + ' · 创新方法库</title><link rel="icon" href="data:,"><link rel="stylesheet" href="' + prefix + 'library.css"></head>'
            '<body><a class="skip" href="#main">跳至正文</a><header><a class="brand" href="' + prefix + 'index.html">好设计 <span>创新方法库</span></a>'
            '<span class="edition">研究内容版 0.1</span></header>' + main + '<footer>方法原典、平台适配与教学示例分别标注。研究内容需结合真实任务与工程证据使用。</footer>'
            '<script src="' + prefix + 'library.js" defer></script></body></html>')


def render_record(d, all_records):
    esc = html.escape
    nav = ''.join(f'<a href="#{k}">{esc(v)}</a>' for k, v in [('understand', '理解方法'), ('operate', '操作指南'), ('example', '案例与边界'), ('relations', '方法关系'), ('sources', '原典与核读')])
    sec = d['sections']
    understand = ''.join('<section><h2>' + SECTIONS[k] + '</h2>' + render_md(sec[k]) + '</section>' for k in ['identity', 'problem', 'principle', 'applicability'])
    inp = '<div class="table-scroll"><table><thead><tr><th>输入</th><th>内容与来源</th><th>缺失时</th></tr></thead><tbody>'
    for i in d['inputs']:
        inp += '<tr><td>' + esc(i['label']) + ('<small>必需</small>' if i['required'] else '<small>可选</small>') + '</td><td>' + render_md(i['description']) + '</td><td>' + esc(MISSING_ACTIONS.get(i['missing_action'], i['missing_action'])) + '</td></tr>'
    inp += '</tbody></table></div>'
    steps = ''
    for n, s in enumerate(d['steps'], 1):
        steps += '<section class="step" id="' + esc(s['step_id']) + '"><span class="step-num">' + str(n).zfill(2) + '</span><h3>' + esc(s['title']) + '</h3>'
        for label, value in [('输入', '、'.join(s['input_refs'])), ('动作', s['operation']), ('判断', s['decision']), ('产物', s['output_key'] + ' · ' + s['output_description']), ('检查', '；'.join(s['checks'])), ('返回或停止', s['stop_condition']), ('知识查询', '；'.join(s.get('knowledge_queries', [])))]:
            steps += '<div class="step-line"><b>' + label + '</b>' + render_md(value) + '</div>'
        steps += '<p class="subtle">依据：' + ' '.join('<a href="#source-' + esc(x) + '">' + esc(x) + '</a>' for x in s.get('source_refs', [])) + '</p></section>'
    outputs = ''.join('<li><b>' + esc(o['label']) + '</b> ' + esc(o.get('interpretation', '')) + '<small>' + esc('、'.join(o.get('required_fields', []))) + '</small></li>' for o in d['outputs'])
    relations = ''
    for r in d.get('relations', []):
        target = r['target_research_id']
        name = all_records.get(target, {}).get('name', target)
        relations += '<li><a href="' + esc(target) + '.html">' + esc(name) + '</a><small>' + esc(r['relation']) + '</small><p>' + esc(r['binding']) + '；' + esc(r['condition']) + '</p></li>'
    sources = ''
    for s in d['sources']:
        sources += '<section class="source" id="source-' + esc(s['source_id']) + '"><h3>' + esc(s['source_id'] + ' · ' + s['title']) + '</h3>'
        sources += '<p>' + esc(s['publisher']) + ' · <a target="_blank" rel="noopener noreferrer" href="' + esc(s['url'], quote=True) + '">原始来源 ↗</a></p>'
        for label, value in [('定位', s['locator']), ('核读范围', s['read_scope']), ('支持内容', '；'.join(s['supports'])), ('核读释义', s['evidence_note']), ('权利', s['rights'])]:
            sources += '<p><b>' + label + '：</b>' + esc(value) + '</p>'
        sources += '</section>'
    body = '<div class="layout"><aside><a href="../index.html">← 返回全部方法</a><nav>' + nav + '</nav><p class="subtle">' + esc(d['research_id'] + ' / ' + d['method_id'] + '\n版本 ' + d['version']) + '</p></aside><main id="main">'
    body += '<div class="hero"><p class="eyebrow">' + esc(d['category']) + '</p><h1>' + esc(d['name']) + '</h1><p class="english">' + esc(d['english_name']) + '</p><p class="intro">' + esc(d['summary']) + '</p><div class="tags"><span>' + esc(KINDS.get(d['kind'], d['kind'])) + '</span>' + ''.join('<span>' + esc(x) + '</span>' for x in d.get('lineage', [])) + '</div>'
    body += '<p class="notice">平台研究与操作适配 · 未专家审核 · 工程效果未验证</p><div class="actions"><a href="../档案/' + esc(d['research_id']) + '/方法结构.md">方法结构</a><a href="../档案/' + esc(d['research_id']) + '/操作指南.md">操作文档</a><a href="../档案/' + esc(d['research_id']) + '/档案.json">JSON档案</a><a href="../档案/' + esc(d['research_id']) + '/深度说明.md">深度文档</a><button type="button" id="print">打印</button></div></div>'
    body += '<details class="module" id="understand" open><summary>01 理解方法</summary><div>' + understand + '</div></details>'
    body += '<details class="module" id="operate"><summary>02 怎样使用</summary><div><h2>输入准备</h2>' + inp + steps + '<h2>产物</h2><ul>' + outputs + '</ul>' + render_md(sec['interpretation']) + '</div></details>'
    body += '<details class="module" id="example"><summary>03 案例与边界</summary><div><h2>完整示例</h2>' + render_md(sec['example']) + '<h2>反例与误用</h2>' + render_md(sec['pitfalls']) + '<h2>检查与验证</h2>' + render_md(sec['validation']) + '</div></details>'
    body += '<details class="module" id="relations"><summary>04 方法关系</summary><div><ul class="relations">' + relations + '</ul><h2>平台适配</h2>' + render_md(sec['adaptation']) + '</div></details>'
    body += '<details class="module" id="sources"><summary>05 原典与核读</summary><div>' + sources + '<h2>尚待补证</h2>' + render_md(sec['gaps']) + '</div></details></main></div>'
    return page(d['name'], body, True)


def build(work=WORK, output=DEFAULT_OUTPUT, allow_partial=False):
    records, report = inspect(work, allow_unfinished_relations=allow_partial)
    failures = [r for r in report['results'] if r['errors']]
    if report['read_errors'] or report['duplicate_ids'] or report['duplicate_method_ids'] or report['unexpected_ids'] or failures:
        raise ValueError('档案结构尚未通过：' + json.dumps(report, ensure_ascii=False))
    if not allow_partial and (report['missing_methods'] or report['missing_topics']):
        raise ValueError('范围未完整，不得生成完整交付；调试预览可显式--allow-partial')
    output = Path(output)
    if (output/'发布冻结.json').exists():
        raise ValueError('此内容版本已冻结，请使用新版本目录')
    if output.resolve() == Path(work).resolve() or output.resolve() in Path(work).resolve().parents:
        raise ValueError('输出不得覆盖工作区或其父目录')
    output.mkdir(parents=True, exist_ok=True)
    rows, all_records = [], {d['research_id']: d for _, d in records}
    (output / 'methods').mkdir(exist_ok=True)
    for path, d in records:
        rid = d['research_id']
        target = output / '档案' / rid
        target.mkdir(parents=True, exist_ok=True)
        dump(target / '档案.json', d)
        (target / '深度说明.md').write_text(markdown(d))
        (target / '操作指南.md').write_text(markdown(d, True))
        (target / '方法结构.md').write_text(structure_markdown(d))
        dump(target / '输入模板.json', {
            'method_id': d['method_id'], 'version': d['version'],
            'status': 'unfilled_template_not_execution',
            'inputs': {i['key']: {'value': None, 'type': i['type'], 'required': i['required'],
                                  'description': i['description'], 'evidence_refs': [],
                                  'missing_action': i['missing_action']} for i in d['inputs']}})
        dump(target / '产物字段模板.json', {
            'method_id': d['method_id'], 'version': d['version'],
            'status': 'unfilled_template_not_result',
            'outputs': {o['key']: {'fields': {k: None for k in o['required_fields']},
                                    'evidence_refs': [], 'unknowns': [],
                                    'interpretation': o['interpretation']} for o in d['outputs']}})
        notes = path.parent / '来源核读.md'
        if notes.exists():
            shutil.copy2(notes, target / notes.name)
        (output / 'methods' / (rid + '.html')).write_text(render_record(d, all_records))
        rows.append({k: d.get(k) for k in ['research_id', 'method_id', 'version', 'name', 'english_name', 'kind', 'category', 'summary', 'lineage', 'aliases', 'search_terms', 'content_status', 'execution_status', 'review_status', 'validation_status']}
                    | {'path': '档案/' + rid + '/档案.json', 'page': 'methods/' + rid + '.html', 'sha256': sha(target / '档案.json'), 'source_count': len(d['sources']), 'step_count': len(d['steps'])})
    dump(output / '目录.json', {'version': '0.1.0', 'status': 'partial_preview' if report['missing_methods'] or report['missing_topics'] else 'research_content_release', 'note': '研究内容可读，不代表既有运行执行器已经接入', 'methods': rows})
    dump(output / '结构验收.json', report)
    with (output / '方法目录.csv').open('w', encoding='utf-8-sig', newline='') as f:
        columns = ['research_id', 'method_id', 'name', 'kind', 'category', 'summary', 'source_count', 'step_count', 'content_status', 'review_status', 'validation_status']
        writer = csv.DictWriter(f, columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    render_index(output, rows, report)
    build_registers(output, records, work)
    assets = Path(__file__).with_name('method_library_assets_051')
    for name in ['library.css', 'library.js', 'library_cli.py']:
        shutil.copy2(assets / name, output / name)
    (output / 'README.md').write_text('# 产品与机械创新方法库\n\n打开[index.html](index.html)浏览与搜索。逐方法目录、操作指南、来源核读和JSON在档案目录。\n\n48项方法与12个闻邦椿专题分别计数，不把专题子项计为独立原创方法。\n\n每个档案含方法结构、深度说明、操作指南、原始JSON、来源核读、输入模板和产物字段模板；模板的null均为待填，不代表实测或已执行。\n\n离线读取：在本目录执行 `python3 library_cli.py search --query 形态学` 或 `python3 library_cli.py read --id IM-ML-017 --level steps --step-id R17-S01`。工具只读文件并校验档案指纹，不执行工程求解。\n\n结构验收只证明文件与引用关系可读，不证明方法已专家审核、工程验证或接入生产推理。\n')
    manifest = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
    dump(output / 'manifest.json', {'version': '0.1.0', 'files': manifest, 'note': 'SHA256用于完整性，不是来源真实性认证'})
    return {'output': str(output), 'methods': report['methods'], 'topics': report['topics'], 'files': len(manifest), 'warnings': sum(len(r['warnings']) for r in report['results'])}


def render_index(output, rows, report):
    esc = html.escape
    category_options = ''.join('<option value="' + k + '">' + k + ' · ' + v + '</option>' for k, v in CATEGORIES.items())
    cards = ''
    for d in rows:
        keywords = ' '.join([d['name'], d['english_name'], d['research_id'], d['method_id'], d['summary']] + (d.get('lineage') or []) + (d.get('aliases') or []) + (d.get('search_terms') or []))
        cards += '<a class="method-card" href="' + esc(d['page']) + '" data-category="' + esc(d['category'][:1]) + '" data-kind="' + ('topic' if d['research_id'].startswith('WB') else 'method') + '" data-search="' + esc(keywords.lower(), quote=True) + '"><div class="card-meta"><span>' + esc(d['research_id']) + '</span><span>' + esc(KINDS.get(d['kind'], d['kind'])) + '</span></div><h2>' + esc(d['name']) + '</h2><p>' + esc(d['summary']) + '</p><div class="card-bottom"><span>' + str(d['step_count']) + '个操作环节 · ' + str(d['source_count']) + '条来源</span><span>阅读 →</span></div></a>'
    body = '<main id="main" class="catalog"><div class="hero"><p class="eyebrow">PRODUCT & MECHANICAL INNOVATION</p><h1>把设计方法，变成可用的思考能力。</h1><p class="intro">从需求、功能、原理，到工程与验证。了解什么时候用、怎样一步步做，以及结果的边界。</p><div class="stats"><b>' + str(report['methods']) + '<small>方法档案</small></b><b>' + str(report['topics']) + '<small>闻邦椿体系专题</small></b><b>7<small>任务分类</small></b></div></div>'
    if report['missing_methods'] or report['missing_topics']:
        body += '<p class="notice">建设中预览，尚未完成全部范围。方法缺档：' + esc('、'.join(report['missing_methods'])) + '；专题缺档：' + esc('、'.join(report['missing_topics'])) + '</p>'
    body += '<section class="filters" aria-label="检索方法"><label>搜索方法<input id="query" type="search" placeholder="方法名、问题、原理或关键词"></label><label>按任务找<select id="category"><option value="">全部分类</option>' + category_options + '</select></label><label>内容类型<select id="record-kind"><option value="">方法与专题</option><option value="method">方法档案</option><option value="topic">闻邦椿专题</option></select></label></section><p id="result-count" role="status" aria-live="polite">' + str(len(rows)) + '项内容</p><div class="cards">' + cards + '</div><p id="empty" hidden>没有匹配结果。可以换一个功能、问题或方法关键词。</p><div class="catalog-links"><a href="常用方法路线.md">常用路线</a><a href="闻邦椿体系导览.md">闻邦椿体系</a><a href="方法库结构规范.md">结构规范</a><a href="来源总台账.json">来源总账</a><a href="入库依据与类型边界.md">入库依据</a><a href="证据缺口总表.md">待补证</a><a href="引擎接入说明.md">引擎接口</a><a href="目录.json">结构化目录</a><a href="方法目录.csv">CSV目录</a><a href="结构验收.json">结构检查记录</a></div></main>'
    (output / 'index.html').write_text(page('产品与机械创新方法', body))


def search(query, library=DEFAULT_OUTPUT, limit=10):
    if not 1 <= limit <= 60:
        raise ValueError('limit须在1–60之间')
    rows = load(Path(library) / '目录.json')['methods']
    tokens = query.casefold().split()
    matches = []
    for r in rows:
        hay = json.dumps(r, ensure_ascii=False).casefold()
        if all(t in hay for t in tokens):
            matches.append(r)
    return {'search_type': 'catalog_keywords_not_semantic', 'total': len(matches), 'data': matches[:limit]}


def read(rid, library=DEFAULT_OUTPUT, level='overview', step_id=None):
    if not re.fullmatch(r'(R\d{2}|WB\d{2}|IM-[A-Z]{2}-\d{3})', rid):
        raise ValueError('档案ID格式无效')
    library = Path(library)
    row = next((r for r in load(library / '目录.json')['methods'] if rid in {r['research_id'], r['method_id']}), None)
    if row is None:
        raise ValueError('档案不存在')
    rid = row['research_id']
    if not re.fullmatch(r'(R\d{2}|WB\d{2})', rid):
        raise ValueError('目录研究ID格式无效')
    path = library / '档案' / rid / '档案.json'
    if sha(path) != row['sha256']:
        raise ValueError('档案自目录发布后已改变')
    d = load(path)
    if level == 'full':
        return d
    if level == 'overview':
        return {k: d[k] for k in ['research_id', 'method_id', 'version', 'name', 'summary', 'kind', 'category', 'inputs', 'outputs', 'execution_status', 'review_status', 'validation_status']}
    if level == 'steps':
        result = [s for s in d['steps'] if step_id is None or s['step_id'] == step_id]
        if step_id and not result:
            raise ValueError('步骤不存在')
        return {'research_id': rid, 'method_id': d['method_id'], 'version': d['version'],
                'execution_status': d['execution_status'], 'review_status': d['review_status'],
                'validation_status': d['validation_status'], 'steps': result,
                'sources': d['sources'], 'adaptation': d['sections']['adaptation']}
    if level == 'sources':
        return {'research_id': rid, 'sources': d['sources'], 'gaps': d['sections']['gaps']}
    raise ValueError('读取层级无效')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['inspect', 'build', 'search', 'read'])
    p.add_argument('--work', type=Path, default=WORK)
    p.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    p.add_argument('--allow-partial', action='store_true')
    p.add_argument('--query', default='')
    p.add_argument('--id')
    p.add_argument('--level', choices=['overview', 'steps', 'sources', 'full'], default='overview')
    p.add_argument('--step-id')
    args = p.parse_args()
    if args.command == 'inspect':
        result = inspect(args.work)[1]
    elif args.command == 'build':
        result = build(args.work, args.output, args.allow_partial)
    elif args.command == 'search':
        result = search(args.query, args.output)
    else:
        result = read(args.id or '', args.output, args.level, args.step_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
