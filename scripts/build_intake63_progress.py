"""066 private progress from submitted batches and explicit per-project receipts."""
import json,hashlib,html,datetime,sys
from pathlib import Path
import agent_intake as intake
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/research-051/intake-processing-63'
E=lambda s:html.escape(str(s),quote=True)
def build():
 OUT.mkdir(parents=True,exist_ok=True);rows=[]
 for pid,x in intake.catalog().items():
  if x.get('year')not in [2024,2025]:continue
  batches=[];counts={'sources':0,'claims':0,'queries':0};allpass=True
  for bid in ['20261027-doubao-full-01','20261027-doubao-patents-01']:
   p=intake.batch_path(pid,bid);r=intake.validate(p);allpass&=not r['errors'];pins={n:hashlib.sha256((p/n).read_bytes()).hexdigest()for n in ['batch.json','sources.jsonl','claims.jsonl','queries.jsonl']}
   for k in counts:counts[k]+=len(intake.rows(p/(k+'.jsonl')))
   batches.append({'batch_id':bid,'input_sha256':pins,'mechanical_status':r['status']})
  receipt=OUT/'receipts'/f'{pid}.json';detail=json.loads(receipt.read_text())if receipt.exists()else {}
  pin_digest=hashlib.sha256(json.dumps(batches,sort_keys=True).encode()).hexdigest()
  stale=bool(detail)and detail.get('input_pin_sha256')!=pin_digest
  row={'project_id':pid,'name':x['name'],'year':x['year'],'award':x['award'],'counts':counts,'batches':batches,'input_pin_sha256':pin_digest,'mechanical_checked':allpass,'content_reviewed_claims':0,'native_pending':0,'published_fields':0,'reader_mcp_verified':False,'stage':'待内容核读','gaps':['尚未逐条核读，不代表事实成立或质量达标']}
  if detail and not stale:
   for k in ['content_reviewed_claims','native_pending','published_fields','reader_mcp_verified','stage','gaps','evidence_paths','revision','dispositions']:
    if k in detail:row[k]=detail[k]
  if stale:row.update(stage='输入变化待重新核对',gaps=['交付源文件已变化，旧处置不沿用'])
  rows.append(row)
 rows.sort(key=lambda r:(r['award']!='金奖',-r['year'],r['project_id']))
 totals={k:sum(r['counts'][k]for r in rows)for k in ['sources','claims','queries']}
 summary={'generated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'projects':len(rows),'batches':sum(len(r['batches'])for r in rows),'mechanical_pass_projects':sum(r['mechanical_checked']for r in rows),'content_reviewed_claims':sum(r['content_reviewed_claims']for r in rows),'native_pending_fields':sum(r['native_pending']for r in rows),'published_fields':sum(r['published_fields']for r in rows),'reader_mcp_verified_projects':sum(bool(r['reader_mcp_verified'])for r in rows),**totals,'quality_score_claim':None}
 data={'summary':summary,'projects':rows};(OUT/'progress.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 tr=''.join('<tr><td>'+E(r['project_id'])+'</td><td>'+E(r['name'])+'</td><td>'+E(r['award'])+'</td><td>'+str(r['counts']['claims'])+'</td><td>'+str(r['content_reviewed_claims'])+'</td><td>'+str(r['native_pending'])+'</td><td>'+str(r['published_fields'])+'</td><td>'+E(r['stage'])+'</td><td>'+E('；'.join(r['gaps']))+'</td></tr>'for r in rows)
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>63项目资料核读入档进度</title><style>body{font:15px/1.7 system-ui;margin:32px;color:#202432;background:#f7f8fc}main{max-width:1400px;margin:auto}h1{font-size:28px}section{background:white;padding:20px;border-radius:12px;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:12px;text-align:left;border-bottom:1px solid #e5e7ef;vertical-align:top}th{white-space:nowrap}input{padding:12px;min-width:250px;border:1px solid #ccd0dd;border-radius:8px}.scroll{overflow:auto}p{max-width:1000px}</style><main><h1>63项目资料核读与入档</h1>'''
 page+='<p>更新于 '+E(summary['generated_at'])+'。本机内部进度；机械通过不等核读、发布或80分。处理数仅计本轮外部批次，既有档案版本不冒充本轮成果。调用验收仅指已发布范围（当前可仅为身份版），不代表全案资料核读完成。</p><section>'+E(f"63项目 / {summary['batches']}批次 · {summary['claims']}候选 · 已核读处置{summary['content_reviewed_claims']}条 · 待审核候选{summary['native_pending_fields']}字段 · 已发布{summary['published_fields']}字段 · 阅读与MCP验收{summary['reader_mcp_verified_projects']}案")+'</section><input id="q" aria-label="搜索项目" placeholder="搜索项目ID、名称、状态或缺口"><section class="scroll"><table><thead><tr><th>ID</th><th>项目</th><th>奖级</th><th>候选</th><th>核读处置</th><th>待审核字段</th><th>发布字段</th><th>阶段</th><th>缺口</th></tr></thead><tbody>'+tr+'</tbody></table></section><script>document.querySelector("#q").addEventListener("input",e=>{let q=e.target.value.toLowerCase();document.querySelectorAll("tbody tr").forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))})</script></main></html>'
 (OUT/'63项目核读入档进度.html').write_text(page);print(json.dumps(summary,ensure_ascii=False));return data
if __name__=='__main__':build()
