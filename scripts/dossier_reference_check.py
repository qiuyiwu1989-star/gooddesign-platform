# coding: utf-8
"""Compare reported experimental settings, never certify a target operating envelope."""
import math
UNITS={'N':('force',1),'kN':('force',1000),'r/min':('rotation',1),'rpm':('rotation',1),'r/s':('rotation',60),'mm/min':('linear_speed',1),'mm/s':('linear_speed',60),'m/min':('linear_speed',1000)}
def compare_reference(card,request,profiles):
 check=request.get('reference_check')
 if check is None:return dict(status='not_requested',questions=[],outside=[],note='未请求来源工况比较，不代表目标条件已验证。')
 if not isinstance(check,dict):raise ValueError('reference_check must be object')
 profile=next((x for x in profiles if x['id']==check.get('profile_id')),None)
 if not profile or profile['id']not in card.get('evidence_profile_ids',[]):raise ValueError('profile not linked to card')
 questions=[];outside=[];normalized={}
 material=check.get('material_key')
 if material is None:questions.append('请说明实际使用的材料。')
 elif material!=profile['material_key']:outside.append('材料与该来源工况不同，不能直接沿用结果。')
 measures=check.get('measurements',{})
 if not isinstance(measures,dict):raise ValueError('measurements must be object')
 allowed={c['key']for c in profile['controls']}
 if set(measures)-allowed:raise ValueError('unrecognized physical quantity for profile')
 for setting in profile['controls']:
  value=measures.get(setting['key'])
  if value is None:questions.append('请补充'+setting['label']+'及单位。');continue
  if not isinstance(value,dict):raise ValueError('measurement must be object')
  n=value.get('value');unit=value.get('unit')
  if n is None or unit is None:questions.append('请补充'+setting['label']+'及单位。');continue
  if type(n)not in [int,float]or not math.isfinite(n):raise ValueError('measurement must be finite numeric')
  if unit not in UNITS or UNITS[unit][0]!=setting['dimension']:raise ValueError('incompatible unit')
  canonical=n*UNITS[unit][1]/UNITS[setting['unit']][1];normalized[setting['key']]=dict(value=canonical,unit=setting['unit'])
  if not any(math.isclose(canonical,x,rel_tol=1e-9,abs_tol=1e-8)for x in setting['values']):outside.append(setting['label']+'不在该来源明确报告的设定点/档位中；不据此判定工程不可行。')
 return dict(status='outside_source_conditions'if outside else 'needs_information'if questions else 'reported_settings_match',profile_id=profile['id'],questions=questions,outside=outside,normalized=normalized,source_ids=profile['source_ids'],locator=profile['locator'],limits=profile['limits'],note='只比较已报告的设定，不证明各组合、连续区间或目标行业已验证。')
