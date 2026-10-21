# coding: utf-8
"""038: evidence candidates, review, immutable publications, and local OCR.
All mutation entry points take the existing library lock. No source text is executed.
"""
import argparse, copy, hashlib, json, math, re, shutil, subprocess, tempfile
from collections import Counter
from pathlib import Path
import project_pipeline as pp
import project_ownership as own
ROOT=pp.ROOT
SCHEMA=ROOT/'04-知识库/项目档案标准-v1/原子字段字典-v3.json'
BENCH=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样/原子字段档案.json'
POLICY='evidence-workflow-1.0'
RESTRICTED={'current_holder','legal_status','project_relation','reading_scope','status_checked_at','license_conditions'}

def digest(v):return pp.sha(json.dumps(v,ensure_ascii=False,sort_keys=True,allow_nan=False).encode())
def schema():return {e['key']:{f['name']:f for f in e['fields']}for e in pp.load(SCHEMA)['entities']}
def workspace(p):return p/'研究工作区'
def current(p):
 f=workspace(p)/'工作状态.json'
 if f.exists():
  w=pp.load(f)
  # Recover a completed immutable publication if the process stopped before advancing the queue pointer.
  while (workspace(p)/'版本'/('research-%06d'%(w['revision']+1))).exists():
   folder,_=check_version(p,'research-%06d'%(w['revision']+1));d=pp.load(folder/'档案.json');w['revision']+=1
   for c in w['candidates']:
    if c['id']in d.get('applied_candidate_ids',[]):c.update(status='published',published_revision=d['publication_revision'])
  return w
 baseline=pp.load(BENCH)if p.name=='2025-00'else dict(version='atomic-case-3.0',project_id=p.name,records=[])
 return dict(policy=POLICY,revision=0,base_sha256=pp.sha(BENCH.read_bytes())if p.name=='2025-00'else None,baseline=baseline,candidates=[],events=[])
def save(p,w):pp.save(workspace(p)/'工作状态.json',w)
def event(w,action,actor,**args):
 if not isinstance(actor,str)or not actor.strip()or len(actor)>200:raise ValueError('请填写操作者（1–200字）')
 w['events'].append(dict(at=pp.now(),action=action,actor=actor,**args))
def source(p,sid):
 s=pp.state(p);x=own.select(p,s['sources']).get(sid)
 if not x:raise ValueError('来源不在当前项目范围内')
 return x

def check_version(p,revision):
 if not re.fullmatch(r'research-\d{6}',revision):raise ValueError('研究版本格式无效')
 folder=workspace(p)/'版本'/revision;m=pp.load(folder/'manifest.json')
 if m['revision']!=revision:raise ValueError('版本身份不符')
 n=int(revision.split('-')[1])
 if n>1:
  prev=workspace(p)/'版本'/('research-%06d'%(n-1))/'manifest.json'
  if not prev.exists()or pp.sha(prev.read_bytes())!=m['previous_manifest_sha256']:raise ValueError('版本前序指纹链不符')
 for name,expected in m['files'].items():
  f=pp.safe(folder,name)
  if pp.sha(f.read_bytes())!=expected:raise ValueError('已发布版本校验失败，请检查:'+name)
 return folder,m

def dataset(p,w=None,revision=None):
 w=w or current(p)
 if revision or w['revision']:
  folder,_=check_version(p,revision or 'research-%06d'%w['revision']);return pp.load(folder/'档案.json')
 return copy.deepcopy(w['baseline'])

def cell(data,rid,field):
 r=next((r for r in data['records']if r['id']==rid),None)
 return r.get('cells',{}).get(field)if r else None

def validate_type(value,typ):
 if value is None:raise ValueError('候选值不能为空；未知值请保留待补而非猜填')
 ok=True
 if typ in ['number','integer']:ok=isinstance(value,(int,float))and not isinstance(value,bool)and math.isfinite(value)and(typ!='integer'or isinstance(value,int))
 elif typ.endswith('_list'):ok=isinstance(value,list)and bool(value)and all(isinstance(x,dict)if typ=='object_list'else isinstance(x,str)for x in value)
 elif typ=='object':ok=isinstance(value,dict)
 elif typ=='boolean':ok=isinstance(value,bool)
 else:ok=isinstance(value,str)and 0<len(value)<=12000
 if not ok:raise ValueError('字段类型不符：'+typ)
 if typ=='date'and not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value):raise ValueError('日期须YYYY-MM-DD')
 if typ=='url'and not re.match(r'https?://',value):raise ValueError('URL须http(s)')

