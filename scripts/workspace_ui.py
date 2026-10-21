# coding: utf-8
"""041: shared private workspace navigation; no source data changes."""
import html,re,urllib.parse
import project_pipeline as pp
ROOT=pp.ROOT
CSS='''
.workspace-header[hidden]{display:none!important}.workspace-header{min-height:72px!important;height:auto!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:20px!important;padding:14px 32px!important;background:#fff!important;border-bottom:1px solid #e4e5ef!important;font:14px/1.5 system-ui,-apple-system,"PingFang SC",sans-serif!important;position:relative;z-index:40;color:#25273c}.workspace-header a{text-decoration:none}.workspace-brand{color:#25273c;font-weight:700;font-size:18px;white-space:nowrap}.workspace-brand small{font-size:11px;color:#687083;font-weight:400;margin-left:10px}.workspace-nav{display:flex;gap:6px}.workspace-nav a{padding:10px 16px;border-radius:9px;color:#596074;white-space:nowrap}.workspace-nav a[aria-current=page]{color:#5947d9;background:#f0edff;font-weight:600}.workspace-private{font-size:11px;color:#687d6c;white-space:nowrap}.workspace-skip{position:absolute;left:16px;top:-80px;background:white;padding:12px;z-index:100}.workspace-skip:focus{top:8px}@media(max-width:700px){.workspace-header{padding:12px 16px!important;gap:10px!important;flex-wrap:wrap}.workspace-private,.workspace-brand small{display:none}.workspace-nav{width:100%;justify-content:space-between}.workspace-nav a{text-align:center;flex:1;padding:10px 12px;font-size:13px}.workspace-brand{font-size:17px}}@media print{.workspace-header,.workspace-skip{display:none!important}}
'''
def nav(active,project='2025-00'):
 q=urllib.parse.urlencode({'project':project});h=html.escape
 links=[('dossier','/dossier/?'+q,'项目档案'),('files','/?'+q,'资料管理'),('research','/methods/?'+q,'应用案例')]
 return '<a class="workspace-skip" href="#workspace-content">跳到内容</a><header class="workspace-header"><a class="workspace-brand" href="/dossier/?'+h(q)+'">创新设计<small>项目工作区</small></a><nav class="workspace-nav" aria-label="工作区">'+''.join('<a data-workspace="'+key+'" href="'+h(url)+'"'+(' aria-current="page"'if key==active else'')+'>'+title+'</a>'for key,url,title in links)+'</nav><span class="workspace-private">● 本地私有</span></header>'
def admin(text,project):
 return re.sub(r'<header>.*?</header>',lambda m:nav('files',project),text,count=1,flags=re.S).replace('</head>','<style>'+CSS+'</style></head>').replace('<main>','<main id="workspace-content">',1)
def empty(project,active,title,explanation):
 return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'body{margin:0;background:#f7f8fc;color:#25273c;font:15px/1.8 system-ui}main{max-width:700px;margin:60px auto;padding:30px}a{color:#5947d9}</style>'+nav(active,project)+'<main id="workspace-content"><h1>'+html.escape(title)+'</h1><p>'+html.escape(explanation)+'</p><a href="/?'+urllib.parse.urlencode({'project':project})+'">整理本项目资料 →</a><p><a href="/dossier/?project=2025-00">查看嫦娥标杆档案 →</a></p></main></html>'
def dossier(project):
 if project!='2025-00':return empty(project,'dossier','这个项目的研究档案还有待整理','已保留本项目的资料入口。嫦娥是当前已整理的标杆案例；这里不会用其他项目内容代替。')
 p=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样';text=(p/'档案.html').read_text(encoding='utf-8')
 text=re.sub(r'<header>.*?</header>',lambda m:nav('dossier',project),text,count=1,flags=re.S)
 text=text.replace('</head>','<style>'+CSS+'.reader-shell{--muted:#687083}.reader-tools{display:none}.reader-shell .hero{padding-top:26px}.workspace-context{font:13px/1.7 system-ui;color:#687083;margin:0 0 22px}.workspace-context a{color:#5947d9}.reader-shell .toc{top:26px;max-height:calc(100vh - 48px)}#view-bar{top:0}.reader-shell [id]{scroll-margin-top:90px}</style></head>')
 text=text.replace('<div class="hero">','<div class="hero" id="workspace-content"><p class="workspace-context">人工整合档案 · 8 个阅读模块　<a href="/?project=2025-00#research-panel">整理与查看研究版本 →</a></p>',1)
 text=text.replace('style="color:#a78145"','class="archive-caution"')
 text=text.replace('</head>','<style>.archive-caution{color:#8b6634}</style></head>')
 text=text.replace('href="项目图谱.html"','href="/dossier/graph/"')
 # Private research attachments are intentionally not exposed as a generic file server.
 text=re.sub(r'href="(?!https?:|#|/|mailto:)([^\"]+)"', 'aria-disabled="true" title="研究文件请在资料管理中查看"',text)
 text=text.replace('onclick="window.print()"','data-print="true"')
 text=text.replace('</body>','<script>document.querySelectorAll("[data-print]").forEach(b=>b.addEventListener("click",()=>window.print()));</script></body>')
 return text
def graph():
 text=(ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样/项目图谱.html').read_text(encoding='utf-8')
 text=re.sub(r'<header>.*?</header>',lambda m:nav('research'),text,count=1,flags=re.S)
 text=text.replace('</head>','<style>'+CSS+'</style></head>').replace('档案.html?v=5.1.0','/dossier/?project=2025-00').replace('<main>','<main id="workspace-content">',1)
 text=re.sub(r'href="(?:项目图谱|图谱调用样例)\.json"','aria-disabled="true" title="历史研究数据保留于项目源目录"',text)
 return text
