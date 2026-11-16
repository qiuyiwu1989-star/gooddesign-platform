import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import build_application_registry
import build_method_reader
import data_report_page
import innovation_gateway_page
import info_pages_095
import needs_research_page
import project_portal
from gooddesign_assets import FILES, ORDER, links
from gooddesign_chrome import replace_chrome

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'
REPORT = ROOT / 'output/inno-preview/gooddesign-site-report.json'


def family(relative):
    parts = relative.parts
    if parts[0] == 'inno':
        return 'inno-' + (parts[1] if len(parts) > 1 else 'home')
    if parts[0] in ('project', 'atom', 'lesson', 'industry-demo', 'explore', 'education-tools', 'courseware', 'teacher-workbench', 'model'):
        return parts[0]
    if parts[0] in ('exhibit-sim.html', 'exhibit-xray.html', 'playground.html', 'x-ray.html', 'dismantle'):
        return 'interactive-exhibit'
    return 'legacy-' + parts[0]


def navigation_target(relative):
    if relative.parts[0] == 'inno':
        section = relative.parts[1] if len(relative.parts) > 1 else 'projects'
        return {'methods': 'methods', 'museum': 'museum', 'apps': 'apps', 'cases': 'apps', 'needs': 'needs', 'needs-v2': 'needs', 'report': 'report', 'mcp': 'mcp', 'about': 'about', 'model': 'about', 'guide': 'about'}.get(section, 'projects')
    if relative.as_posix() == 'atom/index.html':
        return 'report'
    kind = family(relative)
    if kind == 'legacy-assistant.html':
        return 'museum'
    if kind == 'industry-demo':
        return 'needs'
    if kind in ('model', 'legacy-migration-report.html'):
        return 'about'
    if kind in ('lesson', 'education-tools', 'courseware', 'teacher-workbench', 'legacy-learn.html', 'legacy-teacher-dash.html', 'legacy-workshop.html'):
        return 'learn'
    if kind in ('interactive-exhibit', 'legacy-index.html', 'legacy-hall.html', 'legacy-categories.html', 'legacy-award.html', 'legacy-laureates.html'):
        return 'museum'
    if kind == 'explore':
        return 'learn' if 'teacher' in relative.as_posix() else 'museum'
    return 'projects'


CANONICAL_BASE = 'https://haoshejiguan.com'


def canonical_url(relative):
    rel = relative.as_posix()
    if rel == 'inno/museum/index.html':
        return CANONICAL_BASE + '/'
    section_map = {'inno/index.html': '/projects/', 'inno/needs-v2/index.html': '/needs/'}
    if rel in section_map:
        return CANONICAL_BASE + section_map[rel]
    museum_map = {'categories.html': '/museum/zones', 'hall.html': '/museum/hall',
                  'x-ray.html': '/museum/x-ray', 'playground.html': '/museum/playground',
                  'laureates.html': '/projects/', 'assistant.html': '/museum/assistant',
                  'connect.html': '/museum/connect', 'award.html': '/museum/award'}
    if rel in museum_map:
        return CANONICAL_BASE + museum_map[rel]
    if rel.startswith('inno/'):
        if rel.endswith('/index.html'):
            return CANONICAL_BASE + rel[4:-len('index.html')]
        if rel.endswith('.html'):
            return CANONICAL_BASE + rel[4:]
        return None
    if rel.endswith('.html'):
        return CANONICAL_BASE + '/inno/legacy/' + rel
    return None


# 122 博物馆系干净地址：构建期改写展品页相互链接（源文件保持渠道中立，不改 original-app）
MUSEUM_LINK_MAP = {
    'href="categories.html': 'href="/museum/zones',
    'href="hall.html': 'href="/museum/hall',
    'href="x-ray.html': 'href="/museum/x-ray',
    'href="playground.html': 'href="/museum/playground',
    'href="laureates.html': 'href="/projects/',
    'href="assistant.html': 'href="/museum/assistant',
    'href="connect.html': 'href="/museum/connect',
    'href="award.html': 'href="/museum/award',
    'href="index.html': 'href="/"',
    "href='categories.html": "href='/museum/zones",
    "href='hall.html": "href='/museum/hall",
}


