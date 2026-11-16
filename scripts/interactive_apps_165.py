import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value), quote=True)


def page(app, title, description, body, data=False):
    play_data = '<script src="/inno/legacy/js/play-data.js"></script>' if data else ''
    return f'''<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(description)}"><title>{esc(title)} · 好设计馆</title><link rel="stylesheet" href="/inno/portal/interactive-apps.css?v=165"></head><body class="ia-page" data-app="{app}"><main id="main">{body}</main>{play_data}<script src="/inno/portal/{app}.js?v=165" defer></script></body></html>'''


def lab():
    body = '''<header class="ia-hero"><p>GOODDESIGN LAB · 极限实验室</p><h1>做一次实验，<br>看见设计如何权衡。</h1><span>调整转速、进给和冲击，观察样芯、设备风险与能耗的变化。教学模拟，结果不代表工程精确或实际验证。</span></header>
<section class="ia-lab-grid" aria-label="嫦娥钻取实验">
  <div class="ia-stage"><div class="ia-stage-head"><span>月壤剖面 · 钻进作业</span><strong id="lab-status" aria-live="polite">准备就绪</strong></div><svg id="lab-scene" viewBox="0 0 420 340" role="img" aria-label="钻具穿过五层月壤与未知岩块"></svg><div class="ia-timeline"><span id="lab-progress"></span></div><div class="ia-stage-actions"><button class="ia-primary" id="lab-start" type="button">开始钻进</button><button id="lab-pause" type="button" disabled>暂停</button><button id="lab-reset" type="button">复位</button></div></div>
  <aside class="ia-controls"><p class="ia-eyebrow">实验参数</p><label>钻头转速 <output id="lab-rpm-value">180 rpm</output><input id="lab-rpm" type="range" min="60" max="300" value="180" step="10"></label><label>进给速度 <output id="lab-feed-value">8 mm/s</output><input id="lab-feed" type="range" min="2" max="20" value="8" step="1"></label><fieldset><legend>冲击功率</legend><div class="ia-segment" id="lab-hit"><button type="button" data-value="0" aria-pressed="false">低</button><button type="button" data-value="1" aria-pressed="true">中</button><button type="button" data-value="2" aria-pressed="false">高</button></div></fieldset><div class="ia-live"><span>当前策略</span><p id="lab-strategy">转速、进给和冲击保持均衡。</p><div><small>样芯完整</small><strong id="lab-core">92%</strong><small>设备风险</small><strong id="lab-risk">24%</strong><small>能耗压力</small><strong id="lab-energy">66%</strong></div></div></aside>
</section>
<section class="ia-review" id="lab-review" aria-labelledby="lab-review-title"><div class="ia-section-head"><div><p class="ia-eyebrow">EXPERIMENT REVIEW</p><h2 id="lab-review-title">实验复盘</h2></div><button id="lab-export" type="button" disabled>导出观察卡</button></div><div id="lab-runs" class="ia-run-list"><p class="ia-empty">完成一次钻进后，这里会保留结果。再完成一次，就能比较两种策略。</p></div></section>'''
    return page('lab', '极限实验室', '通过可暂停的钻取实验和A/B复盘理解设计权衡', body)


def quest():
    body = '''<header class="ia-hero ia-hero-compact"><p>GOODDESIGN QUEST · 观展任务</p><h1>沿着线索，<br>解锁八件国之重器。</h1><span>每关先看线索，再完成两个判断。答案和解释都来自真实项目资料。</span><div class="ia-progress-label"><span id="quest-progress" aria-live="polite">已解锁 1 / 8</span><button id="quest-export" type="button">导出任务单</button></div></header>
<section class="ia-quest-grid"><nav class="ia-quest-map" id="quest-map" aria-label="八关任务地图"></nav><div class="ia-quest-current" id="quest-current"><p class="ia-empty">选择第一关，开始观展任务。</p></div></section>'''
    return page('quest', '观展任务', '通过八关线索探索与判断解锁真实项目', body, data=True)


