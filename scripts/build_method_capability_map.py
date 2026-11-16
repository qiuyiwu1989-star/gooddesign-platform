"""Build the ML-028 candidate capability map from immutable method dossiers."""
import argparse
import hashlib
import json
from pathlib import Path

import method_library_catalog

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '04-知识库/创新方法库/能力地图-v0.1'
CONTRACTS = ROOT / '04-知识库/创新方法库/执行契约-v0.2.0'
CONTRACT_IDS = {'R48', 'R14', 'R17', 'R36', 'R44', 'R42'}

STAGES = {
    'S0': '资产、权限与版本预检',
    'S1': '需求结构化',
    'S2': '功能图与接口建模',
    'S3': '生成检索计划',
    'S4': '案例召回与分层',
    'S5': '机制抽象与双侧映射',
    'S6': '功能选项形成',
    'S7': '概念组合与约束剪枝',
    'S8': '逐项比较与推荐门禁',
    'S9': '生成验证计划',
    'S10': '保存、回放与有限回流',
}

CAPABILITIES = {
    'process_orchestration': ('流程编排', ['S1', 'S2', 'S6', 'S7', 'S8', 'S9'], ['ResearchPlan']),
    'evidence_collection': ('证据采集', ['S1'], ['EvidencePackage']),
    'need_interpretation': ('需求解释', ['S1'], ['NeedEvidence']),
    'problem_framing': ('问题定义', ['S1'], ['ProblemBrief']),
    'requirement_deployment': ('要求展开', ['S1', 'S2'], ['RequirementDeployment']),
    'function_modeling': ('功能建模', ['S2', 'S5'], ['FunctionModel']),
    'causal_analysis': ('因果分析', ['S1', 'S5'], ['CausalRecord']),
    'concept_composition': ('概念组合', ['S6', 'S7'], ['ConceptSet']),
    'analogy_generation': ('类比与迁移', ['S3', 'S4', 'S5', 'S6'], ['TransferMap', 'MechanismOptions']),
    'concept_transformation': ('概念变换', ['S5', 'S6'], ['ConceptSet']),
    'contradiction_solving': ('矛盾求解', ['S5', 'S6'], ['MechanismOptions', 'ValidationPlan']),
    'architecture_analysis': ('架构分析', ['S2', 'S7', 'S8'], ['ArchitectureRecord']),
    'mechanism_synthesis': ('机构与动态综合', ['S5', 'S6', 'S7', 'S9'], ['MechanismOptions', 'ValidationPlan']),
    'material_selection': ('材料选择', ['S6', 'S7', 'S8'], ['MaterialSelectionRecord']),
    'manufacturability': ('制造与装配分析', ['S7', 'S8', 'S9'], ['ManufacturabilityRecord']),
    'structural_optimization': ('结构与参数优化', ['S6', 'S7', 'S8', 'S9'], ['OptimizationRecord']),
    'concept_comparison': ('概念比较', ['S8'], ['ComparisonRecord']),
    'experiment_design': ('试验设计', ['S8', 'S9'], ['ExperimentPlan']),
    'risk_analysis': ('风险分析', ['S7', 'S8', 'S9'], ['RiskRegister']),
    'verification_validation': ('验证与确认', ['S8', 'S9'], ['ValidationPlan']),
    'sustainability_assessment': ('生命周期与生态评价', ['S7', 'S8', 'S9'], ['SustainabilityRecord']),
    'value_analysis': ('价值分析', ['S6', 'S7', 'S8'], ['ValueRecord']),
    'technology_intelligence': ('技术情报与路线', ['S1', 'S3', 'S4', 'S5'], ['TechnologyLandscape']),
    'quality_evaluation': ('质量评价', ['S8', 'S9'], ['QualityAssessment']),
    'intelligent_system_design': ('智能使用性能设计', ['S5', 'S6', 'S7', 'S9'], ['ConceptSet', 'ValidationPlan']),
    'method_governance': ('方法知识与规则治理', ['S0', 'S1', 'S3'], ['MethodRegistryRecord']),
    'service_design': ('服务协同设计', ['S1', 'S2', 'S6', 'S7'], ['ServiceBlueprint']),
    'research_prioritization': ('验证优先级', ['S8', 'S9'], ['ResearchPriorityRecord']),
}