def evidence(p,c):
 x=source(p,c['source_id'])
 if pp.sha(pp.safe(p,x['original']).read_bytes())!=x['sha256']:raise ValueError('原件指纹不符，请先检查资料完整性')
 blocks=pp.load(pp.safe(p,x['chunks']))
 b=next((b for b in blocks if b['id']==c['chunk_id']),None)
 if not b or not c['quote']or c['quote']not in b['text']:raise ValueError('原文摘录必须存在于指定证据块，不能改写原文')
 if c.get('chunks_sha256')and c['chunks_sha256']!=pp.sha(pp.safe(p,x['chunks']).read_bytes()):raise ValueError('来源文本已更新，请重新提炼和审核')
 if c.get('quote_sha256')and c['quote_sha256']!=pp.sha(c['quote'].encode()):raise ValueError('证据摘录指纹不符')
 return x,b

def add_candidate(p,w,args,actor):
 fields=schema();entity=args['entity'];field=args['field'];rid=args['record_id']
 if entity not in fields or field not in fields[entity]:raise ValueError('字段不在字典中')
 if not re.fullmatch(r'[A-Za-z0-9_-]{1,90}',rid):raise ValueError('记录ID无效')
 value=args.get('value');operation=args.get('operation','set')
 if operation not in ['set','clear']:raise ValueError('候选操作无效')
 if operation=='set':validate_type(value,fields[entity][field]['type'])
 elif value is not None or not args.get('limitations'):raise ValueError('清空字段须传null并说明撤回原因')
 nature=args.get('content_nature','source_statement')
 if nature not in ['source_statement','ai_interpretation','ai_hypothesis']:raise ValueError('内容性质无效')
 if operation=='clear'and nature!='source_statement':raise ValueError('当前撤回操作仅用于事实字段；AI层请提交新的有边界解读')
 if field in RESTRICTED and not args.get('conditions'):raise ValueError('归属/核读/权利状态等敏感判断必须填写适用条件与证据边界')
 x,b=evidence(p,args)
 if nature=='source_statement'and operation=='set':
  values=value if isinstance(value,list)else [value]
  norm=lambda v:re.sub(r'\s+','',str(v)).lower()
  def supported(v):
   quote=norm(args['quote'])
   if isinstance(v,(int,float))and not isinstance(v,bool):return bool(re.search(r'(?<![\d.])'+re.escape(str(v))+r'(?![\d.])',quote))
   if fields[entity][field]['type']=='date':
    pp.datetime.date.fromisoformat(v)
    return bool(re.search(r'[-./年月]'.join(re.escape(part)for part in v.split('-'))+'日?',quote))or v in quote
   return norm(v)in quote
  if not all(supported(v)for v in values):raise ValueError('事实值须能在摘录中直接找到；归纳改写请标AI解读')
  if entity=='metric'and field in ['value','baseline_value']and not all(args.get(k)for k in ['object','unit','conditions']):raise ValueError('指标数值须填写对象、单位和工况/口径')
 elif nature!='source_statement'and(not args.get('conditions')or not args.get('limitations')):raise ValueError('AI解读/假设必须填写适用前提与限制')
 if len(args['quote'])>4000:raise ValueError('摘录过长，请缩小证据范围')
 data=dataset(p,w);existing=next((r for r in data['records']if r['id']==rid),None)
 if existing and existing['entity']!=entity:raise ValueError('记录实体类型冲突')
 c=dict(operation=operation,entity=entity,field=field,record_id=rid,title=str(args.get('title')or(existing or {}).get('title')or rid),value=value,content_nature=nature,source_id=x['id'],source_sha256=x['sha256'],chunks_path=x['chunks'],chunks_sha256=pp.sha(pp.safe(p,x['chunks']).read_bytes()),chunk_id=b['id'],locator=b['locator'],quote=args['quote'],quote_sha256=pp.sha(args['quote'].encode()),source_read_scope=x['read_scope'],ingest_revision=pp.state(p)['revision'],ownership_revision=own.registry(p).get('version',0),object=str(args.get('object','')),unit=str(args.get('unit','')),conditions=str(args.get('conditions','')),limitations=str(args.get('limitations','')),extraction_method=str(args.get('extraction_method','manual_or_agent_submission')),base_cell_sha256=digest(cell(data,rid,field)))
 identity=digest({k:v for k,v in c.items()if k not in ['ingest_revision','ownership_revision']})
 old=next((x for x in w['candidates']if x['fingerprint']==identity),None)
 if old:return old
 c.update(id='CAND-'+identity[:16],fingerprint=identity,status='pending',created_at=pp.now(),created_by=actor)
 event(w,'candidate_created',actor,candidate_id=c['id']);w['candidates'].append(c);return c

