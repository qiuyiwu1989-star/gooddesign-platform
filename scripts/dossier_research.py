# coding: utf-8
"""019: reproducible descriptive statistics and source-condition relationships."""
import json,statistics,html
from pathlib import Path
read=lambda p:json.loads(p.read_text())
def build(p):
 d=read(p/'档案数据.json');e=read(p/'研究证据.json');profiles=e['profiles'];studies={x['id']:x for x in d['validations']}
 sources={x['id']for x in d['sources']};claims={x['id']for x in d['claims']};assert len({x['id']for x in profiles})==len(profiles)
 for x in profiles:
  assert set(x['source_ids'])<=sources and set(x['claim_ids'])<=claims and x['validation_id']in studies
  assert x['locator']and x['limits']
  for c in x['controls']:assert c['kind']in ['discrete_test_levels','reported_setpoint']and c['values']and c['unit']
 rows=studies['V02']['trials'];groups=[]
 for group in ['SY01','SY02']:
  rr=[r for r in rows if r['group']==group];results={}
  for field,unit in [('sample_mass_g','g'),('sample_length_mm','mm')]:
   values=[r[field]for r in rr];results[field]=dict(mean=round(statistics.mean(values),4),sample_sd=round(statistics.stdev(values),4),minimum=min(values),maximum=max(values),unit=unit)
  groups.append(dict(group=group,n=len(rr),row_ids=[r['id']for r in rr],metrics=results))
 comparisons=[]
 for field in ['sample_mass_g','sample_length_mm']:
  a=groups[0]['metrics'][field];b=groups[1]['metrics'][field]
  comparisons.append(dict(metric=field,absolute_difference=round(b['mean']-a['mean'],4),relative_difference_percent=round((b['mean']/a['mean']-1)*100,4),unit=a['unit']))
 result=dict(version='descriptive-analysis-0.1.0',nature='platform_derived_not_original_measurement',source_ids=['S23'],locator='1032页表4',input_validation='V02',groups=groups,comparisons=comparisons,formula=dict(mean='sum(values)/n',sample_sd='sqrt(sum((x-mean)^2)/(n-1))',relative_difference='(mean_SY02-mean_SY01)/mean_SY01*100'),limits=['每组仅5次，随机化和样本独立性未明确','不作显著性、因果效应、飞行收益或商业收益判断','质量与长度分别统计；不作为层序保持程度指标'])
 (p/'研究分析.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');return result

def render(p):
 stats=build(p);data=read(p/'研究证据.json');audit=read(p/'引擎审计.json');e=lambda v:html.escape(str(v))
 rows=''.join(f'<tr><td>{e(x["title"])}</td><td>{e(x["material_label"])}</td><td>{e(x["result"])}</td></tr>'for x in data['profiles'])
 body='<details class="reader-expand" id="reader-research-depth"><summary>工况与结果：哪些数据可以一起比较</summary><p class="reader-note">相同控制方法在不同材料和目标下，结果可能不同。来源中的设定点不等于可用范围。</p><div class="table-wrap reader-table"><table><thead><tr><th>试验</th><th>对象</th><th>结果与边界</th></tr></thead><tbody>'+rows+'</tbody></table></div><h3>两种取芯控制方式的描述统计</h3><div class="table-wrap reader-table"><table><thead><tr><th>组别</th><th>次数</th><th>平均质量 / g</th><th>平均长度 / mm</th></tr></thead><tbody>'+''.join(f'<tr><td>{"恒速"if x["group"]=="SY01"else "恒力载"}</td><td>{x["n"]}</td><td>{x["metrics"]["sample_mass_g"]["mean"]:g}</td><td>{x["metrics"]["sample_length_mm"]["mean"]:g}</td></tr>'for x in stats['groups'])+'</tbody></table></div><p class="reader-note">平台按论文表4的10行数据复算；每组仅5次。均值差不等于因果收益，也不代表飞行性能或样品层序保持效果。</p><button class="reader-link" data-paper="A04">阅读原论文解读 ↗</button></details>'
 rows=''.join(f'<tr><td>{e(x["dimension"])}</td><td>{e(x["finding"])}</td><td>{e(x["this_round"])}</td><td>{e(x["remaining"])}</td></tr>'for x in audit['dimensions'])
 assessment='<details class="reader-expand" id="reader-engine-audit"><summary>创新引擎视角：12项深度检查</summary><p class="reader-note">'+e(audit['summary'])+'</p><div class="table-wrap reader-table"><table class="engine-audit-table"><thead><tr><th>维度</th><th>发现</th><th>本轮处理</th><th>仍需补充</th></tr></thead><tbody>'+rows+'</tbody></table></div><p class="reader-note">'+e(audit['score_review'])+'</p></details>'
 return dict(body=body,assessment=assessment)
