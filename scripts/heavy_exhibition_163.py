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
CONCLUSIONS = {
    '2015-02': '真正的极限设计，是让每一次出发，都有返回的可能。',
    '2015-01': '深海平台不是一件设备，而是一座必须长期稳定工作的海上工厂。',
    '2015-00': '速度只有与安全、安静和舒适一起实现，才构成更好的出行。',
    '2023-00': '制造大飞机之前，先要有能够制造它的可靠装备。',
    '2021-01': '清洁能源的价值，要在几十年的稳定运行中兑现。',
    '2024-03': '动力的先进，不只在温度与转速，也在热管理和可靠服役。',
    '2024-02': '安全不是附加要求，而是系统设计的第一原则。',
    '2025-00': '无法现场维修的任务，必须在地面把未知尽可能变成已验证。',
}


def esc(value):
    return html.escape(str(value), quote=True)


def render():
    data = json.loads((ROOT / 'original-app/public/exhibits-heavy.json').read_text())
    catalog = {row['id']: row for row in json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())}
    featured = data['featured']
    assert len(featured) == 8
    hero_project = catalog[featured[0]['slug']]
    chapter_sections = []
    browser_links = []
    project_index = 0
    for chapter_number, chapter in enumerate(CHAPTERS, 1):
        matches = [item for item in featured if item['chapter'] == chapter[0]]
        projects = []
        for item in matches:
            project_index += 1
            project = catalog[item['slug']]
            cover = '/inno/portal/' + project['cover']
            browser_links.append(f'<a href="#project-{esc(item["slug"])}"><span>{project_index:02d}</span><strong>{esc(item["title"])}</strong><small>{esc(project["name"])}</small></a>')
            projects.append(f'''<article class="heavy-project" id="project-{esc(item['slug'])}" data-active-step="1" aria-label="{esc(project['name'])}">
  <figure class="heavy-project-media"><img src="{esc(cover)}" alt="{esc(project['name'])}" loading="lazy"><figcaption>{esc(project['year'])} · {esc(project['award'])} · {esc(project['name'])}</figcaption></figure>
  <div class="heavy-project-story">
    <section class="heavy-step" data-step="1" aria-label="真实任务"><p class="heavy-step-label">01 · 真实任务</p><h3>{esc(item['title'])}</h3><p class="heavy-step-question">{esc(item['ask'])}</p></section>
    <section class="heavy-step" data-step="2" aria-label="设计局部"><p class="heavy-step-label">02 · 设计局部</p><h3>{esc(item['look'])}</h3><p class="heavy-project-note">{esc(item['note'])}</p></section>
    <section class="heavy-step" data-step="3" aria-label="策展收束"><p class="heavy-step-label">03 · 策展收束</p><h3>{esc(CONCLUSIONS[item['slug']])}</h3><p class="heavy-project-boundary">{esc(item['maturity'])}</p><a class="heavy-evidence-link" href="/dossier/?project={esc(item['slug'])}">查看项目证据</a></section>
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
<meta name="description" content="国之重器沉浸式专题展：八件真实项目，四种极限任务，以滚动镜头看见设计如何回应真实约束。">
<title>国之重器 · 在极限中设计 · 好设计馆</title>
<link rel="stylesheet" href="/inno/portal/heavy-exhibition.css?v=164">
</head>
<body class="heavy-page">
<main id="main">
  <section class="heavy-hero" id="hall-heavy" aria-labelledby="heavy-title">
    <img class="heavy-hero-image" src="/inno/portal/{esc(hero_project['cover'])}" alt="{esc(hero_project['name'])}" fetchpriority="high">
    <div class="heavy-hero-shade"></div>
    <div class="heavy-hero-content">
      <p class="heavy-kicker">GOOD DESIGN SPECIAL EXHIBITION · 好设计馆专题展</p>
      <h1 id="heavy-title">国之重器<span>在极限中设计</span></h1>
      <p class="heavy-hero-lead">八件真实项目，四种极限任务。向下滚动，看见设计如何把科学目标、工程系统、人的安全和产业能力，组织成可靠结果。</p>
      <a class="heavy-start" href="#project-2015-02">开始参观</a>
    </div>
    <p class="heavy-hero-caption">{esc(hero_project['name'])} · {esc(hero_project['year'])} {esc(hero_project['award'])}</p>
  </section>
  {''.join(chapter_sections)}
  <section class="heavy-finale" id="hall-chron" aria-labelledby="heavy-finale-title">
    <p>THE NEXT INNOVATION</p>
    <h2 id="heavy-finale-title">看见已经实现的创新，<br>也开始下一次创新。</h2>
    <span>从真实项目证据出发，继续阅读、学习，或研究一个自己的真实问题。</span>
    <div><a href="/needs/">研究一个真实问题</a><a href="/projects/">返回项目库</a></div>
  </section>
</main>
<nav class="heavy-controls" aria-label="观展控制">
  <span class="heavy-current" aria-live="polite">01 / 08</span>
  <span class="heavy-progress" aria-hidden="true"><span></span></span>
  <button type="button" data-heavy-browse aria-haspopup="dialog" aria-controls="heavy-browser">快速浏览</button>
  <button type="button" data-heavy-present aria-pressed="false">细看</button>
</nav>
<dialog class="heavy-browser" id="heavy-browser" aria-labelledby="heavy-browser-title">
  <div class="heavy-browser-head"><div><p>QUICK VISIT</p><h2 id="heavy-browser-title">选择一件作品</h2></div><button type="button" data-heavy-close aria-label="关闭快速浏览">关闭</button></div>
  <div class="heavy-browser-links">{''.join(browser_links)}</div>
</dialog>
<script src="/inno/portal/heavy-exhibition.js?v=164" defer></script>
</body>
</html>'''
