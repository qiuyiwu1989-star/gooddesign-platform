import html
import json

E = lambda value: html.escape(str(value), quote=True)

CSS = '''
html:has(.app-store),body:has(.app-store){overflow-x:hidden}
body:has(.app-store) .gd-shell{width:min(calc(100% - 80px),1200px);max-width:1200px}
body:has(.app-store) .pp-page{max-width:1200px;padding-inline:40px}
[data-tone=museum]{--tone:#6257C8;--toneSoft:rgba(98,87,200,.11)}
[data-tone=education]{--tone:#2475B7;--toneSoft:rgba(36,117,183,.11)}
[data-tone=needs]{--tone:#147C64;--toneSoft:rgba(20,124,100,.12)}
[data-tone=enterprise]{--tone:#A96525;--toneSoft:rgba(169,101,37,.13)}
[data-tone=canvas]{--tone:#0F6674;--toneSoft:rgba(15,102,116,.11)}
[data-tone=mcp]{--tone:#4C5BAA;--toneSoft:rgba(76,91,170,.12)}
[data-tone=regional]{--tone:#A84C6D;--toneSoft:rgba(168,76,109,.12)}
[data-tone=xray]{--tone:#34758B;--toneSoft:rgba(52,117,139,.12)}
[data-tone=lab]{--tone:#147C64;--toneSoft:rgba(20,124,100,.12)}
[data-tone=quest]{--tone:#8B6A27;--toneSoft:rgba(139,106,39,.13)}
[data-tone=studio]{--tone:#A84C6D;--toneSoft:rgba(168,76,109,.12)}
[data-tone=transfer]{--tone:#0F6674;--toneSoft:rgba(15,102,116,.11)}
[data-theme=dark] [data-tone=xray]{--toneSoft:rgba(93,180,205,.16)}
[data-theme=dark] [data-tone=museum]{--toneSoft:rgba(127,119,255,.18)}[data-theme=dark] [data-tone=education]{--toneSoft:rgba(74,162,230,.18)}[data-theme=dark] [data-tone=needs]{--toneSoft:rgba(49,190,151,.18)}[data-theme=dark] [data-tone=enterprise]{--toneSoft:rgba(230,157,74,.18)}[data-theme=dark] [data-tone=canvas]{--toneSoft:rgba(94,196,210,.16)}[data-theme=dark] [data-tone=mcp]{--toneSoft:rgba(116,132,225,.18)}[data-theme=dark] [data-tone=regional]{--toneSoft:rgba(220,109,150,.18)}
.app-store{display:grid;gap:26px;padding-block:34px 40px}
.app-store-head{display:grid;gap:14px;max-width:640px}
.app-store-head h1{margin:0;font-size:clamp(30px,3.4vw,40px);font-weight:650;letter-spacing:-.03em;line-height:1.2}
.app-store-head p{margin:0;color:var(--fg2);font-size:14px;line-height:1.75}
.app-search{position:relative;max-width:420px}.app-search input{width:100%;min-height:46px;padding:10px 15px 10px 40px;border:1px solid var(--bdrSoft);border-radius:14px;background:var(--card);color:var(--fg);font-size:14px;box-shadow:var(--sh1)}.app-search::before{content:"⌕";position:absolute;left:16px;top:50%;color:var(--fg2);font-size:16px;transform:translateY(-52%)}.app-search input::placeholder{color:var(--fg2)}
.app-store-tabs{display:flex;flex-wrap:wrap;gap:8px;border-bottom:1px solid var(--bdrSoft);padding-bottom:14px}
.app-store-tabs button{min-height:38px;padding:7px 14px;border:1px solid transparent;border-radius:var(--r-full);background:transparent;color:var(--fg2);font-size:13px;transition:background var(--t-fast),color var(--t-fast),border-color var(--t-fast)}
.app-store-tabs button:hover{background:var(--glassA);color:var(--fg)}
.app-store-tabs button[aria-pressed=true]{border-color:var(--bdrSoft);background:var(--acBg);color:var(--accentDeep);font-weight:550}
.app-store-meta{display:flex;align-items:center;justify-content:space-between;gap:14px}#app-count{margin:0;color:var(--fg2);font-size:12px}
.app-store-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(246px,1fr));gap:14px}
.app-card{position:relative;display:grid;grid-template-rows:auto auto 1fr auto;gap:9px;width:100%;min-height:196px;padding:18px;border:1px solid var(--bdrSoft);border-radius:20px;background:var(--card);color:var(--fg);text-align:left;box-shadow:var(--sh1);transition:transform var(--t-fast),border-color var(--t-fast),box-shadow var(--t-fast)}
.app-card[hidden]{display:none}
.app-card:hover{border-color:var(--bdrBrt);box-shadow:var(--sh2);transform:translateY(-2px)}
.app-card:focus-visible{outline:2px solid var(--tone);outline-offset:2px}
.app-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.app-icon{display:grid;place-items:center;flex:none;width:44px;height:44px;border:1px solid var(--tone);border-radius:14px;background:var(--toneSoft);color:var(--tone);font-size:17px;font-weight:650}
.app-status{display:inline-flex;align-items:center;justify-content:center;min-height:25px;padding:3px 8px;border-radius:var(--r-full);font-size:11px;font-weight:500;line-height:1.3;white-space:nowrap}
.app-status--live{background:var(--okBg);color:var(--gd-ok-text)}.app-status--pilot{background:var(--warnBg);color:var(--gd-warn-text)}.app-status--planned{background:var(--infoBg);color:var(--gd-info-text)}
.app-card-title{display:block;font-size:17px;font-weight:650;line-height:1.45;letter-spacing:-.01em}
.app-card-value{display:-webkit-box;margin:0;overflow:hidden;color:var(--fg2);font-size:13px;line-height:1.7;-webkit-box-orient:vertical;-webkit-line-clamp:2}
.app-card-foot{display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px;align-items:center;margin-top:2px;padding-top:11px;border-top:1px solid var(--bdrSoft);color:var(--fg2);font-size:11px}.app-card-foot span:last-child{overflow:hidden;text-align:right;color:var(--tone);font-weight:600;text-overflow:ellipsis;white-space:nowrap}
.app-sheet{overflow:auto;width:min(560px,calc(100% - 40px));max-height:min(86vh,760px);padding:0;border:1px solid var(--bdr);border-radius:22px;background:var(--card);color:var(--fg);box-shadow:var(--sh3,var(--sh2))}
.app-sheet::backdrop{background:rgba(18,20,32,.42);backdrop-filter:blur(3px)}
.app-sheet[open]{animation:sheetIn .24s var(--ease)}@keyframes sheetIn{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.app-sheet-body{position:relative;display:grid;gap:18px;padding:22px}
.app-sheet-close{position:absolute;top:14px;right:14px;display:grid;place-items:center;width:34px;height:34px;border:1px solid var(--bdrSoft);border-radius:50%;background:var(--card);color:var(--fg2);font-size:16px;line-height:1}.app-sheet-close:hover{color:var(--fg);border-color:var(--bdrBrt)}
.app-detail-hero{display:grid;grid-template-columns:58px minmax(0,1fr);gap:14px;align-items:center;padding:18px;border:1px solid var(--bdrSoft);border-radius:18px;background:linear-gradient(135deg,var(--toneSoft),transparent 72%)}
.app-detail-icon{width:58px;height:58px;border-radius:17px;font-size:24px}
.app-detail-title-wrap{display:grid;gap:5px;min-width:0;justify-items:start}.app-detail-title-wrap span{color:var(--fg2);font-size:11px}
.app-detail h2{margin:0;font-size:24px;font-weight:650;line-height:1.35;letter-spacing:-.02em}
.app-detail-value{margin:0;color:var(--fg);font-size:15px;line-height:1.75}
.app-meta{display:grid;gap:8px}.app-meta-item{display:grid;grid-template-columns:86px 1fr;gap:10px;padding:10px 0;border-bottom:1px solid var(--bdrSoft)}.app-meta-item span{color:var(--fg2);font-size:11px}.app-meta-item strong{font-size:12px;font-weight:550;line-height:1.5}
.app-case-strip{display:grid;gap:10px;padding:14px;border:1px solid var(--bdrSoft);border-radius:15px;background:var(--acBg)}.app-case-strip h3{margin:0;font-size:15px;line-height:1.5}.app-case-strip p{margin:0;color:var(--fg2);font-size:12px;line-height:1.65}.app-case-strip small{display:block;color:var(--fg2);font-size:11px;line-height:1.55}.app-case-link{display:inline-flex;align-items:center;justify-content:center;min-height:36px;padding:7px 11px;border:1px solid var(--bdrBrt);border-radius:10px;background:var(--card);color:var(--accentDeep);font-size:12px}
.app-detail-action{display:inline-flex;align-items:center;justify-content:center;width:100%;min-height:44px;padding:10px 14px;border-radius:12px;background:var(--tone);color:#fff;font-size:13px;font-weight:550;white-space:nowrap}.app-detail-action:active{transform:translateY(1px)}
@media(max-width:760px){body:has(.app-store) .gd-shell{width:calc(100% - 32px)}body:has(.app-store) .pp-page{padding-inline:16px}.app-store{gap:20px;padding-block:24px 30px}.app-store-head h1{font-size:30px}.app-store-tabs{flex-wrap:nowrap;overflow-x:auto;padding-bottom:10px}.app-store-tabs button{flex:none}.app-store-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.app-card{min-height:0;padding:14px;gap:8px}.app-icon{width:40px;height:40px;border-radius:12px;font-size:15px}.app-card-title{font-size:15px}.app-card-value{font-size:12px}.app-card-foot{grid-template-columns:1fr;gap:2px;padding-top:9px}.app-card-foot span:last-child{text-align:left}.app-sheet{width:100%;max-width:100%;max-height:88dvh;margin:auto 0 0;inset:auto 0 0;border-radius:20px 20px 0 0}}
@media(max-width:390px){.app-store-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media print{.app-store-tabs,.app-search,.app-sheet,.gd-ip-trigger{display:none!important}.app-store-grid{grid-template-columns:repeat(2,1fr)}.app-card{break-inside:avoid}}
@media(prefers-reduced-motion: reduce){.app-sheet[open]{animation:none}}
/* 157 应用货架、特色应用与详情阅读 */
.app-store-head{max-width:none;grid-template-columns:minmax(0,1fr) minmax(320px,440px);align-items:end;gap:40px}
.app-store-head h1{max-width:720px;font-size:clamp(36px,4vw,48px);letter-spacing:-.045em}
.app-store-head>.gd-kicker{grid-column:1;grid-row:1}.app-store-head>h1{grid-column:1;grid-row:2}.app-store-head>p{grid-column:1;grid-row:3}.app-store-head>.app-search{grid-column:2;grid-row:1/4}
.app-store-head p{max-width:650px;font-size:14px;line-height:1.85}
.app-search{width:100%;max-width:none}.app-search input{min-height:50px;border-radius:15px;box-shadow:none}
.app-store-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.app-card{min-height:210px;padding:22px;box-shadow:none;overflow:hidden}
.app-card:before{content:"";position:absolute;top:0;right:22px;left:22px;height:2px;background:var(--tone);opacity:0;transition:opacity .18s}
.app-card:hover:before,.app-card:focus-visible:before{opacity:.72}
.app-card:hover{border-color:var(--tone);box-shadow:var(--sh1)}
.app-card-title{font-size:18px}.app-card-value{font-size:13px;line-height:1.75}
.app-card[data-app-id="regional"]{grid-column:1/-1;grid-template-columns:64px minmax(0,1.2fr) minmax(190px,.8fr);grid-template-rows:auto auto 1fr;align-items:center;gap:10px 24px;min-height:154px;background:linear-gradient(110deg,var(--toneSoft),var(--card) 62%)}
.app-card[data-app-id="regional"] .app-card-top{grid-row:1/4;align-self:start}
.app-card[data-app-id="regional"] .app-icon{width:56px;height:56px;border-radius:17px;font-size:21px}
.app-card[data-app-id="regional"] .app-card-title{grid-column:2;font-size:23px}
.app-card[data-app-id="regional"] .app-card-value{grid-column:2;max-width:640px;font-size:14px;-webkit-line-clamp:3}
.app-card[data-app-id="regional"] .app-card-foot{grid-column:3;grid-row:1/4;grid-template-columns:1fr;gap:8px;margin:0;padding:12px 0 12px 24px;border-top:0;border-left:1px solid var(--bdrSoft)}
.app-card[data-app-id="regional"] .app-card-foot span:last-child{text-align:left;font-size:13px}
.app-card[data-app-id="regional"] .app-status{position:absolute;top:22px;right:22px}
#app-clear{padding:0;border:0;background:none;color:var(--accentDeep);font:inherit;font-size:12px;cursor:pointer}
.app-store-empty{padding:42px 24px;border:1px dashed var(--bdrBrt);border-radius:18px;color:var(--fg2);text-align:center;font-size:14px;line-height:1.8}
.app-sheet{width:min(640px,calc(100% - 40px));border-radius:24px}
.app-sheet-body{gap:20px;padding:28px}
.app-sheet-close{width:40px;height:40px;font-size:18px}
.app-detail-hero{padding:22px;background:var(--toneSoft);border:0}
.app-detail h2{font-size:26px}.app-detail-value{font-size:16px;line-height:1.85}
.app-case-strip{padding:18px;background:var(--demo)}
.app-detail-action{min-height:48px;font-size:14px}
@media(max-width:1000px){.app-store-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.app-card[data-app-id="regional"]{grid-column:1/-1}}
@media(max-width:760px){.app-store-head{grid-template-columns:1fr;gap:22px}.app-store-head h1{font-size:36px}.app-store-head>.app-search{grid-column:1;grid-row:4}.app-card[data-app-id="regional"]{grid-template-columns:56px minmax(0,1fr);grid-template-rows:auto auto auto auto}.app-card[data-app-id="regional"] .app-card-top{grid-row:1/3}.app-card[data-app-id="regional"] .app-card-title,.app-card[data-app-id="regional"] .app-card-value{grid-column:2}.app-card[data-app-id="regional"] .app-card-foot{grid-column:1/-1;grid-row:auto;border-left:0;border-top:1px solid var(--bdrSoft);padding:12px 0 0}}
@media(max-width:600px){.app-store-grid{grid-template-columns:1fr;gap:14px}.app-card{min-height:0;padding:20px}.app-card[data-app-id="regional"]{grid-column:auto;grid-template-columns:52px minmax(0,1fr);gap:10px 16px}.app-card[data-app-id="regional"] .app-card-title{font-size:20px}.app-card[data-app-id="regional"] .app-icon{width:48px;height:48px}.app-card[data-app-id="regional"] .app-card-value{font-size:13px}.app-card[data-app-id="regional"] .app-card-foot{border-top:1px solid var(--bdrSoft)}.app-sheet-body{padding:22px 18px}.app-detail-hero{padding:18px}.app-detail h2{font-size:23px}.app-detail-value{font-size:15px}}
@media print{.app-card[data-app-id="regional"]{display:block}.app-card[data-app-id="regional"] .app-card-foot{border-left:0}}
'''

