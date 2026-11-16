"""063 public reporting projection; 075 visual dashboard using safe summaries only."""
import collections
import hashlib
import html
import json
import math
from urllib.parse import urlencode

from project_portal import shell, ASSETS, catalog as current_catalog
import project_pipeline as pp

E = lambda value: html.escape(str(value), quote=True)
AWARD_ORDER = ('金奖', '银奖', '铜奖', '创意奖', '提名奖', '菁英奖')
AWARD_TONES = {'金奖': 'gold', '银奖': 'silver', '铜奖': 'bronze', '创意奖': 'creative', '提名奖': 'nominee', '菁英奖': 'elite'}
QUALITY_ORDER = ('Agent初评，待校准', '独立Agent校准，非专家', '待补证与内容评估', '版本变更，待复评')
QUALITY_TONES = {'Agent初评，待校准': 'initial', '独立Agent校准，非专家': 'calibrated', '待补证与内容评估': 'evidence', '版本变更，待复评': 'review'}


def number(value):
    return f'{value:,}'


def horizontal_bars(rows, value_label='项'):
    maximum = max((value for _, value, _ in rows), default=1) or 1
    return ''.join(
        f'<div class="dr-hbar dr-tone-{tone}"><span>{E(label)}</span><svg viewBox="0 0 100 8" aria-hidden="true"><rect class="dr-hbar-track" width="100" height="8" rx="4"/><rect class="dr-hbar-fill" width="{value / maximum * 100:.3f}" height="8" rx="4"/></svg><b>{number(value)}<small>{E(value_label)}</small></b></div>'
        for label, value, tone in rows
    )


def award_chart(catalog):
    counts = collections.Counter(row['award'] for row in catalog)
    offset = 0
    segments = []
    legends = []
    for award in AWARD_ORDER:
        count = counts.get(award, 0)
        if not count:
            continue
        tone = AWARD_TONES[award]
        share = count / len(catalog) * 100
        segments.append(f'<circle class="dr-donut-segment dr-tone-{tone}" cx="100" cy="100" r="70" pathLength="100" stroke-dasharray="{share:.4f} {100 - share:.4f}" stroke-dashoffset="{-offset:.4f}"><title>{E(award)} {count}项，占{share:.1f}%</title></circle>')
        href = '/projects/?' + urlencode({'award': award}) + '#collection'
        legends.append(f'<a class="dr-legend-item dr-tone-{tone}" href="{href}"><i class="dr-swatch" aria-hidden="true"></i><span>{E(award)}</span><b>{count}</b><small>{share:.1f}%</small></a>')
        offset += share
    return f'<article class="dr-panel dr-award-panel"><header class="dr-panel-heading"><div><h3>奖项构成</h3><p>点击奖项进入项目筛选</p></div><strong>{len(counts)}<small>类别</small></strong></header><div class="dr-donut-layout"><svg class="dr-donut" viewBox="0 0 200 200" role="img" aria-label="{len(catalog)}个项目的奖项构成"><g transform="rotate(-90 100 100)">' + ''.join(segments) + f'</g><text x="100" y="98" class="dr-donut-number">{len(catalog)}</text><text x="100" y="121" class="dr-donut-label">真实项目</text></svg><div class="dr-legend">' + ''.join(legends) + '</div></div></article>'


def year_chart(catalog):
    counts = collections.Counter(int(row['year']) for row in catalog)
    years = sorted(counts)
    maximum = max(counts.values())
    bars = []
    for index, year in enumerate(years):
        count = counts[year]
        height = count / maximum * 160
        x = 40 + index * 55
        y = 200 - height
        href = '/projects/?' + urlencode({'year': year}) + '#collection'
        bars.append(f'<a href="{href}" aria-label="{year}年 {count}个项目"><rect class="dr-year-bar" x="{x}" y="{y:.2f}" width="34" height="{height:.2f}" rx="7"><title>{year}年：{count}个项目</title></rect><text class="dr-chart-value" x="{x + 17}" y="{y - 9:.2f}">{count}</text><text class="dr-chart-text" x="{x + 17}" y="226">{year}</text></a>')
    return f'<article class="dr-panel dr-year-panel"><header class="dr-panel-heading"><div><h3>年度资产分布</h3><p>每个柱形是一年，可直接进入该年项目</p></div><strong>{len(years)}<small>个有数据年度</small></strong></header><div class="dr-chart-scroll"><svg class="dr-year-chart" viewBox="0 0 660 250" role="img" aria-label="{years[0]}至{years[-1]}年项目数量分布，无数据年份不绘制"><line class="dr-chart-axis" x1="28" y1="200" x2="630" y2="200"/>' + ''.join(bars) + '</svg></div></article>'


