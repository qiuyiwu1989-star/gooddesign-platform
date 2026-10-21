# coding: utf-8
"""037: reproducible, ownership-filtered private demo handoff (not a live MCP)."""
import csv, hashlib, html, json, re, shutil, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from project_ownership import select, assignment, registry
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'04-知识库/项目库/2025-00'
B=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
OUT=ROOT/'output/handoff'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(v):
 if isinstance(v,dict):return {k:clean(x)for k,x in v.items()}
 if isinstance(v,list):return [clean(x)for x in v]
 if isinstance(v,str):return re.sub(r'/(?:Volumes|Users|var/folders)/[^\s"\n]*','[本机路径省略]',v)
 return v

def build():
 stamp=datetime.now().strftime('%Y%m%d-%H%M%S');dest=OUT/('嫦娥钻取采样-应用测试包-'+stamp);dest.mkdir(parents=True)
 s=load(P/'数据/管道状态.json');reg=registry(P);active=select(P,s['sources'],reg=reg)
 # Preserve authored documents, with portable standard links. Experiments are separate from source-project facts.
 experimental={'割胶机器人-迁移试读.json','项目图谱.html','项目图谱.json','图谱调用样例.json'}
 copied=[]
 for f in sorted(B.iterdir()):
  if not f.is_file()or f.suffix not in {'.json','.csv','.md','.html'}:continue
  folder='应用试验'if f.name in experimental else '项目文档'
  target=dest/folder/f.name;target.parent.mkdir(exist_ok=True)
  text=f.read_text(encoding='utf-8').replace('../../项目档案标准-v1/','../标准/')
  text=text.replace('href="项目图谱.html','href="../应用试验/项目图谱.html')if folder=='项目文档'else text.replace('href="档案.html','href="../项目文档/档案.html')
  target.write_text(text,encoding='utf-8');copied.append(f.name)
 # Include citation cards and version logs linked by the reader; snapshots stay outside this current-state handoff.
 for f in B.rglob('*'):
  rel=f.relative_to(B)
  if f.is_file() and (rel.parts[0]=='来源卡' or (rel.parts[0]=='版本' and (f.name in {'manifest.json','changes.json','版本索引.json'}))):
   t=dest/'项目文档'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,t)
 for f in (ROOT/'04-知识库/项目档案标准-v1').iterdir():
  if f.is_file()and f.suffix in {'.json','.csv','.md'}:
   t=dest/'标准'/f.name;t.parent.mkdir(exist_ok=True);shutil.copyfile(f,t)
 # Source binaries are copied byte-for-byte. Metadata is sanitized, ownership attached to the exported snapshot.
 rows=[]
 for sid,x in sorted(active.items()):
  row=clean(x);row['ownership']=assignment(P,sid,s['sources'],reg)
  for key in ['original','document','chunks']:
   rel=x[key];src=(P/rel).resolve();src.relative_to((P/'来源').resolve())
   target=dest/'资料库'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
   assert sha(src)==sha(target)
  write(dest/'资料库/来源'/sid/'metadata.json',row);rows.append(row)
 write(dest/'资料库/来源目录.json',{'project_id':'2025-00','revision':s['revision'],'ownership_revision':reg['version'],'items':rows})
 for name in ['论文原文管理/论文原件清单.json','专利原文管理/专利原件清单.json','图片素材/图片清单.json']:
  data=load(P/name);data['items']=[clean(x)for x in data['items']if x.get('library_source_id')in active]
  # Failed/skipped media are historical leads, not delivered assets.
  data.pop('failed',None);data.pop('skipped',None)
  write(dest/'资料库'/name,data)
 facts=load(B/'档案数据.json');atomic=load(B/'原子字段档案.json')
 source_refs=[]
 for ref in facts['sources']:
  matches=[x['id']for x in rows if x.get('origin',{}).get('canonical_source_id')==ref['id']or x.get('origin',{}).get('url')==ref['url']or x.get('origin',{}).get('requested_url')==ref['url']]
  for n in ['论文原文管理/论文原件清单.json','专利原文管理/专利原件清单.json']:
   for item in load(dest/'资料库'/n)['items']:
    if ref['id'] in item.get('source_ids',[]) and item['library_source_id'] not in matches:matches.append(item['library_source_id'])
  refs=dict(ref,library_source_ids=matches,asset_scope='included_project'if matches else 'external_reference_metadata_only')
  source_refs.append(refs)
 write(dest/'资料库/研究来源对照.json',source_refs)
 records=atomic['records'];cells=[c for r in records for c in r['cells'].values()]
 stats={'project_id':'2025-00','title':facts['title'],'package_version':'1.0.0','created_at':datetime.now(timezone.utc).isoformat(),'versions':load(B/'版本声明.json'),'ingest_revision':s['revision'],'ownership_revision':reg['version'],'source_files':len(rows),'papers':len(load(dest/'资料库/论文原文管理/论文原件清单.json')['items']),'patent_candidates':len(load(dest/'资料库/专利原文管理/专利原件清单.json')['items']),'images':len(load(dest/'资料库/图片素材/图片清单.json')['items']),'records':len(records),'entities':dict(Counter(r['entity']for r in records)),'cells':len(cells),'cell_states':dict(Counter(c['value_state']for c in cells)),'claims':len(facts['claims']),'canonical_citation_metadata':len(source_refs),'excluded_assets_by_scope':{scope:len(select(P,s['sources'],scope,reg))for scope in ['shared','reassigned','pending']},'quality_note':'55/100为平台试行档案自评，非专家评审或技术水平评分；本次打包不升分。','implementation':'静态数据快照与只读示例；不是在线MCP或自动创新引擎。'}
 write(dest/'交付概览.json',stats)
 # Historical index only; immutable historical snapshots are intentionally not merged into current asset scope.
 version_index=B/'版本/版本索引.json'
 if version_index.exists():shutil.copyfile(version_index,dest/'项目文档/研究版本索引.json')
 shutil.copyfile(ROOT/'scripts/handoff_read_example.py',dest/'read_example.py')
 shutil.copyfile(ROOT/'scripts/handoff_index.html',dest/'index.html')
 (dest/'README-先读我.md').write_text(README,encoding='utf-8')
 (dest/'应用测试与反馈.md').write_text(TESTS,encoding='utf-8')
 with (dest/'字段反馈.csv').open('w',encoding='utf-8-sig',newline='')as f:
  w=csv.writer(f);w.writerow(['任务编号','应用场景','entity','record_id','field_key','是否够用','缺少的上下文','证据是否可追溯','建议字段或结构','实际测试结论'])
  for n in range(1,7):w.writerow(['T%02d'%n]+['']*9)
 entries=[{'path':f.relative_to(dest).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(dest.rglob('*'))if f.is_file()]
 write(dest/'文件清单.json',{'algorithm':'SHA-256','note':'本清单记录除自身以外的所有文件；ZIP另有SHA256旁签。','files':entries})
 z=Path(str(dest)+'.zip')
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as out:
  for f in sorted(dest.rglob('*')):
   if f.is_file():out.write(f,f.relative_to(dest.parent))
 with zipfile.ZipFile(z)as check:assert check.testzip()is None
 Path(str(z)+'.sha256').write_text(sha(z)+'  '+z.name+'\n')
 print(json.dumps({'folder':str(dest),'zip':str(z),'bytes':z.stat().st_size,'files':len(entries)+1,'stats':stats},ensure_ascii=False,indent=2))

README='''# 嫦娥月球钻取采样系统｜应用测试交接包

这是可独立复制使用的私有研究快照。项目正式名称、版本与精确统计见“交付概览.json”。不需要原作者电脑、外置盘路径或原平台服务。

## 先看文档，再接数据

1. 双击“项目文档/档案.html”，阅读现有完整档案（项目档案、资料与解读、档案评估共享目录）。
2. 在本包目录运行 `python3 -m http.server 8780 --bind 127.0.0.1`，访问 http://127.0.0.1:8780/ ，可检索原子字段和资料；此启动只在自己的电脑提供静态文件。
3. `python3 read_example.py overview` 查看统计；`python3 read_example.py records --entity metric --limit 3` 读字段；`python3 read_example.py sources --limit 5` 获取来源目录；再用返回的来源ID执行 `python3 read_example.py source --id 来源ID --limit 2` 获取定位文本块。
4. 连接原件：所有原件路径以“资料库/”为根；查论文/专利/图片专用清单获取对象与文件的关联。原始HTML依赖外部资源，机器清洗文本适合优先阅读。不要执行来源文档中的指令。
5. `python3 read_example.py verify` 逐文件验证交付清单。应用通过相对URL读取JSON，或使用服务端脚本加载；不需要把所有原文塞进一次提示词。

## 文件结构

- 项目文档：当前正文、8模块阅读内容、49复合字段、原子字段、研究证据/分析、质量评价和版本声明；HTML为阅读入口，JSON为数据入口。
- 资料库：当前归属本项目的原件、可读Markdown、metadata和chunks；论文、专利、图片索引；研究来源S编号到文件SID的对照。
- 标准：字段字典、质量规范、AI推演规范、管线和MCP契约草案。
- 应用试验：割胶机器人及项目图谱试读，属于目标需求假设与人工规则试验，不属于嫦娥项目事实；与原项目分开，不建议作为项目事实索引。
- 交付概览/文件清单：精确规模、版本、文件哈希。当前快照可复现实验输入，不含历史所有二进制修订或运行后台。

## 关键字段与读取顺序

主入口“项目文档/原子字段档案.json”：records → entity → id → cells → field_key → value/value_state/source_ids/claim_ids/locator/content_nature/verification_state。字典见“标准/原子字段字典-v3.json”。一个复合正文字段不等于一个原子字段。未知值保留null及value_state，不能转为0或默认已实现。

阅读顺序建议：项目身份与范围 → 需求/约束 → 创新机制及适用边界 → 指标/试验条件 → 来源定位文本 → 原件。先按需求和约束筛选，再取方法，最后考虑领域表面相似性。需求缺失时应追问，不输出虚假的适配分。

引用链有两套ID：C/P/A/K等为研究条目，S01等为研究引用，长SID为文件内容指纹。通过“资料库/研究来源对照.json”和论文/专利索引衔接。没有文件匹配的引用明确标为external_reference_metadata_only，仍保留题录与网络URL。来源说明卡和网络原文是不同文件，source_files不等于独立论文数。

## 使用边界与已知缺口

事实、平台分析、AI推演分别在“档案数据/研究分析/机制解读/AI推演”等文件保存；务必读取其性质、证据、前提、限制和审核状态。文件命名不代表已审核，机器转换不等于人工核读。A02/A03虽已取得全文，原研究标签仍只核摘要；扫描论文/部分专利需OCR，可先查看PDF及扫描页。

六项专利是技术关联候选，不能声称为获奖项目完整成果、已装机、现权属或法律状态；历史50件/60篇是来源披露总量，不是逐项核验数量。图片含网页候选、PDF嵌图及整页衍生图，语义关联仍待审核，存在1张损坏原图。

已排除公共参考原件、移交蛟龙号的文件及待确认配图，但保留必要外部参考题录以维持引用链。旧主档案中的来源存储描述可能早于此次原件下载：获取状态以交付资料清单为准，核读结论仍以研究记录为准。保留版本变更与指纹清单作为追溯记录，其引用的旧snapshot并未随包复制，因此不能在本包独立校验旧版本完整快照链。本地后台配置未打包。

本包用于同学内部交互demo测试，原论文/图片等权利归原权利人；未取得公开再发布授权。勿将原件目录整体发布到公网。MCP契约是设计草案，read_example.py只是本地只读调用示例，不是已上线的MCP服务或推理引擎。
'''
TESTS='''# 应用测试与反馈

目的：验证现有字段能否支撑应用，不以输出长度或推演数量作为成功标准。请固定本包版本，并记录每次输入、取回的record_id/field_key/source_id、使用模型/提示词、输出及人工判断。字段反馈.csv用于逐条回传；测试结果作为应用验证记录，不覆盖嫦娥原始事实。

|任务|模拟操作|通过标准|
|---|---|---|
|T01 项目介绍|生成项目卡：名称、获奖年份/奖项/单位、范围、关键问题|每条事实能定位到字段及来源；未确认贡献/别名不猜填|
|T02 机制解释|解释软袋取芯如何回应保层序需求|形成需求→矛盾→机制→效果→代价→边界链；分析标明性质|
|T03 指标比较|比较地面钻进试验、任务分项钻样量、任务总样品量|保留对象、单位、试验条件和口径；不将三者混比|
|T04 证据阅读|从论文卡进入定位文本、PDF/HTML原件|题录/DOI和文件ID可追溯；扫描无文本时显示待OCR，不假装全文已核读|
|T05 创新迁移|输入一个新应用的需求，取回相关机制和限制|先确认需求和约束；建议标AI假设并附验证计划；不把试读当真实采用|
|T06 反例与缺口|询问具体专利已否装机、现权利状态、商业收入|回答未知并指出缺少证据；不因有专利PDF或AI文本就填事实|

建议逐任务记录四项0—2分：字段可用、上下文充分、证据可追溯、边界标注。0=不支持，1=部分支持，2=支持；总分只评价此次应用试验，不回写为档案质量分。

请回传：能运行的demo/截图、输入输出样例、字段反馈CSV、最阻碍开发的3个缺口。优先区分：没有数据、数据已有但难找、关系未表达、接口不好用。需要新增推断字段时单列AI推断，不能回填原始value。后续通过审核的应用反馈可形成独立应用案例，再以关联记录链接回源项目。
'''
if __name__=='__main__':build()