ICONS = {'museum': '馆', 'education': '教', 'needs': '研', 'enterprise': '企', 'canvas': '画', 'mcp': '接', 'regional': '区', 'xray': '拆', 'lab': '实', 'quest': '关', 'studio': '创', 'transfer': '迁'}
KINDS = {'museum': 'experience', 'education': 'experience', 'needs': 'innovation', 'enterprise': 'innovation', 'canvas': 'innovation', 'mcp': 'access', 'regional': 'access', 'xray': 'experience', 'lab': 'experience', 'quest': 'experience', 'studio': 'experience', 'transfer': 'innovation'}
KIND_LABELS = {'all': '全部应用', 'experience': '内容学习', 'innovation': '创新研究', 'access': '接入扩展'}
STATUS_NAMES = {'live': '现在可用', 'pilot': '试点推进', 'planned': '规划建设'}


def status_badge(app, element_id=None):
    ident = f' id="{element_id}"' if element_id else ''
    return f'<span{ident} class="app-status app-status--{E(app["status"])}">{E(app["status_label"])}</span>'


def app_icon(app, detail=False):
    glyph = ICONS.get(app['id'], app['title'][0])
    klass = 'app-icon app-detail-icon' if detail else 'app-icon'
    return f'<span class="{klass}" aria-hidden="true">{E(glyph)}</span>'


