"""Private evidence-gap queue; report presence never implies admission or score."""
from pathlib import Path
import json,html,hashlib
ROOT=Path(__file__).resolve().parents[3]
b=ROOT/'output/research-051';q=json.loads((b/'coverage-round2/逐案深化队列-v1.json').read_text());reports={}
for p in sorted((b/'deepening-round1').glob('batch*/index.json')):
 for c in json.loads(p.read_text()).get('cases',[]):
  report=ROOT/c['report']
  if c.get('report_sha256') and hashlib.sha256(report.read_bytes()).hexdigest()!=c['report_sha256']:raise ValueError(report)
  json.loads(report.read_text());reports[c['project_id']]=c
assert len(q['items'])==98 and len({x['project_id']for x in q['items']})==98
E=lambda x:html.escape(str(x));rows=[]
for x in sorted(q['items'],key=lambda x:(x['priority'],x['project_id'])):
 c=reports.get(x['project_id']);status='本轮定向补证报告已保存 · 待独立审核' if c else '待定向补证'
 rows.append('<tr>'+''.join('<td>'+E(v)+'</td>'for v in [x['project_id'],x['name'],x['priority'],status,x['critical_gap']])+'</tr>')
page='<!doctype html><meta charset="utf-8"><title>98案逐项深化</title><style>body{font:15px/1.7 system-ui;margin:32px;color:#263044}table{border-collapse:collapse;width:100%}td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}input{padding:12px}.scroll{overflow:auto}</style><h1>98案：从基础覆盖到定向深化</h1><p>基础检索报告98案齐备；本轮定向补证已有'+str(len(reports))+'案报告。报告保存、独立审核、生产入档和质量评分是不同状态。本页不替代内容审核，不宣称已审、采用或80分。</p><p>P0先解身份归属冲突；P1补一手正文；P2补验证条件与采用映射。优先级不是质量分数。</p><input id="q" placeholder="搜索项目、缺口或状态"><div class="scroll"><table><thead><tr><th>编号</th><th>项目</th><th>顺序</th><th>本轮状态</th><th>首要缺口</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div><script>q.oninput=()=>document.querySelectorAll("tbody tr").forEach(x=>x.hidden=!x.textContent.includes(q.value))</script>'
out=b/'deepening-round1/深化进度.html';out.write_text(page);print('98 rows;',len(reports),'saved reports; no admission inferred')
