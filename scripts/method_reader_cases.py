"""055 fixed, independently reviewed teaching-run presentation. No live engine execution."""
from pathlib import Path
import json,hashlib,html
ROOT=Path(__file__).resolve().parents[1];E=lambda s:html.escape(str(s),quote=True)
def teaching_case(rid):
 if rid=='R02':return double_diamond_case()
 if rid=='R01':return systematic_case()
 if rid=='R42':return verification_case()
 if rid=='R44':return prototype_case()
 if rid=='R36':return pugh_case()
 if rid=='R48':return chain_example()
 if rid=='R14':return function_case()+chain_example()
 if rid!='R17':return ''
 b=ROOT/'output/method-reader-review/upgrades/R17-v0.2.2'
 if not(b/'manifest.json').exists():return ''
 for x in json.loads((b/'manifest.json').read_text())['files']:
  if hashlib.sha256((b/x['path']).read_bytes()).hexdigest()!=x['sha256']:raise ValueError('R17教学包已变化，停止展示')
 load=lambda f:json.loads((b/'artifacts'/f).read_text());d=load('02-dimensions-and-options.json');c=load('04-all-combinations.json');names={o['id']:o['label']for o in d['options']};states={'excluded':'排除：模型内冲突','conditional_research':'待研究：整体条件未明','model_comparison_candidate':'仅作模型比较基线'}
 out='<section id="reproducible-example"><h2>把方法走完整：试样夹持教学案例</h2><p>这是固定教学假设的真实程序复算，不是真实客户方案。0.2.2案例已经独立隔离复测，判断ID冲突已拦截；这里只支持限定教学输入复算。原生离线映射和只读MCP跨方法结构检查已通过，尚未生产提交，也未证明工程有效。</p><h3>① 先把功能分开</h3><div class="relation-grid">'
 for dim in d['dimensions']:out+='<article class="relation"><h3>'+E(dim['function'])+'</h3><p>'+E(' / '.join(names[x]for x in dim['option_ids']))+'</p></article>'
 out+='</div><h3>② 配对检查以后，还要看整体</h3><p>三个功能、每功能两个选项，共8个组合。12个跨功能配对判断均为教学模型预录；程序只检查记录与枚举，不会自行发现物理相容。配对未冲突，也不能替代整体检查。</p><div class="table-scroll"><table><thead><tr><th>组合</th><th>组成</th><th>研究状态</th><th>依据与未决</th></tr></thead><tbody>'
 for row in c['combinations']:out+='<tr><td>'+E(row['id'])+'</td><td>'+E(' + '.join(names[x]for x in row['option_ids']))+'</td><td>'+E(states[row['state']])+'</td><td>'+E(row['reason'])+'</td></tr>'
 out+='</tbody></table></div><h3>③ 选择下一步比较对象，而不是宣称最优</h3><p>结果为4个排除、3个条件性研究、1个模型比较基线。载荷、材料、寿命和几何尺寸仍未知，全部工程验证未执行。</p><h3>④ 看实际负例能否拦住错误</h3><p>18次隔离正负例执行检查了缺需求、悬空引用、不完整矩阵、未知暗填、冲突选择及判断状态等情形。独立追加的跨类型判断ID重名探针已被拒绝，输出引用可唯一反查；18项通过仍不等于原生契约已接通、工程有效或80分达标。</p><h3>⑤ 转成引擎能读的研究草稿</h3><p>独立复核的离线映射保留16条判断和全部未知；原有4个非排除组合全部保守标为未知，模型内可比较不升级成工程候选。实际MCP仅调用只读结构与跨方法绑定检查，未创建运行、未提交产物、未调用生成模型。原生门禁与附加保真检查各自的作用单独记录。</p></section>'
 return out+adapter_examples()+chain_example()

