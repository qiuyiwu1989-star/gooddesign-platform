import html

LINKS = (
    ('projects', '/projects/', '项目库'),
    ('museum', '/museum/', '好设计馆'),
    ('methods', '/methods/', '方法库'),
    ('apps', '/apps/', '应用中心'),
    ('needs', '/needs/', '需求研究'),
    ('report', '/report/', '数据总览'),
)


def navigation(active='projects', project=None):
    if active not in {'projects', 'methods', 'needs', 'report', 'museum', 'learn', 'mcp', 'admin', 'about', 'apps', 'model', 'guide'}:
        raise ValueError('unsupported_navigation_target')
    from urllib.parse import urlencode
    home = '/dossier/?' + urlencode({'project': project}) if project else '/projects/'
    links = ''.join(
        f'<a href="{url}" data-gd-nav="{key}"'
        + (' aria-current="page"' if key == active else '')
        + f'>{label}</a>'
        for key, url, label in LINKS
    )
    return f'''<a class="gd-skip" href="#main">跳到主要内容</a>
<header class="gd-nav" data-gd-chrome="navigation">
  <div class="gd-shell gd-nav-inner">
    <a class="gd-brand" href="/" aria-label="好设计 GoodDesign 首页">
      <img class="gd-brand-logo" src="/inno/portal/brand-logo.svg?v=084" alt="">
      <span class="gd-brand-text"><strong>好设计</strong><small>GoodDesign</small></span>
    </a>
    <nav class="gd-links" aria-label="主导航">{links}</nav>
    <div class="gd-nav-actions">
      <a href="/about/" data-gd-nav="about"{(' aria-current="page"' if active in {'about', 'model', 'guide'} else '')}>关于</a>
      <a href="/mcp/" data-gd-nav="mcp"{(' aria-current="page"' if active == 'mcp' else '')}>MCP 接入</a>
      <a href="/admin/" data-gd-nav="admin"{(' aria-current="page"' if active == 'admin' else '')}>资料管理</a>
      <button class="gd-button gd-button--quiet" id="theme-toggle" type="button" data-gd-theme-toggle aria-label="切换为深色主题">深色</button>
    </div>
  </div>
</header>
<button class="gd-ip-trigger" type="button" data-gd-assistant-open aria-label="打开好设计IP助理小好"><img src="/inno/portal/ip-xiaohao.svg?v=078" alt=""><span>小好</span></button>
<dialog class="gd-drawer gd-assistant" data-gd-assistant aria-labelledby="assistant-title">
  <div class="gd-drawer-head"><div class="gd-assistant-identity"><img src="/inno/portal/ip-xiaohao.svg?v=078" alt="小好，GoodDesign的研究搭子"><div><span class="gd-kicker">GoodDesign AI Agent</span><h2 id="assistant-title">你好，我是小好</h2></div></div><button class="gd-button gd-button--quiet" type="button" data-gd-assistant-close>关闭</button></div>
  <p>我是你的研究搭子，可以陪你找项目、读方法、核证据。一起把问题看清楚，再决定下一步。</p>
  <div class="gd-assistant-actions" aria-label="小好导览动作">
    <a class="gd-assistant-action gd-assistant-action--primary" href="/projects/"><img src="/inno/portal/ip-xiaohao.svg?v=078" alt=""><span><strong>找项目</strong><small>从真实案例和设计取舍开始</small></span></a>
    <a class="gd-assistant-action" href="/methods/"><img src="/inno/portal/ip-xiaohao-method.svg" alt=""><span><strong>读方法</strong><small>理解输入、步骤与适用边界</small></span></a>
    <a class="gd-assistant-action" href="{home}"><img src="/inno/portal/ip-xiaohao-evidence.svg" alt=""><span><strong>核证据</strong><small>回到项目版本与原文引用</small></span></a>
  </div>
  <div class="gd-assistant-note"><strong>我会把依据留给你</strong><p>现在提供真实导览，不把演示当成自动研究。这里不调用模型，也不会修改你的资料。</p></div>
</dialog>
<script src="/inno/portal/chrome.js" defer></script>'''


def footer():
    return '''<footer class="gd-shell gd-footer" data-gd-chrome="footer">
  <div class="gd-footer-brand"><a class="gd-brand" href="/"><img class="gd-brand-logo" src="/inno/portal/brand-logo.svg?v=084" alt=""><span class="gd-brand-text"><strong>好设计</strong><small>GoodDesign</small></span></a><p>从真实项目出发，连接设计知识与创新应用。</p></div>
  <nav class="gd-footer-links" aria-label="相关栏目"><a href="/projects/">项目库</a><a href="/methods/">方法库</a><a href="/apps/">应用中心</a><a href="/museum/#education">科技教育</a><a href="/loop/">企业创新</a><a href="/model/">创新设计大模型</a><a href="/guide/">使用指南</a><a href="/about/">关于</a><a href="/mcp/">MCP 接入</a><a href="/admin/">资料管理</a></nav>
  <p class="gd-footer-note">GoodDesign · OpenDesign 创新项目区</p>
</footer>'''


