import json

CSS = '''
.model-explorer{display:grid;grid-template-columns:minmax(0,.88fr) minmax(0,1.12fr);gap:42px;align-items:center;margin:34px 0 42px}.model-intro{max-width:520px}.model-intro h2{margin:12px 0 18px;font-size:clamp(30px,3.4vw,44px);line-height:1.22;letter-spacing:-.04em;text-wrap:balance}.model-intro p{max-width:500px;color:var(--fg2);font-size:16px;line-height:1.85}.model-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:24px}.model-actions a{display:inline-flex;align-items:center;min-height:44px;padding:9px 16px;border:1px solid var(--bdrSoft);border-radius:99px;background:var(--card);font-size:var(--fs-caption)}.model-actions a:first-child{background:var(--accent);color:white;border-color:var(--accent)}.model-facts{display:flex;flex-wrap:wrap;gap:18px;margin-top:28px;color:var(--fg2);font-size:var(--fs-xs)}.model-facts strong{margin-right:4px;color:var(--fg);font-size:20px;font-weight:500}.model-map{overflow:hidden;border:1px solid #292b38;border-radius:24px;background:#181a22;color:#f4f4f8;box-shadow:0 18px 50px -34px rgb(15 17 28 / 65%)}.model-map-head{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:20px 22px;border-bottom:1px solid rgb(255 255 255 / 9%)}.model-map-head strong{font-size:13px;font-weight:500}.model-map-head span{color:#a6aabc;font-size:11px}.model-chain{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));padding:14px 14px 4px}.model-step{min-width:0;min-height:112px;padding:16px 12px;border:1px solid transparent;border-radius:14px;background:transparent;color:#c4c8d8;text-align:left;position:relative}.model-step:before{content:'';position:absolute;left:12px;right:12px;top:26px;height:1px;background:rgb(255 255 255 / 10%)}.model-step span{display:block;margin-bottom:16px;color:#949bb5;font-size:10px}.model-step strong{display:block;font-size:16px;font-weight:500;line-height:1.45}.model-step small{display:block;margin-top:8px;color:#a6aabc;font-size:11px;line-height:1.55}.model-step[aria-pressed=true]{border-color:rgb(165 180 252 / 35%);background:rgb(165 180 252 / 10%);color:#fff}.model-step[aria-pressed=true] span{color:#c7d0fe}.model-step:hover{background:rgb(255 255 255 / 5%)}.model-detail{margin:14px;padding:20px;border:1px solid rgb(255 255 255 / 9%);border-radius:16px;background:rgb(255 255 255 / 5%)}.model-detail-kicker{display:block;margin-bottom:10px;color:#b3bbdc;font-size:11px}.model-detail h3{margin:0 0 10px;color:#f4f4f8;font-size:20px;line-height:1.45}.model-detail p{margin:0;color:#b7bdd0;font-size:13px;line-height:1.8}.model-detail a{display:inline-flex;margin-top:14px;color:#c7d0fe;font-size:13px}.model-map-note{padding:0 22px 18px;color:#9299ae;font-size:11px;line-height:1.6}@media(max-width:1050px){.model-explorer{grid-template-columns:1fr;gap:26px}.model-intro{max-width:720px}.model-intro p{max-width:680px}}@media(max-width:640px){.model-chain{grid-template-columns:repeat(2,minmax(0,1fr))}.model-step{min-height:104px;padding:12px 10px}.model-map-head{padding:16px}.model-detail{margin:10px}.model-intro h2{font-size:32px}.model-facts{gap:12px}}@media print{.model-explorer{display:block}.model-map{color:#181a22;background:white;border-color:#ddd;box-shadow:none}.model-step,.model-detail{color:#181a22}.model-step span,.model-step small,.model-detail p,.model-map-note{color:#555}.model-actions{display:none}}
'''

