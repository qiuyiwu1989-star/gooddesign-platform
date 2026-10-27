"""068 whole-library scope queue; inclusion is not research completion or a score."""
import json,hashlib,datetime,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];LIB=ROOT/'04-知识库/项目库';OUT=ROOT/'output/research-051/library-campaign'
def build():
 index=LIB/'项目索引.json';xs=json.loads(index.read_text())['projects'];assert len({x['id']for x in xs})==len(xs)
 progress=ROOT/'output/research-051/intake-processing-63/progress.json';active={r['project_id']:r for r in json.loads(progress.read_text())['projects']}if progress.exists()else{}
 rows=[]
 for x in xs:
  r=active.get(x['id']);receipt=OUT/'receipts'/f"{x['id']}.json"
  if r is None and receipt.exists():
   candidate=json.loads(receipt.read_text())
   if candidate.get('project_id')==x['id']:r=candidate
  rows.append({'project_id':x['id'],'name':x['name'],'year':x['year'],'award':x['award'],'priority':0 if x['award']=='金奖'else 1 if r else 2,'current_cycle_stage':r['stage']if r else'已纳入范围，本轮尚未逐项核读','scope_only':not bool(r),'source_intake_directory':str((LIB/x['id']/'04-深研素材/外部投递').relative_to(ROOT)),'quality_score':None,'quality_note':'本队列不评分；旧评分须绑定当前内容版本另核','published_fields_this_cycle':r.get('published_fields',0)if r else 0,'native_pending_fields':r.get('native_pending',0)if r else 0,'partial_reader_mcp_verified':bool(r and r.get('reader_mcp_verified')),'gaps':r['gaps']if r else['先核现档与原件，形成具体缺口；不得假定全库无资料']})
 rows.sort(key=lambda r:(r['priority'],-r['year'],r['project_id']));OUT.mkdir(parents=True,exist_ok=True)
 data={'generated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'index_sha256':hashlib.sha256(index.read_bytes()).hexdigest(),'scope_count':len(rows),'awards':{a:sum(x['award']==a for x in xs)for a in dict.fromkeys(x['award']for x in xs)},'notice':'560是授权处理范围，不是560案已完成Research。现63案进度是局部流程，独立评分/专家/工程验证另列。','projects':rows};(OUT/'全库项目质量提升队列.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 E=lambda s:html.escape(str(s),quote=True)
 table=''.join('<tr><td>'+E(r['project_id'])+'</td><td>'+E(r['name'])+'</td><td>'+E(r['award'])+'</td><td>'+E(r['current_cycle_stage'])+'</td><td>'+E('；'.join(r['gaps']))+'</td></tr>'for r in rows)
 page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>全库项目质量提升队列</title><style>body{font:15px/1.7 system-ui;margin:30px;color:#242637;background:#f7f8fc}main{max-width:1400px;margin:auto}table{width:100%;border-collapse:collapse;background:white}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}input{padding:12px;width:300px;max-width:90%}.scroll{overflow:auto}</style><main><h1>全库项目质量提升队列 · '+str(len(rows))+'项</h1><p>'+E(data['notice'])+'</p><p>'+E(data['generated_at'])+'</p><input aria-label="搜索项目" id="q" placeholder="搜索ID、名称、奖级或阶段"><div class="scroll"><table><thead><tr><th>ID</th><th>项目</th><th>奖级</th><th>本轮阶段</th><th>缺口</th></tr></thead><tbody>'+table+'</tbody></table></div><script>document.querySelector("#q").addEventListener("input",e=>{let q=e.target.value.toLowerCase();document.querySelectorAll("tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))})</script></main></html>'
 (OUT/'全库项目质量提升队列.html').write_text(page);print(json.dumps({'scope_count':data['scope_count'],'awards':data['awards'],'current_intake_cohort':len(active)},ensure_ascii=False))
if __name__=='__main__':build()