METHOD_MAP = {
    'R01': ('process_orchestration', ['problem_framing', 'function_modeling', 'verification_validation'], None),
    'R02': ('process_orchestration', ['evidence_collection', 'concept_transformation', 'verification_validation'], None),
    'R03': ('process_orchestration', ['need_interpretation', 'concept_transformation', 'verification_validation'], None),
    'R04': ('process_orchestration', ['requirement_deployment', 'architecture_analysis', 'verification_validation'], ['S1', 'S2', 'S7', 'S9']),
    'R05': ('process_orchestration', ['architecture_analysis', 'verification_validation'], ['S1', 'S2', 'S7', 'S9']),
    'R06': ('process_orchestration', ['quality_evaluation'], ['S8', 'S9']),
    'R07': ('process_orchestration', ['requirement_deployment', 'experiment_design', 'structural_optimization'], ['S1', 'S2', 'S7', 'S8', 'S9']),
    'R08': ('evidence_collection', ['need_interpretation'], None),
    'R09': ('need_interpretation', ['evidence_collection'], None),
    'R10': ('evidence_collection', ['need_interpretation', 'analogy_generation'], None),
    'R11': ('need_interpretation', ['requirement_deployment'], None),
    'R12': ('requirement_deployment', ['function_modeling', 'verification_validation'], None),
    'R13': ('need_interpretation', ['requirement_deployment', 'risk_analysis'], None),
    'R14': ('function_modeling', ['architecture_analysis'], None),
    'R15': ('function_modeling', ['concept_transformation'], None),
    'R16': ('causal_analysis', ['problem_framing', 'risk_analysis'], None),
    'R17': ('concept_composition', ['concept_transformation', 'architecture_analysis'], None),
    'R18': ('analogy_generation', ['concept_transformation'], None),
    'R19': ('concept_transformation', ['concept_composition'], None),
    'R20': ('concept_transformation', ['evidence_collection'], None),
    'R21': ('contradiction_solving', ['process_orchestration'], ['S5', 'S6']),
    'R22': ('contradiction_solving', ['concept_transformation', 'verification_validation'], None),
    'R23': ('contradiction_solving', ['concept_transformation', 'experiment_design'], None),
    'R24': ('contradiction_solving', ['function_modeling', 'concept_transformation'], None),
    'R25': ('contradiction_solving', ['function_modeling'], None),
    'R26': ('contradiction_solving', ['function_modeling', 'architecture_analysis'], None),
    'R27': ('analogy_generation', ['technology_intelligence', 'concept_transformation'], None),
    'R28': ('contradiction_solving', ['process_orchestration'], ['S5', 'S6']),
    'R29': ('technology_intelligence', ['contradiction_solving', 'concept_transformation'], ['S3', 'S5', 'S6']),
    'R30': ('architecture_analysis', ['function_modeling', 'concept_comparison'], None),
    'R31': ('architecture_analysis', ['concept_composition'], None),
    'R32': ('mechanism_synthesis', ['architecture_analysis', 'structural_optimization'], None),
    'R33': ('material_selection', ['concept_comparison'], None),
    'R34': ('manufacturability', ['function_modeling', 'value_analysis'], None),
    'R35': ('structural_optimization', ['mechanism_synthesis'], None),
    'R36': ('concept_comparison', [], None),
    'R37': ('concept_comparison', [], None),
    'R38': ('experiment_design', ['structural_optimization'], None),
    'R39': ('structural_optimization', ['experiment_design'], None),
    'R40': ('risk_analysis', ['causal_analysis', 'verification_validation'], None),
    'R41': ('risk_analysis', ['verification_validation'], None),
    'R42': ('verification_validation', ['quality_evaluation'], None),
    'R43': ('sustainability_assessment', ['value_analysis'], None),
    'R44': ('verification_validation', ['experiment_design'], None),
    'R45': ('value_analysis', ['function_modeling', 'manufacturability'], None),
    'R46': ('technology_intelligence', ['evidence_collection'], None),
    'R47': ('architecture_analysis', ['concept_composition', 'experiment_design'], None),
    'R48': ('problem_framing', ['requirement_deployment'], None),
    'R49': ('function_modeling', ['causal_analysis', 'concept_transformation'], None),
    'R50': ('service_design', ['need_interpretation', 'function_modeling'], None),
    'R51': ('risk_analysis', ['causal_analysis', 'function_modeling'], None),
    'R52': ('research_prioritization', ['concept_comparison', 'experiment_design'], None),
    'WB01': ('process_orchestration', ['evidence_collection', 'function_modeling', 'quality_evaluation'], ['S1', 'S2', 'S6', 'S7', 'S9']),
    'WB02': ('evidence_collection', ['need_interpretation', 'risk_analysis'], None),
    'WB03': ('process_orchestration', ['requirement_deployment', 'quality_evaluation'], ['S1', 'S2', 'S7', 'S9']),
    'WB04': ('process_orchestration', ['function_modeling', 'architecture_analysis'], ['S2', 'S6', 'S7']),
    'WB05': ('function_modeling', ['concept_composition'], None),
    'WB06': ('mechanism_synthesis', ['structural_optimization', 'experiment_design'], None),
    'WB07': ('intelligent_system_design', ['function_modeling', 'verification_validation'], None),
    'WB08': ('manufacturability', ['mechanism_synthesis', 'verification_validation'], None),
    'WB09': ('mechanism_synthesis', ['structural_optimization', 'experiment_design'], None),
    'WB10': ('quality_evaluation', ['concept_comparison', 'verification_validation'], None),
    'WB11': ('method_governance', ['process_orchestration'], None),
    'WB12': ('method_governance', ['technology_intelligence'], None),
}

