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
 return '<section id="content-quality"><h2>逐方法内容质量进度</h2><p>'+str(calibrated)+'份已有独立Agent校准，'+str(initial)+'份初评待校准，其余待内容核读。这是档案内容质量，不是方法本身的价值，也不是工程或专家认证。未评不算0，界面测试不加内容分；本轮尚无达到80分的结论。</p><div class="table-scroll"><table><thead><tr><th>方法</th><th>研究试评分</th><th>状态</th><th>下一步</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section>'+upgrade_section()


def upgrade_section():
 """Keep reviewed upgrade snapshots separate from frozen baseline scores."""
 b=ROOT/'output/method-reader-review/reviews';rows=[]
 specs=[('R17','R17-composite-v2-calibration/calibration.json','76.25','组合升级版 · 独立Agent校准','教学跨情境程序实测；仍缺真实使用者与工程应用证据'),('R36','R36-composite-v1-reassessment/assessment.json','75','组合升级版 · 初评待另一Agent校准','缺跨实际任务应用、真实可读性观测及多轮改进'),('R44','R44-composite-v1-reassessment/assessment.json','68.75','组合升级版 · 初评待另一Agent校准','缺操作原典深度，以及真实原型、原始观察和学习决定链')]
 for rid,rel,score,status,gap in specs:
  p=b/rel
  if not p.exists():continue
  d=json.loads(p.read_text())
  if rid=='R17':
   src=ROOT/d['source_assessment']
   if hashlib.sha256(src.read_bytes()).hexdigest()!=d['source_assessment_sha256']:continue
   if str(d['calibrated_total'])!=score:continue
  elif str(d['total_score']).rstrip('0').rstrip('.')!=score:continue
  if rid in ['R36','R44']:
   cp=b/(rid+'-composite-v1-calibration/calibration.json')
   if cp.exists():
    c=json.loads(cp.read_text())
    if c.get('independent_calibration_completed') and float(c['calibrated_total'])==float(score):status='组合升级版 · 独立Agent校准'
  rows.append('<tr><td><a href="methods/'+rid+'.html">'+rid+'</a></td><td>'+E(score)+'</td><td>'+E(status)+'</td><td>'+E(gap)+'</td></tr>')
 if not rows:return ''
 return '<section id="upgrade-quality"><h2>增补版本有了哪些进步</h2><p>以下单独评估新教学产物与适配组合，不覆盖上表冻结档案的分数。分数按各次报告的版本与证据快照解释；软件通过、教学复算、真实应用和专家审核分别记录，均未达到80分验收。</p><div class="table-scroll"><table><thead><tr><th>方法</th><th>增补试评分</th><th>评审状态</th><th>主要未达项</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section>'
