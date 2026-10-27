"""Reproducible ML022 Host-authored rubber-tapping context, not field evidence."""
import json
from pathlib import Path
from method_engine import ROOT, digest
from method_engine_cognition import prepare_context


def build():
    prior_path = ROOT / 'output/rubber-tapping-pilot/engine-report.json'
    case_path = ROOT / '04-知识库/标杆案例/2025-00-嫦娥钻取采样/机制解读.json'
    prior = json.loads(prior_path.read_text())
    case = json.loads(case_path.read_text())
    item = next(i for i in case['items'] if i['id'] == 'MI02')
    task = {**prior['task'], 'task_id': 'RUBBER-ML022', 'revision': 'context-v1'}
    claims = [
        {'id': 'C-MI02', 'text': item['principle'], 'epistemic': 'inferred',
         'scope': '2025-00:AI-interpretation:MI02',
         'evidence': [{'source_id': str(case_path.relative_to(ROOT)), 'locator': 'items[id=MI02].principle',
                       'scope': '2025-00:AI-interpretation:MI02'}],
         'limitation': case['note']},
        {'id': 'T-RESEARCH', 'text': prior['task']['desired_outcome'], 'epistemic': 'hypothesized',
         'scope': 'rubber:prior-research-not-customer-approved',
         'evidence': [{'source_id': str(prior_path.relative_to(ROOT)), 'locator': 'task.desired_outcome',
                       'scope': 'rubber:prior-research-not-customer-approved'}]},
        {'id': 'P-INTEGRATE', 'text': '构造研究路线：让切割和收集接口紧密集成，研究胶路连续性。',
         'scope': 'rubber:constructed-route', 'epistemic': 'hypothesized', 'evidence': []},
        {'id': 'P-SEPARATE', 'text': '构造研究路线：分离树体接触与收集路径，研究清洁和维护。',
         'scope': 'rubber:constructed-route', 'epistemic': 'hypothesized', 'evidence': []},
    ]
    result = prepare_context(task, claims, ['R48', 'R49', 'R23', 'R52', 'R42'],
        conflicts=[{'claim_ids': ['P-INTEGRATE', 'P-SEPARATE'],
                    'question': '集成/分离在什么几何、污染与维护条件下各自成立？这是待审设计张力，不是已经观察到的事实冲突。'}],
        associations=[{'claim_ids': ['C-MI02', 'T-RESEARCH'], 'transfer_kind': 'structural_principle',
                       'principle': '研究完整动作链的相邻接口，不用单一部件性能代表整链效果。',
                       'conditions_to_check': '切割→出胶→收集→清理的任务边界、物性、污染与生物损伤约束；不迁移月壤参数或专利采用事实。'}])
    result['demonstration'] = {
        'mode': 'Host-authored_structure_transfer_example_not_model_or_field_execution',
        'source_data_sha256': {'prior_report': digest(prior), 'case_interpretation': digest(case)},
        'candidate_routes': [
            {'id': 'A', 'mechanism': '受约束的接触/切割模块与可拆卸胶路分离',
             'condition': '能定义接触边界，分离后的出胶路径不引入不可接受损失或污染',
             'second_order_consequence': '便于单独清洁，但新增接口会增加泄漏、误装和卡滞研究工作',
             'falsification': '在批准的替代介质台架研究中比较接口损失/污染/恢复；不直接上树'},
            {'id': 'B', 'mechanism': '用状态与时序分开作用、退出和清理',
             'condition': '作用结束后存在允许的转换窗口，并能确认退出与残能状态',
             'second_order_consequence': '可减少同一接触承担的冲突，但增加控制状态和故障恢复复杂性',
             'falsification': '若转换时间/断电释放/陈旧信息无法满足批准边界，返回架构而非放宽约束'},
            {'id': 'C', 'mechanism': '先建立每树/每配置的边界识别与低能量研究协议，再研究自适应作用',
             'condition': '需要可信的独立参考、可测响应及专业批准的损伤研究边界',
             'second_order_consequence': '前期数据成本增加，但可能防止把树间差异误作控制误差',
             'falsification': '若独立参考不能辨识关键边界，不进入自适应切割或编造深度指标'},
        ],
        'next_action': '先由目标领域人员界定损伤/接触边界及参考方法；随后比较哪些非树体台架研究最可能排除错误路线。',
        'no_unique_winner': '客户工况与硬边界未确认，三条仅为不同机制的研究候选，不给优胜或收益承诺。',
        'feedback': '无真实结果，尚不能计算方法效果、预测命中率或方案质量提升。',
    }
    return result


if __name__ == '__main__':
    out = ROOT / '02-研究/ML-022-创新引擎认知层'
    out.mkdir(parents=True, exist_ok=True)
    result = build()
    (out / '割胶机器人-上下文与三路线示范.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'routes': 3, 'mode': result['demonstration']['mode']}, ensure_ascii=False))