def propose(lib,pid,args,actor):
 with pp.lock(lib):
  p=pp.project(lib,pid);w=current(p);c=add_candidate(p,w,args,actor);save(p,w);return c

def extract(lib,pid,sid,actor):
 """Conservative rules: bibliographic identifiers and verbatim abstract sections only."""
 with pp.lock(lib):
  p=pp.project(lib,pid);x=source(p,sid);blocks=pp.load(pp.safe(p,x['chunks']));w=current(p);made=[]
  target=None
  for path,key,entity in [('论文原文管理/论文原件清单.json','paper_id','paper'),('专利原文管理/专利原件清单.json','patent_id','patent')]:
   if (p/path).exists():
    item=next((i for i in pp.load(p/path)['items']if i['library_source_id']==sid),None)
    if item:target=(item[key],entity,item);break
  # Unindexed sources still yield DOI/CN identifiers, but are not automatically linked to an existing project outcome.
  guessed='patent'if re.search(r'CN\s*\d{8,10}\s*[AB]',' '.join(b['text']for b in blocks[:2]))else'paper'
  rid,entity,item=target if target else ('DOC-'+sid,guessed,{})
  found=set()
  def add(field,value,b,quote):
   key=(field,digest(value))
   if key in found:return
   found.add(key)
   made.append(add_candidate(p,w,dict(entity=entity,record_id=rid,title=item.get('title',x['title']),field=field,value=value,source_id=sid,chunk_id=b['id'],quote=quote,extraction_method='conservative_rules_v1'),actor))
  for b in blocks[:4]:
   text=b['text']
   if entity=='paper':
    for m in re.finditer(r'(?:DOI|doi)\s*[:：]\s*(10\.\d{4,9}/[A-Za-z0-9._;/()\-]+)',text):add('doi',m.group(1).rstrip('.'),b,m.group(0))
    if target or 'DOI' in text or 'doi' in text:
     m=re.search(r'摘\s*要\s*[:：]([\s\S]+?)(?:关键词|关\s*键\s*词)',text)
     if m:
      abstract=m.group(1).strip();start=abstract.find('针对');end=abstract.find('的问题')
      if 0<=start<end:add('research_question',abstract[start+2:end+3],b,abstract[start:end+3])
      end=abstract.find('结果表明')
      if end>0:
       method=abstract[:end].strip();start=method.find('采用')
       if start>=0:add('method',method[start:],b,method[start:])
       add('findings',abstract[end:].strip(),b,abstract[end:].strip())
   if entity=='patent':
    for m in re.finditer(r'CN\s*\d{8,10}\s*[AB]',text):
     value=re.sub(r'\s+','',m.group());add('grant_number'if value.endswith('B')else 'publication_number',value,b,m.group())
    m=re.search(r'\(73\)\s*专利权人\s*([^\n]+)',text)
    if m:add('publication_holder',m.group(1).strip(),b,m.group())
    m=re.search(r'\(72\)\s*发明人\s*([\s\S]+?)(?=\(74\)|\(51\))',text)
    if m:
     names=re.split(r'[\s、,，]+',m.group(1).strip())
     if names:add('inventors',names,b,m.group())

  save(p,w)
  return dict(status='completed',source_id=sid,candidates=[c['id']for c in made],coverage='DOI/CN标识与完整摘要内的问题、方法、结果；其余字段由人工/Agent提交证据候选',pending_review=True)