def evidence_scatter(projects):
    max_sources = max(row['source_entries'] for row in projects)
    max_known = max(row['known_cells'] for row in projects)
    max_records = max(row['records'] for row in projects)

    def px(value):
        return 64 + math.log1p(value) / math.log1p(max_sources) * 650

    def py(value):
        return 292 - math.log1p(value) / math.log1p(max_known) * 250

    chart = ['<line class="dr-chart-axis" x1="64" y1="292" x2="714" y2="292"/><line class="dr-chart-axis" x1="64" y1="42" x2="64" y2="292"/>']
    for tick in (2, 10, 50, max_sources):
        x = px(tick)
        chart.append(f'<line class="dr-chart-grid" x1="{x:.2f}" y1="42" x2="{x:.2f}" y2="292"/><text class="dr-chart-text" x="{x:.2f}" y="316">{tick}</text>')
    for tick in (1, 10, 100, max_known):
        y = py(tick)
        chart.append(f'<line class="dr-chart-grid" x1="64" y1="{y:.2f}" x2="714" y2="{y:.2f}"/><text class="dr-chart-text" x="54" y="{y + 4:.2f}" text-anchor="end">{tick}</text>')
    chart.append('<text class="dr-chart-axis-title" x="64" y="27">已知值字段</text><text class="dr-chart-axis-title" x="714" y="343" text-anchor="end">项目来源登记条目</text>')
    for row in projects:
        x = px(row['source_entries'])
        y = py(row['known_cells'])
        radius = 3.5 + math.sqrt(row['records'] / max_records) * 5.5
        tone = 'deep' if row['deepening'] else 'base'
        label = f"{row['id']} {row['name']}：{row['source_entries']}条来源，{row['known_cells']}个已知值字段，{row['records']}条结构化记录"
        chart.append(f'<a class="dr-evidence-link" href="/dossier/?project={E(row["id"])}" aria-label="{E(label)}" tabindex="0" role="link"><circle class="dr-evidence-point dr-evidence-point--{tone}" cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}"><title>{E(label)}</title></circle></a>')
        if row['id'] == '2025-00':
            chart.append(f'<text class="dr-chart-callout" x="{x - 12:.2f}" y="{y - 10:.2f}" text-anchor="end">{E(row["id"])}</text>')
        elif row['id'] == '2015-02':
            chart.append(f'<text class="dr-chart-callout" x="{x + 12:.2f}" y="{y - 10:.2f}">{E(row["id"])}</text>')
        elif row['id'] == '2017-01':
            chart.append(f'<text class="dr-chart-callout" x="{x + 12:.2f}" y="{y + 22:.2f}">{E(row["id"])}</text>')
    return f'<div class="dr-chart-scroll"><svg class="dr-scatter" viewBox="0 0 760 360" role="img" aria-label="{len(projects)}个金奖项目的来源登记与已知值字段密度，采用对数刻度">' + ''.join(chart) + '</svg></div>'