def function_case():
 b=ROOT/'output/method-reader-review/upgrades/R14-v0.2.2-proposal'
 if not (b/'manifest.json').exists():return ''
 manifest=json.loads((b/'manifest.json').read_text())
 files=manifest['files'];entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('R14固定教学包变化，停止展示')
 load=lambda f:json.loads((b/'artifacts'/f).read_text())['data']
 f=load('03-functional-decomposition.json');flows=load('02-black-box-flows.json')['flows'];sc=load('05-scenarios-and-alternatives.json')
 names={x['id']:x['verb_object']for x in f['functions']}
 names.update({'EXT-IN':'试样输入边界','EXT-OUT':'试样移出边界','EXT-ENERGY':'外部供能边界','EXT-ENV':'环境边界','EXT-USER':'使用者边界','EXT-SIGNAL':'外部信息边界'})
 out='<section id="reproducible-function-example"><h2>把功能分析走完整：试样夹持教学案例</h2><p>这个案例先分析要完成的功能，不提前指定机构。需求为教学假设，真实载荷、尺寸和安全阈值未知。固定案例通过30项程序检查及独立复测，正常路径短路与外部物料链缺失均已拦截。覆盖检查目前限定明确起终点的单向功能链；不能泛化到任意反馈、并行或分支黑箱。</p><h3>从总功能分到必要功能</h3><p>'+E(f['functions'][0]['verb_object'])+'</p><ol class="flow">'
 for row in f['functions'][1:]:out+='<li><strong>'+E(row['verb_object'])+'</strong><p>对应 '+E('、'.join(row['requirement_refs']))+'</p><p>未实现时：'+E(row['failure_mode'])+'</p></li>'
 out+='</ol><h3>把物料、能量、信息穿过系统边界</h3><div class="table-scroll"><table><thead><tr><th>类型</th><th>从哪里到哪里</th><th>含义</th><th>量值</th></tr></thead><tbody>'
 kinds={'material':'物料','energy':'能量','signal':'信息','information':'信息'}
 for x in flows:out+='<tr><td>'+E(kinds.get(x['flow_type'],x['flow_type']))+'</td><td>'+E(names.get(x['from_id'],'外部边界'))+' → '+E(names.get(x['to_id'],'外部边界'))+'</td><td>'+E(x['description'])+'</td><td>未知，未测量</td></tr>'
 out+='</tbody></table></div><h3>用正常与异常情景核对遗漏</h3>'
 for x in sc['scenarios']:out+='<article class="relation"><h3>'+E(x['name'])+'</h3><p>'+E(' → '.join(names[y]for y in x['function_path']))+'</p><p>'+E(x['expected'])+'</p><p>情景尚未实际试验。</p></article>'
 return out+'<p>功能覆盖不证明结构可制造或动态性能。两条结构路线仍是未知假设，下一步交给形态分析比较；不能把功能框图直接当作产品方案。</p></section>'

