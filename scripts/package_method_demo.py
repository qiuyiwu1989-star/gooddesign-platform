# coding: utf-8
"""040: compact portable handoff of a method-case demonstration, without the private source library."""
import csv,io,json,zipfile
from pathlib import Path
import innovation_methods as im,project_pipeline as pp

def package():
 run=im.read_run('latest','full');im.validate_run(run);folder=im.RUNS/run['run_id'];out=pp.ROOT/'output/handoff'/('三方法-嫦娥双库联动-'+run['run_id']+'.zip');out.parent.mkdir(parents=True,exist_ok=True)
 files={('运行记录/'+f.name):f.read_bytes()for f in folder.iterdir()if f.is_file()}
 for m in run['method_versions']:
  data=im.read_method(m['method_id'],m['version'],'full');f=im.LIB/'方法'/m['method_id']/m['version']/'方法卡.json';files['方法卡/'+m['method_id']+'.json']=f.read_bytes();files['方法卡/'+m['method_id']+'.md']=f.with_name('方法说明.md').read_bytes()
 files['企业输出.json']=(json.dumps(run['enterprise_output'],ensure_ascii=False,indent=2)+'\n').encode()
 files['方法卡规范-v1.md']=(im.LIB/'方法卡规范-v1.md').read_bytes()
 text=io.StringIO();writer=csv.writer(text);writer.writerow(['方法ID','版本','步骤ID','标题','输入引用','产物键','实际知识调用','证据ID','性质'])
 for stage in run['stages']:
  for s in stage['steps']:writer.writerow([stage['method_id'],stage['method_version'],s['step_id'],s['title'],';'.join(s['input_refs']),s['output_key'],json.dumps(s.get('knowledge_retrievals',{}),ensure_ascii=False),';'.join(s['evidence_ids']),s['nature']])
 files['方法与字段调用对照.csv']=text.getvalue().encode('utf-8-sig')
 files['先读我.md']='''# 三方法 × 嫦娥：双库联动研究演示

解压后打开“运行记录/联动报告.html”，无需安装可阅读三个视图：企业建议、分析过程、参考资料。三种方法在分析过程中按需展开，运行工具位于文末。也可阅读“运行记录/企业创新建议.md”。HTML依赖同目录style.css/app.js，勿只转发HTML单文件。原件下载需要原平台后台运行；本小包不包含论文/专利二进制原件。

方法卡目录提供三种平台改编方法的完整JSON和Markdown。企业输出.json适合应用展示；运行记录/run.json保存模拟任务、逐步产物、实际MCP响应、案例记录、证据块及版本。调用对照CSV便于检验应用所需字段。

这是一份固定模拟需求的研究演示：双库检索真实执行，分析由Codex在本轮研究编写，重放固定分析不等于通用LLM实时推理。企业名称/材料/基线/验收阈值未由真实客户确认，没有目标设备试验、效果提升、收益或最优方案结论。文献陈述、平台解释和迁移假设有区别；未认定嫦娥团队实际采用这些方法。

仅用于内部研究/交互测试；原典和来源文献权利归原权利人。版本清单校验文件完整性，不替代专业审核。
'''.encode()
 manifest=dict(run_id=run['run_id'],files=[dict(path=k,bytes=len(v),sha256=pp.sha(v))for k,v in sorted(files.items())]);files['交付文件清单.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED)as z:
  for name,body in files.items():z.writestr(name,body)
 with zipfile.ZipFile(out)as z:
  assert z.testzip()is None
  for f in manifest['files']:assert pp.sha(z.read(f['path']))==f['sha256']
 Path(str(out)+'.sha256').write_text(pp.sha(out.read_bytes())+'  '+out.name+'\n')
 result=dict(zip=str(out),bytes=out.stat().st_size,files=len(files),run_id=run['run_id'],integrity='CRC/SHA256 passed');print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':package()
