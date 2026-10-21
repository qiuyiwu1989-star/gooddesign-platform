# coding: utf-8
"""040: real SDK retrieval plus an explicitly authored, fixed-scenario research demonstration.
This script replays a Codex-authored analysis. It is not a general automatic inference engine.
"""
import argparse,asyncio,copy,datetime,hashlib,json,os,secrets,sys,tempfile,shutil
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
import project_pipeline as pp
import research_workflow as rw
import innovation_methods as im
ROOT=pp.ROOT
TASK=im.LIB/'联动示例/模拟企业需求.json'
def build_analysis(task,methods,records,evidence):
 gate=im.task_gate(task)
 seed=pp.load(TASK)
 if any(task.get(k)!=seed[k]for k in ['actor','object','desired_outcome','boundary']):raise ValueError('场景核心内容已变更，固定分析不能套用新场景')
 if task['task_id']!='DEMO-GRANULAR-001':raise ValueError('只支持已编写的DEMO-GRANULAR-001研究演示；请为新任务开展独立研究')
 ev={e['evidence_id']:e for e in evidence}
 for key,phrase in [('E01','几乎没有相对运动'),('E02','取芯通道保持通畅'),('E03','不利于封口'),('E04','塑形变形'),('E05','开展10次'),('E06','表4')]:
  if phrase not in ''.join(ev[key]['text'].split()):raise ValueError('示例所需原文不匹配:'+key)
 problem=dict(task_id=task['task_id'],actor=task['actor'],object=task['object'],desired_outcome=task['desired_outcome'],boundary=task['boundary'],requirements=copy.deepcopy(task['success_metrics']),constraints=copy.deepcopy(task['constraints']),unknowns=gate['unknowns'],decision_level=gate['decision_level'],root_cause_status='not_established',baseline=task['existing_system'],framing='在目标材料与设备约束下，同时研究样品信息保持和完整取样链的稳定性；不能仅用回收质量代表层序保持。',nature='platform_analysis_of_simulated_task')
 functions=[
  dict(id='F01',verb='建立',object='可进入的取样路径',output='进入取样区域',requirement='取得足够样品',evidence_ids=['E01'],status='target_function_hypothesis'),
  dict(id='F02',verb='引导',object='原位样品进入收集界面',output='受控进样',requirement='取样连续性',evidence_ids=['E01','E02'],status='target_function_hypothesis'),
  dict(id='F03',verb='包覆/保持',object='样品原有排列',output='可检查的层序信息',requirement='层序保持',evidence_ids=['E01'],status='target_function_hypothesis'),
  dict(id='F04',verb='隔离',object='不应进入机构间隙的颗粒',output='机构间隙受保护',requirement='堵塞与泄漏控制',evidence_ids=['E02','E03'],status='target_function_hypothesis'),
  dict(id='F05',verb='封装并转送',object='已获取样品',output='可识别的封装样品',requirement='完整作业链成功',evidence_ids=['E03','E04'],status='target_function_hypothesis'),
  dict(id='F06',verb='观测并调节',object='作业载荷与运动',output='过程状态及调整',requirement='异常工况可控',evidence_ids=['E05','E06'],status='conditional_on_sensing_and_need')]
 interactions=[
  dict(id='I01',subject='进样部件',action='将样品送入',object='收集界面',result='连续收集',kind='useful',phase='采样',epistemic_status='target_required_function',evidence_ids=['E01']),
  dict(id='I02',subject='收集界面',action='相对滑移或挤压',object='样品结构',result='可能扰动层序',kind='potential_harm',phase='采样',epistemic_status='target_risk_not_observed_failure',evidence_ids=['E01']),
  dict(id='I03',subject='细颗粒',action='进入',object='机构间隙',result='可能造成阻塞或泄漏',kind='potential_harm',phase='采样',epistemic_status='patent_describes_source_risk_target_unverified',evidence_ids=['E02','E03']),
  dict(id='I04',subject='刚性环/封口接口',action='施加约束',object='软袋及封口件',result='可能增加封口负担',kind='potential_harm',phase='封装',epistemic_status='source_patent_statement_target_unverified',evidence_ids=['E03']),
  dict(id='I05',subject='开槽/开瓣结构',action='改变柔顺性',object='封口及进样界面',result='可能改善兼容，同时引入泄漏/变形风险',kind='tradeoff_hypothesis',phase='采样与封装',epistemic_status='source_patent_comparison_not_independent_test',evidence_ids=['E03','E04'])]
 model=dict(boundary=task['boundary'],nodes=['取样部件','样品','收集界面','间隙保护','封口件','转送端','状态观测'],functions=functions,interactions=interactions,priority_issues=[dict(id='ISSUE01',function_ids=['F03','F04','F05'],description='收集信息保持、颗粒隔离与封口接口的协同',basis='源专利对不同环构型记载了具体取舍；目标材料和结构尚未确定',evidence_ids=['E01','E02','E03','E04'])],nature='platform_function_model_not_existing_enterprise_machine')
 technical=[dict(id='TC01',source_case_statement='专利描述整环刚度较高时可能增加封口提芯力；开槽/开瓣提高柔顺性与兼容性，同时存在细颗粒泄漏和变形风险。',target_statement='若企业采用类似收集/封口接口，提高柔顺性以便封装，可能损失隔离与形状稳定性。',improved='封口兼容性/收集界面通过性',worsened='泄漏、颗粒隔离与结构稳定性风险',variable='接口局部柔顺性与间隙构型',conditions='仅当目标构型和颗粒路径确有相同耦合时',proof_status='source_patent_description_target_hypothesis',evidence_ids=['E03','E04'],missing_causal_data=['企业材料与目标构型','可重复的变形/泄漏/封口对照']),dict(id='TC02',source_case_statement='论文研究样心与软袋相对运动及取心率。',target_statement='提高处理强度或速度是否损害层序保持，需要企业对照数据；当前不能确认因果矛盾。',improved='处理速度或适应性（待定义）',worsened='层序扰动（待测）',variable=None,conditions='目标工况未知',proof_status='target_candidate_not_confirmed',evidence_ids=['E01'],missing_causal_data=['速度—扰动的实测关系','目标处理量与层序阈值'])]
 physical=[dict(id='PC01',object='收集/封口接口',property='局部柔顺性',opposing_requirements=['可顺应封口动作','能维持保护性几何'],conditions='位置、载荷和阶段待澄清',status='candidate_not_proven_physical_contradiction',evidence_ids=['E03','E04'],next_question='这些要求能否由不同部位承担？是否真的要求同一部位在同一条件下具备相反属性？'),dict(id='PC02',object='取样通道',property='开闭状态',opposing_requirements=['采样时开放','封装时关闭'],conditions='不同作业阶段',status='ordinary_sequence_possible_not_counted_as_inventive_conflict',evidence_ids=['E03'],next_question='仅有先开后关不足以认定发明矛盾；需要证明现结构/资源导致两要求不可兼容。')]
 directions=[
 dict(id='D01',title='先研究样品与收集界面的相对运动',proposal='把“取到样品”与“保留层序信息”设为独立要求，比较现有收集方式和低相对滑移的收集界面；柔性内衬仅为候选实现。',requires=['flexible_contact_allowed'],evidence_ids=['E01'],method_step_ids=['IM-PD-001-S04','IM-FA-001-S02','IM-CA-001-S04'],source_knowledge_ids=['K01','TECH-01'],assumptions=['允许接触材料且材料相容','目标样品确需保持排列'],costs_and_risks=['内衬磨损、褶皱、清洁与污染风险','回收量相近仍可能存在层序偏差'],validation_id='V-TARGET-01'),
 dict(id='D02',title='把间隙保护和封口兼容作为一个接口问题研究',proposal='分别定义隔离颗粒、顺应封口及结构支撑的功能，比较功能分区或不同阶段的约束方式；按目标粒径重新设计，不复制专利尺寸或假定可实施权利。',requires=['interface_redesign_allowed'],evidence_ids=['E02','E03','E04'],method_step_ids=['IM-FA-001-S04','IM-CA-001-S02','IM-CA-001-S04','IM-CA-001-S05'],source_knowledge_ids=['K02','P04'],assumptions=['目标系统确有相同接口耦合','可改造接口并能测试样品偏倚'],costs_and_risks=['额外结构/动作增加复杂度','防颗粒方案可能筛除目标颗粒，改变代表性','相关实施权利未知'],validation_id='V-TARGET-02'),
 dict(id='D03',title='在确认载荷波动是瓶颈后，再探索反馈控制',proposal='仅当企业测得载荷波动影响取样且允许传感改造时，比较固定运动与载荷反馈策略。先识别目标动态特性，不能使用月壤试验的设定作为企业参数。',requires=['load_sensing_allowed'],evidence_ids=['E05','E06'],method_step_ids=['IM-FA-001-S03','IM-CA-001-S05','IM-CA-001-S06'],source_knowledge_ids=['K06','TEST-02'],assumptions=['问题确与载荷波动相关','能取得足够可靠的观测与控制响应'],costs_and_risks=['传感、调参、超调与故障处置成本','原文地面试验不能保证企业性能'],validation_id='V-TARGET-03')]
 directions=im.filter_directions(directions,task['constraints'])
 questions=[dict(priority='先确认',question='实际材料是什么？粒径分布、黏聚性、含水量、温度和相容性如何？',blocks=['D01','D02','D03']),dict(priority='先确认',question='层序保持怎样测量？允许的偏移/混合程度及样品量下限是什么？',blocks=['工程验收','效果比较']),dict(priority='先确认',question='现有设备和真实失败记录是什么？目前最主要的问题是哪一环节？',blocks=['根因诊断','方案优先级']),dict(priority='先确认',question='是否允许柔性材料接触、接口改造及载荷传感？',blocks=['D01','D02','D03']),dict(priority='随后确认',question='目标深度、作业节拍、功耗、空间、清洁要求和预算各是什么？',blocks=['工程定型','成本评估'])]
 validations=[
 dict(id='V-TARGET-01',direction='D01',hypothesis='低相对滑移界面在目标材料下能减少扰动，同时维持足够回收量',comparison='现有方式（企业需提供）与候选界面；先控制材料、分层标记、作业规程和样品尺度',measurements=['层序偏移/混合程度','回收量','卡滞、损伤与污染'],acceptance='指标阈值由企业在试验前确认；当前留空',thresholds=None,stop='若不能改善层序，或材料不相容/产生额外污染，则停止该方向',result='not_tested'),
 dict(id='V-TARGET-02',direction='D02',hypothesis='功能分担的接口能改善封口兼容，并不引入不可接受泄漏/偏倚',comparison='目标接口不同构型；记录粒径、间隙、构型、载荷和封口动作',measurements=['封口力/行程与成功情况','泄漏量','堵塞/变形','采后粒径分布偏差'],acceptance='先确认隔离对象、允许泄漏/偏倚和封口要求',thresholds=None,stop='封口改善伴随不可接受泄漏、损伤或样品偏倚时不通过',result='not_tested'),
 dict(id='V-TARGET-03',direction='D03',hypothesis='反馈策略在目标设备上改善过程稳定性且不引入不可接受超调',comparison='同目标材料与机构，比较固定输入和反馈；试验次数与控制参数待设计',measurements=['峰值和稳定时间','回收量与层序保持','异常恢复和全链成功'],acceptance='企业确认安全边界、响应与样品质量阈值',thresholds=None,stop='超调、传感失效或层序破坏超过确认边界则停止',result='not_tested')]
 brief=dict(task_id=task['task_id'],title='颗粒材料分层取样设备：基于嫦娥案例的创新研究建议',decision_level=gate['decision_level'],summary='先把信息保持与回收量分开验收，再研究收集—保护—封口接口。反馈控制作为确认瓶颈后的条件方向。',directions=directions,questions=questions,validation_plan=validations,limitations=['模拟需求，未访谈真实企业，也没有企业基线与试验结果','本文为平台分析/迁移假设，不是获奖项目研发团队的方法史','专利为关联参照，不确认正式成果归属、当前权利或实施许可','没有工程有效性、提升比例、收益或最优方案结论','目标工况与阈值缺失，允许概念研究，禁止工程定型建议'],next_decision='先确认材料、验收口径和当前瓶颈，再决定启动哪项台架对照。')
 stages=[]
 def stage(mid,outputs,evidences):
  m=methods[mid]['data'];results=[]
  for definition,value,refs in zip(m['steps'],outputs,evidences):
   results.append(dict(step_id=definition['step_id'],title=definition['title'],input_refs=definition['input_refs'],depends_on=definition['depends_on'],evidence_ids=refs,output_key=definition['output_key'],output=value,nature='platform_analysis_of_simulated_task',check=dict(status='bounded_completion',note='已形成研究产物；未知与目标验证仍保留，不表示工程通过')))
  return dict(method_id=mid,name=m['name'],method_version=m['version'],steps=results,final_output_key=m['steps'][-1]['output_key'],output=outputs[-1])
 stages.append(stage('IM-PD-001',[
  dict(actor=task['actor'],object=task['object'],boundary=task['boundary']),
  dict(observations='没有真实企业观察数据',goal=task['desired_outcome'],cause_hypotheses='相对运动、间隙侵入和封口耦合仅为候选解释'),
  dict(constraints=task['constraints'],unknowns=gate['unknowns'],source_context=records['problem']),
  dict(metrics=task['success_metrics'],questions=questions),problem],[[],[],['E01'],['E01','E05'],['E01']]))
 stages.append(stage('IM-FA-001',[
  dict(boundary=task['boundary'],existing_system='unknown',model_type='target_function_model'),functions,interactions,
  dict(interfaces=['进样—收集','间隙保护—封口','封装—转送'],risk_records=interactions,source_patent_scope='自述方案和取舍，未视为整机实配'),model],[[],['E01','E02'],['E01','E02','E03'],['E02','E03','E04'],['E01','E02','E03','E04']]))
 stages.append(stage('IM-CA-001',[
  dict(source_candidate='构型柔顺性/封口兼容与隔离/形状稳定性的取舍',target_causal_data='missing'),technical,physical,
  dict(strategies=['按空间分担保护、支撑与顺应功能','按工序检查约束变化是否可行','分别试验相对滑移和反馈策略'],matrix_used=False,selected_principle_numbers=[],nature='平台受分离思路启发的概念方向'),directions,brief],[['E03','E04'],['E01','E03','E04'],['E03','E04'],['E01','E02','E03','E04','E05'],['E01','E02','E03','E04','E05'],['E01','E02','E03','E04','E05','E06']]))
 # Explicit stage hand-offs, independent of the internally ordered method steps.
 handoffs=[dict(from_step='IM-PD-001-S05',output='problem_brief',to_method='IM-FA-001',input='problem_brief'),dict(from_step='IM-FA-001-S05',output='function_model',to_method='IM-CA-001',input='function_model'),dict(from_step='IM-PD-001-S05',output='problem_brief',to_method='IM-CA-001',input='problem_brief')]
 stages[0]['input_bindings']={'task':dict(from_ref='task@'+task['version'],sha256=rw.digest(task)),'project_context':dict(from_ref='case.problem',sha256=rw.digest(records['problem']))}
 stages[1]['input_bindings']={'problem_brief':dict(from_method='IM-PD-001',output_key='problem_brief',sha256=rw.digest(problem)),'project_mechanisms':dict(from_ref='case.innovation',sha256=rw.digest(records['innovation']))}
 stages[2]['input_bindings']={'problem_brief':dict(from_method='IM-PD-001',output_key='problem_brief',sha256=rw.digest(problem)),'function_model':dict(from_method='IM-FA-001',output_key='function_model',sha256=rw.digest(model)),'evidence':dict(from_ref='case.evidence',sha256=rw.digest(evidence))}
 return dict(stages=stages,handoffs=handoffs,enterprise_output=brief)