CONTRACT_OUTPUTS = {
    'R48': ['ProblemBrief'],
    'R14': ['FunctionModel'],
    'R17': ['ConceptSet'],
    'R36': ['ComparisonRecord'],
    'R44': ['PrototypePlan'],
    'R42': ['VerificationPlan'],
}


def contract_ref(rid):
    if rid not in CONTRACT_IDS:
        return None
    raw = (CONTRACTS / rid / 'contract.json').read_bytes()
    data = json.loads(raw)
    return {'version': data['contract_version'], 'sha256': hashlib.sha256(raw).hexdigest()}


def build():
    catalog = method_library_catalog.catalog()
    rows = catalog['methods']
    assert len(rows) == 64 and len({r['research_id'] for r in rows}) == 64
    assert {r['research_id'] for r in rows} == set(METHOD_MAP)
    methods = []
    for row in rows:
        rid = row['research_id']
        dossier = method_library_catalog.read(rid)
        primary, secondary, stage_override = METHOD_MAP[rid]
        capabilities = [primary] + secondary
        assert len(capabilities) == len(set(capabilities))
        assert all(c in CAPABILITIES for c in capabilities)
        stages = stage_override or CAPABILITIES[primary][1]
        assert stages and all(s in STAGES for s in stages)
        skill_level = 'S2' if rid in CONTRACT_IDS else ('S0' if dossier['execution_status'].startswith('research_only') else 'S1')
        methods.append({
            'research_id': rid,
            'method_id': dossier['method_id'],
            'name': dossier['name'],
            'kind': dossier['kind'],
            'content_ref': {'collection': row['collection'], 'version': dossier['version'], 'sha256': row['sha256']},
            'primary_capability': primary,
            'secondary_capabilities': secondary,
            'engine_stages': stages,
            'dossier_inputs': [{'key': i['key'], 'required': i['required']} for i in dossier['inputs']],
            'dossier_outputs': [o['key'] for o in dossier['outputs']],
            'logical_outputs': CONTRACT_OUTPUTS.get(rid, CAPABILITIES[primary][2]),
            'skill_level': skill_level,
            'execution_status': dossier['execution_status'],
            'contract_ref': contract_ref(rid),
            'relations': dossier['relations'],
            'review_status': dossier['review_status'],
            'validation_status': dossier['validation_status'],
            'mapping_status': 'platform_candidate_not_independently_reviewed',
        })
    ids = {m['research_id'] for m in methods}
    for method in methods:
        for relation in method['relations']:
            assert relation['target_research_id'] in ids, (method['research_id'], relation)
    capabilities = {
        key: {'label': value[0], 'engine_stages': value[1], 'logical_outputs': value[2]}
        for key, value in CAPABILITIES.items()
    }
    stage_index = {stage: [m['research_id'] for m in methods if stage in m['engine_stages']] for stage in STAGES}
    return {
        'schema_version': 'method-capability-map-0.1',
        'map_version': '0.1.0',
        'status': 'candidate_not_production_routing',
        'scope': '64份现有档案的平台能力映射候选；不是独立语义专家审核、执行契约或工程验证',
        'source_catalog_version': catalog['version'],
        'stages': STAGES,
        'capabilities': capabilities,
        'stage_index': stage_index,
        'methods': methods,
    }