def museum_project_links(relative):
    slug = relative.name[:-len('.html')]
    return f'<div class="gd-project-apps" aria-label="项目互动学习入口"><span>继续探索这个项目</span><a href="/museum/x-ray?slug={slug}">拆解实验室</a><a href="/museum/playground?slug={slug}&tab=migrate">互动学习</a></div>'


def decorate(path, relative):
    text = path.read_text(encoding='utf-8')
    text = text.replace(str(ROOT), '<PROJECT_ROOT>')
    if relative.parts[0] in ('project', 'atom') and relative.suffix == '.html':
        text = text.replace('<body>', '<body>' + museum_project_links(relative), 1)
        text = text.replace('</head>', '<link rel="stylesheet" href="/inno/portal/museum-learning.css"></head>', 1)
    if relative.as_posix() == 'playground.html':
        text = text.replace('互动乐园', '互动学习')
        text = text.replace('动手玩懂<em>国之重器</em>。', '从真实项目，<em>动手理解设计</em>。')
        text = text.replace('看完、拆完,再来亲手试一试:模拟月球钻取、拼装采样系统、闯关集徽章、猜猜是哪件重器、设计你的国之重器——从「看懂」到「再造」。', '通过模拟实验、观展闯关、设计创作和技术迁移，理解设计如何工作。模拟仅用于教学，结果不代表工程精确或实际验证。')
        text = text.replace('</head>', '<link rel="stylesheet" href="/inno/portal/museum-learning.css"></head>', 1)
    if 'gooddesign.css' not in text:
        text = text.replace('</head>', links() + '</head>', 1) if '</head>' in text else links() + text
    text = text.replace('/library/reader.css', '/inno/methods/reader.css')
    text = text.replace('/library/reader.js', '/inno/methods/reader.js')
    if relative.as_posix() == 'inno/museum/index.html' or not relative.as_posix().startswith(('inno/', 'atom/', 'project/', 'explore/', 'lesson/', 'courseware/', 'education-tools/', 'industry-demo/')):
        for old, new in MUSEUM_LINK_MAP.items():
            text = text.replace(old, new)
    # Preserve source-directory context when production supplies a legacy base URL.
    if relative.parts[0] != 'inno':
        def legacy_link(match):
            value = match.group(2)
            part = value.split('#', 1)[0].split('?', 1)[0]
            if not part or part.startswith('/') or ':' in part or not part.endswith('.html'):
                return match.group(0)
            target = (ROOT / 'original-app/public' / relative.parent / part).resolve()
            try:
                rel = target.relative_to((ROOT / 'original-app/public').resolve())
            except ValueError:
                return match.group(0)
            if not target.is_file():
                return match.group(0)
            return match.group(1) + '/inno/legacy/' + rel.as_posix() + value[len(part):] + match.group(3)
        text = re.sub(r'''(href=["'])([^"']+)(["'])''', legacy_link, text)
    if relative.as_posix() in {'categories.html', 'x-ray.html', 'playground.html'} and '<base href=' not in text:
        text = text.replace('<head>', '<head><base href="/inno/legacy/">', 1)
    if relative.as_posix() == 'inno/museum/index.html':
        text = text.replace('</head>', '<link rel="stylesheet" href="/inno/portal/museum-polish.css?v=20261116-157">' + '</head>', 1)
        text = text.replace('</body>', '<script src="/inno/portal/museum-polish.js?v=20261116-157" defer></script></body>', 1)
    if relative.as_posix() in {'inno/museum/index.html', 'categories.html', 'hall.html', 'laureates.html', 'connect.html', 'playground.html', 'award.html'}:
        text = text.replace('</body>', '<script src="/inno/portal/museum-scenes.js?v=20261116-3" defer></script></body>', 1)
    if relative.as_posix() == 'categories.html':
        text = text.replace('</head>', '<link rel="stylesheet" href="/inno/portal/museum-zone-ui.css?v=20261116-1"></head>', 1)
        text = text.replace('</body>', '<script src="/inno/portal/museum-zone-ui.js?v=20261116-1" defer></script></body>', 1)
    from project_cover_display import rewrite_html
    text = rewrite_html(text)
    text = replace_chrome(text, navigation_target(relative))
    url = canonical_url(relative)
    if url and 'rel="canonical"' not in text:
        text = text.replace('</head>', f'<link rel="canonical" href="{url}"></head>', 1)
    if 'data-theme=' not in text:
        text = re.sub(r'<html([^>]*)>', r'<html\1 data-theme="light" data-zw-mode="product">', text, count=1)
    kind = family(relative)
    text = re.sub(r'<html([^>]*)>', lambda match: '<html' + match.group(1) + ' data-gd-family="' + kind + '">', text, count=1)
    text = re.sub(r'<h1>(.*?)</h1>', lambda match: '<h1>' + re.sub(r'(?<=[a-z])(?=[A-Z])', '<wbr>', match.group(1)) + '</h1>', text, flags=re.S)
    if relative.as_posix() in ('inno/museum/index.html', 'categories.html'):
        text = text.replace('</head>', '<link rel="stylesheet" href="/inno/portal/museum-hero.css"></head>', 1)
    path.write_text(text, encoding='utf-8')


