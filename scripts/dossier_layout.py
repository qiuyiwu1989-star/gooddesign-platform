# coding: utf-8
"""045 shared archive presentation: the Chang'e reader remains the visual reference."""
from dossier_reader_ui import CSS as UI_CSS,icon
from render_reader_dossier import CSS as READER_CSS
KEYS=['overview','technical','innovation','validation','ip','history','applications','governance']
# Structural rules that the authored reader inherits from its master document.
BASE_CSS='''*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink)}a{color:var(--accent);text-underline-offset:4px}button,input,select{font:inherit;color:inherit}button{cursor:pointer}main{min-width:0}.shell{display:grid;margin:auto}.toc{position:sticky;align-self:start;overflow:auto}.toc a{text-decoration:none}.hero{padding:32px 0}h2{margin:0}h3{margin:0}.view-bar{display:flex;flex-wrap:wrap}.view-bar #print{margin-left:auto}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;text-align:left}td,th{padding:12px;border-bottom:1px solid var(--line);vertical-align:top}.reader-shell [id]{scroll-margin-top:90px}[hidden]{display:none!important}'''
CONTEXT_CSS='''.reader-shell{--muted:#687083}.reader-shell .hero{padding-top:26px}.workspace-context{font:13px/1.7 system-ui;color:#687083;margin:0 0 22px}.workspace-context a{color:var(--accent)}.reader-shell .toc{top:26px;max-height:calc(100vh - 48px)}#view-bar{top:0}.reader-shell [id]{scroll-margin-top:90px}'''
CSS=BASE_CSS+READER_CSS+UI_CSS+CONTEXT_CSS

def view_bar():
 return '<nav class="view-bar" id="view-bar" aria-label="档案阅读方式">'+''.join('<button data-reader-tab="'+key+'" aria-pressed="'+str(key=='archive').lower()+'">'+icon(glyph)+title+'</button>'for key,glyph,title in [('archive','overview','项目档案'),('library','ip','资料与解读'),('assessment','governance','档案评估')])+'<button id="print" data-print="true">'+icon('print')+'打印 / 保存 PDF</button></nav>'
