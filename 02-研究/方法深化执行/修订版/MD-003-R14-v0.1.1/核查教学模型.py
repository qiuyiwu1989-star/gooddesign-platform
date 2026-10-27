"""v0.1.1 fixed source closure plus declared model checks. No engineering semantics inferred."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
class Reject(ValueError):pass
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(d):
 if d.get('schema')!='R14-research-teaching-model-0.1.1'or d.get('version')!='0.1.1':raise Reject('unsupported_model_version')
 if d.get('mode')!='constructed_teaching_not_customer_evidence':raise Reject('unsupported_execution_scope')
 if d.get('customer_approved')is not False or d.get('engineering_validated')is not False:raise Reject('unsubstantiated_or_missing_approval')
 u=d.get('upstream',{});lock=json.loads((P/'上游锁定.json').read_text());entry=lock['contexts'].get(d.get('problem_id'))
 if not entry or u!={'path':entry['path'],'sha256':entry['sha256'],'version':entry['version'],'problem_id':d['problem_id']}:raise Reject('upstream_identity_or_version_mismatch')
 
 for artifact in lock['method_artifacts']:
  if sha(ROOT/artifact['path'])!=artifact['sha256']:raise Reject('method_artifact_changed')
 source=ROOT/entry['path']
 if sha(source)!=entry['sha256']:raise Reject('upstream_sha_changed')
 s=json.loads(source.read_text())
 if s.get('problem_id')!=d['problem_id']or s.get('version')!=u['version']:raise Reject('source_body_identity_mismatch')
 if d.get('source_needs')!=s.get('needs') or d.get('source_unknowns')!=s.get('unknowns'):raise Reject('source_need_or_unknown_registry_changed')
 # Preserve each shared unknown body and origin; additions have a different explicit registry.
 expected_unknowns=[dict(x,origin='locked_shared_context')for x in s['unknowns']]
 if d.get('unknowns')!=expected_unknowns:raise Reject('shared_unknowns_erased_or_changed')
 if not isinstance(d.get('derived_unknowns'),list):raise Reject('missing_derived_unknown_registry')
 source_ids={x['id']for x in s['unknowns']};derived_ids=set()
 for x in d['derived_unknowns']:
  if not isinstance(x.get('id'),str)or not x['id'].strip()or not isinstance(x.get('text'),str)or not x['text'].strip()or x.get('id')in source_ids or x.get('id')in derived_ids or x.get('value')is not None or x.get('origin')!='platform_derived_unknown':raise Reject('invalid_derived_unknown')
  derived_ids.add(x['id'])
 fs=d.get('functions');interfaces=d.get('interfaces');coverage=d.get('coverage')
 if not all(isinstance(x,list)and x for x in [fs,interfaces,coverage]):raise Reject('missing_model_arrays')
 ids=[f['id']for f in fs]
 if len(ids)!=len(set(ids)):raise Reject('duplicate_function_id')
 needs={x['id']for x in s['needs']};expectedmap={n:set()for n in needs}
 for f in fs:
  refs=f.get('parent_need_ids')
  if not isinstance(refs,list)or not refs or not set(refs)<=needs:raise Reject('dangling_or_missing_function_need')
  for n in refs:expectedmap[n].add(f['id'])
  if f['verb_object'].startswith(('配置','安装','选用')):raise Reject('component_wording_requires_review')
 if len(coverage)!=len(needs)or {c['need_id']for c in coverage}!=needs:raise Reject('shared_need_coverage_erased')
 for c in coverage:
  if not c.get('function_ids')or len(c['function_ids'])!=len(set(c['function_ids']))or set(c['function_ids'])!=expectedmap[c['need_id']]:raise Reject('need_function_trace_not_closed')
  if c.get('status')!='research_allocation_not_satisfaction'or c.get('coverage_scope')not in {'declared_research_functions','partial_research_boundary'}:raise Reject('coverage_not_satisfaction')
 if d['problem_id']=='TAP-TEACH-001':
  n4=next(c for c in coverage if c['need_id']=='N-T04')
  if n4['coverage_scope']!='partial_research_boundary':raise Reject('partial_service_scope_promoted')
 known=set(ids)|set(d['external_entities']);iids=[i['id']for i in interfaces]
 if len(iids)!=len(set(iids)):raise Reject('duplicate_interface_id')
 for i in interfaces:
  if i['origin']not in known or i['destination']not in known:raise Reject('dangling_interface_endpoint')
  required={'producer_unit','consumer_unit','conversion','representation_units','threshold','unit_state'}
  if not required<=set(i):raise Reject('missing_explicit_unit_or_unknown_fields')
  if i['unit_state']not in {'unknown','declared_representation'}:raise Reject('bad_unit_state')
  if i['unit_state']=='unknown'and any(i[k]is not None for k in ['producer_unit','consumer_unit','conversion','representation_units']):raise Reject('unknown_unit_filled')
  if i['unit_state']=='declared_representation'and (not i['producer_unit']or not i['consumer_unit']or not i['representation_units']):raise Reject('missing_declared_representation_unit')
  if i['producer_unit']!=i['consumer_unit']and not i['conversion']:raise Reject('declared_unit_conflict')
  if i['threshold']is not None:raise Reject('unapproved_target_injected')
 for sc in d['scenarios']:
  if not set(sc['function_ids'])<=set(ids)or not set(sc['interface_ids'])<=set(iids):raise Reject('dangling_scenario')
 if d['problem_id']=='TAP-TEACH-001':
  if not any(s['kind']=='stale_feedback_or_loss'for s in d['scenarios']):raise Reject('missing_recovery_scenario')
  if not any(i['origin']=='EXT-POWER'for i in interfaces):raise Reject('declared_boundary_energy_missing')
 return {'status':'accepted_for_research_only','function_count':len(fs),'interface_count':len(interfaces),'preserved_shared_needs':len(needs),'preserved_shared_unknowns':len(source_ids),'derived_unknowns':len(derived_ids),'global_engineering_coverage':False,'semantic_sufficiency':'not_automatically_checked','customer_approved':False}
