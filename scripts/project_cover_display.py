# -*- coding: utf-8 -*-
"""Display-only illustration overlay. Original catalog/photos remain unchanged."""
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'extensions/project-portal'
MANIFEST=ASSETS/'illustrations/2025-pixel-v1/display-manifest.json'


def mapping():
    if not MANIFEST.exists():return {}
    rows=json.loads(MANIFEST.read_text())['covers']
    assert len(rows)==33 and len({r['id'] for r in rows})==33
    return {r['id']:{'cover':r['cover'],'cover_full':r['cover_full'],'cover_kind':'scene_illustration','cover_usage':r['usage']} for r in rows}


def write_script():
    data=json.dumps(mapping(),ensure_ascii=False,separators=(',',':'))
    # Called before the catalog renderer; no API or factual record is mutated.
    script='''/* GoodDesign editorial covers. Source photos remain in the archive. */
window.GD_PROJECT_COVERS=Object.freeze('''+data+''');
(()=>{function decorate(){
 const style=document.createElement('style');style.textContent='.gd-cover-caption{position:absolute;right:10px;bottom:10px;z-index:2;padding:3px 7px;border-radius:6px;background:rgba(14,23,50,.72);color:#fff!important;font:400 10px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;pointer-events:none;letter-spacing:.04em}.gd-project-cover,.gd-feature-cover,.pp-cover,.pp-feature-image{position:relative}.gd-feature-cover[data-cover-kind="scene_illustration"]{height:auto;aspect-ratio:16/9}.gd-feature-cover>img[data-cover-kind="scene_illustration"]{object-fit:cover;filter:none}.gd-project-cover[data-cover-kind="scene_illustration"]>img{filter:none}.gd-project-cover[data-cover-kind="scene_illustration"]{aspect-ratio:16/9;height:auto;min-height:0;padding:0;display:block}.gd-project-cover[data-cover-kind="scene_illustration"]>img{width:100%;height:100%;object-fit:cover;object-position:center}';document.head.append(style);
 document.querySelectorAll('img').forEach(img=>{
 const m=img.getAttribute('src')?.match(/(?:covers\\/case-|2025-pixel-v1\\/)(2025-(?:\\d{2}|s\\d{2}|e\\d{2}))(?:[.-])/);if(!m)return;
 const cover=window.GD_PROJECT_COVERS[m[1]];if(!cover)return;
 img.src='/inno/portal/'+cover.cover_full;img.dataset.coverKind='scene_illustration';img.title='应用场景插画，非现场照片';
 if(!img.alt.includes('场景插画'))img.alt+=' · 场景插画';
 const parent=img.parentElement;parent.dataset.coverKind='scene_illustration';if(parent.matches('.gd-feature-cover,.pp-feature-image')){parent.style.position='relative';if(!parent.querySelector('.gd-cover-caption')){const label=document.createElement('span');label.className='gd-cover-caption';label.textContent='场景插画';parent.append(label)}}
 });
 }if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',decorate,{once:true});else decorate();
})();'''
    target=ASSETS/'project-cover-display.js';target.write_text(script)
    return target


def script_tag():
    p=ASSETS/'project-cover-display.js'
    if not p.exists():return ''
    return '<script src="/inno/portal/project-cover-display.js?v='+hashlib.sha256(p.read_bytes()).hexdigest()[:10]+'"></script>'


def rewrite_html(text):
    maps=mapping()
    if not maps:return text
    changed=False
    def image(match):
        nonlocal changed
        tag=match.group(0)
        found=re.search(r'(?:project-portal/|/inno/portal/)covers/case-(2025-(?:\d{2}|s\d{2}|e\d{2}))\.jpg(?:\?[^"\'\s>]*)?',tag)
        if not found or found[1] not in maps:return tag
        changed=True
        # Match and replace the complete URL to avoid ../ prefix inconsistencies.
        tag=re.sub(r'''(src=["'])[^"']*covers/case-'''+re.escape(found[1])+r'''\.jpg(?:\?[^"']*)?(["'])''',lambda m:m[1]+'/inno/portal/'+maps[found[1]]['cover_full']+m[2],tag)
        tag=tag[:-1]+' data-cover-kind="scene_illustration" title="应用场景插画，非现场照片">'
        tag=re.sub(r'''alt=(["'])(.*?)\1''',lambda m:'alt='+m[1]+m[2]+('' if '场景插画' in m[2] else ' · 场景插画')+m[1],tag)
        return tag
    text=re.sub(r'<img\b[^>]*>',image,text,flags=re.I)
    needs_script=changed or 'portal-page.js' in text or 'model-official.js' in text or re.search(r'/inno/portal/portal\.js',text)
    if 'project-cover-display.js' in text:
        text=re.sub(r'<script\b[^>]*src=[\"\'][^\"\']*project-cover-display\.js[^\"\']*[\"\'][^>]*>\s*</script>',lambda m:script_tag(),text)
    elif needs_script:text=text.replace('</head>',script_tag()+'</head>',1)
    text=re.sub(r'(/inno/portal/portal-page\.js)(?:\?v=[^"\'\s<>]*)?',r'\1?v=pixel2025-20261116',text)
    return text