DETAILS = {
    'evidence': {
        'kicker': '真实项目证据', 'title': '45条记录，180个有值事实字段',
        'text': '每一条事实都绑定来源、原文位置和研究版本。申报、论文实验、媒体报道和后续产业化分别保存。',
        'label': '阅读079项目档案', 'route': '/dossier/?project=2019-s19',
    },
    'method': {
        'kicker': '方法组织研究', 'title': 'R48、R14、R17形成分析路径',
        'text': '问题定义、功能分解和形态组合用于组织研究，不把方法名称当成项目实际采用证明。',
        'label': '查看创新方法库', 'route': '/methods/',
    },
    'research': {
        'kicker': '研究过程可追溯', 'title': '42条带边界AI分析',
        'text': '事实与AI分析分层，保留适用条件、限制和待补证据。质量未评、专家未审，不生成无依据的迁移结论。',
        'label': '进入需求研究', 'route': '/needs/',
    },
    'application': {
        'kicker': '连接真实应用', 'title': '需求研究、企业创新与MCP',
        'text': '同一研究版本可以进入需求简报、企业验证任务和Agent研究上下文，不复制成第二份数据。',
        'label': '查看应用案例', 'route': '/cases/pump-079/',
    },
}


def explorer():
    steps = ''.join(f'<button class="model-step" type="button" data-model-step="{key}" aria-pressed="{str(index == 0).lower()}"><span>0{index + 1}</span><strong>{title}</strong><small>{subtitle}</small></button>' for index, (key, title, subtitle) in enumerate([
        ('evidence', '证据', '45记录 · 180事实'),
        ('method', '方法', 'R48 · R14 · R17'),
        ('research', '研究', '42条AI分析'),
        ('application', '应用', '需求 · 企业 · MCP'),
    ]))
    return f'''<style>{CSS}</style><section class="model-explorer" aria-labelledby="model-explorer-title"><div class="model-intro"><span class="gd-kicker">创新设计大模型</span><h2 id="model-explorer-title">把项目证据，变成可执行的创新研究。</h2><p>不是聊天页面，也不是基础模型演示。以真实项目档案数据库为底座，把方法、研究Agent和验证反馈连成一条可追溯的创新路径。</p><div class="model-actions"><a href="/model/">了解模型定义</a><a href="/apps/">查看真实应用</a></div><div class="model-facts"><span><strong>560</strong>项目目录</span><span><strong>103</strong>原生研究版</span><span><strong>64</strong>方法档案</span><span><strong>8</strong>只读工具</span></div></div><figure class="model-map" aria-label="079真实研究路径"><div class="model-map-head"><strong>079 / 6000HP电动压裂泵</strong><span>research-000001</span></div><div class="model-chain" role="group" aria-label="选择研究路径">{steps}</div><div class="model-detail" aria-live="polite"><span class="model-detail-kicker" id="model-detail-kicker">真实项目证据</span><h3 id="model-detail-title">45条记录，180个有值事实字段</h3><p id="model-detail-text">每一条事实都绑定来源、原文位置和研究版本。申报、论文实验、媒体报道和后续产业化分别保存。</p><a id="model-detail-link" href="/dossier/?project=2019-s19">阅读079项目档案</a></div><p class="model-map-note">真实研究数据，不是模型执行进度。点击四层查看各自证据和入口。</p></figure></section><script>const modelDetails={json.dumps(DETAILS, ensure_ascii=False)};document.querySelectorAll('[data-model-step]').forEach(button=>button.addEventListener('click',()=>{{const item=modelDetails[button.dataset.modelStep];document.querySelectorAll('[data-model-step]').forEach(step=>step.setAttribute('aria-pressed',String(step===button)));document.getElementById('model-detail-kicker').textContent=item.kicker;document.getElementById('model-detail-title').textContent=item.title;document.getElementById('model-detail-text').textContent=item.text;const link=document.getElementById('model-detail-link');link.href=item.route;link.textContent=item.label}}))</script>'''
