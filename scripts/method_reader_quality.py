"""055 evidence-bound private presentation of content reviews, never production scores."""
from pathlib import Path
import hashlib,json,html
from method_library_catalog import public_document_base
ROOT=Path(__file__).resolve().parents[1]
E=lambda s:html.escape(str(s))
def quality_section(records):
 base=ROOT/'output/method-reader-review/content-quality';rows=[];calibrated=0;initial=0
 for rid,d in sorted(records.items()):
  status='待内容核读';score='—';task='按原典、操作、完整产物及实际正负例补证';data=None
  for folder in sorted(x.name for x in base.glob('batch*') if x.is_dir()):
   p=base/folder/f'{rid}-assessment.json'
   if p.exists():
    x=json.loads(p.read_text());raw=public_document_base(rid)/'档案'/rid/'档案.json'
    if hashlib.sha256(raw.read_bytes()).hexdigest()==x['dataset_sha256']:data=x;status='内容初评 · 待独立校准';score=str(x.get('total',x.get('score','—')));initial+=1
  for folder in sorted(x for x in base.glob('calibration*') if x.is_dir()):
   p=folder/f'{rid}-calibration-v1.json'
   if data and p.exists():
    c=json.loads(p.read_text())
    if c['dataset_sha256']==data['dataset_sha256']:status='独立Agent校准 · 非专家';score=str(c['calibrated_total']);calibrated+=1;initial-=1;break
  if data:task=data.get('primary_research_task',task)
  rows.append('<tr><td><a href="methods/'+E(rid)+'.html">'+E(d['name'])+'</a></td><td>'+E(score)+'</td><td>'+E(status)+'</td><td>'+E(task)+'</td></tr>')
 return '<section id="content-quality"><h2>逐方法内容质量进度</h2><p>'+str(calibrated)+'份已有独立Agent校准，'+str(initial)+'份初评待校准，其余待内容核读。这是档案内容质量，不是方法本身的价值，也不是工程或专家认证。未评不算0，界面测试不加内容分；本轮尚无达到80分的结论。</p><div class="table-scroll"><table><thead><tr><th>方法</th><th>研究试评分</th><th>状态</th><th>下一步</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section>'
