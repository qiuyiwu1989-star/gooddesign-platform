/* animations.js —— 机制动画播放器(SVG 示意,JS 驱动)
 * 用法:Animations.open({ title, subtitle, anim })
 * anim 定义: { id, w, h, steps:[{name,dur}], render(t, step, sp, ctx) }
 * 说明:动画为教学示意,展示运动机制而非工程精确。
 */
(function () {
  'use strict';
  var state = null;

  var NS = 'http://www.w3.org/2000/svg';

  /* ============ 动画一:钻头「冲-切-排-拨-挤」 ============ */
  var DRILL = {
    id: 'drill-bore', w: 460, h: 300,
    steps: [
      { name: '冲:内刃冲击,突破岩块', dur: 1.4 },
      { name: '切:外刃切削,破碎大颗粒', dur: 1.4 },
      { name: '排:渐阔流道,高效排粉', dur: 1.4 },
      { name: '拨:多点挤拨,置换侧方颗粒', dur: 1.4 },
      { name: '挤:持续钻进,深入月壤', dur: 1.4 }
    ],
    render: function (t, step, sp, ctx) {
      var drillY = ctx.drillY0 + (step + sp) * 26;
      ctx.drill.setAttribute('transform', 'translate(230,' + drillY + ')' + (step === 1 ? ' rotate(' + (sp * 90 - 45) + ')' : ''));
      ctx.drill.style.opacity = 1;
      ctx.head.textContent = '钻头下探深度 ' + Math.round(20 + (step + sp) * 12) + '%';
      for (var i = 0; i < 6; i++) {
        var px = ctx.part[i];
        var ang = ctx.pAng[i] + (step + sp) * ctx.pSpd[i] * 0.16;
        var pr = ctx.pR[i] + (step + sp) * 9;
        px.setAttribute('cx', 230 + Math.cos(ang) * pr);
        px.setAttribute('cy', drillY + 46 + Math.sin(ang) * pr * 0.7 - 8);
        px.setAttribute('opacity', Math.max(0, 1 - (step + sp) * 0.35));
      }
    },
    build: function (root) {
      var s = document.createElementNS(NS, 'svg');
      s.setAttribute('viewBox', '0 0 460 300'); s.setAttribute('width', '100%');
      s.innerHTML =
        '<defs><linearGradient id="soilG" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0" stop-color="#C9A06B"/><stop offset="1" stop-color="#8A6A42"/></linearGradient></defs>' +
        '<rect x="0" y="0" width="460" height="300" fill="#F6F7FA"/>' +
        '<text x="230" y="24" text-anchor="middle" font-size="13" fill="#8A8F98">月球钻取采样 · 组合式钻进工艺</text>' +
        '<rect id="soilTop" x="60" y="168" width="340" height="34" fill="#C9A06B" opacity="0.55"/>' +
        '<rect id="soilMid" x="60" y="202" width="340" height="40" fill="#A98257"/>' +
        '<rect id="soilBot" x="60" y="242" width="340" height="44" fill="#8A6A42"/>' +
        '<circle id="rock" cx="240" cy="232" r="10" fill="#5A4A36"/>' +
        '<circle id="rock2" cx="262" cy="258" r="7" fill="#6B5942"/>' +
        '<g id="drillG">' +
          '<rect x="-8" y="-120" width="16" height="120" fill="#B9BECB" rx="3"/>' +
          '<path d="M-17 0 L-13 -34 L-8 -34 L-8 -86 L8 -86 L8 -34 L13 -34 L17 0 Z" fill="#B08936"/>' +
          '<path d="M-13 -34 L-8 -34 L-8 -86 L8 -86 L8 -34 L13 -34" stroke="#fff" stroke-width="2" fill="none" opacity="0.6"/>' +
          '<circle cx="0" cy="-64" r="4" fill="#4F58C0"/>' +
        '</g>' +
        '<g id="partG"></g>' +
        '<text id="headT" x="230" y="52" text-anchor="middle" font-size="14" font-weight="600" fill="#16181D">准备钻进</text>' +
        '<g id="stepBar"></g>';
      root.appendChild(s);
      var ctx = { drill: s.querySelector('#drillG'), head: s.querySelector('#headT'), part: [], pAng: [], pR: [], pSpd: [], drillY0: 60 };
      ctx.drillY0 = 60;
      var pg = s.querySelector('#partG');
      for (var i = 0; i < 6; i++) {
        var c = document.createElementNS(NS, 'circle');
        c.setAttribute('r', 3 + Math.random() * 3); c.setAttribute('fill', '#8A6A42');
        pg.appendChild(c);
        ctx.part.push(c);
        ctx.pAng.push(Math.random() * Math.PI * 2);
        ctx.pR.push(10 + Math.random() * 14);
        ctx.pSpd.push(0.7 + Math.random() * 0.9);
      }
      ctx.stepBar = s.querySelector('#stepBar');
      ctx.render = DRILL.render;
      return ctx;
    }
  };

  /* ============ 动画二:双管单袋内翻包覆 ============ */
  var BAG = {
    id: 'bag-invert', w: 460, h: 300,
    steps: [
      { name: '外层护管下行,软袋随钻杆同步进给', dur: 1.5 },
      { name: '软袋在管口内翻,包住样芯表面', dur: 1.5 },
      { name: '样芯被软袋连续包覆,无滑差收进', dur: 1.5 },
      { name: '样芯入袋,封口机构待命', dur: 1.3 }
    ],
    render: function (t, step, sp, ctx) {
      var y = ctx.baseY - (step + sp) * 16;
      ctx.outer.setAttribute('y', y - 150);
      ctx.inner.setAttribute('y', y - 100);
      var phase = step + sp;
      var bagY = y - 26 + Math.min(1, Math.max(0, (phase - 0.5) / 2)) * 18;
      ctx.bag.setAttribute('d', 'M' + (ctx.xL - 22) + ' ' + (y - 26) + ' L' + (ctx.xL - 22) + ' ' + bagY +
        ' Q' + ctx.xL + ' ' + (bagY + 30) + ' ' + (ctx.xL + 20) + ' ' + bagY + ' L' + (ctx.xL + 20) + ' ' + (y - 26) + ' Z');
      ctx.sample.setAttribute('y', y - 40 - Math.min(1, Math.max(0, (phase - 1.2) / 1.5)) * 46);
      ctx.sample.setAttribute('opacity', phase > 1.1 ? 1 : 0);
      ctx.sample2.setAttribute('opacity', phase > 2.2 ? 1 : 0);
      ctx.sample2.setAttribute('y', y - 40 - Math.min(1, Math.max(0, (phase - 2.2) / 1.3)) * 46);
      ctx.tip.textContent = '样芯收进 ' + Math.round(Math.min(100, (phase / 3.5) * 100)) + '%';
    },
    build: function (root) {
      var s = document.createElementNS(NS, 'svg');
      s.setAttribute('viewBox', '0 0 460 300'); s.setAttribute('width', '100%');
      s.innerHTML =
        '<rect x="0" y="0" width="460" height="300" fill="#F6F7FA"/>' +
        '<text x="230" y="24" text-anchor="middle" font-size="13" fill="#8A8F98">双管单袋无滑差取芯 · 软袋内翻包覆</text>' +
        '<g id="outerG"><rect x="190" y="110" width="80" height="150" fill="#B9BECB" opacity="0.55" rx="4"/>' +
        '<rect x="186" y="100" width="88" height="12" fill="#8B92A3" rx="3"/></g>' +
        '<g id="innerG"><rect x="202" y="110" width="56" height="150" fill="#8B92A3" opacity="0.35" rx="4"/></g>' +
        '<path id="bagP" fill="#5E6AD2" opacity="0.75"/>' +
        '<rect id="sampleR" x="218" y="80" width="24" height="16" rx="3" fill="#A87E2A"/>' +
        '<rect id="sampleR2" x="222" y="80" width="16" height="12" rx="2" fill="#C08F3A"/>' +
        '<text id="tipT" x="230" y="288" text-anchor="middle" font-size="14" font-weight="600" fill="#16181D">准备开始</text>' +
        '<g id="stepBar2"></g>';
      root.appendChild(s);
      var ctx = {
        outer: s.querySelector('#outerG'), inner: s.querySelector('#innerG'),
        bag: s.querySelector('#bagP'), sample: s.querySelector('#sampleR'), sample2: s.querySelector('#sampleR2'),
        tip: s.querySelector('#tipT'), xL: 230, baseY: 240
      };
      ctx.render = BAG.render;
      return ctx;
    }
  };

  var ANIMS = { 'drill-bore': DRILL, 'bag-invert': BAG };

  /* ============ 播放器 ============ */
  function open(opts) {
    if (state) close();
    var def = ANIMS[opts.anim];
    if (!def) return;

    var root = document.createElement('div');
    root.className = 'sch-mask';
    root.innerHTML =
      '<div class="sch-panel">' +
        '<div class="sch-head">' +
          '<div class="sch-titles"><div class="sch-title">' + esc(opts.title) + '</div>' +
          '<div class="sch-sub">' + esc(opts.subtitle || '') + ' · 机制示意动画</div></div>' +
          '<div class="sch-tools">' +
            '<button type="button" class="sch-btn" data-act="play">⏸ 暂停</button>' +
            '<button type="button" class="sch-btn" data-act="replay">↻ 重播</button>' +
            '<button type="button" class="sch-btn sch-close" data-act="close">关闭 ESC</button>' +
          '</div>' +
        '</div>' +
        '<div class="sch-stage anim-stage"><div class="anim-box"></div>' +
          '<div class="anim-steps" id="animSteps"></div>' +
        '</div>' +
      '</div>';
    document.body.appendChild(root);

    var box = root.querySelector('.anim-box');
    var ctx = def.build(box);
    ctx.def = def;
    /* 步骤条 */
    var stepsEl = root.querySelector('#animSteps');
    var stepNodes = def.steps.map(function (st, i) {
      var d = document.createElement('div');
      d.className = 'anim-step';
      d.innerHTML = '<span class="no">' + (i + 1) + '</span><span>' + esc(st.name) + '</span>';
      stepsEl.appendChild(d);
      return d;
    });

    var total = def.steps.reduce(function (a, s) { return a + s.dur; }, 0);
    var t0 = performance.now(), paused = false, pauseAt = 0, raf = 0;

    function tick(now) {
      raf = requestAnimationFrame(tick);
      if (paused) return;
      var el = ((now - t0) / 1000) % total;
      var acc = 0, step = 0, sp = 0;
      for (var i = 0; i < def.steps.length; i++) {
        if (el < acc + def.steps[i].dur) { step = i; sp = (el - acc) / def.steps[i].dur; break; }
        acc += def.steps[i].dur;
      }
      stepNodes.forEach(function (n, k) { n.classList.toggle('on', k === step); });
      ctx.render(el, step, sp, ctx);
    }
    raf = requestAnimationFrame(tick);

    var btnPlay = root.querySelector('[data-act="play"]');
    root.querySelector('[data-act="play"]').addEventListener('click', function () {
      paused = !paused;
      if (!paused) t0 = performance.now() - (pauseAt || 0);
      else pauseAt = ((performance.now() - t0) / 1000) % total;
      btnPlay.textContent = paused ? '▶ 继续' : '⏸ 暂停';
    });
    root.querySelector('[data-act="replay"]').addEventListener('click', function () {
      t0 = performance.now(); pauseAt = 0; paused = false;
      btnPlay.textContent = '⏸ 暂停';
    });
    root.querySelector('[data-act="close"]').addEventListener('click', close);

    state = { root: root, raf: raf };
  }

  function close() {
    if (!state) return;
    cancelAnimationFrame(state.raf);
    state.root.parentNode && state.root.parentNode.removeChild(state.root);
    state = null;
  }
  function escKey(e) { if (e.key === 'Escape') close(); }
  document.addEventListener('keydown', escKey);

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  window.Animations = { open: open, close: close };
})();
