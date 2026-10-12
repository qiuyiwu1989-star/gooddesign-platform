'use strict';

let data;
let step = 0;
let track = 'process';
let note = '';
let report = '';
let reportHtml = '';
let playing = false;
let paused = false;
let timer = null;

const names = ['识别企业', '调研画像', '提出问题', '匹配融合', '生成报告'];
const hints = ['确认主体与边界', '读取公开资料', '形成研究问题', '连接项目机制', '输出网页简报'];
const panel = document.getElementById('panel');
const status = document.getElementById('status');
const flow = document.getElementById('flow');
const signal = document.getElementById('signal');

const escape = s => String(s).replace(/[&<>"']/g, c => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;'
}[c]));

function selected() {
  return data.tracks.find(t => t.id === track);
}

function casesFor(t = selected()) {
  return t.cases.map(id => data.cases.find(x => x.id === id)).filter(Boolean);
}

function line(i, text, state) {
  return `<div class="flow-line ${state || ''}"><span>0${i + 1}</span><p>${text}</p></div>`;
}

function events() {
  const t = selected();
  const c = casesFor(t);
  return [
    '企业主体已识别：双环传动与机器人传动方向',
    `企业画像已形成：${data.companyProfile.capabilities.slice(0, 3).join('、')}`,
    `研究问题池已生成：${data.researchQuestions.length} 个问题，当前聚焦 ${t.title}`,
    `已匹配 ${c.length} 个好设计项目：${c.map(x => x.id).join('、')}`,
    '已生成网页研究简报：含问题来源、匹配证据、验证路径和边界'
  ];
}

function metrics() {
  const t = selected();
  return t.metrics.split('、').slice(0, 5).map(x => `<span>${escape(x.replace(/[；。].*$/, ''))}</span>`).join('');
}

function processing(label, items) {
  return `<div class="processing-card"><div><b>${escape(label)}</b><span>模拟深度研究处理中</span></div>${items.map((x, i) => `<p style="--i:${i}">${escape(x)}</p>`).join('')}</div>`;
}

function caseCard(id) {
  const c = data.cases.find(x => x.id === id);
  return `<article class="evidence reveal">
    <span class="tag">库内档案 · ${c.year} ${c.level}</span>
    <h3><a href="/project/${id}.html" target="_blank" rel="noopener">${escape(c.name)} ↗</a></h3>
    <p class="meta">${escape(c.unit)}</p>
    <blockquote>${escape(c.excerpt.slice(0, 240))}...</blockquote>
    <p><b>可借鉴的视角：</b>${escape(c.insight)}</p>
  </article>`;
}

function questionCard(q, i) {
  return `<article class="question-card reveal" style="--i:${i}">
    <small>问题 0${i + 1}</small>
    <h3>${escape(q.title)}</h3>
    <p>${escape(q.question)}</p>
    <dl>
      <dt>来源</dt><dd>${escape(q.source)}</dd>
      <dt>原因</dt><dd>${escape(q.why)}</dd>
    </dl>
  </article>`;
}

