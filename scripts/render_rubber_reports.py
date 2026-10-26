"""Render ML-005 Markdown as offline Zaowuyun-styled reports; no external JS or hidden model calls."""
import html,json,re,zipfile,hashlib
from pathlib import Path
from method_engine import ROOT
OUT=ROOT/'output/rubber-tapping-pilot'
def inline(t):
 t=html.escape(t)
 t=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>',t)
 t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
 return t

def render(text):
 lines=text.splitlines();out=[];heads=[];i=0
 while i<len(lines):
  line=lines[i]
  if not line.strip():i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].startswith('|'):
    row=[x.strip() for x in lines[i].strip().strip('|').split('|')];i+=1
    if all(re.fullmatch(r'[:\- ]+',x) for x in row):continue
    rows.append(row)
   out.append('<div class="table-wrap" role="region" aria-label="研究对照表" tabindex="0"><table>'+''.join('<tr>'+''.join(('<th scope="col">' if n==0 else '<td>')+inline(c)+('</th>' if n==0 else '</td>') for c in r)+'</tr>' for n,r in enumerate(rows))+'</table></div>');continue
  match=re.match(r'^(#{1,3}) (.+)',line)
  if match:
   level=len(match[1]);anchor='section-'+str(len(heads));heads.append((level,anchor,match[2]));out.append(f'<h{level} id="{anchor}">{inline(match[2])}</h{level}>');i+=1;continue
  if line.startswith('- '):
   rows=[]
   while i<len(lines) and lines[i].startswith('- '):rows.append('<li>'+inline(lines[i][2:])+'</li>');i+=1
   out.append('<ul>'+''.join(rows)+'</ul>');continue
  out.append('<p>'+inline(line)+'</p>');i+=1
 return ''.join(out),heads
CSS='''*{box-sizing:border-box}body{margin:0;background:var(--surface-canvas);color:var(--fg);font:var(--fs-body)/1.85 var(--font-sans)}header{border-bottom:1px solid var(--bdr);padding:var(--sp-5) var(--page-gutter);display:flex;gap:var(--sp-5);align-items:center;flex-wrap:wrap}header strong{margin-right:auto}a{color:var(--accentDeep);text-underline-offset:4px}button{font:inherit}header a{font-size:var(--fs-sm)}.wrap{max-width:var(--container-doc);margin:auto;padding:var(--sp-8) var(--page-gutter)}.reading{display:grid;grid-template-columns:210px minmax(0,1fr);gap:var(--sp-10)}aside{position:sticky;top:var(--sp-5);align-self:start}aside a{display:block;font-size:var(--fs-caption);padding:var(--sp-2);text-decoration:none}article{min-width:0;background:var(--surface-content);border:1px solid var(--bdr);border-radius:var(--r-lg);padding:var(--sp-8)}article>p,article>ul{max-width:680px}h1{font-size:var(--fs-h1);line-height:1.4;font-weight:600}h2{font-size:var(--fs-h2);margin-top:var(--sp-10);line-height:1.5}h3{font-size:var(--fs-h3);line-height:1.5}.badge{display:inline-block;background:var(--acBg);color:var(--accentDeep);padding:var(--sp-1) var(--sp-3);border-radius:var(--r-xs);font-size:var(--fs-caption)}.lead{color:var(--fg2);max-width:680px}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--sp-6);margin:var(--sp-8) 0}.card{background:var(--surface-content);border:1px solid var(--bdr);border-radius:var(--r-lg);padding:var(--sp-6)}.card p{color:var(--fg2)}.flow{display:flex;flex-wrap:wrap;gap:var(--sp-3);margin:var(--sp-6) 0}.flow span{background:var(--surface-content);border:1px solid var(--bdr);padding:var(--sp-3);border-radius:var(--r-md)}.table-wrap{max-width:100%;overflow:auto;margin:var(--sp-6) 0}table{border-collapse:collapse;font-size:var(--fs-sm);min-width:640px}td,th{border-bottom:1px solid var(--bdr);padding:var(--sp-3);text-align:left;vertical-align:top}th{background:var(--acBg)}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--surface-content);padding:var(--sp-5);border:1px solid var(--bdr);border-radius:var(--r-md);font-size:var(--fs-caption)}a:focus-visible,button:focus-visible,.table-wrap:focus-visible{outline:2px solid var(--accent);outline-offset:4px}@media(max-width:767px){.reading,.cards{grid-template-columns:1fr}aside{position:static}aside a{display:inline-block}article{padding:var(--sp-5)}.wrap{padding:var(--sp-6) var(--page-gutter)}h1{overflow-wrap:anywhere}}@media print{header,aside,button{display:none}.reading{display:block}article{border:0;padding:0}.wrap{padding:0}.table-wrap{overflow:visible}table{min-width:0}body{background:white;color:black}}'''
def shell(title,body):
 return '<!doctype html><html lang="zh-CN" data-theme="light"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><link rel="stylesheet" href="vendor/tokens.css"><link rel="stylesheet" href="vendor/design-system.css"><link rel="stylesheet" href="reports.css"><header><strong>造物云 / 好设计创新实验</strong><a href="index.html">实验概览</a><a href="需求报告.html">需求报告</a><a href="创新方案报告.html">创新方案报告</a><a href="推理记录.html">实际调用</a><button class="zw-btn" id="theme">切换明暗</button></header>'+body+'<script>document.querySelector("#theme").onclick=()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==="light"?"dark":"light"}</script></html>'