def render(apps, cases):
    case_map = {'museum': 'chang-e', 'education': 'chang-e', 'needs': 'pump-079', 'enterprise': 'rubber-tapping', 'canvas': 'rubber-tapping', 'mcp': 'mcp-research', 'regional': 'yuhuan', 'xray': 'x-ray', 'lab': 'chang-e', 'quest': 'x-ray', 'studio': 'chang-e', 'transfer': 'rubber-tapping'}
    case_by_id = {case['id']: case for case in cases}
    tabs = ''.join(
        f'<button type="button" data-app-kind="{E(kind)}" aria-pressed="{str(kind == "all").lower()}">{E(label)}</button>'
        for kind, label in KIND_LABELS.items()
    )
    buttons = ''.join(
        f'<button class="app-card" type="button" data-app-id="{E(app["id"])}" data-kind="{E(KINDS[app["id"]])}" data-status="{E(app["status"])}" data-tone="{E(app["id"])}" aria-haspopup="dialog" aria-label="查看应用详情：{E(app["title"])}"><span class="app-card-top">{app_icon(app)}{status_badge(app)}</span><strong class="app-card-title">{E(app["title"])}</strong><p class="app-card-value">{E(app["value"])}</p><span class="app-card-foot"><span>{E(app["developer"])}</span><span>{E(KIND_LABELS[KINDS[app["id"]]])}</span></span></button>'
        for app in apps
    )
    data = json.dumps({'apps': apps, 'cases': case_by_id, 'case_map': case_map}, ensure_ascii=False).replace('<', '\\u003c')
    first = apps[0]
    first_case = case_by_id[case_map[first['id']]]
    script = f'''<script type="application/json" id="app-data">{data}</script><script>
const appData=JSON.parse(document.getElementById('app-data').textContent);let activeAppId='{first['id']}',activeKind='all';const ICONS={{museum:'馆',education:'教',needs:'研',enterprise:'企',canvas:'画',mcp:'接',regional:'区',xray:'拆',lab:'实',quest:'关',studio:'创',transfer:'迁'}};const KINDS={json.dumps(KINDS)};const KIND_LABELS={json.dumps(KIND_LABELS, ensure_ascii=False)};
const $=selector=>document.querySelector(selector);const $$=selector=>Array.from(document.querySelectorAll(selector));
const sheet=$('#app-sheet');let lastCard=null;
function selectApp(id){{const app=appData.apps.find(item=>item.id===id);if(!app)return;activeAppId=id;$('.app-sheet-body').dataset.tone=id;$('#app-detail-cat').textContent=KIND_LABELS[KINDS[id]];const badge=$('#app-detail-badge');badge.textContent=app.status_label;badge.className='app-status app-status--'+app.status;$('#app-detail-status').textContent=app.status_label;$('#app-detail-developer').textContent=app.developer;$('#app-detail-title').textContent=app.title;$('#app-detail-icon').textContent=ICONS[id]||app.title.slice(0,1);$('#app-detail-value').textContent=app.value;const route=$('#app-detail-route');route.href=app.route.runtime;route.textContent=app.action;const item=appData.cases[appData.case_map[id]];$('#app-case-title').textContent=item.title;$('#app-case-summary').textContent=item.summary;$('#app-case-boundary').textContent=item.boundary;$('#app-case-link').href='/cases/'+item.id+'/'}}
function openApp(id,card){{selectApp(id);lastCard=card||null;if(typeof sheet.showModal==='function'){{sheet.showModal()}}}}
sheet.addEventListener('click',event=>{{if(event.target===sheet)sheet.close()}});sheet.addEventListener('close',()=>{{if(lastCard)lastCard.focus()}});$('#app-sheet-close').addEventListener('click',()=>sheet.close());
function applyFilters(updateUrl=true){{const query=($('#app-search-input').value||'').trim().toLowerCase();let count=0;$$('.app-card').forEach(card=>{{const app=appData.apps.find(item=>item.id===card.dataset.appId);const matchesKind=activeKind==='all'||card.dataset.kind===activeKind;const haystack=[app.title,app.value,app.developer,app.summary,app.output,KIND_LABELS[card.dataset.kind]].join(' ').toLowerCase();const show=matchesKind&&(!query||haystack.includes(query));card.hidden=!show;if(show)count+=1}});$('#app-count').textContent=`显示 ${{count}} 项应用`;$('#app-empty').hidden=count!==0;$('#app-clear').hidden=activeKind==='all'&&!query;if(updateUrl){{const url=new URL(location.href);if(activeKind==='all')url.searchParams.delete('kind');else url.searchParams.set('kind',activeKind);if(query)url.searchParams.set('q',query);else url.searchParams.delete('q');history.replaceState({{}},'',url);}}}}
$$('.app-card').forEach(button=>button.addEventListener('click',()=>openApp(button.dataset.appId,button)));$$('[data-app-kind]').forEach(button=>button.addEventListener('click',()=>{{activeKind=button.dataset.appKind;$$('[data-app-kind]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));applyFilters()}}));$('#app-search-input').addEventListener('input',()=>applyFilters());
$('#app-clear').addEventListener('click',()=>{{activeKind='all';$('#app-search-input').value='';$$('[data-app-kind]').forEach(item=>item.setAttribute('aria-pressed',String(item.dataset.appKind==='all')));applyFilters()}});
const initialParams=new URLSearchParams(location.search);const initialKind=initialParams.get('kind')||'all';activeKind=Object.hasOwn(KIND_LABELS,initialKind)?initialKind:'all';$('#app-search-input').value=initialParams.get('q')||'';$$('[data-app-kind]').forEach(item=>item.setAttribute('aria-pressed',String(item.dataset.appKind===activeKind)));applyFilters(false);
</script>'''
    return f'''<style>{CSS}</style><section class="app-store"><header class="app-store-head"><span class="gd-kicker">GoodDesign Applications</span><h1>选择合适的应用，<br>开始一次创新任务。</h1><p>{len(apps)} 个真实应用，共用同一套项目证据。按任务浏览，点卡片查看价值、开发者与真实案例。</p><label class="app-search"><span class="pp-sr-only">搜索应用</span><input id="app-search-input" type="search" placeholder="搜索应用" autocomplete="off"></label></header><nav class="app-store-tabs" aria-label="应用分类">{tabs}</nav><div class="app-store-meta"><p id="app-count" aria-live="polite">显示 {len(apps)} 项应用</p><button id="app-clear" type="button" hidden>清除搜索与筛选</button></div><div class="app-store-grid" role="group" aria-label="全部应用">{buttons}</div><p class="app-store-empty" id="app-empty" hidden>没有找到匹配的应用。试试其他关键词，或清除搜索与分类筛选。</p></section><dialog class="app-sheet app-detail" id="app-sheet" aria-labelledby="app-detail-title"><div class="app-sheet-body" data-tone="{E(first['id'])}"><button class="app-sheet-close" id="app-sheet-close" type="button" aria-label="关闭">×</button><div class="app-detail-hero"><span class="app-icon app-detail-icon" id="app-detail-icon" aria-hidden="true">{E(ICONS.get(first['id'], first['title'][0]))}</span><div class="app-detail-title-wrap"><span>当前应用</span><h2 id="app-detail-title">{E(first['title'])}</h2>{status_badge(first, 'app-detail-badge')}</div></div><p class="app-detail-value" id="app-detail-value">{E(first['value'])}</p><div class="app-meta" aria-label="应用信息"><div class="app-meta-item"><span>分类</span><strong id="app-detail-cat">{E(KIND_LABELS[KINDS[first['id']]])}</strong></div><div class="app-meta-item"><span>状态</span><strong id="app-detail-status">{E(first['status_label'])}</strong></div><div class="app-meta-item"><span>开发者</span><strong id="app-detail-developer">{E(first['developer'])}</strong></div></div><section class="app-case-strip"><h3 id="app-case-title">{E(first_case['title'])}</h3><p id="app-case-summary">{E(first_case['summary'])}</p><small id="app-case-boundary">{E(first_case['boundary'])}</small><a class="app-case-link" id="app-case-link" href="/cases/{E(first_case['id'])}/">查看完整案例</a></section><a class="app-detail-action" id="app-detail-route" href="{E(first['route']['runtime'])}">{E(first['action'])}</a></div></dialog>{script}'''