def review(lib,pid,cid,decision,actor,reason):
 if decision not in ['approved','rejected','needs_more']:raise ValueError('审核决定无效')
 if not isinstance(reason,str)or not reason.strip():raise ValueError('审核必须写明理由')
 with pp.lock(lib):
  p=pp.project(lib,pid);w=current(p);c=next((x for x in w['candidates']if x['id']==cid),None)
  if not c:raise ValueError('候选不存在')
  if c['status']=='published':raise ValueError('已发布内容不能回改，请建立新候选形成新版本')
  if decision=='approved':evidence(p,c)
  c.update(status=decision,reviewer=actor,review_reason=reason,reviewed_at=pp.now());event(w,'review',actor,candidate_id=cid,decision=decision,reason=reason);save(p,w);return c

def render_docs(data,changes,revision):
 groups={e['key']:e for e in pp.load(SCHEMA)['entities']};fact=['# 项目档案 · '+revision,'','以下为研究整理版。原项目专家审核及平台55自评保持原状态。AI解读不计事实字段覆盖。',''];analysis=['# 资料与解读 · '+revision,''];known=total=0
 for record in data['records']:
  fact.extend(['## '+record['title']+' · '+record['id'],''])
  for k,c in record['cells'].items():
   total+=1;value=c.get('value');is_known=c.get('value_state')=='known'and value is not None;known+=int(is_known)
   field=groups.get(record['entity'],{});label=next((f['label']for f in field.get('fields',[])if f['name']==k),k)
   fact.append('- **'+label+'**（'+c.get('content_nature','未标注性质')+'）：'+(json.dumps(value,ensure_ascii=False)if is_known else '—（'+c.get('value_state','not_researched')+'）'))
   if c.get('evidence'):fact.append('  - 依据：'+c['evidence']['source_id']+' / '+c['evidence']['chunk_id']+' · '+c['locator'])
  fact.append('')
 for c in data.get('interpretations',[]):analysis.extend(['## '+c['title']+' · '+c['id'],'','性质：'+c['content_nature'],'',json.dumps(c['value'],ensure_ascii=False),'','前提：'+c['conditions'],'','限制：'+c['limitations'],'','依据：'+c['source_id']+' / '+c['chunk_id']+' · '+c['locator'],'','> '+c['quote'].replace('\n','\n> '),''])
 analysis+=['## 本次字段更新的证据','']
 for x in changes:analysis.extend(['### '+x['record_id']+'.'+x['field'],'','来源：'+x['source_id']+' / '+x['chunk_id'],'','> '+x['quote'].replace('\n','\n> '),''])
 assessment=['# 档案评估 · '+revision,'',f'记录：{len(data["records"])}；数据单元：{total}；有值字段（含原档案标注的分析）：{known}（{known/total:.1%}）。'if total else '暂无字段。','','该比例仅为数据填充，不是研究完整度、技术水平或专家审核结论。','',f'本次审核更新：{len(changes)}；AI解读/假设另列，不计事实填充。','','评分：沿用原研究量规，自动发布不升分。专业审核仍待安排。']
 return {'01-项目档案.md':'\n'.join(fact),'02-资料与解读.md':'\n'.join(analysis),'03-档案评估.md':'\n'.join(assessment)}

