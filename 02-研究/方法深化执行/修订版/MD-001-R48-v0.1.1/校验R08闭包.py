"""v0.1.1 fixed cross-package lineage validation, not general causal inference."""
from pathlib import Path
import hashlib,json

def validate(ex,raw,coding,shared,shared_path,raw_path,coding_path):
 shared_path=Path(shared_path).resolve();raw_path=Path(raw_path).resolve();coding_path=Path(coding_path).resolve()
 def binding(d):
  b=d.get('source_binding')
  if not isinstance(b,dict)or any(b.get(k)!=shared[k]for k in ['problem_id','version','sha256']):raise ValueError('r08_shared_problem_version_or_sha_mismatch')
  if not isinstance(b.get('path'),str)or(raw_path.parent/b['path']).resolve()!=shared_path:raise ValueError('r08_shared_path_outside_allowed_input')
 for d in [ex,raw,coding]:
  binding(d)
  if d.get('package_version')!='0.1.1':raise ValueError('r08_package_version_mismatch')
 if not raw.get('all_records_constructed')or raw.get('field_research_conducted')or raw.get('real_participants')!=0:raise ValueError('r08_material_promoted')
 def artifact(d,key,path):
  r=d.get('artifact_bindings',{}).get(key,{})
  if not isinstance(r.get('path'),str)or(raw_path.parent/r['path']).resolve()!=path:raise ValueError('r08_artifact_path_mismatch')
  if r.get('sha256')!=hashlib.sha256(path.read_bytes()).hexdigest():raise ValueError('r08_artifact_hash_mismatch')
 artifact(ex,'raw_records',raw_path);artifact(ex,'coding',coding_path);artifact(coding,'raw_records',raw_path)
 if raw!=json.loads(raw_path.read_text())or coding!=json.loads(coding_path.read_text()):raise ValueError('r08_payload_and_bound_file_differ')
 notes=raw.get('records',[])
 if not notes or len({n.get('id')for n in notes})!=len(notes)or any(not n.get('id')for n in notes):raise ValueError('r08_note_identity_not_closed')
 bynote={n['id']:n for n in notes};codes=coding.get('coding',[])
 if len(codes)!=len(notes)or {c.get('note_id')for c in codes}!=set(bynote):raise ValueError('r08_coding_coverage_not_closed')
 for c in codes:
  n=bynote[c['note_id']]
  if c.get('event_id')!=n.get('event_id')or c.get('evidence_layer')!=n.get('kind'):raise ValueError('r08_note_event_or_type_mismatch')
 hs=ex.get('hypotheses',[])
 if len({h.get('id')for h in hs})!=len(hs):raise ValueError('r08_duplicate_hypothesis_id')
 byhyp={h.get('id'):h for h in hs}
 if set(byhyp)!={'H-T01','H-T02','H-T03'}:raise ValueError('r08_hypothesis_identity_not_closed')
 for h in hs:
  for key in ['support_note_ids','counter_note_ids']:
   refs=h.get(key)
   if not isinstance(refs,list)or len(set(refs))!=len(refs)or any(n not in bynote for n in refs):raise ValueError('r08_dangling_or_duplicate_evidence_reference')
 h=byhyp['H-T01']
 if h.get('status')!='rejected_in_fixture'or h.get('scope')!='fixed_fixture_only':raise ValueError('r08_withdrawal_status_or_scope_mismatch')
 if h.get('proposition')!='在本构造记录中，残留只会在暂停后出现':raise ValueError('r08_fixed_hypothesis_meaning_changed')
 if not h['counter_note_ids']:raise ValueError('r08_withdrawal_has_no_counterevidence')
 counter=[]
 for nid in h['counter_note_ids']:
  n=bynote[nid]
  if n.get('kind')=='constructed_observation'and n.get('independent_observation')is True and n.get('pause_before')is False and n.get('residue_observed')is True:counter.append(nid)
 if not counter:raise ValueError('r08_counterexample_does_not_refute_fixed_necessity')
 if byhyp['H-T02'].get('status')!='unknown'or byhyp['H-T03'].get('status')!='unknown':raise ValueError('r08_unconfirmed_alternatives_promoted')
 return {'package_version':'0.1.1','source_problem_version':shared['version'],'retired_hypotheses':['H-T01'],'counterevidence_note_ids':counter,'scope':'fixed_constructed_necessity_counterexample_only_not_real_world_causal_result','state':'lineage_and_fixed_withdrawal_closed'}
