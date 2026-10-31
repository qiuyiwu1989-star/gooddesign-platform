"""Audit actual frozen internal pilot files, retain failures, never synthesize outputs."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'output/innovation-loop-024/evaluation/round2'
def sha(b):return hashlib.sha256(b).hexdigest()
def collect():
 p=BASE/'internal-pilot-protocol.json';protocol=json.loads(p.read_text());psha=sha(p.read_bytes());records=[]
 for pin in protocol['input_pins']+protocol['source_pins']:
  if sha((ROOT/pin['path']).read_bytes())!=pin['sha256']:raise ValueError('frozen_input_changed:'+pin['path'])
 for run in protocol['runs']:
  target=BASE/'outputs'/(run['run_id']+'.md');r={'run_id':run['run_id'],'task_id':run['task_id'],'arm':run['arm'],'replicate':run['replicate'],'input_sha256':run['input_sha256'],'protocol_sha256':psha,'model_declared':protocol['model'],'provider_build':None,'actual_tokens':None,'fee':None,'elapsed_seconds':None,'timeout_evidence':'supervisor_observed_no_timeout; exact per-run timing not captured, cannot certify 600s cap','generation_agent':'pilot024_%02d'%(protocol['runs'].index(run)+1)}
  if not target.exists():r.update(status='missing')
  else:
   raw=target.read_bytes();text=raw.decode();r.update(output_ref=str(target.relative_to(BASE)),output_sha256=sha(raw),characters=len(text),bytes=len(raw))
   if not text.strip():r.update(status='failed',failure_reason='empty_output')
   elif len(text)>5000:r.update(status='failed',failure_reason='output_cap_exceeded_original_preserved')
   else:r.update(status='succeeded')
  records.append(r)
 result={'protocol_sha256':psha,'planned':24,'succeeded':sum(r['status']=='succeeded' for r in records),'failed':sum(r['status']=='failed' for r in records),'missing':sum(r['status']=='missing' for r in records),'records':records,'io_recoveries':[{'run_id':i,'error':'initial_outputs_directory_missing','recovery':'same_original_text_resaved_without_regeneration'} for i in ['polish-v1-B-2','rubber-v1-C-2']],'limitations':['per-run elapsed/token/fee not captured; no equal-total-compute claim','domain effectiveness not established']}
 (BASE/'actual-run-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result
if __name__=='__main__':
 x=collect();print(json.dumps({k:x[k] for k in ['planned','succeeded','failed','missing']},ensure_ascii=False))