def publish(lib,pid,actor,reason,expected_candidate_ids=None):
 if not reason or not reason.strip():raise ValueError('请填写发布理由')
 if not isinstance(actor,str)or not actor.strip():raise ValueError('请填写发布操作者')
 with pp.lock(lib):
  p=pp.project(lib,pid);w=current(p);data=dataset(p,w);prior_revision=w['revision'];applied=set(data.get('applied_candidate_ids',[]));batch=[c for c in w['candidates']if c['status']=='approved'and c['id']not in applied]
  if expected_candidate_ids is not None:
   if not isinstance(expected_candidate_ids,list)or any(not isinstance(x,str)for x in expected_candidate_ids)or sorted(expected_candidate_ids)!=sorted(c['id']for c in batch):raise ValueError('待入档内容已变化，请刷新并重新预览')
  if not batch:return dict(status='no_changes',revision='research-%06d'%prior_revision)
  if p.name=='2025-00'and w['base_sha256']!=pp.sha(BENCH.read_bytes()):raise ValueError('人工深研底稿已更新，请先核对基线，不覆盖新研究')
  seen=set();changes=[]
  for c in batch:
   evidence(p,c)
   if c['content_nature']=='source_statement':
    key=(c['record_id'],c['field'])
    if key in seen:raise ValueError('同一字段有多个待发布候选，请只保留一个审核通过值')
    seen.add(key)
    if digest(cell(data,*key))!=c['base_cell_sha256']:raise ValueError('字段自提炼后已变化，请重新提炼审核:'+str(key))
    r=next((r for r in data['records']if r['id']==c['record_id']),None)
    if not r:
     r=dict(id=c['record_id'],project_id=pid,entity=c['entity'],title=c['title'],cells={key:dict(value=None,value_state='not_researched',content_nature='source_statement')for key in schema()[c['entity']]});data['records'].append(r)
    before=copy.deepcopy(r['cells'].get(c['field']));r['cells'][c['field']]=dict(value=c['value'],value_state='not_obtained'if c.get('operation')=='clear'else'known',content_nature='source_statement',source_ids=[c['source_id']],claim_ids=[],locator=c['locator'],verification_state='research_editor_checked_not_expert',visibility='internal_research',valid_as_of=None,evidence={k:c[k]for k in ['source_id','source_sha256','chunk_id','chunks_path','chunks_sha256','quote','quote_sha256','source_read_scope','ingest_revision']},reviewer=c['reviewer'],review_reason=c['review_reason'],object=c['object'],unit=c['unit'],conditions=c['conditions'],limitations=c['limitations'])
   else:
    before=None;data.setdefault('interpretations',[]).append(copy.deepcopy(c))
   changes.append(dict(operation=c.get('operation','set'),candidate_id=c['id'],record_id=c['record_id'],field=c['field'],before=before,after=c['value'],source_id=c['source_id'],chunk_id=c['chunk_id'],quote=c['quote'],content_nature=c['content_nature'],reviewer=c['reviewer']))
  rev='research-%06d'%(prior_revision+1);data.update(publication_revision=rev,published_at=pp.now(),applied_candidate_ids=sorted(applied|{c['id']for c in batch}),quality_score_status='unchanged_from_authored_baseline',expert_reviewed=False)
  parent=None
  if prior_revision:
   oldfolder,_=check_version(p,'research-%06d'%prior_revision);parent=pp.sha((oldfolder/'manifest.json').read_bytes())
  base=workspace(p)/'版本';base.mkdir(parents=True,exist_ok=True);temp=Path(tempfile.mkdtemp(prefix='.publishing-',dir=str(base)));folder=base/rev
  try:
   if folder.exists():raise ValueError('版本目录已存在，禁止覆盖')
   pp.save(temp/'档案.json',data);pp.save(temp/'changes.json',dict(revision=rev,previous_revision='research-%06d'%prior_revision,changes=changes,actor=actor,reason=reason,published_at=data['published_at']))
   for name,text in render_docs(data,changes,rev).items():(temp/name).write_text(text,encoding='utf-8')
   pp.save(temp/'manifest.json',dict(revision=rev,previous_manifest_sha256=parent,baseline_sha256=w['base_sha256'],files={f.name:pp.sha(f.read_bytes())for f in temp.iterdir()if f.is_file()},actor=actor,reason=reason))
   temp.rename(folder)
  finally:
   if temp.exists():shutil.rmtree(temp)
  w['revision']=prior_revision+1
  for c in batch:c.update(status='published',published_revision=rev)
  event(w,'publish',actor,revision=rev,reason=reason,candidate_ids=[c['id']for c in batch]);save(p,w)
  return dict(status='published',revision=rev,changes=len(changes),expert_reviewed=False,quality_score_changed=False)

