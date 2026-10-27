# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,re
D=Path(__file__).parent;ROOT=D.parents[2];audit=json.loads((D/'质量缺口台账.json').read_text());dimensions=['身份与边界准确','机制讲透','判断可操作','完整示范','反例与迁移','依据可追溯','阅读与交接'];maps=[];selfchecks=[];externals=[]
new=json.loads((D/'优先三法来源与改动.json').read_text())['sources']
for m in audit['methods']:
 rid=m['method_id'];p=D/'稿件'/(rid+'.md');lines=p.read_text().splitlines();assert len(lines)>5
 find=lambda terms:next((i+1 for i,t in enumerate(lines)if any(x in t for x in terms)),1)
 locs=[find(['出处','作者','NASA','NIST','依据','原论文']),find(['先','从','用于']),find(['决定','选择','返回','行动']),find(['完整构造','完整独立','构造例','教学候选','可跟随']),find(['两种','两类','误用']),find(['https://','出处定位']),find(['交接','输出','交付','引擎'])]
 claims={'method_id':rid,'manuscript':'稿件/'+rid+'.md','manuscript_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'prior_source_claims_path':m['evidence_locations'][1]['path'],'prior_source_claims_sha256':hashlib.sha256((ROOT/m['evidence_locations'][1]['path']).read_bytes()).hexdigest(),'selected_source_range':'source-specific locators in manuscript and previous locked source claims; not all full originals','new_sources':new.get(rid,[]),'source_urls_in_manuscript':re.findall(r'https?://[^)\s]+',p.read_text()),'platform_material':'all new examples/decision rules beyond named source principles explicitly constructed or adapted; no customer observation','tutorial_identity':'公开资料例'if rid=='R46'else'构造例/方法说明，不是真实现场试验'}
 maps.append(claims)
 vals=[]
 for dim,ln in zip(dimensions,locs):vals.append({'dimension':dim,'rating':'局部'if dim=='依据可追溯'and rid in['WB09','WB10','WB11','WB12']else'充分','location':{'path':claims['manuscript'],'line':ln},'reason':{'身份与边界准确':'版本/方法层级及近邻边界在正文具体说明；不冒原著全实现','机制讲透':'解释表示/模型为什么推进设计并列前提','判断可操作':'给证据、选择/返回和下一行动，未知不默认通过','完整示范':'给完整正向构造推演/记录及行动，原始身份明确','反例与迁移':'至少两种实质误用与另一情境差异，非只非法输入测试','依据可追溯':'关键原理回源；WB专著/公式具体不足保留，其余核读范围逐项说明','阅读与交接':'连贯解释、阶段产物和相邻方法输入输出'}[dim]})
 selfchecks.append({'method_id':rid,'dimensions':vals,'assessor':'authoring agent self-check only, not independent approval','status':'pending_independent_content_review'})
 externals.append({'method_id':rid,'external_need':m['work_items'][2]['action'],'affected_conclusion':m['work_items'][2]['blocks'],'usable_scope':'manuscript method teaching and explicit construction; not target engineering/customer conclusion','newly_resolved':'R49 actual author-uploaded body selected passages now reviewed, no longer abstract-only'if rid=='R49'else'body and teaching reasoning expanded; source gaps not silently erased'})
assert len(maps)==21
for n,v in [('来源主张映射.json',{'methods':maps}),('七维作者自查.json',{'purpose':'qualitative drafting aid; independent reviewer may disagree','methods':selfchecks}),('实际外部缺口.json',{'methods':externals})]:(D/n).write_text(json.dumps(v,ensure_ascii=False,indent=2))
(D/'README.md').write_text('''# ML021 内容深化：validation组21法

21稿位于稿件/，逐项源头/构造身份见来源主张映射；旧稿实质缺口与本轮计划见质量缺口台账。教学附件和两份复算脚本保存完整决策例，不能解释为实际工程试验。

本轮补了可跟随的选择/修订/行动，研究状态和技术检查未占正文主体。R49由摘要边界推进到原作者上传正文选段；R38补完整RSM；R52补信息与行动阈值；其他条目按任务机制展开。

七维作者自查不是自批上线，21项均待独立内容审核。外部材料/专业/客户/实测依赖逐项列明。原件private-sources忽略且不进入manifest，不发布、不改旧包或核心。独立审核-needs/是本组另承担的只读评审，不属于这21篇作者冻结稿范围。
''')
files=[{'path':str(p.relative_to(D)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(D.rglob('*'))if p.is_file()and'private-sources'not in p.parts and'__pycache__'not in p.parts and'独立审核-needs'not in p.parts and p.name!='manifest.json']
(D/'manifest.json').write_text(json.dumps({'schema':'ML021-content-manifest-1','version':'0.1.0','date':'2026-10-28','methods':21,'status':'frozen_for_independent_content_review_not_online_approval','exclude':['private-sources','独立审核-needs'],'files':files},ensure_ascii=False,indent=2));print('21 manuscripts frozen',len(files),'files; manifest',hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest())