def markdown(data):
    lines = [
        '# 方法能力矩阵 v0.1',
        '',
        '> 由64份冻结/增补档案生成的候选能力地图，不是独立语义专家审核、执行契约或工程验证。S0可读、S1引导、S2契约执行。',
        '',
        '## 能力定义',
        '',
        '| 能力 | 中文 | 引擎阶段 | 逻辑产物（非运行Schema） |',
        '|---|---|---|---|',
    ]
    for key, value in data['capabilities'].items():
        lines.append(f"| `{key}` | {value['label']} | {', '.join(value['engine_stages'])} | {', '.join(value['logical_outputs'])} |")
    lines.extend(['', '## 引擎阶段索引', '', '| 阶段 | 含义 | 方法 |', '|---|---|---|'])
    for stage, label in data['stages'].items():
        members = ', '.join(data['stage_index'][stage]) or '—（由引擎运行与版本系统承担）'
        lines.append(f"| {stage} | {label} | {members} |")
    lines.extend([
        '', '## 64方法路由矩阵', '',
        '| 方法 | 等级 | 阶段 | 主能力 | 次要能力 | 必需输入 | 档案产物 | 逻辑产物 |',
        '|---|---|---|---|---|---|---|---|',
    ])
    for m in data['methods']:
        required = ', '.join(i['key'] for i in m['dossier_inputs'] if i['required'])
        lines.append(
            f"| {m['research_id']} {m['name']} | {m['skill_level']} | {', '.join(m['engine_stages'])} "
            f"| `{m['primary_capability']}` | {', '.join(m['secondary_capabilities']) or '—'} "
            f"| {required} | {', '.join(m['dossier_outputs'])} | {', '.join(m['logical_outputs'])} |"
        )
    lines.extend([
        '', '## 调用边界', '',
        '- 逻辑产物只用于候选路由；六契约的实际Artifact以冻结Contract为准。',
        '- S1计算方法没有实际求解器时，只能形成模型、计划或待计算项。',
        '- 每次调用仍须检查精确版本、必需输入、权限、成本和停止条件。',
        '- 本地图接入引擎前，需要代表方法语义抽查与任务正负例。',
        '',
    ])
    return '\n'.join(lines)


def rendered():
    data = build()
    return (
        json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n',
        markdown(data),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    json_text, md_text = rendered()
    targets = [(OUTPUT / '能力地图.json', json_text), (OUTPUT / '能力矩阵.md', md_text)]
    if args.check:
        stale = [str(path) for path, text in targets if not path.exists() or path.read_text(encoding='utf-8') != text]
        if stale:
            raise SystemExit('stale capability map: ' + ', '.join(stale))
        print('PASS: capability map outputs are current (64 methods)')
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for path, text in targets:
        path.write_text(text, encoding='utf-8')
    print(f'Wrote {len(build()["methods"])} methods to {OUTPUT}')


if __name__ == '__main__':
    main()
