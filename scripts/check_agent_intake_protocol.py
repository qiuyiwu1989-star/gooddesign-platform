import sys,json,hashlib,tempfile,copy
from pathlib import Path
sys.path.insert(0,'scripts');import agent_intake as a
h=lambda b:hashlib.sha256(b).hexdigest()
results=[]
with tempfile.TemporaryDirectory(dir='output/agent-intake-validation')as tmp:
 lib=Path(tmp).resolve();a.LIB=lib;a.dump(lib/'项目索引.json',{'projects':[{'id':'2025-04','name':'协议测试夹具，非研究资料'}]})
 batch='20261027-fixture-only-01';a.init('2025-04',batch,'fixture','protocol_check');p=a.batch_path('2025-04',batch)
 results.append({'case':'empty_draft_refused','pass':a.validate(p)['status']=='needs_correction'})
 raw=b'fixture only';text='测试夹具：延时为3秒，非项目事实。';(p/'原件/test.txt').write_bytes(raw);(p/'可读件/test.txt').write_text(text)
 b=json.loads((p/'batch.json').read_text());b['status']='submitted';a.dump(p/'batch.json',b)
 source={'source_id':'S1','url':'https://example.org/fixture','title':'fixture','publisher':'fixture','retrieved_at':'2026-10-27T00:00:00Z','source_type':'other','access_status':'downloaded','read_scope':'excerpt','project_relation':'unresolved','relation_basis':'测试夹具非事实','rights_status':'private','files':[{'path':'原件/test.txt','role':'original','sha256':h(raw)},{'path':'可读件/test.txt','role':'readable','sha256':h(text.encode())}]}
 claim={'claim_id':'C1','module':'指标与验证','kind':'source_statement','statement':'测试夹具','object':'fixture','limitations':'非事实','evidence':[{'source_id':'S1','readable_path':'可读件/test.txt','quote':'延时为3秒','locator':'第1段'}]}
 query={'query':'fixture','site_or_engine':'fixture','searched_at':'2026-10-27T00:00:00Z','outcome':'found','source_ids':['S1']}
 def write(s=source,c=claim,q=query):
  for name,row in [('sources',s),('claims',c),('queries',q)]:(p/f'{name}.jsonl').write_text(json.dumps(row,ensure_ascii=False)+'\n')
 write();before=h((p/'原件/test.txt').read_bytes());results.append({'case':'valid_excerpt_pass','pass':a.validate(p)['status']=='mechanical_pass_pending_content_review'})
 cases=[]
 s=copy.deepcopy(source);s['files'][0]['sha256']='0'*64;cases.append(('bad_hash',s,claim,query))
 s=copy.deepcopy(source);s['files'][0]['path']='../escape';cases.append(('path_traversal',s,claim,query))
 c=copy.deepcopy(claim);c['evidence']=[];cases.append(('fact_without_evidence',source,c,query))
 c=copy.deepcopy(claim);c['evidence'][0]['quote']='不在原文';cases.append(('nonverbatim_quote',source,c,query))
 s=copy.deepcopy(source);s['read_scope']='unread';cases.append(('unread_fact',s,claim,query))
 s=copy.deepcopy(source);s['read_scope']='fulltext';s['files']=s['files'][1:];cases.append(('fulltext_without_original',s,claim,query))
 q=copy.deepcopy(query);q['outcome']='planned';cases.append(('planned_query',source,claim,q))
 for name,s,c,q in cases:write(s,c,q);results.append({'case':name,'pass':a.validate(p)['status']=='needs_correction'})
 try:a.init('2025-04',batch,'other','collision');ok=False
 except FileExistsError:ok=True
 results.append({'case':'no_batch_overwrite','pass':ok});results.append({'case':'original_bytes_unchanged','pass':h((p/'原件/test.txt').read_bytes())==before})
 assert all(x['pass']for x in results),results
Path('output/agent-intake-validation/result.json').write_text(json.dumps({'fixture_only':True,'checks':results,'production_data_modified':False},ensure_ascii=False,indent=2));print(json.dumps(results))
