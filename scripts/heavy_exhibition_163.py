import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = (
    ('CHAPTER 01 · 进入不可达之地', '进入不可达之地', '深海装备如何把未知环境转化为可进入、可作业、可返回的工作空间。'),
    ('CHAPTER 02 · 组织高速与巨力', '组织高速与巨力', '交通与重型装备如何在速度、尺度、精度和安全之间取得平衡。'),
    ('CHAPTER 03 · 设计能源心脏', '设计能源心脏', '能源装备如何把效率、安全和长期可靠运行统一起来。'),
    ('CHAPTER 04 · 抵达深空任务', '抵达深空任务', '航天采样系统如何在极端约束下完成高可靠自主作业。'),
)


def esc(value):
    return html.escape(str(value), quote=True)


def render():
    data = json.loads((ROOT / 'original-app/public/exhibits-heavy.json').read_text())
    catalog = {row['id']: row for row in json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())}
    featured = data['featured']
    assert len(featured) == 8
    hero = featured[0]
    hero_project = catalog[hero['slug']]
    chapter_nav = []
    chapter_sections = []
    project_index = 0
    for chapter_number, chapter in enumerate(CHAPTERS, 1):
        matches = [item for item in featured if item['chapter'] == chapter[0]]
        chapter_nav.append(f'<a href="#chapter-{chapter_number}" data-chapter-link="chapter-{chapter_number}"><span>0{chapter_number}</span><strong>{esc(chapter[1])}</strong><small>{len(matches)} 件项目</small></a>')
        projects = []
        for item in matches:
            project_index += 1
            project = catalog[item['slug']]
            cover = '/inno/portal/' + project['cover']
            projects.append(f'''<article class="heavy-project" id="project-{esc(item['slug'])}" aria-labelledby="title-{esc(item['slug'])}">
  <figure class="heavy-project-media"><img src="{esc(cover)}" alt="{esc(project['name'])}" loading="lazy"><figcaption>{esc(project['year'])} · {esc(project['award'])} · 真实获奖项目</figcaption></figure>
  <div class="heavy-project-copy">
    <p class="heavy-project-index">EXHIBIT {project_index:02d} / 08</p>
    <h3 id="title-{esc(item['slug'])}">{esc(item['title'])}</h3>
    <p class="heavy-project-name">{esc(project['name'])}</p>
    <p class="heavy-project-note">{esc(item['note'])}</p>
    <dl class="heavy-project-lenses"><div><dt>设计看点</dt><dd>{esc(item['look'])}</dd></div><div><dt>核心追问</dt><dd>{esc(item['ask'])}</dd></div></dl>
    <p class="heavy-project-boundary">{esc(item['maturity'])}</p>
    <div class="heavy-project-actions" aria-label="继续探索{esc(project['name'])}"><a class="heavy-action-primary" href="/museum/x-ray?slug={esc(item['slug'])}">拆解实验室</a><a href="/museum/playground?slug={esc(item['slug'])}">互动学习</a><a href="/dossier/?project={esc(item['slug'])}">项目档案</a></div>
  </div>
</article>''')
        chapter_sections.append(f'''<section class="heavy-chapter" id="chapter-{chapter_number}" aria-labelledby="chapter-title-{chapter_number}">
  <header class="heavy-chapter-head"><p>CHAPTER 0{chapter_number}</p><h2 id="chapter-title-{chapter_number}">{esc(chapter[1])}</h2><span>{esc(chapter[2])}</span></header>
  <div class="heavy-project-list">{''.join(projects)}</div>
</section>''')
    return f'''<!doctype html>
<html lang="zh-CN" data-theme="light" data-zw-mode="product">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="国之重器专题展：八件真实项目，四种极限任务，看见设计如何把科学目标、工程系统、人的安全和产业能力组织成可靠结果。">
<title>国之重器 · 在极限中设计 · 好设计馆</title>
<link rel="stylesheet" href="/inno/portal/heavy-exhibition.css?v=163">
</head>
<body class="heavy-page">
<main id="main">
  <section class="heavy-hero" id="hall-heavy" aria-labelledby="heavy-title">
    <img class="heavy-hero-image" src="/inno/portal/{esc(hero_project['cover'])}" alt="{esc(hero_project['name'])}" fetchpriority="high">
    <div class="heavy-hero-shade"></div>
    <div class="heavy-hero-content">
      <p class="heavy-kicker">GOOD DESIGN SPECIAL EXHIBITION · 好设计馆专题展</p>
      <h1 id="heavy-title">国之重器<span>在极限中设计</span></h1>
      <p class="heavy-hero-lead">八件真实项目，四种极限任务。看见设计如何把科学目标、工程系统、人的安全和产业能力，组织成可靠结果。</p>
      <a class="heavy-start" href="#chapter-1">开始参观</a>
    </div>
    <p class="heavy-hero-caption">{esc(hero_project['name'])} · {esc(hero_project['year'])} {esc(hero_project['award'])}</p>
  </section>
  <nav class="heavy-chapter-nav" aria-label="专题展章节">{''.join(chapter_nav)}</nav>
  <div class="heavy-progress" aria-hidden="true"><span></span></div>
  {''.join(chapter_sections)}
  <section class="heavy-finale" id="hall-chron" aria-labelledby="heavy-finale-title">
    <p>THE NEXT INNOVATION</p>
    <h2 id="heavy-finale-title">看见已经实现的创新，<br>也开始下一次创新。</h2>
    <span>从真实项目证据出发，继续阅读、学习，或研究一个自己的真实问题。</span>
    <div><a href="/needs/">研究一个真实问题</a><a href="/projects/">返回项目库</a></div>
  </section>
</main>
<script src="/inno/portal/heavy-exhibition.js?v=163" defer></script>
</body>
</html>'''