def quality_chart(data):
    counts = data['project_quality_counts']
    total = sum(counts.values())
    offset = 0
    segments = []
    buttons = []
    for status in QUALITY_ORDER:
        count = counts.get(status, 0)
        tone = QUALITY_TONES[status]
        width = count / total * 100
        segments.append(f'<rect class="dr-quality-segment dr-tone-{tone}" x="{offset:.3f}" y="0" width="{width:.3f}" height="22"><title>{E(status)} {count}案</title></rect>')
        buttons.append(f'<button class="dr-quality-filter dr-tone-{tone}" type="button" data-quality-filter="{E(status)}" aria-pressed="false"><i class="dr-swatch" aria-hidden="true"></i><span>{E(status)}</span><b>{count}案</b></button>')
        offset += width
    calibrated = counts.get('独立Agent校准，非专家', 0)
    pending = total - calibrated
    return '<article class="dr-panel dr-quality-main"><header class="dr-panel-heading"><div><h3>98案内容评估状态</h3><p>点击状态，直接筛选项目清单</p></div><button class="gd-button gd-button--quiet" type="button" data-quality-filter="">查看全部</button></header><div class="dr-quality-numbers"><div><strong>' + str(calibrated) + '</strong><span>独立Agent校准<small>不是专家审核</small></span></div><div><strong>' + str(pending) + '</strong><span>仍需推进<small>校准、补证或复评</small></span></div></div><svg class="dr-quality-stack" viewBox="0 0 100 22" preserveAspectRatio="none" role="img" aria-label="98个金奖项目的内容评估状态分布">' + ''.join(segments) + '</svg><div class="dr-quality-legend">' + ''.join(buttons) + '</div></article>'


def score_chart(projects):
    buckets = collections.Counter()
    for row in projects:
        score = row['score']
        if score is None:
            buckets['未评或待复评'] += 1
        elif score < 40:
            buckets['40分以下'] += 1
        elif score < 50:
            buckets['40-49分'] += 1
        elif score < 60:
            buckets['50-59分'] += 1
        else:
            buckets['60分以上'] += 1
    order = ('40分以下', '40-49分', '50-59分', '60分以上', '未评或待复评')
    rows = [(label, buckets[label], 'muted' if label == '未评或待复评' else 'accent') for label in order if buckets[label]]
    return '<article class="dr-panel"><header class="dr-panel-heading"><div><h3>当前内容评分分布</h3><p>只显示与当前版本匹配的分数，未评不算0分</p></div></header><div class="dr-hbars">' + horizontal_bars(rows, '案') + '</div><p class="dr-panel-note">评分针对档案内容，不是项目技术价值或获奖水平。</p></article>'


def methods_chart(data):
    counts = collections.Counter(row['category'] for row in data['methods'])
    rows = [(label.replace('全流程规划与创新管理', '全流程规划').replace('性能优化与工程实现', '性能优化').replace('方案决策与验证评价', '方案决策').replace('问题发现与需求定义', '问题定义').replace('功能分析与概念生成', '功能分析').replace('技术发明与矛盾求解', '矛盾求解').replace('机构架构与系统设计', '系统设计'), counts[label], 'accent') for label in sorted(counts)]
    low, high = data['method_baseline_range']

    def sx(score):
        return 50 + score / 100 * 540

    upgrades = ''.join(f'<div><span>{E(row["id"])}</span><strong>{E(row["score"])}</strong><small>教学增补组合</small></div>' for row in data['method_upgrades'])
    scale = f'<svg class="dr-score-scale" viewBox="0 0 640 105" role="img" aria-label="64方法基线内容评分范围{low}至{high}"><rect class="dr-score-track" x="50" y="38" width="540" height="8" rx="4"/><rect class="dr-score-range-band" x="{sx(low):.2f}" y="38" width="{sx(high) - sx(low):.2f}" height="8" rx="4"/>'
    for tick in (0, 20, 40, 60, 80, 100):
        scale += f'<text class="dr-chart-text" x="{sx(tick)}" y="75">{tick}</text>'
    scale += f'<text class="dr-chart-callout" x="{sx(low):.2f}" y="25">{low}</text><text class="dr-chart-callout" x="{sx(high):.2f}" y="25" text-anchor="end">{high}</text></svg>'
    return '<section class="dr-section" id="methods"><header class="dr-section-heading"><h2>64种方法，形成可检索的分析工具箱</h2><p>分类看方法结构，基线与教学增补组合分开呈现。</p></header><div class="dr-method-grid"><article class="dr-panel"><header class="dr-panel-heading"><div><h3>方法分类</h3><p>A至G七类，64份独立校准基线</p></div><strong>64<small>方法</small></strong></header><div class="dr-hbars">' + horizontal_bars(rows, '项') + '</div></article><article class="dr-panel"><header class="dr-panel-heading"><div><h3>内容基线范围</h3><p>独立Agent校准，满分100，不是专家认证</p></div><strong>' + E(low) + '<small>至' + E(high) + '</small></strong></header>' + scale + '<div class="dr-upgrades">' + upgrades + '</div><p class="dr-panel-note">尚无80分验收通过结论。方法内容基线不等于真实工程有效性。</p></article></div></section>'