def register_ocr(p,sid,target,actor):
 pages=pp.load(target/'pages.json');blocks=pp.load(target/'chunks.json')
 s=pp.state(p);sx=s['sources'][sid];sx.update(document=str((target/'可读来源.md').relative_to(p)),chunks=str((target/'chunks.json').relative_to(p)),chunk_count=len(blocks),status='ocr_text_extracted_pending_review',error=None,read_scope='machine_ocr_not_human_read',ocr=dict(engine='apple_vision_v1',path=str((target/'pages.json').relative_to(p)),page_count=len(pages),recognized_at=pp.now(),actor=actor,needs_manual_check=True))
 revision=pp.commit(p,s,'OCR生成可追溯衍生文本，原件与旧清洗结果保留；非人工核读')
 for name in ['论文原文管理/论文原件清单.json','专利原文管理/专利原件清单.json']:
  index=p/name
  if index.exists():
   listing=pp.load(index)
   for item in listing['items']:
    if item['library_source_id']==sid:
     item.setdefault('before_ocr',dict(readable=item.get('readable'),chunks=item.get('chunks'),conversion_status=item.get('conversion_status')))
     item.update(readable=sx['document'],chunks=sx['chunks'],conversion_status=sx['status'],machine_scope='machine_ocr_not_human_read')
   pp.save(index,listing)

 return dict(status='completed',source_id=sid,pages=len(pages),blocks=len(blocks),revision=revision,review_status='pending_human_check')

def ocr(lib,pid,sid,actor):
 # Existing lock prevents source revisions changing between conversion and commit.
 with pp.lock(lib):
  p=pp.project(lib,pid);x=source(p,sid);binary=ROOT/'.runtime/vision-ocr'
  if not binary.exists():raise ValueError('OCR组件未安装，请运行scripts/安装档案管线.command')
  if x.get('ocr')and pp.safe(p,x['ocr']['path']).exists():return dict(status='duplicate',source_id=sid,ocr=x['ocr'])
  import fitz
  original=pp.safe(p,x['original'])
  if pp.sha(original.read_bytes())!=x['sha256']:raise ValueError('原件指纹不符，停止OCR')
  renderdir=p/'衍生/OCR';renderdir.mkdir(parents=True,exist_ok=True);temp=Path(tempfile.mkdtemp(prefix='.ocr-',dir=str(renderdir)));target=renderdir/(sid+'-vision-v1')
  pages=[];blocks=[]
  if target.exists():
   try:
    manifest=pp.load(target/'manifest.json')
    if manifest['original_sha256']!=x['sha256']:raise ValueError('OCR衍生文件身份不符')
    for name,h in manifest['files'].items():
     if pp.sha(pp.safe(target,name).read_bytes())!=h:raise ValueError('OCR衍生文件指纹不符')
    return register_ocr(p,sid,target,actor)
   finally:shutil.rmtree(temp)
  try:
   if original.suffix.lower()=='.pdf':
    with fitz.open(str(original))as doc:
     if len(doc)>200:raise ValueError('单次OCR最多200页，请拆分后处理')
     for i,page in enumerate(doc):
      native=page.get_text().strip()
      if len(native)>30:pages.append(dict(page=i+1,text=native,method='native_pdf',lines=[]));continue
      image=temp/'page.png';page.get_pixmap(matrix=fitz.Matrix(min(2,2400/max(page.rect.width,1),3200/max(page.rect.height,1)),min(2,2400/max(page.rect.width,1),3200/max(page.rect.height,1))),alpha=False).save(str(image));result=subprocess.run([str(binary),str(image)],capture_output=True,text=True,timeout=180,check=True);lines=json.loads(result.stdout)
      pages.append(dict(page=i+1,text='\n'.join(x['text']for x in lines),method='apple_vision_ocr',lines=lines))
   else:
    if original.suffix.lower()not in {'.png','.jpg','.jpeg','.tif','.tiff','.webp','.bmp'}:raise ValueError('OCR只接受PDF或位图')
    result=subprocess.run([str(binary),str(original)],capture_output=True,text=True,timeout=180,check=True);lines=json.loads(result.stdout);pages=[dict(page=1,text='\n'.join(x['text']for x in lines),method='apple_vision_ocr',lines=lines)]
   image=temp/'page.png'
   if image.exists():image.unlink()
   blocks=pp.chunks([('第%d页 · %s（机器识别待核对）'%(v['page'],v['method']),v['text'])for v in pages])
   if not blocks:raise ValueError('OCR未识别到文字，原件保留，请人工核对')
   pp.save(temp/'pages.json',pages);pp.save(temp/'chunks.json',blocks)
   (temp/'可读来源.md').write_text('# OCR清洗来源\n\n机器识别，公式/表格/单位须逐项核对，非人工核读。\n\n'+'\n\n'.join('## '+b['id']+' · '+b['locator']+'\n\n'+b['text']for b in blocks),encoding='utf-8')
   if target.exists():raise ValueError('OCR目录已存在，请检查未完成任务，不覆盖衍生结果')
   pp.save(temp/'manifest.json',dict(original_sha256=x['sha256'],files={f.name:pp.sha(f.read_bytes())for f in temp.iterdir()if f.is_file()}))
   temp.rename(target)
   return register_ocr(p,sid,target,actor)
  finally:
   if temp.exists():shutil.rmtree(temp)

