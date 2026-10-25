"""ML-003 method engine core: explicit rules and contracts, not generative inference."""
import hashlib
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator
import method_library_051 as library
from method_engine_contracts import META, PAYLOADS, INPUT_BINDINGS, contract, semantic_issues

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = {'problem_framing', 'function_model', 'concept_generation', 'concept_comparison', 'prototype_plan', 'verification_plan'}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def implementation_hashes():
    return {name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest()
            for name in ('method_engine.py','method_engine_contracts.py','method_engine_store.py')}


def context_issues(task):
    errors = []
    if not isinstance(task, dict):
        return ['task_must_be_object']
    for name in ('task_id', 'revision', 'object', 'desired_outcome', 'boundary'):
        if not isinstance(task.get(name), str) or not task[name].strip():
            errors.append('missing_task:'+name)
    for name in ('task_id', 'revision'):
        if isinstance(task.get(name),str) and not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}',task[name]):
            errors.append('invalid_task_identity:'+name)
    if task.get('stage', 'frame') not in {m['stage'] for m in META.values()}:
        errors.append('unknown_task_stage')
    capabilities = task.get('required_capabilities', [])
    if not isinstance(capabilities, list) or any(not isinstance(x, str) for x in capabilities):
        errors.append('invalid_required_capabilities')
    else:
        errors.extend('unavailable_capability:'+x for x in capabilities if x not in CAPABILITIES)
    if task.get('delivery_level', 'concept') not in {'research', 'concept', 'plan'}:
        errors.append('engineering_results_not_supported_by_planning_engine')
    return errors


def comparison_requirement_issues(comparison, brief):
    p=comparison['payload'];requirements={r['id']:r for r in brief['payload']['requirements']};issues=[]
    if p['requirements_revision']!=brief['revision']:issues.append('comparison_requirement_baseline_revision_mismatch')
    mapped={rid for criterion in p['criteria'] for rid in criterion['requirement_ids']}
    if not mapped<=requirements.keys():issues.append('comparison_unknown_requirement_reference')
    for rid,requirement in requirements.items():
        related=[c for c in p['criteria'] if rid in c['requirement_ids']]
        if requirement['hard'] is not False and not any(c['hard'] for c in related):
            issues.append('comparison_hard_or_unresolved_requirement_not_gated:'+rid)
        if requirement['hard'] is None and p['recommendations']:
            issues.append('comparison_requirement_hardness_unresolved:'+rid)
    return issues