def strip_arrows(text):
    import re
    return re.sub(r'[↗↘→←↔⇄↑↓]', '', text)


def replace_chrome(text, active):
    import re
    text = re.sub(r'<script\b[^>]*\bsrc=["\']/inno/portal/chrome\.js["\'][^>]*>\s*</script>', '', text, flags=re.I)
    text = re.sub(r'<script\b[^>]*\bsrc=["\'](?:\.\./)?copilot\.js["\'][^>]*>\s*</script>', '', text, flags=re.I)
    text = re.sub(r'<a\b[^>]*class=["\'][^"\']*\bgd-skip\b[^"\']*["\'][^>]*>.*?</a>', '', text, flags=re.S | re.I)
    text = re.sub(r'<a\b[^>]*class=["\'][^"\']*\bskip\b[^"\']*["\'][^>]*>.*?</a>', '', text, flags=re.S | re.I)
    preserved = []
    for ident in ('feedback', 'print'):
        match = re.search(r'<(span|button)\b[^>]*\bid="' + ident + r'"[^>]*>.*?</\1>', text, flags=re.S | re.I)
        if match:
            preserved.append(match.group(0))
    text = re.sub(r'<button\b(?=[^>]*\bdata-gd-assistant-open(?:\s|=|>))[^>]*>.*?</button>', '', text, flags=re.S | re.I)
    text = re.sub(r'<dialog\b(?=[^>]*\bdata-gd-assistant(?:\s|=|>))[^>]*>.*?</dialog>', '', text, flags=re.S | re.I)
    header_match = re.search(r'<header\b[^>]*>.*?</header>', text, flags=re.S | re.I)
    has_header = bool(header_match)
    is_chrome_header = bool(header_match and re.search(r'<nav\b|pp-nav|workspace-header|inno-nav|app-topbar|app-header', header_match.group(0), re.I))
    if is_chrome_header:
        text = re.sub(r'<header\b[^>]*>.*?</header>', '', text, count=1, flags=re.S | re.I)
    else:
        nav_match = re.search(r'<nav\b[^>]*>.*?</nav>', text, flags=re.S | re.I)
        if nav_match and re.search(r'pp-brand|workspace-brand|inno-brand|class=["\'][^"\']*brand', nav_match.group(0), re.I):
            text = text[:nav_match.start()] + text[nav_match.end():]
    def remove_legacy_footer(match):
        return match.group(0) if re.search(r'class=["\'][^"\']*gd-live-', match.group(0), re.I) else ''
    text = re.sub(r'<footer\b[^>]*>.*?</footer>', remove_legacy_footer, text, flags=re.S | re.I)
    if not re.search(r'<main\b', text, re.I) and re.search(r'<body\b[^>]*>', text, re.I):
        text = re.sub(r'(<body\b[^>]*>)', lambda match: match.group(1) + '<main id="main">', text, count=1, flags=re.I)
        text = re.sub(r'</body>', '</main></body>', text, count=1, flags=re.I)
    chrome = navigation(active)
    if preserved:
        chrome = chrome.replace('</div>\n</header>', ''.join(preserved) + '</div>\n</header>')
    if re.search(r'<body\b[^>]*>', text, re.I):
        text = re.sub(r'(<body\b[^>]*>)', lambda match: match.group(1) + chrome, text, count=1, flags=re.I)
    elif re.search(r'<main\b[^>]*>', text, re.I):
        text = re.sub(r'(<main\b[^>]*>)', lambda match: chrome + match.group(1), text, count=1, flags=re.I)
    elif '</head>' in text:
        text = text.replace('</head>', '</head>' + chrome, 1)
    else:
        text = re.sub(r'(<html\b[^>]*>)', lambda match: match.group(1) + chrome, text, count=1, flags=re.I)
    if '</body>' in text:
        text = text.replace('</body>', footer() + '</body>', 1)
    elif '</html>' in text:
        text = text.replace('</html>', footer() + '</html>', 1)
    else:
        text += footer()
    def normalize_main(match):
        tag = match.group(0)
        if re.search(r'\bid=["\']workspace-content["\']', tag, re.I):
            return re.sub(r'\bid=["\']workspace-content["\']', 'id="main"', tag, flags=re.I)
        if not re.search(r'\bid=', tag, re.I):
            return tag[:-1] + ' id="main">'
        return tag
    text = re.sub(r'<main\b[^>]*>', normalize_main, text, flags=re.I)
    return strip_arrows(text)

