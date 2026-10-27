from pathlib import Path
import hashlib,json,urllib.request,re
P=Path(__file__).resolve().parent;Q=P.parent/'MD-004-R17'
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
refs=[(P,'S-NASA-FUNC','https://www.nasa.gov/reference/4-0-system-design-processes/','NASA Systems Engineering Handbook §4.3','§4.3.1.2.1—.3 与 §4.3.1.3；网页选段，未读NASA扩展指南全文'),(P,'S-NASA-IF','https://www.nasa.gov/reference/6-3-interface-management/','NASA Systems Engineering Handbook §6.3','§6.3.1.2.2—.5、§6.3.1.3；网页选段'),(Q,'S-RITCHEY','https://swemorph.com/ma.html','Tom Ritchey, General Morphological Analysis (2002, revised 2013)','GENERAL MORPHOLOGY、CROSS CONSISTENCY ASSESSMENT、CONCLUSIONS；网页正文核读，不声称Zwicky专著或商业软件全文')]
records={P:[],Q:[]}
for dest,sid,url,title,scope in refs:
 raw=dest/'核读原件-不发布'/(sid+'.html')
 status='not_acquired'
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as r:
   data=r.read();raw.write_bytes(data);status='acquired';final=r.url
 except Exception as e:final=None
 records[dest].append({'id':sid,'title':title,'url':url,'selected_read_scope':scope,'date':'2026-10-27','acquisition_status':status,'raw_file':str(raw.relative_to(dest))if raw.exists()else None,'raw_sha256':sha(raw)if raw.exists()else None,'final_url':final,'public_redistribution':'not_included; cite link and original platform analysis only','not_claimed':['full NASA/VDI/ISO conformity','expert certification','customer or engineering validation']})
claimsP=[{'id':'CL-F01','claim':'功能分析以要完成的作用及其输入输出/接口等描述支持要求分配。','source_id':'S-NASA-FUNC','locator':'§4.3.1.2.2，Functional Analysis段','scope':'method rationale, not a specific robot decomposition'}, {'id':'CL-F02','claim':'分解存在替代方式，并随架构理解迭代；派生要求应有来源。','source_id':'S-NASA-FUNC','locator':'§4.3.1.2.1—.3；§4.3.1.3','scope':'general systems engineering explanation'}, {'id':'CL-F03','claim':'接口需要维护变更及相关方协调，不能只有一个端点的自述。','source_id':'S-NASA-IF','locator':'§6.3.1.2.2—.5与§6.3.1.3','scope':'interface management explanation'}]
claimsQ=[{'id':'CL-M01','claim':'GMA定义维度与取值形成形式配置空间。','source_id':'S-RITCHEY','locator':'GENERAL MORPHOLOGY，parameters/conditions段','scope':'non-quantified problem structuring'}, {'id':'CL-M02','claim':'CCA检查一致性而非因果，区分逻辑、实证与规范判断。','source_id':'S-RITCHEY','locator':'CROSS CONSISTENCY ASSESSMENT，pair-wise及three types段','scope':'not proof of engineering compatibility'}, {'id':'CL-M03','claim':'规范性偏好不应混作逻辑/实证排除。','source_id':'S-RITCHEY','locator':'CROSS CONSISTENCY ASSESSMENT，normative judgments段','scope':'ordering of judgments, not a customer approval rule'}]
for d,claims in [(P,claimsP),(Q,claimsQ)]:save(d/'来源与主张.json',{'schema':'method-research-claim-evidence-1','sources':records[d],'claims':claims,'platform_adaptations':['TAP-TEACH-001构造功能/选项与未知','JSON字段、状态机和拒绝规则','教学检查与方法交接建议'],'unsupported_or_missing':['目标树体、组织限值及真实用户证据','机械/生物损伤与现场试验','独立领域专家复核'],'expert_certified':False})
