/* part3d.js —— 拆解实验室 3D 部件查看器
 * 依赖:vendor/three.min.js + vendor/OrbitControls.js + vendor/RoomEnvironment.js(本地,r128)
 * 用法:XRay3D.open({ title, subtitle, recipe, onClose })
 * 模型为「结构示意」,几何特征按官方资料(刃数/叶片数/层数),非工程精确模型。
 */
(function () {
  'use strict';
  if (typeof THREE === 'undefined') return;

  var MAT = {
    body: new THREE.MeshStandardMaterial({ color: 0xC7CBD6, metalness: 0.42, roughness: 0.45 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x8B92A3, metalness: 0.4, roughness: 0.5 }),
    accent: new THREE.MeshStandardMaterial({ color: 0x5E6AD2, metalness: 0.3, roughness: 0.5, transparent: true, opacity: 0.85 }),
    gold: new THREE.MeshStandardMaterial({ color: 0xB08936, metalness: 0.45, roughness: 0.4 }),
    glow: new THREE.MeshStandardMaterial({ color: 0x4F58C0, emissive: 0x2A3173, emissiveIntensity: 0.6 }),
    base: new THREE.MeshStandardMaterial({ color: 0x12151F, metalness: 0.2, roughness: 0.65, transparent: true, opacity: 0.5 })
  };

  /* ================= 钻头(渐阔双排阶梯式取芯钻具) ================= */
  function buildAuger(p) {
    var dia = p.dia || 1, rod = p.rodLen || 2.2, tip = p.tipLen || 0.8;
    var flutes = p.flutes || 2, teeth = p.teeth || 8;

    /* --- 钻杆 + 顶部连接法兰 --- */
    var rodMesh = new THREE.Mesh(new THREE.CylinderGeometry(dia * 0.36, dia * 0.36, rod, 48), MAT.body);
    rodMesh.position.y = tip + rod / 2;
    rodMesh.castShadow = true;
    var flange = new THREE.Mesh(new THREE.CylinderGeometry(dia * 0.46, dia * 0.42, dia * 0.14, 48), MAT.dark);
    flange.position.y = tip + rod + dia * 0.05;
    flange.castShadow = true;

    /* --- 双螺旋排屑槽带(粗螺旋凸棱,模拟渐阔双螺旋) --- */
    var spiralG = new THREE.Group();
    for (var f = 0; f < flutes; f++) {
      var pts = [], seg = 100;
      var turns = 2.2, startY = tip * 0.30, endY = tip + rod * 0.70;
      for (var i = 0; i <= seg; i++) {
        var t = i / seg;
        var y = startY + (endY - startY) * t;
        var a = f * Math.PI + turns * Math.PI * 2 * t;
        var r = dia * (0.30 + 0.07 * t);
        pts.push(new THREE.Vector3(Math.cos(a) * r, y, Math.sin(a) * r));
      }
      var spiral = new THREE.Mesh(
        new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), seg, dia * 0.105, 8, false),
        MAT.dark
      );
      spiral.castShadow = true;
      spiralG.add(spiral);
    }

    /* --- 阶梯钻头锥体(两级台阶,Lathe 剖面) --- */
    var prof = [
      new THREE.Vector2(0.001, 0),
      new THREE.Vector2(0.26 * dia, 0.16 * tip),
      new THREE.Vector2(0.33 * dia, 0.16 * tip),
      new THREE.Vector2(0.33 * dia, 0.38 * tip),
      new THREE.Vector2(0.42 * dia, 0.38 * tip),
      new THREE.Vector2(0.42 * dia, 0.62 * tip),
      new THREE.Vector2(0.50 * dia, tip)
    ];
    var cone = new THREE.Mesh(new THREE.LatheGeometry(prof, 48), MAT.gold);
    cone.castShadow = true;

    /* --- 阶梯刃齿(两级台阶各一圈楔形齿,尖端朝外) --- */
    var teethG = new THREE.Group();
    function addTeethRing(yLevel, radius, n, size) {
      for (var k = 0; k < n; k++) {
        var a = k / n * Math.PI * 2;
        var tooth = new THREE.Mesh(new THREE.ConeGeometry(size * 0.52, size, 4), MAT.glow);
        tooth.position.set(Math.cos(a) * radius, yLevel, Math.sin(a) * radius);
        tooth.lookAt(Math.cos(a) * radius * 2.2, yLevel, Math.sin(a) * radius * 2.2);
        tooth.castShadow = true;
        teethG.add(tooth);
      }
    }
    addTeethRing(tip * 0.16, dia * 0.335, teeth, dia * 0.20);
    addTeethRing(tip * 0.38, dia * 0.425, teeth, dia * 0.22);

    /* --- 分解分组 --- */
    var grpCone = new THREE.Group();
    grpCone.add(cone); grpCone.add(teethG);
    var grpRod = new THREE.Group();
    grpRod.add(rodMesh); grpRod.add(flange); grpRod.add(spiralG);
    var g = new THREE.Group();
    g.add(grpCone); g.add(grpRod);

    return {
      root: g,
      groups: [
        { name: '阶梯钻头与刃齿', obj: grpCone, offset: new THREE.Vector3(0, -tip * 0.62, 0) },
        { name: '钻杆 · 法兰 · 双螺旋排屑槽', obj: grpRod, offset: new THREE.Vector3(0, rod * 0.30, 0) }
      ],
      size: (tip + rod) * 0.9
    };
  }

  /* ================= 透平叶片(弯扭空心叶片) ================= */
  function buildTurbineBlade(p) {
    var h = p.height || 2.2, chord = p.chord || 1.0, thick = p.thick || 0.16;
    var twistDeg = p.twist || 38, bow = p.bow || 0.30;
    var cool = p.cooling || 4;

    /* --- 翼型轮廓 14 点(前缘圆润、后缘收尖) --- */
    var c = chord, t = thick;
    var prof = [
      [0.06 * c, 0.06 * c], [0.0176 * c, 0.0424 * c], [0, 0], [0.0176 * c, -0.0424 * c], [0.06 * c, -0.06 * c],
      [0.15 * c, -0.30 * t], [0.30 * c, -0.46 * t], [0.55 * c, -0.36 * t], [0.80 * c, -0.16 * t], [c, 0],
      [0.80 * c, 0.16 * t], [0.55 * c, 0.36 * t], [0.30 * c, 0.46 * t], [0.15 * c, 0.30 * t]
    ];

    /* --- 弯扭扫掠(带厚度与收缩) --- */
    var layers = 22;
    var verts = [], idx = [];
    for (var L = 0; L <= layers; L++) {
      var f = L / layers;
      var sc = 1 - 0.60 * Math.pow(f, 1.30);
      var tw = twistDeg * Math.PI / 180 * Math.pow(f, 1.45);
      var bz = bow * Math.pow(f, 1.8);
      for (var q = 0; q < prof.length; q++) {
        var x = (prof[q][0] - c * 0.5) * sc;
        var z = prof[q][1] * sc;
        var cs = Math.cos(tw), sn = Math.sin(tw);
        verts.push(new THREE.Vector3(x * cs + z * sn, f * h, -x * sn + z * cs + bz * c));
      }
    }
    var pos = new Float32Array(verts.length * 3);
    verts.forEach(function (v, i) {
      pos[i * 3] = v.x; pos[i * 3 + 1] = v.y; pos[i * 3 + 2] = v.z;
    });
    for (var L2 = 0; L2 < layers; L2++) {
      for (var q2 = 0; q2 < prof.length; q2++) {
        var nxt = (q2 + 1) % prof.length;
        var a0 = L2 * prof.length + q2, a1 = L2 * prof.length + nxt;
        var b0 = (L2 + 1) * prof.length + q2, b1 = (L2 + 1) * prof.length + nxt;
        idx.push(a0, b0, b1, a0, b1, a1);
      }
    }
    var geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setIndex(idx);
    geo.computeVertexNormals();
    var blade = new THREE.Mesh(geo, MAT.body);
    blade.castShadow = true;

    /* --- 叶冠(叶尖的冠带,抑制叶尖泄漏) --- */
    var crown = new THREE.Mesh(new THREE.BoxGeometry(c * 0.72, h * 0.022, t * 0.62), MAT.dark);
    crown.position.set(c * 0.18 - c * 0.5, h, bow * c + t * 0.1);
    crown.castShadow = true;

    /* --- 枞树形榫根(三段阶梯示意) --- */
    var rootG = new THREE.Group();
    var r0 = new THREE.Mesh(new THREE.CylinderGeometry(c * 0.26, c * 0.36, h * 0.07, 4), MAT.gold);
    r0.rotation.y = Math.PI / 4; r0.position.y = -h * 0.05;
    var r1 = new THREE.Mesh(new THREE.CylinderGeometry(c * 0.34, c * 0.24, h * 0.06, 4), MAT.gold);
    r1.rotation.y = Math.PI / 4; r1.position.y = -h * 0.115;
    var r2 = new THREE.Mesh(new THREE.CylinderGeometry(c * 0.24, c * 0.34, h * 0.06, 4), MAT.gold);
    r2.rotation.y = Math.PI / 4; r2.position.y = -h * 0.175;
    rootG.add(r0, r1, r2);

    /* --- 内部冷却空气通道(空心叶片,带根部入口) --- */
    var coolG = new THREE.Group();
    for (var i = 0; i < cool; i++) {
      var cx = chord * (0.24 + 0.16 * i) - c * 0.5;
      var tube = new THREE.Mesh(new THREE.CylinderGeometry(c * 0.024, c * 0.024, h * 0.80, 10), MAT.accent);
      tube.position.set(cx, h * 0.40, 0);
      tube.castShadow = true;
      coolG.add(tube);
      var inlet = new THREE.Mesh(new THREE.CylinderGeometry(c * 0.05, c * 0.034, h * 0.09, 10), MAT.accent);
      inlet.position.set(cx, h * 0.045, 0);
      coolG.add(inlet);
    }

    var grpOuter = new THREE.Group();
    grpOuter.add(blade); grpOuter.add(crown); grpOuter.add(rootG);
    var grpCool = new THREE.Group();
    grpCool.add(coolG);
    var g = new THREE.Group();
    g.add(grpOuter); g.add(grpCool);

    return {
      root: g,
      groups: [
        { name: '叶片外壳 · 叶冠 · 榫根', obj: grpOuter, offset: new THREE.Vector3(0, 0, h * 0.38) },
        { name: '内部冷却空气通道(根部入口)', obj: grpCool, offset: new THREE.Vector3(0, 0, -h * 0.32) }
      ],
      size: h * 1.05
    };
  }

  /* ================= 配方分发 ================= */
  function build(recipe) {
    if (!recipe) return null;
    switch (recipe.type) {
      case 'auger': return buildAuger(recipe.params || {});
      case 'turbine-blade': return buildTurbineBlade(recipe.params || {});
      default: return null;
    }
  }

  /* ================= 弹层与渲染循环 ================= */
  var state = null;

  function open(opts) {
    if (state) close();
    /* 与图纸弹层互斥:打开 3D 前先关闭图纸 */
    if (window.SchematicViewer) SchematicViewer.close();
    var recipe = opts.recipe;
    var built = build(recipe);
    if (!built) return;

    var root = document.createElement('div');
    root.className = 'x3d-mask';
    root.innerHTML =
      '<div class="x3d-panel">' +
        '<div class="x3d-head">' +
          '<div class="x3d-titles"><div class="x3d-title">' + esc(opts.title) + '</div>' +
          '<div class="x3d-sub">' + esc(opts.subtitle || '') + ' · 结构示意模型(非工程精确)</div></div>' +
          '<div class="x3d-tools">' +
            '<button type="button" class="x3d-btn on" data-act="rotate">自动旋转</button>' +
            '<button type="button" class="x3d-btn" data-act="boom">分解视图</button>' +
            '<button type="button" class="x3d-btn x3d-close" data-act="close">关闭 ESC</button>' +
          '</div>' +
        '</div>' +
        '<div class="x3d-stage"><div class="x3d-canvas"></div>' +
          '<div class="x3d-legend" id="x3dLegend"></div>' +
          '<div class="x3d-hint">拖拽旋转 · 滚轮缩放 · 右键平移</div>' +
        '</div>' +
      '</div>';
    var legTxt = built.groups.map(function (x) { return x.name; }).join('  /  ');
    document.body.appendChild(root);

    var stage = root.querySelector('.x3d-stage');
    var renderer = null;
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    } catch (e) {
      close();
      alert('当前浏览器不支持 WebGL 3D 渲染,请更换浏览器或开启硬件加速后重试。');
      return;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    try { renderer.shadowMap.enabled = true; } catch (e) {}
    stage.querySelector('.x3d-canvas').appendChild(renderer.domElement);

    var scene = new THREE.Scene();

    var cam = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
    cam.position.set(built.size * 1.55, built.size * 1.05, built.size * 1.85);
    cam.lookAt(0, built.size * 0.35, 0);

    scene.add(new THREE.AmbientLight(0xffffff, 0.30));
    var key = new THREE.DirectionalLight(0xffffff, 1.05);
    key.position.set(built.size * 2.5, built.size * 4, built.size * 3);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    var sh = key.shadow.camera;
    sh.left = sh.right = -built.size * 2; sh.top = sh.bottom = built.size * 2;
    sh.far = built.size * 10;
    scene.add(key);
    var fill = new THREE.DirectionalLight(0x9fb0ff, 0.45);
    fill.position.set(-built.size * 3, built.size * 1.5, -built.size * 2);
    scene.add(fill);
    var rim = new THREE.PointLight(0xffd9a0, 0.7, built.size * 8);
    rim.position.set(-built.size * 1.8, built.size * 2.5, -built.size * 3);
    scene.add(rim);

    /* 展台底座 + 淡网格 */
    var pedestal = new THREE.Mesh(
      new THREE.CylinderGeometry(built.size * 1.05, built.size * 1.18, 0.03, 64),
      MAT.base
    );
    pedestal.position.y = -built.size * 0.55;
    pedestal.receiveShadow = true;
    scene.add(pedestal);
    var grid = new THREE.GridHelper(built.size * 3.4, 20, 0x37406B, 0x232A44);
    grid.position.y = -built.size * 0.545;
    scene.add(grid);

    var rootG = built.root;
    rootG.position.y = 0;
    scene.add(rootG);

    var controls = new THREE.OrbitControls(cam, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 1.6;
    controls.minDistance = built.size * 0.45;
    controls.maxDistance = built.size * 6;
    controls.target.set(0, built.size * 0.35, 0);

    function resize() {
      var w = stage.clientWidth || 800, h = stage.clientHeight || 500;
      renderer.setSize(w, h);
      cam.aspect = w / h;
      cam.updateProjectionMatrix();
    }
    resize();
    window.addEventListener('resize', resize);

    var raf = 0, renderFailed = false;
    function animate() {
      raf = requestAnimationFrame(animate);
      try {
        controls.update();
        renderer.render(scene, cam);
      } catch (e) {
        if (!renderFailed) {
          renderFailed = true;
          cancelAnimationFrame(raf);
          close();
          alert('3D 渲染出错(可能显卡驱动或浏览器兼容问题),请换 Chrome/Edge 最新版重试。');
        }
      }
    }
    animate();
    /* 首帧立即渲染一次,尽早暴露问题 */
    try { controls.update(); renderer.render(scene, cam); } catch (e) {}

    var btnRot = root.querySelector('[data-act="rotate"]');
    var btnBoom = root.querySelector('[data-act="boom"]');
    var legend = root.querySelector('#x3dLegend');
    function setBoom(on) {
      built.groups.forEach(function (gr) {
        gr.obj.position.copy(on ? gr.offset : new THREE.Vector3(0, 0, 0));
      });
      btnBoom.classList.toggle('on', on);
      legend.textContent = legTxt;
    }
    legend.textContent = legTxt;
    btnRot.addEventListener('click', function () {
      controls.autoRotate = !controls.autoRotate;
      this.classList.toggle('on', controls.autoRotate);
    });
    btnBoom.addEventListener('click', function () {
      setBoom(!this.classList.contains('on'));
    });
    root.querySelector('[data-act="close"]').addEventListener('click', close);

    state = { root: root, renderer: renderer, raf: raf, resize: resize };
  }

  function close() {
    if (!state) return;
    cancelAnimationFrame(state.raf);
    window.removeEventListener('resize', state.resize);
    state.renderer.dispose();
    state.root.parentNode && state.root.parentNode.removeChild(state.root);
    state = null;
  }

  function escKey(e) { if (e.key === 'Escape') close(); }
  document.addEventListener('keydown', escKey);

  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  window.XRay3D = { open: open, close: close };
})();