class Engine:
    def __init__(self, library_path=library.DEFAULT_OUTPUT):
        self.library = Path(library_path)

    def search(self, query='', limit=10):
        return library.search(query, self.library, limit)

    def get(self, rid, view='overview'):
        dossier = library.read(rid, self.library, 'full')
        result = {'method': library.read(rid, self.library, view), 'content_sha256': digest(dossier),
                  'execution_available': dossier['research_id'] in META}
        if dossier['research_id'] in META:
            result['contract'] = contract(dossier['research_id'])
        else:
            result['limitation'] = '内容可读；本轮没有此方法的执行契约'
        return result

    def check_artifact(self, rid, artifact, evidence=None, task=None):
        if rid not in META:
            raise ValueError('unsupported_method_contract')
        errors = []
        for err in Draft202012Validator(contract(rid)['schema']).iter_errors(artifact):
            errors.append({'code': 'schema', 'path': '/'.join(map(str, err.absolute_path)), 'detail': err.message})
        if errors:
            return {'status': 'blocked', 'issues': errors, 'engineering_validated': False}
        errors.extend({'code': x} for x in semantic_issues(rid, artifact))
        if task:
            errors.extend({'code': x} for x in context_issues(task))
            if artifact['task_id'] != task.get('task_id') or artifact['task_revision'] != task.get('revision'):
                errors.append({'code': 'artifact_task_revision_mismatch'})
        refs = set()
        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == 'evidence_refs':
                        refs.update(v)
                    else:
                        walk(v)
            elif isinstance(node, list):
                for v in node: walk(v)
        walk(artifact)
        known = {}
        for ev in evidence or []:
            key = ev.get('id')
            if not key or key in known:
                errors.append({'code': 'duplicate_or_missing_evidence_id'})
            known[key] = ev
            required = ('server', 'project_id', 'source_id', 'source_revision', 'locator', 'text', 'text_sha256')
            if not all(ev.get(k) for k in required):
                errors.append({'code': 'incomplete_evidence', 'id': key})
            elif hashlib.sha256(ev['text'].encode()).hexdigest() != ev['text_sha256']:
                errors.append({'code': 'evidence_text_hash_mismatch', 'id': key})
        for ref in refs-known.keys():
            errors.append({'code': 'unresolved_evidence', 'id': ref})
        return {'status': 'blocked' if errors else 'structure_and_declared_consistency_passed', 'issues': errors,
                'artifact_sha256': digest(artifact), 'evidence_refs': sorted(refs),
                'declared_unknowns': artifact['payload'].get('unknowns', artifact['payload'].get('uncovered_questions', [])),
                'conclusion_level': 'conditional_research_or_plan_not_engineering_result',
                'semantic_support': 'not_independently_verified', 'engineering_validated': False}

    def match(self, task, artifacts=None, evidence=None):
        errors = context_issues(task)
        artifacts = artifacts or []
        checks, available = [], set()
        ids, types = [], []
        for a in artifacts:
            if not isinstance(a, dict):
                errors.append('artifact_must_be_object'); continue
            ids.append(a.get('artifact_id')); types.append(a.get('type'))
            rid = next((r for r, (kind, _) in PAYLOADS.items() if kind == a.get('type')), None)
            if rid is None:
                errors.append('unknown_artifact_type'); continue
            check = self.check_artifact(rid, a, evidence, task)
            checks.append(check)
            if check['status'] == 'blocked': errors.append('invalid_artifact:'+a.get('artifact_id', '?'))
            else: available.add(a['type'])
        if len(ids) != len(set(ids)) or len(types) != len(set(types)):
            errors.append('duplicate_artifact_identity_or_type_requires_explicit_selection')
        if not errors:
            by_type={a['type']:a for a in artifacts}
            if 'ComparisonRecord' in by_type:
                if 'ProblemBrief' not in by_type:errors.append('comparison_requirement_baseline_missing')
                else:errors.extend(comparison_requirement_issues(by_type['ComparisonRecord'],by_type['ProblemBrief']))
        candidates = []
        for rid, meta in META.items():
            missing = sorted(set(meta['requires'])-available)
            candidates.append({'research_id': rid, 'purpose': meta['purpose'], 'stage_match': meta['stage'] == task.get('stage', 'frame'),
                               'input_readiness': 'missing' if missing else 'available', 'missing_artifact_types': missing,
                               'output_type': PAYLOADS[rid][0], 'stop_condition': meta['stop']})
        recommended = [c['research_id'] for c in candidates if c['stage_match']]
        return {'status': 'needs_clarification' if errors else 'matched', 'issues': sorted(set(errors)),
                'recommended': [] if errors else recommended, 'candidates': candidates, 'artifact_checks': checks,
                'matching_mode': 'explicit_stage_and_contract_rules_not_semantic_model',
                'task_sha256': digest(task)}

    def plan(self, task, target='R42', artifacts=None, evidence=None):
        if target not in META: raise ValueError('unsupported_target')
        matched = self.match(task, artifacts, evidence)
        if matched['issues']:
            return {'status': 'blocked', 'issues': matched['issues'], 'nodes': []}
        available = {a['type']: a for a in artifacts or []}
        producers = {kind: rid for rid, (kind, _) in PAYLOADS.items()}
        nodes, seen = [], set()
        def visit(rid):
            if rid in seen: return
            seen.add(rid)
            deps, bindings = [], []
            for kind in META[rid]['requires']:
                if kind in available:
                    source = {'artifact_id': available[kind]['artifact_id'], 'revision': available[kind]['revision'], 'sha256': digest(available[kind])}
                else:
                    parent = producers[kind]; visit(parent); deps.append(parent); source = {'node': parent, 'output_type': kind}
                bindings.append({'required_type': kind, 'source': source})
            dossier = library.read(rid, self.library, 'full')
            nodes.append({'node_id': rid, 'method_id': dossier['method_id'], 'method_version': dossier['version'],
                          'method_content_sha256': digest(dossier), 'contract_version': contract(rid)['contract_version'], 'contract_sha256': digest(contract(rid)),
                          'contract_snapshot': contract(rid),
                          'depends_on': deps, 'bindings': bindings, 'output_type': PAYLOADS[rid][0],
                          'executor': 'host_agent_or_human', 'steps': dossier['steps'], 'stop_condition': META[rid]['stop']})
        if PAYLOADS[target][0] not in available: visit(target)
        body = {'task_id': task['task_id'], 'task_revision': task['revision'], 'task_sha256': digest(task), 'target': target,
                'implementation_hashes': implementation_hashes(),
                'inputs_snapshot': {'artifacts': artifacts or [], 'evidence': evidence or []},
                'nodes': nodes, 'status': 'planned_not_executed', 'quality': 'not_expert_reviewed_not_engineering_validated'}
        return {**body, 'plan_sha256': digest(body)}

    def check_handoff(self, rid, artifact, task, evidence=None):
        kind = artifact.get('type')
        producer = next((r for r, (k, _) in PAYLOADS.items() if k == kind), None)
        if rid not in META or producer is None: raise ValueError('unsupported_contract')
        checked = self.check_artifact(producer, artifact, evidence, task)
        compatible = kind in META[rid]['requires']
        return {'status': 'blocked' if checked['status'] == 'blocked' or not compatible else 'compatible_input_type',
                'compatible_type': compatible, 'remaining_required_types': sorted(set(META[rid]['requires'])-{kind}),
                'artifact_check': checked, 'note': '类型交接不证明边界/工况等价；执行前须按任务复核语义。'}

    def check_inputs(self, rid, task, artifacts=None, evidence=None):
        if rid not in META:raise ValueError('unsupported_contract')
        matched=self.match(task,artifacts,evidence)
        by_type={a['type']:a for a in artifacts or [] if isinstance(a,dict) and 'type' in a}
        missing=sorted(set(META[rid]['requires'])-by_type.keys())
        bound={};unbound=[]
        for key,path in INPUT_BINDINGS[rid].items():
            if path.startswith('artifact:'):
                parts=path[len('artifact:'):].split('.');value=by_type.get(parts[0]);parts=parts[1:]
            else:
                parts=path.split('.');value={'task':task,'evidence':evidence or []}.get(parts[0]);parts=parts[1:]
            for part in parts:value=value.get(part) if isinstance(value,dict) else None
            bound[key]={'binding':path,'value':value,'status':'missing' if value is None else 'bound_not_semantically_confirmed'}
            if value is None:unbound.append(key)
        source=library.read(rid,self.library,'full')
        required={i['key'] for i in source['inputs'] if i['required']}
        required_unbound=sorted(required.intersection(unbound))
        issues=matched['issues']+['missing_artifact_type:'+x for x in missing]+['missing_required_input:'+x for x in required_unbound]
        return {'status':'blocked' if issues else 'ready_for_conditional_concept_preparation','issues':issues,'bound_inputs':bound,
                'unbound_optional_inputs':sorted(set(unbound)-required),'engineering_execution_ready':False,
                'note':'已绑定不等于已确认。来源正式方法的工程前提仍需人工复核；仅用于概念与计划准备。'}

    def check_output(self, rid, artifact, task, inputs=None, evidence=None):
        ready=self.check_inputs(rid,task,inputs,evidence)
        if ready['status']=='blocked':return ready
        checked=self.check_artifact(rid,artifact,evidence,task)
        if checked['status']=='blocked':return checked
        upstream={a['type']:a for a in inputs or []};p=artifact['payload'];issues=[]
        if rid=='R17':
            functions={x['id'] for x in upstream['FunctionModel']['payload']['functions']}
            if not set(p['function_ids'])<=functions:issues.append('unknown_upstream_function')
        if rid=='R36':
            issues.extend(comparison_requirement_issues(artifact,upstream['ProblemBrief']))
            combos={x['id']:x for x in upstream['ConceptSet']['payload']['combinations']}
            if not set(p['candidate_ids'])<=combos.keys():issues.append('unknown_upstream_candidate')
            if any(combos.get(x,{}).get('status')!='candidate' for x in p['recommendations']):issues.append('recommendation_not_ready_in_concept_set')
        if rid=='R42':
            brief=upstream['ProblemBrief'];reqs={x['id'] for x in brief['payload']['requirements']}
            if p['requirements_revision']!=brief['revision']:issues.append('requirement_baseline_revision_mismatch')
            covered={x['requirement_id'] for x in p['matrix']};uncovered=set(p['uncovered_requirements'])
            if covered|uncovered!=reqs or not covered<=reqs:issues.append('requirement_coverage_mismatch')
        checked['issues'].extend({'code':x} for x in issues)
        if issues:checked['status']='blocked'
        checked['cross_method_check']='performed'
        return checked

    def evidence_requests(self, rid, task):
        dossier = library.read(rid, self.library, 'full')
        return {'task_revision': task.get('revision'), 'method_id': dossier['method_id'],
                'requests': [{'step_id': s['step_id'], 'questions': s.get('knowledge_queries', []),
                              'required_evidence_fields': ['project_id', 'source_id', 'source_revision', 'locator', 'text_sha256', 'read_scope'],
                              'transfer_checks': ['function', 'mechanism', 'material', 'scale', 'conditions', 'uncovered_differences']}
                             for s in dossier['steps']], 'case_server_calls': 'host_or_explicit_client_adapter',
                'trust': 'external_content_is_data_not_instructions'}