def research_depth_chart(projects):
    counts = collections.Counter()
    for row in projects:
        value = row['known_cells']
        label = '1—9 个已知字段' if value < 10 else '10—19 个已知字段' if value < 20 else '20—49 个已知字段' if value < 50 else '50 个以上已知字段'
        counts[label] += 1
    order = ('1—9 个已知字段', '10—19 个已知字段', '20—49 个已知字段', '50 个以上已知字段')
    return '<div class="dr-hbars dr-depth-bars">' + horizontal_bars([(label, counts[label], 'accent') for label in order], '案') + '</div>'


def asset_showcase(catalog):
    selected = []
    for year in sorted({int(row['year']) for row in catalog}, reverse=True):
        candidates = [row for row in catalog if int(row['year']) == year and row.get('cover')]
        gold = next((row for row in candidates if row['award'] == '金奖'), None)
        other = next((row for row in candidates if not gold or row['id'] != gold['id']), None)
        selected.extend(row for row in (gold, other) if row)
    cards = []
    for index, row in enumerate(selected):
        cards.append(f'''<article class="dr-showcase-card" data-year="{E(row['year'])}" data-award="{E(row['award'])}"{' hidden' if index >= 6 else ''}><a href="/dossier/?project={E(row['id'])}"><img src="/inno/portal/{E(row['cover'])}" alt="{E(row['name'])}项目封面" loading="lazy"><span class="dr-showcase-meta"><small>{E(row['year'])} · {E(row['award'])}</small><strong>{E(row['name'])}</strong><span>查看项目档案</span></span></a></article>''')
    return ''.join(cards)


