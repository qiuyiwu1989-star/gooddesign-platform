"""Shared site chrome for full-screen apps; research mode keeps its own controls."""
import re
from gooddesign_assets import links
from gooddesign_chrome import navigation, footer


def wrap(text, kind):
    if 'data-gd-immersive-chrome' in text:
        return text
    nav = navigation('apps')
    # Full-screen apps have their own assistant. Keep one assistant entry only.
    nav = re.sub(r'<button class="gd-ip-trigger".*?</dialog>', '', nav, flags=re.S)
    if kind == 'expo':
        css = '''body:has(#home.off)>header.gd-nav{display:none!important}
body>header.gd-nav{position:relative;z-index:60}
#home{inset:var(--site-nav-height,80px) 0 0;overflow:auto;justify-content:flex-start;padding:28px max(24px,8vw) 0;scrollbar-gutter:stable}
#home .mark{position:static;flex:none;align-self:flex-start;margin:12px 0 32px}
#home .home-wrap{flex:none;min-height:440px;padding-bottom:36px}
#home>footer.gd-footer{flex:none;width:100%;max-width:none;display:grid;grid-template-columns:1fr 1.6fr;gap:20px;padding:24px 0;background:transparent;white-space:normal}
#home .gd-footer-note{grid-column:1/-1;margin:0}
#home .gd-footer-links{justify-content:flex-end;flex-wrap:wrap}
@media(max-width:767px){#home{padding:12px 20px 0}#home .mark{margin:8px 0 20px}#home .home-wrap{min-height:0;grid-template-columns:minmax(0,1fr);gap:28px}#home .home-wrap>div{min-width:0}#home #map{max-width:100%;min-height:220px}#home>footer.gd-footer{grid-template-columns:1fr}#home .gd-footer-links{justify-content:flex-start}}
@media print{body>header.gd-nav,#home>footer.gd-footer{display:none!important}}'''
        # Footer belongs to the landing view, never to the research canvas/report.
        text = text.replace('<div id="run">', footer() + '</div>\n<div id="run">', 1)
        # Remove the old home closing tag immediately before the injected footer.
        text = text.replace('</div>\n\n'+footer(), '\n'+footer(), 1)
    else:
        css = '''body{overflow:auto}body>.gd-rc--app{height:calc(100dvh - var(--site-nav-height,80px));min-height:420px}body>footer.gd-footer{margin:0 auto}
@media print{body>header.gd-nav,body>footer.gd-footer{display:none!important}}'''
        text = text.replace('</body>', footer()+'</body>', 1)
    js = '''<script data-gd-immersive-chrome>const siteNav=document.querySelector('body>header.gd-nav');if(siteNav){new ResizeObserver(entries=>{document.documentElement.style.setProperty('--site-nav-height',entries[0].target.getBoundingClientRect().height+'px')}).observe(siteNav)}</script>'''
    text = text.replace('</head>', links()+'<style data-gd-immersive-chrome>'+css+'</style></head>', 1)
    text = text.replace('<body>', '<body>'+nav, 1)
    if '</body>' in text:
        head, tail = text.rsplit('</body>', 1)
        return head + js + '</body>' + tail
    return text + js