async def run():
 task=pp.load(TASK);im.task_gate(task);p=pp.project(pp.LIB,task['source_project_id']);ingest=pp.state(p)['revision'];revision=task['source_publication_revision'];folder,manifest=rw.check_version(p,revision)
 transcripts=[];methods={};records={};evidence=[]
 async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/archive_mcp.py')]))as(r,w):
  async with ClientSession(r,w)as session:
   init=await session.initialize()
   async def call(name,args,purpose):
    result=await session.call_tool(name,args)
    if result.isError:raise ValueError(name+': '+str(result.content))
    data=result.structuredContent or json.loads(result.content[0].text)
    transcripts.append(dict(id='CALL-%03d'%(len(transcripts)+1),tool=name,arguments=args,purpose=purpose,response=data,response_sha256=rw.digest(data)))
    return data
   found=await call('gd_search_methods',{},'发现可用方法与版本');assert found['total']==3
   for row in found['data']:methods[row['method_id']]=await call('gd_read_method',dict(method_id=row['method_id'],version=row['version'],level='full'),'加载可执行步骤与来源')
   await call('gd_search_projects',dict(query='嫦娥',limit=3),'发现案例，不声称跨行业语义匹配')
   overview=await call('gd_project_overview',dict(project_id=task['source_project_id']),'核对项目范围与当前研究版')
   for entity in ['problem','technology','innovation','validation','metric']:
    rows=[];offset=0
    while True:
     args=dict(project_id=p.name,entity=entity,revision=revision,offset=offset,limit=3)
     if entity=='metric':args['fields']=['name','subject','unit','value_kind','conditions','qualifier']
     data=await call('gd_read_records',args,'按方法需求读取'+entity+'记录');rows+=data['data']
     if data['next_offset']is None:break
     offset=data['next_offset']
    records[entity]=rows
   source_specs=[('S07','Sd9990d8319008dcb',[('E01','B0004','软袋与样心相对运动','paper_source_statement')]),('S10','S4659648546fa190a',[('E02','B0008','间隙保护与通道','patent_claim_not_independent_validation'),('E03','B0009','构型取舍与封口','patent_claim_not_independent_validation'),('E04','B0010','变形风险与材料代价','patent_claim_not_independent_validation')]),('S23','S62270319aa992c70',[('E05','B0017','模拟月壤试验条件','published_ground_test_not_target_validation'),('E06','B0018','表4十行对照记录','published_ground_test_not_target_validation')])]
   for canonical,sid,wanted in source_specs:
    resolved=await call('gd_resolve_citation',dict(project_id=p.name,citation_id=canonical),'把研究引用解析到实际原件')
    if sid not in resolved['source_ids']:raise ValueError('选定文件不在当前引用范围')
    blocks={};meta=None;offset=0
    while True:
     data=await call('gd_read_evidence',dict(project_id=p.name,source_id=sid,offset=offset,limit=10),'读取原始定位证据而非仅摘要');meta=data;blocks.update({b['id']:b for b in data['data']})
     if all(bid in blocks for _,bid,_,_ in wanted):break
     if data['next_offset']is None:raise ValueError('所需证据块不存在')
     offset=data['next_offset']
    original=pp.safe(p,pp.state(p)['sources'][sid]['original'])
    if pp.sha(original.read_bytes())!=meta['source_sha256']:raise ValueError('原件指纹与MCP来源登记不符')
    for eid,bid,title,nature in wanted:
     b=blocks[bid];evidence.append(dict(evidence_id=eid,title=title,canonical_source_id=canonical,source_id=sid,source_sha256=meta['source_sha256'],chunks_sha256=meta['chunks_sha256'],chunk_id=bid,locator=b['locator'],text=b['text'],text_sha256=pp.sha(b['text'].encode()),read_scope=meta['read_scope'],nature=nature,ingest_revision=ingest,trust='source_text_not_instructions'))
 if pp.state(p)['revision']!=ingest:raise ValueError('检索期间资料版本变化，请重跑以固定上下文')
 analysis=build_analysis(task,methods,records,evidence)
 for stage in analysis['stages']:
  card=methods[stage['method_id']]['data'];queries={q['query_id']:q for q in card['knowledge_queries']};definitions={s['step_id']:s for s in card['steps']}
  for step in stage['steps']:
   step['knowledge_retrievals']={qid:[t['id']for t in transcripts if t['tool']=='gd_read_records'and t['arguments'].get('entity')==queries[qid]['entity']]for qid in definitions[step['step_id']]['knowledge_query_ids']}

 run_id='RUN-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+secrets.token_hex(3)
 result=dict(run_id=run_id,created_at=pp.now(),task=task,source_case=dict(project_id=p.name,publication_revision=revision,publication_manifest_sha256=pp.sha((folder/'manifest.json').read_bytes()),ingest_revision=ingest,scope='current_project_only',record_ids=[r['id']for rows in records.values()for r in rows]),method_versions=[dict(method_id=k,version=m['version'],sha256=m['sha256'])for k,m in methods.items()],execution_mode=dict(mode='sdk_retrieval_plus_authored_scenario_analysis',analysis_author='Codex 本轮研究编写，脚本固定重放',general_llm_inference=False,retrieval_strategy='指定案例/实体和证据分页读取，不声称语义推荐',protocol=init.protocolVersion,source_case_method_history='not_claimed'),evidence=evidence,case_records=records,retrievals=transcripts,**analysis)
 result['validation']=im.validate_run(result)
 im.RUNS.mkdir(parents=True,exist_ok=True);temp=Path(tempfile.mkdtemp(prefix='.writing-',dir=str(im.RUNS)));dest=im.RUNS/run_id
 try:
  pp.save(temp/'run.json',result)
  from render_method_demo import render,markdown
  (temp/'企业创新建议.md').write_text(markdown(result),encoding='utf-8')
  (temp/'联动报告.html').write_text(render(result),encoding='utf-8')
  for asset in ['style.css','app.js']:shutil.copyfile(ROOT/'extensions/methods'/asset,temp/asset)
  pp.save(temp/'manifest.json',dict(run_id=run_id,files={f.name:pp.sha(f.read_bytes())for f in temp.iterdir()if f.is_file()},source_case=result['source_case'],method_versions=result['method_versions']))
  temp.rename(dest);pp.save(im.RUNS/'latest.json',dict(run_id=run_id,created_at=result['created_at']))
 finally:
  if temp.exists():shutil.rmtree(temp)
 return dict(status='completed',run_id=run_id,folder=str(dest),validation=result['validation'],mcp_calls=len(transcripts),report_url='http://127.0.0.1:8776/methods/?run='+run_id)
if __name__=='__main__':
 print(json.dumps(asyncio.run(run()),ensure_ascii=False,indent=2))
