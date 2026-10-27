"""ML-015 single source for /inno/ website navigation and footer."""
LINKS=(('projects','/inno/projects/','项目库'),('methods','/inno/methods/','方法库'),('needs','/inno/needs/','需求研究'),('report','/inno/report/','数据总览'),('industry','https://gooddesign.qiuyiwu.com/industry-demo/','企业创新 ↗'))

def navigation(active='projects',content_id='workspace-content'):
    if content_id not in ('workspace-content','main'):raise ValueError('unsupported content target')
    return '<a class="pp-skip" href="#'+content_id+'">跳到内容</a><header class="pp-nav"><a class="pp-brand" href="/inno/">好设计<span>OpenDesign</span></a><nav class="pp-links" aria-label="主导航">'+''.join('<a href="'+url+'"'+(' aria-current="page"' if key==active else '')+'>'+label+'</a>'for key,url,label in LINKS)+'</nav><div class="pp-tools"><a href="/inno/mcp/"'+(' aria-current="page"' if active=='mcp' else '')+'>MCP 接入</a><a href="/inno/admin/">资料管理 <small>需登录</small></a></div></header>'

def footer():
    return '<footer class="pp-footer"><a class="pp-brand" href="https://gooddesign.qiuyiwu.com/">好设计</a><p>从真实项目出发，连接设计知识与创新应用。</p><nav aria-label="相关网站"><a href="https://gooddesign.qiuyiwu.com/award.html">好设计奖 ↗</a><a href="https://gooddesign.qiuyiwu.com/hall.html">好设计馆 ↗</a><a href="https://gooddesign.qiuyiwu.com/learn.html">科技教育 ↗</a><a href="/inno/about/">资料与使用说明</a></nav></footer>'