def adapter_examples():
 b=ROOT/'output/method-reader-review/upgrades/R17-native-adapter-v2'
 review=ROOT/'output/method-reader-review/reviews/R17-native-adapter-v2/审核结论-v1.md'
 if not review.exists()or not(b/'manifest.json').exists():return ''
 files=json.loads((b/'manifest.json').read_text())['files'];entries=files.items()if isinstance(files,dict)else[(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('R17跨案例适配包变化，停止展示')
 r=json.loads((b/'execution-report.json').read_text())
 if len(r['cases'])!=3 or r['engineering_validated'] or r['store_or_MCP_write']:raise ValueError('跨案例展示范围变化')
 return '<section id="cross-context-adaptation"><h2>换一个问题，这个结构还能用吗？</h2><div class="relation-grid"><article class="relation"><h3>试样夹持</h3><p>定位、保持、解除：保留全部组合和未决条件。</p></article><article class="relation"><h3>观察记录与交接</h3><p>使用另一组功能与选项，明确协议假设，保留交接未知。</p></article><article class="relation"><h3>条目生成、存储与通知</h3><p>所有配对和整体关系均可未知，不因程序能枚举就产生可行结论。</p></article></div><p>三组教学任务已分别经过显式来源、任务及上游内容指纹绑定，并通过原生结构检查和独立复测。11个原负例及6个追加探针均被拒绝。适配器只处理明确定义的可信教学结构；哈希不是签名或事实认证，不能将任意输入代码视为可信。</p><p>这解除的是原先固定夹持案例的入口限制，不代表任意企业需求或工程模型已经接通。全部未排除组合保守保持未知，没有生产提交。</p></section>'


def chain_example():
 """An independently reviewed fixed teaching chain, not a production run."""
 b=ROOT/'output/method-reader-review/upgrades/three-method-chain-v1'
 r=ROOT/'output/method-reader-review/reviews/three-method-chain-v1/review.json'
 if not (b/'manifest.json').exists() or not r.exists():return ''
 review=json.loads(r.read_text())
 if review.get('verdict')!='fixed_explicit_teaching_chain_native_and_fidelity_passed':return ''
 for x in json.loads((b/'manifest.json').read_text())['files']:
  if hashlib.sha256((b/x['path']).read_bytes()).hexdigest()!=x['sha256']:raise ValueError('三方法教学链变化，停止展示')
 sdk=ROOT/'output/method-reader-review/native-mcp/three-method-chain-readonly-sdk.json'
 protocol=''
 if sdk.exists():
  d=json.loads(sdk.read_text())
  bound=all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in d['source_files'].values())
  checks=d.get('checks',[])
  passed=bound and len(checks)==3 and all(not x['is_error'] and x['response'].get('status')=='structure_and_declared_consistency_passed' and x['response'].get('cross_method_check')=='performed' and x['response'].get('engineering_validated') is False for x in checks)
  if passed:protocol='<p>三步还实际经过本机MCP只读接口检查：问题、功能模型、原理组合各检查一次，需求与输入版本一致。未调用生成模型、未提交生产数据；接口通过只说明结构与声明一致。</p>'
 return '<section id="three-method-chain"><h2>三个方法怎样接起来</h2><p>同一个试样夹持教学任务，先定义问题，再分解功能，最后组合原理。三步共享一份明确的需求版本；修改需求后，需要重新计算后续产物。</p><ol class="flow"><li><strong>问题定义：说清要解决什么</strong><p>保留三项必要需求，以及“操作力较低”的可选偏好。真实载荷、工况和验收阈值仍未知，需求尚未获客户确认。</p></li><li><strong>功能分析：说明各功能承担什么</strong><p>把可选偏好交给保持功能继续研究，完整保留物料、能量、信息流及接口。这是研究分配，不能证明已经实现低操作力。</p></li><li><strong>形态组合：比较原理并保留未决</strong><p>保留12项配对判断和4项整体判断。模型中未被排除的组合仍为未知，不自动变成工程候选；可选偏好也没有被偷偷当作已满足。</p></li></ol><h3>怎样防止交接时丢失信息</h3><p>独立隔离复测通过12项原测试；另加6项篡改探针，需求被改、指标方向反转、来源悬空、整体判断或接口丢失等均被拒绝。264项旧包与核心文件指纹保持不变。这里验证的是固定教学链的结构和信息保真，不是企业效果、工程相容或专家认证，也不是生产提交。</p>'+protocol+'</section>'


def pugh_case():
 b=ROOT/'output/method-reader-review/upgrades/R36-v0.2.1-proposal'
 r=ROOT/'output/method-reader-review/reviews/R36-upgrade-v0.2.1/review.json'
 if not (b/'manifest.json').exists() or not r.exists():return ''
 files=json.loads((b/'manifest.json').read_text())['files']
 entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('Pugh教学包变化，停止展示')
 rows=json.loads((b/'artifacts/02-complete-matrix.json').read_text())
 names={'PAPER':'纸本与封套','EMAIL':'电子记录与邮件','MIXED':'纸本与邮件，未定义转换'}
 criteria={'C-READ':'真实可读性','C-MEDIA':'媒介连续性','C-ACTIONS':'显式动作数'}
 values={'unknown':'未知','pass':'教学规则通过','fail':'教学规则不通过','same':'与基准相同','better':'相对较少','worse':'相对较多'}
 out='<section id="pugh-teaching-example"><h2>看一张完整的相对比较表</h2><p>把纸本与封套作为共同基准，比较三种记录交接路线。这是协议教学假设，动作条目不是实测时间或效率；真实可读性仍未知，基准本身也不能自动算通过。</p><div class="table-scroll"><table><thead><tr><th>路线</th><th>比较准则</th><th>相对基准的判断</th><th>判断依据</th></tr></thead><tbody>'
 for x in rows:out+='<tr><td>'+E(names[x['candidate_id']])+'</td><td>'+E(criteria[x['criterion_id']])+'</td><td>'+E(values[x['value']])+'</td><td>'+E(x['basis'])+'</td></tr>'
 return out+'</tbody></table></div><h3>换基准，检查结论是否被参照物误导</h3><p>程序实际改用电子记录作为基准重新计算9格；动作数的相对符号随参照变化，不能据正号数量选胜者。纸本加邮件缺少转换环节，按教学规则排除；动作少不能抵消硬门槛。其余两条只保留研究，工程推荐为空。</p><h3>原典、平台规则与验证分开</h3><p>MIT原典允许可选权重；本例不加权、保留未知与不可补偿硬门槛，是平台保守适配。19项程序测试、5项输出检查与独立复测支持固定教学展示；原生比较记录9格仍保守为未知，原符号另存，不伪造证据。</p><p>0.2.1已通过独立重复准则探针，拒绝同一操作重复计入矩阵；本例仍不是任意准则输入的通用工具。真实用户验证尚未执行，不代表工程有效或80分达标。</p></section>'


def prototype_case():
 b=ROOT/'output/method-reader-review/upgrades/R44-v0.2.1-proposal'
 r=ROOT/'output/method-reader-review/reviews/R44-upgrade-v0.2.1/review.json'
 if not (b/'manifest.json').exists() or not r.exists():return ''
 files=json.loads((b/'manifest.json').read_text())['files']
 entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('原型教学包变化，停止展示')
 a=json.loads((b/'artifacts/02-prototype-scope-and-tasks.json').read_text())
 rules=json.loads((b/'artifacts/03-protocol-and-bias.json').read_text())['decision_rules']
 out='<section id="prototype-teaching-plan"><h2>把未知变成一份可执行前核对的学习计划</h2><p>上一轮比较留下“接收者是否读懂记录”的未知。本例只计划用虚构文本研究字段标签和阅读顺序，不测试邮件发送、登录、权限或现场绩效。原型未制作、招募未开始、参与者为零；观察和发现均为空，下一步决定仍待定。</p><h3>先安排中性的任务</h3><ol class="flow">'
 for task in a['tasks']:out+='<li>'+E(task['instruction'])+'</li>'
 out+='</ol><h3>在看结果之前，约定怎样解释</h3><div class="relation-grid">'
 for rule in rules:out+='<article class="relation"><h3>'+E(rule['if_signal'])+'</h3><p>'+E(rule['interpretation'])+'</p></article>'
 return out+'</div><p>遗漏、错误复述和研究者提示要保留原话与行为，解释另列；人数和阈值尚未知。未取得同意与执行授权，不把计划写成已验证效果。20项程序测试与4项输出检查只支持固定计划的结构和保真。0.2.1把本教学材料限定为明确允许值，拒绝“现场运行并验证通过”的矛盾声明；这不是通用语义理解，其他自由文字仍需人工核对。</p></section>'


def verification_case():
 b=ROOT/'output/method-reader-review/upgrades/R42-v0.2.0-proposal'
 r=ROOT/'output/method-reader-review/reviews/R42-upgrade-v0.2.0/review.json'
 if not (b/'manifest.json').exists() or not r.exists():return ''
 files=json.loads((b/'manifest.json').read_text())['files']
 entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('验证确认教学包变化，停止展示')
 a=json.loads((b/'artifacts/02-configuration-and-methods.json').read_text())
 out='<section id="verification-teaching-plan"><h2>验证技术要求，也确认预期用途</h2><p>便携检测设备教学计划把两种问题分开：测量误差是否符合技术要求，以及目标用户戴手套能否完成现场任务。做过演示，不能替代误差测试；误差合格也不能替代用途确认。</p><div class="relation-grid">'
 for x in a['activities']:
  title='技术要求验证' if x['purpose']=='verification' else '预期用途确认'
  out+='<article class="relation"><h3>'+title+'</h3><ol>'+''.join('<li>'+E(v)+'</li>'for v in x['procedure'])+'</ol><p>当前：未执行、未验证；判据仍待确认。</p></article>'
 return out+'</div><h3>主动列出尚未覆盖的要求</h3><p>负载、时长和电源边界还未定义，续航要求尚无对应活动。它被明确列为未覆盖，不隐藏成“整体计划已完成”。样机配置尚未制作，软件版本、试样编号、温度与阈值未知，人员和测量资源也未就绪。</p><p>23项软件测试、5项保真检查及独立追加探针检查的是计划声明与追溯。真实产品和用户试验均为零，结果与异常记录为空；当前结论是未验证，不是通过或不合格。正式执行需要另版真实基线、配置、人员、授权与原始数据。</p></section>'


def systematic_case():
 b=ROOT/'output/method-reader-review/upgrades/R01-v0.2.1-proposal'
 r=ROOT/'output/method-reader-review/reviews/R01-upgrade-v0.2.1/review.json'
 if not (b/'manifest.json').exists() or not r.exists():return ''
 files=json.loads((b/'manifest.json').read_text())['files']
 entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('系统化设计教学包变化，停止展示')
 steps=[('先明确要求','定位、保持、解除和取样路径分别列要求；尺寸、载荷、损伤限度未知，不补默认值。'),('再研究作用原理','螺旋与杠杆两条路线分别解释怎样承担功能；都保留未知，不宣布胜者。'),('布置以后允许返回','二维教学布局发现取样区域冲突，返回概念层修订杠杆路线。修订后仍待全行程与三维研究，未关闭工程问题。'),('详细定义保留停点','材料、制造尺寸与公差未确认，不能生成制造放行结论。'),('留下决定与回返记录','每一步对应实际教学产物，回返记录指向发生冲突的原理；可以追问为何改、还缺什么。')]
 out='<section id="systematic-teaching-example"><h2>设计框架怎样留下可追问的过程</h2><p>这个原创夹具教学例子演示要求、功能、原理、布局与待验关系。它不是已经设计好的夹具；坐标与冲突均为教学假设，没有制造、仿真或实际试验。</p><ol class="flow">'
 for title,body in steps:out+='<li><strong>'+title+'</strong><p>'+body+'</p></li>'
 return out+'</ol><p>0.2.1经22项检查及独立追加探针，错误阶段文件、缺文件与回返错误原理被拒绝。验证范围是固定阶段对应和文件存在性，不是任意产物的语义一致性。二维相交面积只是示意算术，不是工程几何或强度证明。</p><p>原典核读限公开VDI摘要与出版社目录，未读取付费章节；教学补充不能冒充完整原典、实际设计经验或可执行MCP。</p></section>'


def double_diamond_case():
 b=ROOT/'output/method-reader-review/upgrades/R02-v0.2.1-proposal'
 r=ROOT/'output/method-reader-review/reviews/R02-upgrade-v0.2.1/review.json'
 if not (b/'manifest.json').exists() or not r.exists():return ''
 files=json.loads((b/'manifest.json').read_text())['files']
 entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('双钻教学包变化，停止展示')
 out='<section id="double-diamond-teaching"><h2>从“给小车加电机”开始，先别急着选方案</h2><p>原创教学请求不是已经确认的用户需求。第一钻尚未有真实研究证据，第二钻也只是研究计划；没有观察、访谈原话或用户测试结果。</p><ol class="flow">'
 steps=[('发现：展开需要核实的假设','把推行、转向、停放和维护等问题分开，安排怎样取得证据；不把作者想象写成用户反馈。'),('定义：保留暂定问题版本','CH-1只是当前讨论起点，尚未证据收敛；另一问题CH-2是条件性提议，未被采用。'),('发展：比较不同作用路径','候选方案声明回应哪些假设，同时显式列出未覆盖项。声明覆盖不代表已经满足，更不能为凑覆盖硬加能力。'),('交付：先安排学习','保留比较、观察与下一轮决定的计划；没有执行就不填成功，也不把返回定义阶段画成已经发生。')]
 for title,text in steps:out+='<li><strong>'+title+'</strong><p>'+text+'</p></li>'
 return out+'</ol><p>0.2.1通过29项结构与一致性检查及独立原漏洞复测。候选覆盖采用“已声明＋明确未覆盖”的分区，条件问题用本教学允许内容校验；这是固定案例门禁，不是通用语义理解。真实共创、现场研究与反馈仍待开展，不能称方法效果或80分已达标。</p></section>'
