from pathlib import Path
import json,copy,importlib.util
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('checker',P/'核查教学模型.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
d=json.loads((P/'教学包/01-功能与接口输入-v0.1.1.json').read_text());results=[]
def run(name,mut=None):
 x=copy.deepcopy(d)
 if mut:mut(x)
 try:r=m.check(x);accepted=True;reason=r
 except (ValueError,KeyError,TypeError)as e:accepted=False;reason=str(e)
 expected=mut is None
 results.append(dict(name=name,expected_accept=expected,accepted=accepted,pass_=accepted==expected,detail=reason))
run('原正例')
run('删除全部未知',lambda x:x.update(unknowns=[]))
run('删除单个未知',lambda x:x['unknowns'].pop())
run('未知填零',lambda x:x['unknowns'][0].update(value=0))
run('删源需求',lambda x:x.update(source_needs=[]))
run('删除需求覆盖',lambda x:x['coverage'].pop())
run('清空需求功能引用',lambda x:x['coverage'][0].update(function_ids=[]))
run('漂移共享版本',lambda x:x['upstream'].update(version='0.1.1'))
run('漂移共享SHA',lambda x:x['upstream'].update(sha256='0'*64))
run('客户状态升级',lambda x:x.update(customer_approved=True))
run('遗漏客户状态',lambda x:x.pop('customer_approved'))
run('省略单位未知字段',lambda x:x['interfaces'][0].pop('producer_unit'))
run('单位冲突无转换',lambda x:x['interfaces'][1].update(consumer_unit='m',conversion=None))
run('维护覆盖升级',lambda x:x['coverage'][-1].update(coverage_scope='declared_research_functions'))
run('删异常恢复情境',lambda x:x.update(scenarios=[x['scenarios'][0]]))
run('组件代替作用',lambda x:x['functions'][0].update(verb_object='安装传感器'))
run('重复功能ID',lambda x:x['functions'][1].update(id=x['functions'][0]['id']))
(P/'教学包/05-修订实际检查.json').write_text(json.dumps({'scope':'fixed declared closure and adversarial mutations; not semantic or physical certification','checks':results,'passed':sum(r['pass_']for r in results),'total':len(results)},ensure_ascii=False,indent=2)+'\n')
assert all(r['pass_']for r in results),results
print(len(results),'passed')

transfer=json.loads((P/"教学包/07-不同情境迁移实际检查.json").read_text());assert m.check(transfer["input"])==transfer["actual_output"]
