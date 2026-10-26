"""055 fixed, independently reviewed teaching-run presentation. No live engine execution."""
from pathlib import Path
import json,hashlib,html
ROOT=Path(__file__).resolve().parents[1];E=lambda s:html.escape(str(s),quote=True)
def teaching_case(rid):
 if rid=='R14':return function_case()
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
 return out

def function_case():
 b=ROOT/'output/method-reader-review/upgrades/R14-v0.2.0-proposal'
 if not (b/'manifest.json').exists():return ''
 manifest=json.loads((b/'manifest.json').read_text())
 files=manifest['files'];entries=files.items() if isinstance(files,dict) else [(x['path'],x['sha256'])for x in files]
 for name,sha in entries:
  if hashlib.sha256((b/name).read_bytes()).hexdigest()!=sha:raise ValueError('R14固定教学包变化，停止展示')
 load=lambda f:json.loads((b/'artifacts'/f).read_text())['data']
 f=load('03-functional-decomposition.json');flows=load('02-black-box-flows.json')['flows'];sc=load('05-scenarios-and-alternatives.json')
 names={x['id']:x['verb_object']for x in f['functions']}
 names.update({'EXT-IN':'试样输入边界','EXT-OUT':'试样移出边界','EXT-ENERGY':'外部供能边界','EXT-ENV':'环境边界','EXT-USER':'使用者边界','EXT-SIGNAL':'外部信息边界'})
 out='<section id="reproducible-function-example"><h2>把功能分析走完整：试样夹持教学案例</h2><p>这个案例先分析要完成的功能，不提前指定机构。需求为教学假设，真实载荷、尺寸和安全阈值未知。固定案例通过17项程序检查及独立复测，但正常情景路径覆盖仍有已知漏检，新版本正在修复，不作通用覆盖保证。</p><h3>从总功能分到必要功能</h3><p>'+E(f['functions'][0]['verb_object'])+'</p><ol class="flow">'
 for row in f['functions'][1:]:out+='<li><strong>'+E(row['verb_object'])+'</strong><p>对应 '+E('、'.join(row['requirement_refs']))+'</p><p>未实现时：'+E(row['failure_mode'])+'</p></li>'
 out+='</ol><h3>把物料、能量、信息穿过系统边界</h3><div class="table-scroll"><table><thead><tr><th>类型</th><th>从哪里到哪里</th><th>含义</th><th>量值</th></tr></thead><tbody>'
 kinds={'material':'物料','energy':'能量','signal':'信息','information':'信息'}
 for x in flows:out+='<tr><td>'+E(kinds.get(x['flow_type'],x['flow_type']))+'</td><td>'+E(names.get(x['from_id'],'外部边界'))+' → '+E(names.get(x['to_id'],'外部边界'))+'</td><td>'+E(x['description'])+'</td><td>未知，未测量</td></tr>'
 out+='</tbody></table></div><h3>用正常与异常情景核对遗漏</h3>'
 for x in sc['scenarios']:out+='<article class="relation"><h3>'+E(x['name'])+'</h3><p>'+E(' → '.join(names[y]for y in x['function_path']))+'</p><p>'+E(x['expected'])+'</p><p>情景尚未实际试验。</p></article>'
 return out+'<p>功能覆盖不证明结构可制造或动态性能。两条结构路线仍是未知假设，下一步交给形态分析比较；不能把功能框图直接当作产品方案。</p></section>'