function plainReport() {
  const t = selected();
  const c = casesFor(t);
  return `好设计 × 双环｜企业创新研究网页简报
研究快照：${data.date}
状态：预置研究 Demo；不是实时调研结果；不是企业确认方案

一、企业画像
${data.companyProfile.facts.map((x, i) => `${i + 1}. ${x}`).join('\n')}

二、当前研究方向
${t.title}
${t.question}

三、问题来源
${data.researchQuestions.map((x, i) => `${i + 1}. ${x.title}：${x.source} 原因：${x.why}`).join('\n')}

四、匹配项目
${c.map(x => `${x.name}（${x.year} ${x.level}）\n${x.insight}\nhttps://gooddesign.qiuyiwu.com/project/${x.id}.html`).join('\n\n')}

五、融合逻辑
${t.bridge}
${t.matches.map((x, i) => `${i + 1}. ${x}`).join('\n')}

六、研究假设
${t.hypothesis}

七、需补资料
${t.missing}
用户补充（未经核验）：${note || '未补充'}

八、验证方案
${t.experiment}

九、观察指标
${t.metrics}

十、边界
${t.limit}

十一、下一步
1. 企业确认真实问题和约束。
2. 补充样件、工况、客户集成和质量数据。
3. 选择一个低风险验证课题。
4. 形成课题卡、样件验证方案和评审材料。

公开来源
${data.sources.map(s => `${s.title} ${s.url}`).join('\n')}`;
}

function htmlReport() {
  const t = selected();
  const c = casesFor(t);
  const section = (title, body) => `<section><h2>${escape(title)}</h2>${body}</section>`;
  return `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>双环传动精密传动创新机会研究报告</title>
<style>
body{margin:0;background:#F7F2E8;color:#0E1218;font:16px/1.8 -apple-system,BlinkMacSystemFont,"Noto Sans SC",sans-serif}
main{max-width:1120px;margin:auto;padding:48px 28px}
h1,h2{font-family:"Noto Serif SC",serif;letter-spacing:.03em}h1{font-size:46px;line-height:1.12}h2{font-size:24px;margin-top:34px}
.hero{background:linear-gradient(180deg,#0E1F4D,#1A3A7A);color:white;border-radius:18px;padding:40px}.hero p{color:rgba(255,255,255,.78);max-width:760px}
.kpis,.grid,.route{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.kpis div,.card,.route div{background:#fffdf7;border:1px solid rgba(14,18,24,.14);border-radius:14px;padding:18px}
.kpis b{display:block;font-size:28px;color:#D4A858}
section{background:#fffdf7;border:1px solid rgba(14,18,24,.14);border-radius:14px;padding:24px;margin:18px 0}
li{margin:8px 0}.meta{color:#5C6577}
.card{background:#F7F2E8;border-left:4px solid #D4A858}
.matrix{display:grid;grid-template-columns:1fr 42px 1fr 42px 1fr;align-items:stretch;margin:18px 0}
.matrix div{background:#F7F2E8;border:1px solid rgba(14,18,24,.14);border-radius:12px;padding:16px}.matrix span{display:grid;place-items:center;color:#D4A858;font-size:30px}
a{color:#2D4FAF}@media(max-width:820px){.grid,.kpis,.route,.matrix{grid-template-columns:1fr}.matrix span{height:24px;transform:rotate(90deg)}h1{font-size:32px}}
</style><main>
<div class="hero"><p>GOOD DESIGN × SHUANGHUAN</p><h1>双环传动精密传动创新机会研究报告</h1><p>围绕双环传动与机器人精密传动场景，基于公开企业资料和好设计项目证据，形成问题来源、案例匹配、迁移机制、验证路径和风险边界。</p><p>研究快照：${escape(data.date)}。本报告为预置研究 Demo 输出，需由企业补充资料后继续核验。</p></div>
<div class="kpis"><div><b>4</b><p>企业公开事实层</p></div><div><b>${data.researchQuestions.length}</b><p>双环相关研究问题</p></div><div><b>${c.length}</b><p>本轮重点匹配案例</p></div></div>
${section('一、企业画像', `<ul>${data.companyProfile.facts.map(x => `<li>${escape(x)}</li>`).join('')}</ul>`)}
${section('二、当前研究方向', `<div class="card"><h3>${escape(t.title)}</h3><p>${escape(t.question)}</p></div>`)}
${section('三、问题来源', `<div class="grid">${data.researchQuestions.map((x, i) => `<div class="card"><b>0${i + 1} ${escape(x.title)}</b><p>${escape(x.question)}</p><p class="meta">来源：${escape(x.source)}</p><p>${escape(x.why)}</p></div>`).join('')}</div>`)}
${section('四、匹配项目', c.map(x => `<div class="card"><h3>${escape(x.name)}</h3><p>${escape(x.year)} ${escape(x.level)} ｜ ${escape(x.unit)}</p><p>${escape(x.insight)}</p><p><a href="https://gooddesign.qiuyiwu.com/project/${x.id}.html">查看项目档案</a></p></div>`).join(''))}
${section('五、融合逻辑', `<div class="matrix"><div><b>企业问题</b><p>${escape(t.question)}</p></div><span>›</span><div><b>项目证据</b><p>${escape(c.map(x=>x.name).join(' / '))}</p></div><span>›</span><div><b>研究假设</b><p>${escape(t.hypothesis)}</p></div></div><p>${escape(t.bridge)}</p><ol>${t.matches.map(x => `<li>${escape(x)}</li>`).join('')}</ol>`)}
${section('六、需补资料与验证方案', `<p><b>需补资料：</b>${escape(t.missing)}</p><p><b>用户补充：</b>${escape(note || '未补充')}</p><p><b>验证方案：</b>${escape(t.experiment)}</p><p><b>观察指标：</b>${escape(t.metrics)}</p>`)}
${section('七、建议推进路线', `<div class="route"><div><b>第一步：确认对象</b><p>选定一个零件、客户任务或机器人关节场景，明确不可变约束。</p></div><div><b>第二步：建立对照</b><p>整理现工艺、现接口或现选型方法，形成基线。</p></div><div><b>第三步：小试验证</b><p>用低风险样件或任务验证假设，不直接承诺量产替代。</p></div></div><p><b>边界：</b>${escape(t.limit)}</p>`)}
${section('公开来源', `<ul>${data.sources.map(s => `<li><a href="${escape(s.url)}">${escape(s.title)}</a></li>`).join('')}</ul>`)}
</main></html>`;
}

function paintFlow() {
  const e = events();
  flow.innerHTML = e.map((x, i) => line(i, x, i < step ? 'done' : i === step ? 'active' : '')).join('');
  signal.innerHTML = `<p><b>${names[step]}</b></p><p>${hints[step]}</p><small>${step < 4 ? '系统正在组织下一层证据' : '可以下载网页简报或打印 PDF'}</small>`;
  document.getElementById('steps').innerHTML = names.map((n, i) => `<button data-step="${i}" ${i === step ? 'aria-current="step"' : ''} ${i > step ? 'disabled' : ''}><span>0${i + 1}</span><b>${n}</b><small>${hints[i]}</small></button>`).join('');
  document.querySelectorAll('[data-step]').forEach(b => {
    b.onclick = () => {
      step = +b.dataset.step;
      stopAuto();
      render();
    };
  });
}

function render() {
  status.textContent = '';
  paintFlow();
  document.getElementById('prev').disabled = step === 0;
  document.getElementById('next').textContent = step === 4 ? '重新开始' : '推进下一步';
  const t = selected();

  if (step === 0) {
    panel.innerHTML = `<p class="label">01 / 企业识别</p><h2>先确认企业主体和演示边界。</h2><p>平台先识别企业，再明确当前 Demo 只配置了双环公开资料、环动科技公开资料和好设计库内案例。</p>${processing('企业识别', ['读取企业名称', '确认业务边界', '标注资料可信层级'])}<label for="company">企业名称</label><input id="company" type="text" value="浙江双环传动机械股份有限公司"><div class="identity-card reveal"><div><small>ENTERPRISE</small><b>双环传动</b><p>齿轮及部组件研发、制造与销售</p></div><div><small>RELATED BUSINESS</small><b>环动科技</b><p>机器人高精密减速器业务线索</p></div><div><small>DEMO BOUNDARY</small><b>公开资料</b><p>未接入内部工艺、客户和质量数据</p></div></div><label class="check"><input id="confirm" type="checkbox"> 我确认以双环及机器人传动方向演示</label>`;
  }

  if (step === 1) {
    panel.innerHTML = `<p class="label">02 / 调研与了解企业</p><h2>形成一张可审核的企业画像。</h2><p>这一页把公开事实、能力标签、待核实问题分开，让现场观众能看到系统不是只给结论，而是在整理证据。</p>${processing('企业调研', ['抽取公开事实', '归纳能力标签', '生成待核实问题', '建立产业语境'])}<div class="research-grid profile-grid"><section><h3>公开事实</h3><ul>${data.companyProfile.facts.map(x => `<li>${escape(x)}</li>`).join('')}</ul></section><section><h3>能力标签</h3><div class="tag-cloud">${data.companyProfile.capabilities.map(x => `<span>${escape(x)}</span>`).join('')}</div></section><section><h3>资料来源</h3>${data.sources.map(s => `<p class="source-chip"><a href="${s.url}" target="_blank" rel="noopener">${escape(s.title)} ↗</a></p>`).join('')}</section><section class="portrait"><span>画像摘要</span><p>传动部件</p><p>机器人减速器</p><p>新能源汽车和工业场景</p><p>未来工厂和质量全周期</p><p>待补内部工况和样件数据</p></section></div><div class="scanner"><span></span><p>正在把企业公开资料转成能力、问题、证据和验证边界</p></div>`;
  }

  if (step === 2) {
    panel.innerHTML = `<p class="label">03 / 企业研究问题</p><h2>生成问题池，再选择一个方向深挖。</h2><p>每个问题都标注来源和提出原因，避免让观众感觉问题是凭空生成的。</p>${processing('问题生成', ['从企业画像抽取矛盾', '从好设计案例寻找类比机制', '检查资料缺口', '形成可验证课题'])}<div class="question-list">${data.researchQuestions.map(questionCard).join('')}</div><h3>选择本轮演示聚焦方向</h3><div class="problem-grid">${data.tracks.map(x => `<label class="choice"><input type="radio" name="track" value="${x.id}" ${track === x.id ? 'checked' : ''}><strong>${escape(x.title)}</strong><div>${escape(x.question)}</div><small>需补资料：${escape(x.missing.split('、').slice(0, 4).join(' / '))}</small></label>`).join('')}</div><label for="note">现场补充目标与约束</label><textarea id="note" placeholder="例如：不能改变现有热处理工艺；先评估小批量试验投入。">${escape(note)}</textarea>`;
    document.querySelectorAll('[name=track]').forEach(x => x.onchange = () => {
      track = x.value;
      paintFlow();
    });
    document.getElementById('note').oninput = e => note = e.target.value;
  }

  if (step === 3) {
    panel.innerHTML = `<p class="label">04 / 匹配效果与知识融合</p><h2>${escape(t.title)}</h2><p>这里不只是匹配案例名称，而是展示企业问题、项目证据、迁移机制和验证边界之间的关系。</p>${processing('匹配融合', ['检索好设计项目库', '提取可迁移机制', '排除不能直接外推的结论', '生成验证假设'])}<div class="fusion-map"><div><small>企业问题</small><b>${escape(t.question)}</b></div><span></span><div><small>好设计证据</small><b>${escape(t.cases.join(' + '))}</b></div><span></span><div><small>融合假设</small><b>${escape(t.hypothesis)}</b></div></div><div class="match-board"><section><h3>迁移依据</h3><ol>${t.matches.map(x => `<li>${escape(x)}</li>`).join('')}</ol></section><section><h3>需补数据</h3><p>${escape(t.missing)}</p><h3>评价指标</h3><div class="metric-row">${metrics()}</div></section></div>${t.cases.map(caseCard).join('')}<p class="notice">${escape(t.limit)}</p>`;
  }

  if (step === 4) {
    report = plainReport();
    reportHtml = htmlReport();
    panel.innerHTML = `<p class="label">05 / 报告生成</p><h2>生成可下载的网页研究简报。</h2><p>最后输出不是一个简单匹配结果，而是一份能继续讨论、下载、打印和交给企业确认的网页报告。</p>${processing('报告生成', ['汇总企业画像', '写入问题来源', '整理匹配证据', '形成验证路线', '标注边界与下一步'])}<div class="report-board reveal"><section><small>方向</small><b>${escape(t.title)}</b><p>${escape(t.question)}</p></section><section><small>问题来源</small><b>${data.researchQuestions.length} 个问题池</b><p>来自公开企业画像、好设计案例机制和待核实资料缺口。</p></section><section><small>融合逻辑</small><b>${escape(t.bridge)}</b><p>${escape(t.hypothesis)}</p></section><section><small>最小验证</small><b>先小试，再判断</b><p>${escape(t.experiment)}</p></section><section><small>评价指标</small><b>可量化检查</b><p>${escape(t.metrics)}</p></section><section><small>边界</small><b>需企业确认</b><p>${escape(t.limit)}</p></section></div><div class="report-actions"><button id="download-html">下载网页报告 .html</button><button id="download">下载文本简报 .txt</button><button id="print">打印 / 保存 PDF</button><a class="link-button" href="workspace.html">进入课题工作台</a><a class="link-button" href="live.html">切到现场研究 Agent</a></div><iframe class="report-preview" title="网页报告预览"></iframe><details open><summary>文本报告备份</summary><pre>${escape(report)}</pre></details>`;
    const iframe = panel.querySelector ? panel.querySelector('iframe') : null;
    if (iframe) iframe.srcdoc = reportHtml;
    document.getElementById('download').onclick = () => downloadBlob(report, '好设计-双环-' + track + '.txt', 'text/plain;charset=utf-8');
    document.getElementById('download-html').onclick = () => downloadBlob(reportHtml, '好设计-双环-企业创新研究简报.html', 'text/html;charset=utf-8');
    document.getElementById('print').onclick = () => window.print();
  }
}

function downloadBlob(content, filename, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function validateStep() {
  if (step !== 0) return true;
  const company = document.getElementById('company');
  const confirm = document.getElementById('confirm');
  const value = company.value.trim();
  const isShuanghuan = ['双环', '双环传动', '浙江双环传动机械股份有限公司', '双环企业'].includes(value) || value.includes('双环');
  if (!isShuanghuan) {
    status.textContent = '本 Demo 仅配置双环传动资料；其他企业需要单独调研。';
    return false;
  }
  if (confirm && !confirm.checked) {
    confirm.checked = true;
    status.textContent = '已按共享演示模式确认双环主体，继续推进。';
  }
  return true;
}

function next() {
  if (!validateStep()) return;
  step = step === 4 ? 0 : step + 1;
  render();
  if (playing && step === 4) stopAuto();
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function stopAuto() {
  playing = false;
  paused = false;
  clearTimeout(timer);
  document.getElementById('auto').textContent = '自动演示';
}

function pauseAuto() {
  paused = true;
  clearTimeout(timer);
  document.getElementById('auto').textContent = '继续演示';
  status.textContent = '演示已暂停。可以讲解当前环节，点击继续演示再推进。';
}

function resumeAuto() {
  paused = false;
  document.getElementById('auto').textContent = '暂停演示';
  const tick = () => {
    if (!playing || paused) return;
    if (step === 4) {
      stopAuto();
      return;
    }
    next();
    timer = setTimeout(tick, 6500);
  };
  timer = setTimeout(tick, 1000);
}

function auto() {
  if (playing && !paused) {
    pauseAuto();
    return;
  }
  if (playing && paused) {
    resumeAuto();
    return;
  }
  playing = true;
  paused = false;
  document.getElementById('auto').textContent = '暂停演示';
  if (step === 0) {
    const confirm = document.getElementById('confirm');
    if (confirm) confirm.checked = true;
  }
  const tick = () => {
    if (!playing) return;
    if (step === 4) {
      stopAuto();
      return;
    }
    next();
    timer = setTimeout(tick, 6500);
  };
  timer = setTimeout(tick, 1800);
}

document.getElementById('next').onclick = () => {
  stopAuto();
  next();
};
document.getElementById('prev').onclick = () => {
  stopAuto();
  step = Math.max(0, step - 1);
  render();
};
document.getElementById('auto').onclick = auto;

fetch('data.json')
  .then(r => {
    if (!r.ok) throw Error('data');
    return r.json();
  })
  .then(d => {
    data = d;
    render();
  })
  .catch(() => {
    panel.textContent = '研究资料加载失败，请刷新重试。';
    document.getElementById('next').disabled = true;
    document.getElementById('auto').disabled = true;
  });