def write(relative, text):
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')


def museum_featured():
    curated = (
        ('2025-00', 'industry', '设计与产业'),
        ('2017-01', 'industry', '设计与产业'),
        ('2015-02', 'industry', '设计与产业'),
        ('2021-00', 'industry', '设计与产业'),
        ('2025-03', 'life', '设计与生活'),
        ('2021-01', 'society', '设计与社会'),
    )
    catalog = {row['id']: row for row in json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text(encoding='utf-8'))}
    scene_covers = {
        '2025-00': 'illustrations/2025-pixel-v1/2025-00-r1-thumb.webp?v=38db61f298',
        '2025-03': 'illustrations/2025-pixel-v1/2025-03-r2-thumb.webp?v=cfab72a99d',
        '2017-01': 'museum-scenes-20261116/2017-01.webp',
        '2021-01': 'museum-scenes-20261116/2021-01.webp',
    }
    cards = []
    for pid, zone, zone_label in curated:
        row = catalog[pid]
        cover = scene_covers.get(pid, row['cover'])
        cards.append(f'''<article class="museum-exhibit" data-zone="{zone}"><a href="/dossier/?project={pid}"><img src="/inno/portal/{cover}" alt="{row['name']}项目封面" loading="lazy"><span class="museum-exhibit-meta"><small>{row['year']} · {row['award']} · {zone_label}</small><strong>{row['name']}</strong><span>阅读项目档案</span></span></a></article>''')
    return '<section class="sec museum-featured" id="featured"><div class="sec-h"><span class="no">02</span><h2>精选展项</h2><span class="en">Selected exhibits</span></div><p class="sec-sub">从一件件真实项目开始看展，理解设计如何回应工程、生活与社会问题。</p><div class="museum-exhibit-filters" role="group" aria-label="精选展项分类"><button type="button" data-exhibit-filter="all" aria-pressed="true">全部展项</button><button type="button" data-exhibit-filter="industry" aria-pressed="false">设计与产业</button><button type="button" data-exhibit-filter="life" aria-pressed="false">设计与生活</button><button type="button" data-exhibit-filter="society" aria-pressed="false">设计与社会</button></div><div class="museum-exhibits">' + ''.join(cards) + '</div></section>'


