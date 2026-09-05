/* 好设计助手 · 全站共享 Copilot 面板（自注入样式与 DOM，零依赖）
   用法：页面引入 <script src="copilot.js" defer></script>（project/atom 子目录页用 ../copilot.js）
   入口：任何 <a href="assistant.html" data-copilot>问导览员</a> 会在当前页打开面板；
        带 data-ask="问题" 会打开并自动发送该问题。无 JS 时回退跳转 assistant.html。 */
(function () {
  if (window.GoodCopilot) return;

  var CSS = `
#gcFab{position:fixed;right:24px;bottom:24px;z-index:9000;width:56px;height:56px;border-radius:50%;cursor:pointer;overflow:hidden;
background:#fff;border:2px solid rgba(94,106,210,.35);padding:2px;
box-shadow:0 8px 24px rgba(94,106,210,.35);transition:transform .16s cubic-bezier(.25,.46,.45,.94),border-color .16s,box-shadow .16s}
#gcFab img{width:100%;height:100%;object-fit:cover;border-radius:50%;display:block}
#gcFab:hover{transform:scale(1.06);border-color:#5E6AD2;box-shadow:0 10px 28px rgba(94,106,210,.5)}
#gcMask{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:8990;opacity:0;pointer-events:none;transition:opacity .3s}
#gcMask.open{opacity:1;pointer-events:auto}
#gcPanel{position:fixed;top:0;right:0;height:100vh;height:100dvh;width:max(33.33vw,380px);z-index:8995;
background:#fff;border-left:1px solid rgba(15,23,42,.09);display:flex;flex-direction:column;
transform:translateX(102%);transition:transform .4s cubic-bezier(.25,.46,.45,.94);box-shadow:-24px 0 70px rgba(15,23,42,.14);
font-family:"Inter","Noto Sans SC","PingFang SC",sans-serif;color:#16181D}
#gcPanel.open{transform:none}
#gcPanel *{margin:0;padding:0;box-sizing:border-box}
#gcPanel .gc-head{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid rgba(15,23,42,.09)}
#gcPanel .gc-av{width:32px;height:32px;border-radius:50%;object-fit:cover;border:1px solid rgba(15,23,42,.09);background:#fff;flex:none}
#gcPanel .gc-dot{width:7px;height:7px;border-radius:50%;background:#4F58C0}
#gcPanel .gc-name{font-size:14px;font-weight:600}
#gcPanel .gc-hello{display:flex;gap:10px;align-items:flex-start;align-self:stretch}
#gcPanel .gc-hello .gc-hi-av{width:38px;height:38px;border-radius:50%;object-fit:cover;border:1px solid rgba(15,23,42,.09);background:#fff;flex:none;margin-top:2px}
#gcPanel .gc-hello .gc-msg{flex:1;max-width:none}
#gcPanel .gc-mode{margin-left:auto;font-family:"JetBrains Mono","Noto Sans SC",monospace;font-size:11px;color:#8A8F98}
#gcPanel .gc-close{background:none;border:1px solid rgba(15,23,42,.09);color:#62666D;width:26px;height:26px;border-radius:4px;cursor:pointer;font-size:14px;line-height:1}
#gcPanel .gc-close:hover{border-color:rgba(15,23,42,.25);color:#16181D}
#gcPanel .gc-pbar{display:flex;align-items:center;gap:6px;padding:8px 14px;border-bottom:1px solid rgba(15,23,42,.09);background:rgba(15,23,42,.02);flex-wrap:wrap}
#gcPanel .gc-pbl{font-family:"JetBrains Mono","Noto Sans SC",monospace;font-size:10.5px;color:#8A8F98;letter-spacing:1px;margin-right:2px}
#gcPanel .gc-chip{border:1px solid rgba(15,23,42,.09);background:#fff;color:#62666D;font-size:12px;border-radius:99px;padding:3px 11px;cursor:pointer;transition:all .15s;font-family:inherit}
#gcPanel .gc-chip:hover{border-color:rgba(94,106,210,.5);color:#3E4454}
#gcPanel .gc-chip.on{border-color:#5E6AD2;background:rgba(94,106,210,.10);color:#4F58C0;font-weight:600}
#gcPanel .gc-deep{margin-left:auto;border-style:dashed}
#gcPanel .gc-deep.on{border-style:solid;border-color:#A87E2A;background:rgba(168,126,42,.10);color:#A87E2A}
#gcPanel .gc-log{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:12px}
#gcPanel .gc-msg{max-width:88%;padding:11px 14px;border-radius:12px;font-size:13.5px;line-height:1.7;word-break:break-word;white-space:pre-wrap}
#gcPanel .gc-msg.bot{background:rgba(15,23,42,.045);border:1px solid rgba(15,23,42,.09);color:#3E4454;align-self:flex-start;border-top-left-radius:4px;white-space:normal}
#gcPanel .gc-msg.user{background:#5E6AD2;color:#fff;align-self:flex-end;border-top-right-radius:4px}
#gcPanel .gc-msg .gc-src{display:block;font-family:"JetBrains Mono","Noto Sans SC",monospace;font-size:10.5px;color:#8A8F98;margin-top:8px}
#gcPanel .gc-msg .gc-refs{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
#gcPanel .gc-msg .gc-refs span{font-family:"JetBrains Mono","Noto Sans SC",monospace;font-size:10.5px;color:#4F58C0;border:1px solid rgba(94,106,210,.35);border-radius:99px;padding:2px 9px;background:rgba(94,106,210,.10)}
#gcPanel .gc-msg.bot p{margin:0 0 10px}
#gcPanel .gc-msg.bot p:last-child{margin-bottom:0}
#gcPanel .gc-msg.bot strong{color:#16181D;font-weight:600}
#gcPanel .gc-msg.bot .md-h{font-weight:600;color:#16181D;margin:12px 0 6px}
#gcPanel .gc-msg.bot .md-list{margin:4px 0 10px}
#gcPanel .gc-msg.bot .md-li{margin:3px 0;line-height:1.65}
#gcPanel .gc-msg.bot .md-mk{color:#4F58C0;font-family:"JetBrains Mono","Noto Sans SC",monospace;font-size:12px;margin-right:6px}
#gcPanel .gc-typing{align-self:flex-start;color:#8A8F98;font-size:12px;padding:2px 14px;font-family:"JetBrains Mono","Noto Sans SC",monospace}
#gcPanel .gc-suggests{display:flex;flex-wrap:wrap;gap:8px;padding:12px 18px;border-top:1px solid rgba(15,23,42,.09)}
#gcPanel .gc-suggests button{border:1px solid rgba(15,23,42,.09);background:transparent;color:#62666D;border-radius:99px;padding:6px 13px;font-size:12px;cursor:pointer;font-family:inherit;transition:all .16s}
#gcPanel .gc-suggests button:hover{border-color:rgba(94,106,210,.55);color:#4F58C0}
#gcPanel .gc-input{display:flex;gap:10px;padding:14px 18px;border-top:1px solid rgba(15,23,42,.09)}
#gcPanel .gc-input input{flex:1;background:rgba(15,23,42,.02);border:1px solid rgba(15,23,42,.09);border-radius:6px;padding:11px 14px;font-size:13.5px;color:#16181D;outline:none;font-family:inherit}
#gcPanel .gc-input input:focus{border-color:rgba(94,106,210,.6)}
#gcPanel .gc-input input::placeholder{color:#8A8F98}
#gcPanel .gc-input button{border:0;background:#5E6AD2;color:#fff;font-weight:600;padding:0 20px;border-radius:6px;font-size:13.5px;cursor:pointer;font-family:inherit}
#gcPanel .gc-input button:hover{background:#4F58C0}
#gcPanel .gc-input button:disabled{opacity:.4;cursor:default}
body.gc-open{margin-right:max(33.33vw,380px);transition:margin-right .4s cubic-bezier(.25,.46,.45,.94)}
body.gc-open #gcFab{display:none}
@media(max-width:760px){
#gcPanel{width:100vw}
body.gc-open{margin-right:0}
#gcFab{right:16px;bottom:16px}
}`;

  // 子目录页（project/ atom/ 等）接口与素材要回上一级
  var IN_SUB = /\/(project|atom|materials|dismantle)\//.test(location.pathname);
  var IS_SHARE_PAGE = /\/serve\/[^/]+\/share\/good-design\//.test(location.pathname);
  var OFFICIAL_API_BASE = 'https://good-design-06676a.apps.zaowuyun.com/api/';
  var API_BASE = window.GOOD_DESIGN_API_BASE || (IS_SHARE_PAGE ? OFFICIAL_API_BASE : (IN_SUB ? '../api/' : 'api/'));
  var ASSET = IN_SUB ? '../assets/brand/' : 'assets/brand/';

  var HTML = `
<div id="gcMask"></div>
<aside id="gcPanel" aria-label="好设计助手">
  <div class="gc-head">
    <img class="gc-av" src="${ASSET}mascot-head.webp" alt="">
    <span class="gc-dot"></span>
    <span class="gc-name">好设计助手</span>
    <span class="gc-mode" id="gcMode">连接中…</span>
    <button class="gc-close" id="gcClose" title="收起面板">×</button>
  </div>
  <div class="gc-pbar" id="gcPbar">
    <span class="gc-pbl">我是</span>
    <button class="gc-chip on" data-persona="public">公众</button>
    <button class="gc-chip" data-persona="student">学生</button>
    <button class="gc-chip" data-persona="designer">设计师</button>
    <button class="gc-chip" data-persona="enterprise">企业</button>
    <button class="gc-chip gc-deep" id="gcDeep" title="深度推理模式（mimo-v2.5-pro）">深度</button>
  </div>
  <div class="gc-log" id="gcLog">
    <div class="gc-hello"><img class="gc-hi-av" src="${ASSET}mascot-head.webp" alt="好设计助手"><div class="gc-msg bot">您好，我是「好设计助手」，也是好设计馆的导览员。我可以为您介绍好设计奖的背景与导向、历届获奖项目（十届 560 项档案）、2026 年申报要点，或带您参观馆里的「国之重器」特展。请问您想了解什么？</div></div>
  </div>
  <div class="gc-suggests" id="gcSuggests">
    <button>好设计奖是什么？</button>
    <button>什么是“好设计”？</button>
    <button>2025 年有哪些金奖项目？</button>
    <button>这个项目好在哪里？</button>
    <button>带我参观好设计馆</button>
  </div>
  <div class="gc-input">
    <input id="gcInput" type="text" placeholder="请输入您的问题…" maxlength="500" autocomplete="off">
    <button id="gcSend">发送</button>
  </div>
</aside>
<button id="gcFab" title="好设计助手"><img src="${ASSET}mascot-head.webp" alt="好设计助手"></button>`;

  function boot() {
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);
    var host = document.createElement('div');
    host.innerHTML = HTML;
    while (host.firstChild) document.body.appendChild(host.firstChild);

    var panel = document.getElementById('gcPanel');
    var mask = document.getElementById('gcMask');
    var log = document.getElementById('gcLog');
    var input = document.getElementById('gcInput');
    var btn = document.getElementById('gcSend');
    var modeEl = document.getElementById('gcMode');
    var history = [];
    var persona = 'public';
    var deepMode = false;
    var PERSONA_NAMES = { public: '公众', student: '学生', designer: '设计师', enterprise: '企业' };

    function isMobile() { return window.innerWidth <= 760; }
    function open(ask) {
      panel.classList.add('open');
      document.body.classList.add('gc-open');
      if (isMobile()) mask.classList.add('open');
      setTimeout(function () { input.focus(); }, 420);
      if (ask) setTimeout(function () { send(ask); }, 500);
    }
    function close() {
      panel.classList.remove('open');
      document.body.classList.remove('gc-open');
      mask.classList.remove('open');
    }
    function toggle() { panel.classList.contains('open') ? close() : open(); }

    document.getElementById('gcFab').addEventListener('click', toggle);
    document.getElementById('gcClose').addEventListener('click', close);
    mask.addEventListener('click', close);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });

    // 入口代理：任何 [data-copilot] 元素在当前页打开
    document.addEventListener('click', function (e) {
      var t = e.target.closest ? e.target.closest('[data-copilot]') : null;
      if (!t) return;
      e.preventDefault();
      open(t.getAttribute('data-ask') || undefined);
    });

    document.getElementById('gcPbar').addEventListener('click', function (e) {
      var t = e.target;
      if (t.id === 'gcDeep') {
        deepMode = !deepMode;
        t.classList.toggle('on', deepMode);
        addMsg('已' + (deepMode ? '开启' : '关闭') + '深度推理模式（' + (deepMode ? 'mimo-v2.5-pro，适合迁移分析、方案评估类问题' : '恢复默认模型') + '）。', 'bot');
        return;
      }
      if (!t.dataset || !t.dataset.persona || t.dataset.persona === persona) return;
      persona = t.dataset.persona;
      document.querySelectorAll('#gcPbar .gc-chip[data-persona]').forEach(function (c) {
        c.classList.toggle('on', c.dataset.persona === persona);
      });
      addMsg('好的，接下来我将以「' + PERSONA_NAMES[persona] + '」视角为您讲解。', 'bot');
    });

    fetch(API_BASE + 'health').then(function (r) { return r.json(); }).then(function (d) {
      modeEl.textContent = d.llm ? ('ONLINE · ' + d.model) : 'KB MODE';
    }).catch(function () { modeEl.textContent = 'DISCONNECTED'; });

    function esc(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
    function renderMd(s) {
      var t = esc(s).replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
      var lines = t.split('\n'), out = [], para = [], list = [];
      function flushPara() { if (para.length) { out.push('<p>' + para.join('<br>') + '</p>'); para = []; } }
      function flushList() { if (list.length) { out.push('<div class="md-list">' + list.join('') + '</div>'); list = []; } }
      lines.forEach(function (raw) {
        var l = raw.trim();
        if (!l) { flushPara(); flushList(); return; }
        var hm = l.match(/^(#{1,4})\s*(.+)$/);
        if (hm) { flushPara(); flushList(); out.push('<div class="md-h">' + hm[2] + '</div>'); return; }
        var im = l.match(/^(\d+[.、)]|[-•*])\s+(.+)$/);
        if (im) { flushPara(); list.push('<div class="md-li"><span class="md-mk">' + im[1] + '</span>' + im[2] + '</div>'); return; }
        flushList(); para.push(l);
      });
      flushPara(); flushList();
      return out.join('');
    }

    function addMsg(text, who) {
      var div = document.createElement('div');
      div.className = 'gc-msg ' + who;
      if (who === 'bot') div.innerHTML = renderMd(text); else div.textContent = text;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
      return div;
    }

    function addFailMsg() {
      var d = addMsg('真实智能体服务连接失败。当前为静态镜像页，AI 助手需要后端服务支持；可前往正式站，在首页右下角唤起在线助手：', 'bot');
      if (d) {
        var a = document.createElement('a');
        a.href = 'https://good-design-06676a.apps.zaowuyun.com/';
        a.target = '_blank';
        a.rel = 'noopener';
        a.textContent = '打开正式站（首页右下角助手）→';
        a.style.cssText = 'display:inline-block;margin-top:8px;color:#2D4FAF;font-weight:600;text-decoration:underline';
        d.appendChild(a);
      }
    }

    function addRefs(botDiv, refs, source) {
      if (refs && refs.length) {
        var line = document.createElement('span');
        line.className = 'gc-refs';
        refs.forEach(function (r) {
          var chip = document.createElement('span');
          chip.textContent = r;
          line.appendChild(chip);
        });
        botDiv.appendChild(line);
      }
      if (source === 'fallback') {
        var s = document.createElement('span');
        s.className = 'gc-src';
        s.textContent = '— 知识库直接作答';
        botDiv.appendChild(s);
      }
    }

    function send(text) {
      text = (text || '').trim();
      if (!text) return;
      addMsg(text, 'user');
      history.push({ role: 'user', content: text });
      input.value = '';
      btn.disabled = true;
      var typing = document.createElement('div');
      typing.className = 'gc-typing';
      typing.textContent = 'agent is thinking…';
      log.appendChild(typing);
      log.scrollTop = log.scrollHeight;

      var botDiv = null, acc = '', finished = false;
      function finish(ev) {
        if (finished) return;
        finished = true;
        typing.remove();
        if (!botDiv) botDiv = addMsg(acc || '真实智能体暂时没有返回内容，请稍后再试。', 'bot');
        if (ev) addRefs(botDiv, ev.refs, ev.source);
        if (ev && ev.model) modeEl.textContent = 'ONLINE · ' + ev.model + (deepMode ? ' · DEEP' : '');
        history.push({ role: 'assistant', content: acc });
        btn.disabled = false;
        input.focus();
      }

      fetch(API_BASE + 'chat', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ message: text, history: history, stream: true, persona: persona, deep: deepMode })
      }).then(function (resp) {
        if (!resp.ok || !resp.body) throw new Error('bad response');
        var reader = resp.body.getReader();
        var dec = new TextDecoder();
        var buf = '';
        function pump() {
          return reader.read().then(function (r) {
            if (r.done) { finish(null); return; }
            buf += dec.decode(r.value, { stream: true });
            var lines = buf.split('\n');
            buf = lines.pop();
            lines.forEach(function (line) {
              var t = line.trim();
              if (t.indexOf('data:') !== 0) return;
              try {
                var ev = JSON.parse(t.slice(5));
                if (ev.text) {
                  if (!botDiv) { typing.remove(); botDiv = addMsg('', 'bot'); }
                  acc += ev.text;
                  botDiv.innerHTML = renderMd(acc);
                  log.scrollTop = log.scrollHeight;
                }
                if (ev.error) {
                  if (!botDiv) { typing.remove(); botDiv = addMsg(ev.error, 'bot'); }
                  else botDiv.innerHTML = renderMd(ev.error);
                  acc = '';
                  log.scrollTop = log.scrollHeight;
                }
                if (ev.done) finish(ev);
              } catch (e) { /* 忽略无法解析的行 */ }
            });
            return pump();
          });
        }
        return pump();
      }).catch(function () {
        typing.remove();
        addFailMsg();
        modeEl.textContent = 'DISCONNECTED';
        btn.disabled = false;
        input.focus();
      });
    }

    btn.addEventListener('click', function () { send(input.value); });
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') send(input.value); });
    document.getElementById('gcSuggests').addEventListener('click', function (e) {
      if (e.target.tagName === 'BUTTON') send(e.target.textContent);
    });

    window.GoodCopilot = { open: open, close: close, toggle: toggle };
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