def build():
 (OUT/'vendor').mkdir(exist_ok=True)
 for name in ['tokens.css','design-system.css']:(OUT/'vendor'/name).write_bytes((ROOT/'extensions/method-workbench/vendor'/name).read_bytes())
 (OUT/'reports.css').write_text(CSS)
 for pattern,name in [('01-*.md','需求报告.html'),('02-*.md','创新方案报告.html')]:
  md=next(OUT.glob(pattern));body,heads=render(md.read_text());toc=''.join(f'<a href="#{a}">{inline(t)}</a>' for l,a,t in heads if l==2)
  (OUT/name).write_text(shell(heads[0][2],'<div class="wrap reading"><aside aria-label="报告目录">'+toc+'</aside><article>'+body+'</article></div>'))
 engine=json.loads((OUT/'engine-report.json').read_text());cases=json.loads((OUT/'case-retrieval-audit.json').read_text())
 overview='''<main class="wrap"><span class="badge">研究实验 · 待客户与专业复核</span><h1>割胶机器人：从需求到创新路线</h1><p class="lead">先理解作业与潜在需求，再调用方法、检索案例机制，形成候选与验证安排。没有把技术演示或案例成功当作客户方案已验证。</p><div class="flow"><span>① 会议线索与公开研究</span><span>② 15项研究需求</span><span>③ 方法与案例调用</span><span>④ 3条候选路线</span><span>⑤ 待执行验证</span></div><div class="cards"><section class="card"><span class="badge">报告一</span><h2>先定义值得解决的问题</h2><p>拆开切割深度、树体保护、切屑污染和全流程效率。列出15项潜在需求、依据、未知和验收口径建议。</p><a class="zw-btn zw-btn--primary" href="需求报告.html">阅读需求描述报告</a></section><section class="card"><span class="badge">报告二</span><h2>让方法与案例参与推理</h2><p>实际读取5个项目、8份来源及8份方法档案。Host Agent形成六份产物，经MCP检查、提交和恢复读取；三条路线暂不排名。</p><a class="zw-btn zw-btn--primary" href="创新方案报告.html">阅读创新方案报告</a></section></div><section class="card"><h2>这次真正验证了什么</h2><p>需求包指纹贯穿运行；六份产物逐步交接；遗漏硬约束的反例被阻断；服务重启后六份记录仍在。验证了数据与执行链，未验证任何候选的工程性能。</p><p>后台模型调用因429限流超时，自动生成步骤未完成；报告与结构化方案采用Host Agent编排，再实际调用方法MCP检查，完整保留失败边界。</p><a href="推理记录.html">查看实际执行与限制</a> · <a href="交付包.zip">下载报告与结构化交付</a></section></main>'''
 (OUT/'index.html').write_text(shell('割胶机器人创新实验',overview))
 summary={'run_id':engine['run_id'],'mode':engine['mode'],'status':engine['status'],'demand_packet_sha256':engine['demand_packet_sha256'],'steps':[{'method':x['method'],'check':x['check']['status'],'saved_revision':x['submission']['revision']} for x in engine['checks']],'restart_revision':engine['restart_revision'],'negative_case':engine['omitted_hard_constraint_negative'],'quality_gate':engine['quality_gate'],'backend_model_attempt':engine['backend_model_attempt'],'case_projects':cases['projects']}
 (OUT/'推理记录.html').write_text(shell('实际调用记录','<main class="wrap"><h1>实际调用与能力边界</h1><p>案例与方法读取、规则匹配、规划、产物检查、持久提交和重启读取均为真实stdio MCP调用。结构化产物由Host Agent组织，不是后台语义模型自动生成。</p><p><a href="engine-report.json">执行JSON</a> · <a href="需求包.json">需求交接JSON</a> · <a href="Agent推理产物.json">六份结构化产物</a> · <a href="case-retrieval-audit.json">来源指纹与定位</a></p><pre>'+html.escape(json.dumps(summary,ensure_ascii=False,indent=2))+'</pre></main>'))
 allowed=[p for p in OUT.iterdir() if p.is_file() and p.suffix in {'.md','.json','.html','.css'}]
 allowed +=list((OUT/'vendor').glob('*.css'))
 manifest={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in allowed}
 with zipfile.ZipFile(OUT/'交付包.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in allowed:z.write(p,str(p.relative_to(OUT)))
  z.writestr('文件指纹.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(OUT/'交付包.zip') as z:assert z.testzip() is None
 print('2 reports, overview, execution page and ZIP built; private source bodies/logs/DB excluded')
if __name__=='__main__':build()