def page():
    data = json.loads((ASSETS / 'data-report.json').read_text())
    catalog = json.loads((ASSETS / 'catalog.json').read_text())
    full_catalog = current_catalog(pp.LIB)
    by_id = {row['id']: row for row in full_catalog}
    research_count = sum(1 for row in full_catalog if row.get('research'))
    apps = json.loads((ASSETS.parent / 'application-center/apps.json').read_text())
    summary = data['summary']
    assert len(catalog) == summary['catalog_entries'] == len(full_catalog)
    projects = data['projects']
    gold_count = summary['gold_projects']
    deepening_share = summary['deepening_reports'] / gold_count * 100
    research_share = research_count / len(catalog) * 100
    snapshot = E(data['generated_at'].replace('T', ' ')[:16])
    parts = [f'''<div class="dr-report"><section class="dr-hero" id="data"><header class="dr-heading"><div><span class="gd-kicker">GoodDesign 数据总览</span><h1>看见设计知识，<br>如何持续生长。</h1><p>从真实项目到可追溯档案、设计方法与创新应用，让数据成为下一次创新的起点。</p></div><div class="dr-snapshot"><span>全库构建时统计 · 金奖专项 {snapshot}</span><button class="gd-button" id="print-report" type="button">打印当前视图</button></div></header><div class="dr-view-switch" role="group" aria-label="数据总览视图"><button type="button" data-view="value" aria-pressed="true">数据价值</button><button type="button" data-view="quality" aria-pressed="false">研究质量</button></div></section><div data-view-panel="value"><section class="dr-core-facts" aria-label="全库核心资产"><div><strong>{len(catalog)}</strong><span>真实项目<small>全库公开目录</small></span></div><div><strong>{research_count}</strong><span>原生研究版<small>当前项目库版本</small></span></div><div><strong>{summary['methods']}</strong><span>创新方法<small>可检索方法档案</small></span></div><div><strong>{len(apps)}</strong><span>应用与试点<small>真实使用入口</small></span></div></section><section class="dr-value-chain" aria-label="设计知识价值链"><div><span>01</span><strong>真实项目</strong><small>可追溯的起点</small></div><div><span>02</span><strong>项目档案</strong><small>事实与证据组织</small></div><div><span>03</span><strong>设计方法</strong><small>可复用的路径</small></div><div><span>04</span><strong>创新研究</strong><small>问题与验证连接</small></div><div><span>05</span><strong>场景应用</strong><small>进入真实任务</small></div></section></div><nav class="dr-sections" data-view-nav="value" aria-label="数据价值章节"><a href="#work">项目资产</a><a href="#research">研究覆盖</a><a href="#benchmarks">标杆档案</a><a href="#applications">场景应用</a></nav><nav class="dr-sections" data-view-nav="quality" aria-label="研究质量章节" hidden><a href="#evidence">证据密度</a><a href="#quality">质量状态</a><a href="#methods">方法结构</a><a href="#details">逐案下钻</a></nav><div data-view-panel="value"><section class="dr-section" id="work"><header class="dr-section-heading"><span class="dr-eyebrow">PROJECT ATLAS</span><h2>{len(catalog)} 个真实项目，构成创新的观察样本</h2><p>点击奖项或年份，图表与代表项目同步筛选；当前筛选也可以直接带入项目库。</p></header><div class="dr-asset-toolbar"><p id="asset-filter-status" role="status" aria-live="polite">全部年份 · 全部奖项</p><div><button type="button" id="asset-clear" hidden>清除筛选</button><a id="asset-explore" href="/projects/#collection">在项目库查看</a></div></div><div class="dr-asset-grid">''']
    parts.append(award_chart(catalog) + year_chart(catalog))
    parts.append(f'''</div><div class="dr-showcase" id="asset-projects">{asset_showcase(catalog)}</div><p class="dr-showcase-empty" id="asset-empty" hidden>当前组合没有预置代表封面，请清除一个筛选条件，或进入项目库查看全部结果。</p></section><section class="dr-section" id="research"><header class="dr-section-heading"><span class="dr-eyebrow">RESEARCH COVERAGE</span><h2>研究积累，不只一个总数</h2><p>全库看版本覆盖，金奖专项看证据与字段深度；两种范围分别计算。</p></header><div class="dr-value-research"><article class="dr-coverage-main"><span>全库原生研究版</span><div><strong>{research_count}</strong><small>/ {len(catalog)} 个项目</small></div><svg viewBox="0 0 100 8" role="img" aria-label="全库原生研究版覆盖{research_share:.1f}%"><rect class="dr-hbar-track" width="100" height="8" rx="4"/><rect class="dr-coverage-fill" width="{research_share:.2f}" height="8" rx="4"/></svg><p>当前覆盖 {research_share:.1f}%。研究整理版持续补证，不等同专家审核。</p><div class="dr-gold-coverage"><span>98 个金奖专项</span><b>{summary['published_research']} 个研究版 · {summary['deepening_reports']} 份定向补证</b></div></article><article class="dr-panel"><header class="dr-panel-heading"><div><h3>金奖档案字段深度</h3><p>按每个项目当前已知值字段分档</p></div><strong>{gold_count}<small>案</small></strong></header>{research_depth_chart(projects)}<p class="dr-panel-note">字段数量用于观察研究覆盖，不代表项目技术价值。</p></article></div></section>''')
    benchmarks = []
    for row in sorted(projects, key=lambda item: item['source_entries'], reverse=True):
        public = by_id.get(row['id'])
        if public and public.get('cover'):
            benchmarks.append((row, public))
        if len(benchmarks) == 3:
            break
    benchmark_html = ''.join(f'''<a class="dr-benchmark-card" href="/dossier/?project={E(row['id'])}"><img src="/inno/portal/{E(public['cover'])}" alt="{E(public['name'])}项目封面" loading="lazy"><span><small>{E(public['award'])} · {row['source_entries']} 条项目来源登记</small><strong>{E(public['name'])}</strong><p>{row['known_cells']} 个已知值字段 · {row['records']} 条结构化记录</p><b>阅读研究档案</b></span></a>''' for row, public in benchmarks)
    parts.append(f'''<section class="dr-section" id="benchmarks"><header class="dr-section-heading"><span class="dr-eyebrow">BENCHMARK DOSSIERS</span><h2>从数据回到真实项目</h2><p>代表档案同时保留项目封面、资料规模与研究入口。数量不代表评分，证据可以继续回查。</p></header><div class="dr-benchmarks">{benchmark_html}</div></section><section class="dr-section dr-value-applications" id="applications"><header class="dr-section-heading"><span class="dr-eyebrow">FROM DATA TO ACTION</span><h2>让知识进入真实创新现场</h2><p>数据的价值不止在页面里，而在它被用于研究、验证、展示和学习的时候。</p></header><div><a href="/expo/"><span>地方与产业</span><strong>产业研究与案例对照</strong><small>进入产业看台</small></a><a href="/loop/"><span>企业与园区</span><strong>研究任务与验证计划</strong><small>授权试点</small></a><a href="/museum/"><span>场馆与公众</span><strong>主题展览与项目讲解</strong><small>进入好设计馆</small></a><a href="/museum/#education"><span>学校与教师</span><strong>真实项目与探究学习</strong><small>查看教育内容</small></a></div></section></div>''')
    top = sorted(projects, key=lambda row: row['source_entries'], reverse=True)[:5]
    top_html = ''.join(f'<a class="dr-source-row" href="/dossier/?project={E(row["id"])}"><span><b>{E(row["id"])}</b>{E(row["name"])}</span><strong>{row["source_entries"]}</strong></a>' for row in top)
    parts.append(f'''<div data-view-panel="quality" hidden><section class="dr-professional-head"><span class="dr-eyebrow">98 GOLD AWARD PROJECTS</span><h2>研究质量与证据工作视图</h2><p>以下字段、来源、补证和评分只统计 98 个金奖专项，快照 {snapshot}。评分针对档案内容，不是项目技术价值。</p></section><div class="dr-asset-strip"><div><strong>{number(summary['project_source_entries'])}</strong><span>项目来源登记<small>按项目，不跨项目去重</small></span></div><div><strong>{number(summary['known_cells'])}</strong><span>已知值字段<small>不等同独立验证</small></span></div><div><strong>{number(summary['fact_records'])}</strong><span>结构化记录<small>{gold_count} 金奖当前库</small></span></div><div><strong>{number(summary['deepening_reports'])}</strong><span>定向补证<small>已保存深化报告</small></span></div></div><section class="dr-section" id="evidence"><header class="dr-section-heading"><h2>逐案查看证据与字段密度</h2><p>每个点都是一个真实项目。位置看来源与已知字段，点大小看结构化记录。</p></header><div class="dr-research-grid"><article class="dr-panel dr-scatter-panel"><header class="dr-panel-heading"><div><h3>{gold_count} 案证据密度</h3><p>对数刻度便于同时查看不同量级，点击进入项目档案</p></div><div class="dr-point-legend"><span><i class="dr-point dr-point--base"></i>基础研究</span><span><i class="dr-point dr-point--deep"></i>已定向补证</span></div></header>{evidence_scatter(projects)}</article><aside class="dr-research-side"><div class="dr-coverage"><article><span>基础检索覆盖</span><strong>{summary['basic_coverage']}<small>/ {gold_count}案</small></strong><svg viewBox="0 0 100 6" aria-label="基础检索覆盖100%"><rect class="dr-hbar-track" width="100" height="6" rx="3"/><rect class="dr-hbar-fill" width="100" height="6" rx="3"/></svg></article><article><span>定向补证覆盖</span><strong>{summary['deepening_reports']}<small>/ {gold_count}案</small></strong><svg viewBox="0 0 100 6" aria-label="定向补证覆盖{deepening_share:.1f}%"><rect class="dr-hbar-track" width="100" height="6" rx="3"/><rect class="dr-hbar-fill" width="{deepening_share:.2f}" height="6" rx="3"/></svg><p>深化报告占金奖项目 {deepening_share:.1f}%</p></article></div><article class="dr-panel dr-top-sources"><header class="dr-panel-heading"><div><h3>来源登记较多</h3><p>数量不代表内容评分</p></div></header>{top_html}</article></aside></div></section>''')
    parts.append('<section class="dr-section" id="quality"><header class="dr-section-heading"><h2>覆盖已经形成，质量缺口也要一眼可见</h2><p>独立校准、初评、待补证与待复评分层呈现，不用数量掩盖质量。</p></header><div class="dr-quality-grid">' + quality_chart(data) + score_chart(projects) + '</div></section>')
    parts.append(methods_chart(data))
    parts.append(f'''<section class="dr-section" id="details"><header class="dr-section-heading"><h2>从图表回到每一个项目与方法</h2><p>清单保留版本、补证、评分与具体缺口，支持搜索和分页。</p></header><div class="dr-tabs" role="group" aria-label="数据清单"><button type="button" data-table="projects" aria-pressed="true">{gold_count}个金奖项目</button><button type="button" data-table="methods" aria-pressed="false">{summary['methods']}个创新方法</button></div><label class="dr-search">检索清单<input id="report-search" type="search" placeholder="搜索名称、ID、状态或缺口"></label><p id="detail-count" role="status" aria-live="polite"></p><div class="dr-table-panel" data-panel="projects"><div class="dr-table-scroll"><table><thead><tr><th>项目</th><th>当前版本</th><th>基础 / 深化</th><th>内容分数</th><th>评估状态与缺口</th></tr></thead><tbody>''')
    for row in projects:
        parts.append(f'<tr data-quality="{E(row["quality_status"])}"><td><small>{E(row["id"])}</small><a href="/dossier/?project={E(row["id"])}">{E(row["name"])}</a></td><td>{E(row["revision"] or "未发布")}</td><td>基础检索已保存<br>{"定向报告已保存" if row["deepening"] else "待定向补证"}</td><td>{E(row["score"] if row["score"] is not None else "未评 / 待复评")}</td><td><b>{E(row["quality_status"])}</b><p>{E("；".join(row["gaps"][:2]))}</p></td></tr>')
    parts.append('</tbody></table></div></div><div class="dr-table-panel" data-panel="methods" hidden><div class="dr-table-scroll"><table><thead><tr><th>方法</th><th>版本 / 分类</th><th>基线内容分数</th><th>状态与下一步</th></tr></thead><tbody>')
    for row in data['methods']:
        parts.append(f'<tr><td><small>{E(row["id"])}</small><a href="/methods/methods/{E(row["id"])}.html">{E(row["name"])}</a></td><td>{E(row["version"])}<br>{E(row["category"])}</td><td>{E(row["score"] if row["score"] is not None else "未评")}</td><td><b>{E(row["quality_status"])}</b><p>{E("；".join(row["gaps"]))}</p></td></tr>')
    parts.append('</tbody></table></div></div><div class="pp-pagination"><button type="button" id="detail-prev">上一页</button><span id="detail-page"></span><button type="button" id="detail-next">下一页</button></div></section></div>')
    parts.append('<details class="dr-scope" id="next"><summary>数据口径与后续重点</summary><div><p>全库项目、原生研究版、方法与应用数量按构建时真源统计；项目字段、来源、补证与质量状态使用98金奖专项快照。两套范围不互相替代。</p><p>' + E(data['scope']) + ' 来源按项目登记，不跨项目去重；已知值不等于独立验证，检索报告不等于内容审核入档。</p><p>' + E(data['quality_notice']) + '</p><ol>' + ''.join('<li>' + E(item) + '</li>' for item in data['next_actions']) + '</ol><p>本页为按实际记录生成的汇报快照，并非实时监控。数据刷新不自动更新原始评估或提升分数。</p></div></details></div>')
    asset_version = hashlib.sha256((ASSETS / 'data-report.css').read_bytes() + (ASSETS / 'data-report.js').read_bytes()).hexdigest()[:8]
    assets = f'<link rel="stylesheet" href="/inno/portal/data-report.css?v={asset_version}"><script src="/inno/portal/data-report.js?v={asset_version}"></script>'
    return shell('数据总览', ''.join(parts), assets, active='report', description='好设计数据总览：从真实项目、原生研究版、设计方法与创新应用，查看数据价值、研究覆盖和可追溯质量状态。')