def build():
    from project_cover_display import write_script
    write_script()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copytree(ROOT / 'original-app/public', OUT, dirs_exist_ok=True)
    build_method_reader.build()
    shutil.copytree(ROOT / 'extensions/method-reader', OUT / 'inno/methods', dirs_exist_ok=True)
    for name in ORDER:
        source = FILES[name]
        write(Path('inno/portal') / name, source.read_text(encoding='utf-8'))
    for name in ['brand-logo.svg', 'ip-xiaohao.svg', 'ip-xiaohao-method.svg', 'ip-xiaohao-evidence.svg', 'xiaohao-bot-20261115.png', 'chrome.js']:
        shutil.copy2(ROOT / 'extensions/design-system' / name, OUT / 'inno/portal' / name)
    shutil.copytree(ROOT / 'extensions/design-system/awards', OUT / 'inno/portal/awards', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'extensions/design-system/museum-hero.css', OUT / 'inno/portal/museum-hero.css')
    for asset in ('museum-polish.css', 'museum-polish.js', 'museum-learning.css'):
        shutil.copy2(ROOT / 'extensions/design-system' / asset, OUT / 'inno/portal' / asset)
    for name in ['model-official.css', 'model-official.js']:
        shutil.copy2(ROOT / 'extensions/design-system' / name, OUT / 'inno/portal' / name)
    for source_name, target_name in [('portal.css', 'portal-page.css'), ('portal.js', 'portal-page.js')]:
        content = (ROOT / 'extensions/design-system' / source_name).read_text(encoding='utf-8')
        content = content.replace('../project-portal/', '/inno/portal/')
        (OUT / 'inno/portal' / target_name).write_text(content, encoding='utf-8')
    shutil.copy2(ROOT / 'extensions/inno/system.css', OUT / 'inno/portal/system.css')
    for name in ['portal.css', 'data-report.css', 'data-report.js', 'mcp-guide.js', 'mcp-center.css', 'project-cover-display.js']:
        source = ROOT / 'extensions/project-portal' / name
        if source.exists():
            shutil.copy2(source, OUT / 'inno/portal' / name)
    for name in ['needs.css', 'needs.js', 'method-catalog.json']:
        shutil.copy2(ROOT / 'extensions/needs-research' / name, OUT / 'inno/portal' / name)
    shutil.copytree(ROOT / 'extensions/project-portal/covers', OUT / 'inno/portal/covers', dirs_exist_ok=True)
    from build_illustration_skill import build as build_illustration_skill
    build_illustration_skill(OUT / 'inno/portal/skills')
    shutil.copy2(ROOT / 'extensions/design-system/museum-scenes.js', OUT / 'inno/portal/museum-scenes.js')
    for name in ('museum-zone-ui.css', 'museum-zone-ui.js'):
        shutil.copy2(ROOT / 'extensions/design-system' / name, OUT / 'inno/portal' / name)
    shutil.copytree(ROOT / 'extensions/design-system/museum-zone-icons', OUT / 'inno/portal/museum-zone-icons', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'extensions/design-system/museum-scenes-20261116', OUT / 'inno/portal/museum-scenes-20261116', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'extensions/project-portal/illustrations', OUT / 'inno/portal/illustrations', dirs_exist_ok=True)
    portal = (ROOT / 'extensions/design-system/portal.html').read_text(encoding='utf-8')
    portal = portal.replace('../method-workbench/vendor/tokens.css', '/inno/portal/tokens.css')
    portal = portal.replace('../method-workbench/vendor/design-system.css', '/inno/portal/design-system.css')
    portal = portal.replace('href="gooddesign.css"', 'href="/inno/portal/gooddesign.css"')
    portal = portal.replace('href="portal.css"', 'href="/inno/portal/portal-page.css"')
    portal = portal.replace('href="site-bridge.css"', 'href="/inno/portal/site-bridge.css"')
    portal = portal.replace('src="portal.js"', 'src="/inno/portal/portal-page.js"')
    portal = portal.replace('../project-portal/', '/inno/portal/')
    portal = portal.replace('<!-- MODEL_EXPLORER -->', info_pages_095.model_explorer_096.explorer())
    write('inno/index.html', portal)
    museum = (ROOT / 'original-app/public/index.html').read_text(encoding='utf-8')
    museum = museum.replace('互动乐园', '互动学习')
    museum = re.sub(r'<nav>.*?</nav>', '', museum, count=1, flags=re.S)
    museum = museum.replace('<head>', '<head><base href="/inno/legacy/">', 1)
    museum = museum.replace('<script src="copilot.js" defer></script>', '')
    museum = museum.replace('<section class="sec">\n    <div class="sec-h"><span class="no">02</span>', museum_featured() + '<section class="sec" id="education">\n    <div class="sec-h"><span class="no">02</span>', 1)
    museum = museum.replace('四种身份，四种讲法。<br>一件展品，<i>四种顿悟</i>。', '从一件展品，<br><i>继续提出问题。</i>')
    museum = museum.replace('导览员「好设计助手」：公众讲故事、学生讲原理、设计师讲方法、企业讲迁移。点亮深度推理模式，还能做技术迁移分析与对比评估。', '导览员小好陪你找项目、读方法、核证据。从公开展项进入真实档案，继续理解设计背后的选择。')
    write('inno/museum/index.html', museum)
    write('inno/needs/index.html', needs_research_page.page())
    needs_workspace = (ROOT / 'extensions/design-system/needs-workspace.html').read_text(encoding='utf-8')
    needs_assets = ['needs-workspace.css', 'needs-workspace.js', 'needs-live-demo.css', 'needs-live-demo.js']
    needs_digest = hashlib.sha256()
    for name in needs_assets:
        needs_digest.update((ROOT / 'extensions/design-system' / name).read_bytes())
    needs_version = needs_digest.hexdigest()[:8]
    needs_workspace = needs_workspace.replace('../method-workbench/vendor/tokens.css', '/inno/portal/tokens.css')
    needs_workspace = needs_workspace.replace('../method-workbench/vendor/design-system.css', '/inno/portal/design-system.css')
    needs_workspace = needs_workspace.replace('href="gooddesign.css"', 'href="/inno/portal/gooddesign.css"')
    needs_workspace = needs_workspace.replace('href="needs-workspace.css"', f'href="/inno/portal/needs-workspace.css?v={needs_version}"')
    needs_workspace = needs_workspace.replace('href="needs-live-demo.css"', f'href="/inno/portal/needs-live-demo.css?v={needs_version}"')
    needs_workspace = needs_workspace.replace('src="needs-workspace.js"', f'src="/inno/portal/needs-workspace.js?v={needs_version}"')
    needs_workspace = needs_workspace.replace('src="needs-live-demo.js"', f'src="/inno/portal/needs-live-demo.js?v={needs_version}"')
    write('inno/needs-v2/index.html', needs_workspace)
    for name in needs_assets:
        for directory in (OUT / 'inno/needs-v2', OUT / 'inno/portal'):
            shutil.copy2(ROOT / 'extensions/design-system' / name, directory / name)
    write('inno/report/index.html', data_report_page.page())
    write('inno/mcp/index.html', innovation_gateway_page.page())
    write('inno/about/index.html', info_pages_095.about())
    write('inno/model/index.html', info_pages_095.model())
    write('inno/guide/index.html', info_pages_095.guide())
    write('inno/apps/index.html', info_pages_095.apps())
    write('inno/apps/registry.json', json.dumps(build_application_registry.build_registry(), ensure_ascii=False, indent=2))
    shutil.copy2(ROOT / 'extensions/application-center/application.schema.json', OUT / 'inno/apps/application.schema.json')
    for case in info_pages_095.CASES:
        write(Path('inno/cases') / case['id'] / 'index.html', info_pages_095.case(case['id']))
    review_index = (ROOT / 'extensions/design-system/site-index.html').read_text(encoding='utf-8')
    write('site-index.html', replace_chrome(review_index, 'projects'))
    import build_museum_assistant_page
    write('assistant.html', build_museum_assistant_page.render())
    for asset in ('css', 'js'):
        shutil.copy2(ROOT / 'extensions/museum-assistant' / ('assistant.' + asset), OUT / 'inno/portal' / ('museum-assistant.' + asset))
    from heavy_exhibition_163 import render as render_heavy_exhibition
    write('hall.html', render_heavy_exhibition())
    for asset in ('heavy-exhibition.css', 'heavy-exhibition.js'):
        shutil.copy2(ROOT / 'extensions/design-system' / asset, OUT / 'inno/portal' / asset)
    pages = sorted(path for path in OUT.rglob('*.html') if path.name != 'site-index.html')
    groups = Counter()
    for path in pages:
        relative = path.relative_to(OUT)
        decorate(path, relative)
        groups[family(relative)] += 1
    report = {
        'status': 'built_not_deployed',
        'output': str(OUT.relative_to(ROOT)),
        'html_pages': len(pages),
        'groups': dict(groups),
        'design_assets': list(ORDER),
        'private_sources_exported': False,
        'production_changed': False,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    print(json.dumps(build(), ensure_ascii=False))