def process(lib,pid,sid,actor):
 """Run the machine half of the pipeline; never auto-approve or publish."""
 p=pp.project(lib,pid);x=source(p,sid);result=dict(source_id=sid,status='completed')
 if x['status']in ['needs_ocr','partial_needs_ocr','partial_text_needs_ocr']:result['ocr']=ocr(lib,pid,sid,actor)
 x=source(p,sid)
 if x.get('origin',{}).get('kind')=='source_reference':return dict(status='completed',source_id=sid,note='来源说明卡保留为线索，不作原文提炼')
 if pp.load(pp.safe(p,x['chunks'])):result['extraction']=extract(lib,pid,sid,actor)
 else:result['note']='原件已保存；图片语义/不支持格式需要人工处理'
 return result

def status(lib,pid):
 p=pp.project(lib,pid);w=current(p);data=dataset(p,w);sources=own.select(p,pp.state(p)['sources']);applied=set(data.get('applied_candidate_ids',[]))
 rows=copy.deepcopy(w['candidates'])
 for c in rows:
  if c['id']in applied:c['status']='published'
 return dict(project_id=pid,revision='research-%06d'%w['revision'],candidates=rows,counts=dict(Counter(c['status']for c in rows)),source_count=len(sources),needs_ocr=[x['id']for x in sources.values()if x['status']in ['needs_ocr','partial_needs_ocr','partial_text_needs_ocr']],ocr_completed=sum(bool(x.get('ocr'))for x in sources.values()),record_count=len(data['records']),events=w['events'][-100:],capabilities=dict(ocr=(ROOT/'.runtime/vision-ocr').exists(),extract='conservative_rules_v1_and_evidence_submission',review=True,publish=True,mcp='stdio_read_only'),schema=pp.load(SCHEMA))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['status','extract','ocr','propose','review','publish']);ap.add_argument('project');ap.add_argument('--source');ap.add_argument('--file',type=Path);ap.add_argument('--candidate');ap.add_argument('--decision',choices=['approved','rejected','needs_more']);ap.add_argument('--actor',default='本地操作员');ap.add_argument('--reason',default='');a=ap.parse_args()
 if a.action=='status':result=status(pp.LIB,a.project)
 elif a.action=='propose':result=propose(pp.LIB,a.project,pp.load(a.file),a.actor)
 elif a.action in ['ocr','extract']:result=globals()[a.action](pp.LIB,a.project,a.source,a.actor)
 elif a.action=='review':result=review(pp.LIB,a.project,a.candidate,a.decision,a.actor,a.reason)
 else:result=publish(pp.LIB,a.project,a.actor,a.reason)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
