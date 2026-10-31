"""Read-only byte and exact quotation checks; never semantic approval."""
import hashlib,json,re
from pathlib import Path
from innovation_loop_experience import validate_experience
from innovation_loop_store import ROOT
import project_pipeline as pp
import research_workflow as rw

def verify_experience_files(record,library_root=ROOT/'04-知识库/项目库'):
 r=validate_experience(record);lib=Path(library_root).resolve();checks=[]
 def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
 for e in r['evidence_refs']:
  if not re.fullmatch(r'[0-9]{4}-[a-z0-9]+',e['project_id']):raise ValueError('invalid_project_id')
  project=lib/e['project_id'];chunk=(project/e['chunks_path']).resolve();dataset=Path(e['dataset_path']).resolve()
  if not chunk.is_relative_to(project.resolve()) or not dataset.is_relative_to(project.resolve()):raise ValueError('evidence_path_outside_project')
  if sha(chunk)!=e['chunks_sha256'] or sha(dataset)!=e['dataset_sha256']:raise ValueError('evidence_file_hash_mismatch')
  source=pp.state(project)['sources'].get(e['source_id'])
  if source is None or source['sha256']!=e['source_sha256'] or sha(pp.safe(project,source['original']))!=e['source_sha256']:raise ValueError('source_original_hash_mismatch')
  if pp.safe(project,source['chunks']).resolve()!=chunk:raise ValueError('source_chunk_path_mismatch')
  blocks=json.loads(chunk.read_text());block=next((b for b in blocks if b['id']==e['chunk_id']),None)
  if block is None or e['quote'] not in block['text']:raise ValueError('quote_not_in_exact_block')
  if e.get('quote_sha256') and hashlib.sha256(e['quote'].encode()).hexdigest()!=e['quote_sha256']:raise ValueError('quote_hash_mismatch')
  if e.get('provenance_layer')=='source_level' or dataset==chunk:
   if dataset!=chunk or e.get('dataset_role')!='conversion_blocks_only_not_published_native_dataset' or e.get('native_published_record') is not False:raise ValueError('source_level_cannot_claim_native_publication')
  else:
   folder,_=rw.check_version(project,e['research_revision'])
   if dataset!=(folder/'档案.json').resolve():raise ValueError('not_exact_native_dataset')
   cell=rw.cell(json.loads(dataset.read_text()),e['record_id'],e['field'])
   if not isinstance(cell,dict):raise ValueError('native_field_not_found')
   native=cell.get('evidence',{})
   for key in ['source_id','source_sha256','chunk_id','chunks_sha256','quote']:
    if native.get(key)!=e[key]:raise ValueError('native_field_evidence_mismatch:'+key)
  # Conversion/source-level provenance is explicit and cannot pose as published field verification.
  checks.append({'source_id':e['source_id'],'chunk_id':e['chunk_id'],'quote_bytes_verified':True,'native_record_claimed':e.get('native_published_record',True)})
 return {'experience_id':r['id'],'checks':checks,'semantic_approval':False}