def studio():
    catalog = json.loads((ROOT / 'extensions/project-portal/catalog.json').read_text())
    ids = ['2025-00', '2015-02', '2015-00', '2021-01', '2024-03', '2024-02']
    projects = [{'id': row['id'], 'name': row['name'], 'cover': '/inno/portal/' + row['cover']} for row in catalog if row['id'] in ids]
    projects_json = json.dumps(projects, ensure_ascii=False).replace('<', '\\u003c')
    options = ''.join(f'<option value="{esc(project["id"])}">{esc(project["name"])}</option>' for project in projects)
    body = f'''<header class="ia-hero ia-hero-compact"><p>GOODDESIGN STUDIO · 设计创作室</p><h1>把灵感，<br>做成一张自己的作品。</h1><span>选择真实项目，写下你要解决的问题。作品只保存在本机，也可以导出图片或生成分享链接。</span></header>
<section class="ia-studio-grid"><form class="ia-editor" id="studio-form"><p class="ia-eyebrow">创作设置</p><label>灵感项目<select id="studio-project">{options}</select></label><label>设计名称<input id="studio-name" maxlength="18" value="我的极限设计" required></label><label>它解决什么问题？<textarea id="studio-problem" maxlength="70" rows="3" placeholder="例如：怎样让户外设备在极端环境中更可靠？"></textarea></label><label>设计说明<textarea id="studio-desc" maxlength="140" rows="5" placeholder="写下你的设计思路、取舍和需要继续验证的地方。"></textarea></label><fieldset><legend>作品色调</legend><div class="ia-theme-picker" id="studio-theme"><button type="button" data-value="ocean" aria-pressed="true">深海蓝</button><button type="button" data-value="graphite" aria-pressed="false">石墨黑</button><button type="button" data-value="coral" aria-pressed="false">珊瑚红</button></div></fieldset><label>标题大小 <output id="studio-size-value">44px</output><input id="studio-size" type="range" min="30" max="64" value="44"></label><div class="ia-editor-actions"><button class="ia-primary" id="studio-save" type="button">保存草稿</button><button id="studio-new" type="button">重新创作</button></div><p class="ia-form-status" id="studio-status" aria-live="polite"></p></form><div class="ia-preview-wrap"><div class="ia-preview" id="studio-preview" data-theme="ocean"><img id="studio-image" alt="作品项目背景"><div class="ia-preview-shade"></div><div class="ia-preview-content"><p id="studio-project-name"></p><h2 id="studio-title" title="拖动调整标题位置">我的极限设计</h2><p id="studio-problem-preview">拖动标题可以调整位置</p><p id="studio-description">你的设计说明会出现在这里。</p></div><small>GoodDesign Studio · 概念作品，未经工程验证</small></div><div class="ia-preview-actions"><button class="ia-primary" id="studio-export" type="button">导出 PNG</button><button id="studio-share" type="button">生成分享链接</button></div></div></section><script type="application/json" id="studio-projects">{projects_json}</script>'''
    return page('studio', '设计创作室', '用真实项目图片创作、编辑、保存并导出设计作品', body)


def transfer():
    body = '''<header class="ia-hero ia-hero-compact"><p>GOODDESIGN TRANSFER · 迁移研究所</p><h1>从项目证据，<br>走到可验证的新方向。</h1><span>不是自动推荐，而是把可借鉴机制、目标问题、差异和验证步骤放在同一张研究图上。</span></header>
<section class="ia-transfer-flow" aria-label="迁移研究步骤"><span data-step="1" aria-current="step">01 选择机制</span><span data-step="2">02 定义问题</span><span data-step="3">03 形成验证</span></section>
<section class="ia-transfer-grid" id="transfer-step-1"><div><p class="ia-eyebrow">选择真实项目</p><div class="ia-choice-list" id="transfer-project"></div></div><div><p class="ia-eyebrow">选择可借鉴机制</p><div class="ia-choice-list" id="transfer-mechanism"></div></div></section>
<section class="ia-transfer-define" id="transfer-step-2" hidden><div><p class="ia-eyebrow">目标产业</p><div class="ia-choice-list ia-industries" id="transfer-industry"></div></div><label>你的真实问题<textarea id="transfer-problem" rows="5" placeholder="例如：我们的户外机器人需要在复杂地形中稳定作业，但现有结构能耗高、维护困难。"></textarea></label><p class="ia-form-status" id="transfer-status" aria-live="polite"></p><button class="ia-primary" id="transfer-review" type="button">形成双侧映射</button></section>
<section class="ia-transfer-result" id="transfer-step-3" hidden><div class="ia-section-head"><div><p class="ia-eyebrow">EVIDENCE → APPLICATION</p><h2>迁移假设与验证计划</h2></div><div><button id="transfer-copy" type="button">复制研究上下文</button><button class="ia-primary" id="transfer-export" type="button">导出并进入需求研究</button></div></div><div id="transfer-map"></div></section>'''
    return page('transfer', '迁移研究所', '从真实项目机制形成差异明确的迁移假设和验证计划', body, data=True)


def playground():
    cards = (
        ('/lab/', '极限实验室', '调参数、看过程、做复盘', '通过钻取实验理解设计权衡'),
        ('/quest/', '观展任务', '看线索、做判断、解锁项目', '用八关探索建立真实设计认知'),
        ('/studio/', '设计创作室', '选项目、写问题、做作品', '把灵感编成可导出的设计作品'),
        ('/transfer/', '迁移研究所', '找机制、看差异、做验证', '把项目证据转成研究假设'),
    )
    body = '<header class="ia-hero ia-hero-compact"><p>互动学习 · GOODDESIGN PLAYGROUND</p><h1>选择一种方式，<br>继续理解设计。</h1><span>四个独立应用，分别对应实验、探索、创作和迁移研究。</span></header><section class="ia-app-choices">' + ''.join(f'<a href="{href}"><span>{esc(kicker)}</span><h2>{esc(title)}</h2><p>{esc(desc)}</p><strong>进入应用</strong></a>' for href, title, kicker, desc in cards) + '</section><script>const tab=new URLSearchParams(location.search).get("tab");const routes={experiment:"/lab/",questline:"/quest/",create:"/studio/",migrate:"/transfer/"};if(routes[tab])location.replace(routes[tab]+location.search);</script>'
    return f'''<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="选择极限实验室、观展任务、设计创作室或迁移研究所"><title>互动学习 · 好设计馆</title><link rel="stylesheet" href="/inno/portal/interactive-apps.css?v=165"></head><body class="ia-page"><main id="main">{body}</main></body></html>'''


RENDERERS = {'lab': lab, 'quest': quest, 'studio': studio, 'transfer': transfer, 'playground': playground}
