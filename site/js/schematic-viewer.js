/* schematic-viewer.js —— 官方图纸查看器(缩放/平移/多图切换)
 * 用法:SchematicViewer.open({ title, subtitle, list: [{name, file}] })
 * 纯 DOM 实现,零依赖;大图按需加载。
 */
(function () {
  'use strict';
  var state = null;

  function open(opts) {
    if (state) close();
    var list = opts.list || [];
    if (!list.length) return;

    /* 与 3D 弹层互斥:打开图纸前先关闭 3D */
    if (window.XRay3D) XRay3D.close();

    var root = document.createElement('div');
    root.className = 'sch-mask';
    var thumbs = list.map(function (it, i) {
      return '<button type="button" class="sch-thumb' + (i === 0 ? ' on' : '') + '" data-i="' + i + '">' +
        '<img src="' + esc(it.file) + '" alt="" loading="lazy">' +
        '<span>' + esc(it.name) + '</span></button>';
    }).join('');
    root.innerHTML =
      '<div class="sch-panel">' +
        '<div class="sch-head">' +
          '<div class="sch-titles"><div class="sch-title">' + esc(opts.title) + '</div>' +
          '<div class="sch-sub">' + esc(opts.subtitle || '') + ' · 设计方官方原图(来源:好设计官网获奖详情)</div></div>' +
          '<div class="sch-tools">' +
            '<button type="button" class="sch-btn" data-act="mark">标注工具</button>' +
            '<button type="button" class="sch-btn" data-act="fit">适应窗口</button>' +
            '<button type="button" class="sch-btn" data-act="zoomout">−</button>' +
            '<button type="button" class="sch-btn" data-act="zoomin">+</button>' +
            '<button type="button" class="sch-btn sch-close" data-act="close">关闭 ESC</button>' +
          '</div>' +
        '</div>' +
        '<div class="sch-stage">' +
          '<div class="sch-loading" id="schLoading">图纸加载中,请稍候…</div>' +
          '<div class="sch-cap" id="schCap"></div>' +
          '<div class="sch-hint">滚轮缩放 · 拖拽平移 · 双击复位</div>' +
          '<div class="sch-marklayer" id="schMarks"></div>' +
          '<div class="sch-imgwrap"><img class="sch-img" id="schImg" alt=""></div>' +
        '</div>' +
        (list.length > 1 ? '<div class="sch-thumbs">' + thumbs + '</div>' : '') +
      '</div>';
    document.body.appendChild(root);

    var stage = root.querySelector('.sch-stage');
    var img = root.querySelector('#schImg');
    var cap = root.querySelector('#schCap');
    var markLayer = root.querySelector('#schMarks');
    var scale = 1, tx = 0, ty = 0, cur = 0;
    var dragging = false, sx = 0, sy = 0, ox = 0, oy = 0;

    /* ---------- 标注工具(点图添加/拖拽/编辑/本地保存) ---------- */
    var markMode = false, marks = [], selMark = -1, markKey = '';
    var mdrag = null;
    function loadMarks() {
      markKey = 'schmarks-' + (opts.markKey || list[cur].file);
      marks = [];
      try { marks = JSON.parse(localStorage.getItem(markKey) || '[]'); } catch (e) {}
    }
    function saveMarks() {
      try { localStorage.setItem(markKey, JSON.stringify(marks)); } catch (e) {}
    }
    function renderMarks() {
      markLayer.innerHTML = '';
      marks.forEach(function (m, i) {
        var d = document.createElement('div');
        d.className = 'sch-mark' + (i === selMark ? ' sel' : '');
        d.style.left = m.x + '%'; d.style.top = m.y + '%';
        d.innerHTML = '<span class="no">' + (i + 1) + '</span><span class="lb">' + esc(m.label || '') + '</span>';
        d.addEventListener('mousedown', function (e) {
          if (!markMode) return;
          e.stopPropagation(); e.preventDefault();
          selMark = i; renderMarks(); showMarkInput(i);
          mdrag = { i: i, sx: e.clientX, sy: e.clientY, ox: m.x, oy: m.y };
        });
        d.addEventListener('dblclick', function (e) {
          e.stopPropagation();
          marks.splice(i, 1); selMark = -1; renderMarks(); saveMarks(); hideMarkInput();
        });
        markLayer.appendChild(d);
      });
    }
    window.addEventListener('mousemove', function (e) {
      if (!mdrag) return;
      var r = stage.getBoundingClientRect();
      var m = marks[mdrag.i]; if (!m) return;
      m.x = Math.min(97, Math.max(3, mdrag.ox + (e.clientX - mdrag.sx) / r.width * 100));
      m.y = Math.min(97, Math.max(3, mdrag.oy + (e.clientY - mdrag.sy) / r.height * 100));
      renderMarks();
    });
    window.addEventListener('mouseup', function () {
      if (mdrag) { saveMarks(); mdrag = null; }
    });
    var markInput = document.createElement('div');
    markInput.className = 'sch-markinput';
    markInput.innerHTML = '<input type="text" maxlength="24" placeholder="标注文字"><button type="button">确定</button><button type="button" class="del">删除</button>';
    markInput.style.display = 'none';
    stage.appendChild(markInput);
    markInput.querySelector('input').addEventListener('keydown', function (e) { if (e.key === 'Enter') saveLabel(); });
    markInput.querySelector('button').addEventListener('click', saveLabel);
    markInput.querySelector('.del').addEventListener('click', function () {
      if (selMark >= 0) { marks.splice(selMark, 1); selMark = -1; renderMarks(); saveMarks(); hideMarkInput(); }
    });
    function saveLabel() {
      if (selMark >= 0) {
        marks[selMark].label = markInput.querySelector('input').value.trim();
        renderMarks(); saveMarks();
      }
      hideMarkInput();
    }
    function showMarkInput(i) {
      var r = stage.getBoundingClientRect();
      markInput.style.display = 'flex';
      markInput.style.left = Math.min(marks[i].x, 72) + '%';
      markInput.style.top = (marks[i].y + 6) + '%';
      markInput.querySelector('input').value = marks[i].label || '';
      markInput.querySelector('input').focus();
    }
    function hideMarkInput() { markInput.style.display = 'none'; }
    stage.addEventListener('click', function (e) {
      if (!markMode) return;
      if (e.target === markLayer) {
        var r = stage.getBoundingClientRect();
        marks.push({
          x: Math.min(97, Math.max(3, (e.clientX - r.left) / r.width * 100)),
          y: Math.min(97, Math.max(3, (e.clientY - r.top) / r.height * 100)),
          label: ''
        });
        selMark = marks.length - 1;
        renderMarks(); saveMarks(); showMarkInput(selMark);
      }
    });
    root.querySelector('[data-act="mark"]').addEventListener('click', function () {
      markMode = !markMode;
      this.classList.toggle('on', markMode);
      markLayer.classList.toggle('on', markMode);
      if (markMode) { loadMarks(); renderMarks(); }
    });

    function fit() {
      var w = stage.clientWidth, h = stage.clientHeight;
      if (!w || !h) return;
      var iw = img.naturalWidth, ih = img.naturalHeight;
      if (!iw) { scale = 1; } else { scale = Math.min(w / iw, h / ih) * 0.96; }
      tx = 0; ty = 0;
      apply();
    }
    function apply() {
      img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
    }
    var loadingEl = root.querySelector('#schLoading');
    function load(i) {
      cur = i;
      cap.textContent = list[i].name;
      img.style.opacity = 0;
      loadingEl.style.display = 'block';
      img.src = list[i].file;
      Array.prototype.forEach.call(root.querySelectorAll('.sch-thumb'), function (b, k) {
        b.classList.toggle('on', k === i);
      });
    }
    img.addEventListener('load', function () {
      img.style.opacity = 1;
      loadingEl.style.display = 'none';
      fit();
    });
    img.addEventListener('error', function () {
      loadingEl.style.display = 'none';
      cap.textContent = list[cur].name + '(图纸加载失败,请稍后重试)';
      img.style.opacity = 1;
    });

    /* 缩放 */
    stage.addEventListener('wheel', function (e) {
      e.preventDefault();
      var f = e.deltaY < 0 ? 1.12 : 1 / 1.12;
      scale = Math.min(8, Math.max(0.2, scale * f));
      apply();
    }, { passive: false });

    /* 平移(鼠标 + 触摸) */
    function down(x, y) {
      dragging = true; sx = x; sy = y; ox = tx; oy = ty;
    }
    function move(x, y) {
      if (!dragging) return;
      tx = ox + (x - sx); ty = oy + (y - sy);
      apply();
    }
    function up() { dragging = false; }
    img.addEventListener('mousedown', function (e) { e.preventDefault(); down(e.clientX, e.clientY); });
    window.addEventListener('mousemove', function (e) { move(e.clientX, e.clientY); });
    window.addEventListener('mouseup', up);
    img.addEventListener('touchstart', function (e) { if (e.touches.length === 1) down(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
    img.addEventListener('touchmove', function (e) { if (e.touches.length === 1) { e.preventDefault(); move(e.touches[0].clientX, e.touches[0].clientY); } }, { passive: false });
    img.addEventListener('touchend', up);

    /* 双击复位 */
    img.addEventListener('dblclick', fit);

    /* 按钮与缩略图 */
    root.querySelector('[data-act="fit"]').addEventListener('click', fit);
    root.querySelector('[data-act="zoomin"]').addEventListener('click', function () { scale = Math.min(8, scale * 1.3); apply(); });
    root.querySelector('[data-act="zoomout"]').addEventListener('click', function () { scale = Math.max(0.2, scale / 1.3); apply(); });
    root.querySelector('[data-act="close"]').addEventListener('click', close);
    root.querySelectorAll('.sch-thumb').forEach(function (b) {
      b.addEventListener('click', function () { load(+this.getAttribute('data-i')); });
    });

    state = { root: root, fit: fit };
    load(0);
  }

  function close() {
    if (!state) return;
    state.root.parentNode && state.root.parentNode.removeChild(state.root);
    state = null;
  }
  function escKey(e) { if (e.key === 'Escape') close(); }
  document.addEventListener('keydown', escKey);

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  window.SchematicViewer = { open: open, close: close };
})();
