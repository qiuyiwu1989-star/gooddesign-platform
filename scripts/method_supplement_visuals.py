"""Editorial icons for ML-012 only; preserve 055-owned base icon definitions."""
from html import escape
from method_reader_visuals import semantic_icon
ICONS={
'R49':('功能行为结构桥','区分功能、行为和结构并回查','<rect x="3" y="20" width="12" height="15" rx="2"/><circle cx="28" cy="27" r="8"/><path d="M41 18h12v18H41zM15 27h5m16 0h5M47 40q-19 17-38 0"/>'),
'R50':('服务泳道','用户前台后台与支持交接','<path d="M3 12h50M3 27h50M3 42h50M13 8v38m15-38v38m15-38v38"/><circle cx="13" cy="12" r="4"/><circle cx="28" cy="27" r="4"/><circle cx="43" cy="42" r="4"/><path d="m16 15 9 9m6 6 9 9"/>'),
'R51':('控制反馈约束','控制动作与情境反馈相互检查','<rect x="17" y="5" width="23" height="12" rx="2"/><rect x="17" y="38" width="23" height="12" rx="2"/><path d="M22 17v21m-4-5 4 5 4-5M36 38V17m-4 5 4-5 4 5M7 18l5 9-5 9-5-9z"/>'),
'R52':('学习后的决策分支','新证据是否改变后续选择','<circle cx="10" cy="28" r="6"/><circle cx="43" cy="12" r="6"/><circle cx="43" cy="44" r="6"/><path d="M16 28h10m0 0 12-13M26 28l12 13M27 4v12m-4-8h8M25 45h8"/>')}
def icon(d):
    if d['research_id'] not in ICONS:return semantic_icon(d)
    title,reason,geometry=ICONS[d['research_id']]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" role="img"><title>'+escape(d['name']+'：'+title)+'</title><desc>'+escape(reason+'；平台编辑示意，不是原作者标识')+'</desc><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+geometry+'</g></svg>'
