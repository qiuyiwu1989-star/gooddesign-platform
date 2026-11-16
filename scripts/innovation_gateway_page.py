"""064/077 remote read-only MCP center. Never embeds credentials or local paths."""
import html
import json
from project_portal import shell

E = lambda value: html.escape(str(value), quote=True)
ENDPOINT = 'https://haoshejiguan.com/inno/mcp/api'
GROUPS = {'discovery': '发现', 'read': '深读', 'prepare': '组包'}
TOOLS = [
    {'name': 'inno_capabilities', 'group': 'discovery', 'summary': '检查远程入口、只读范围与调用边界。', 'args': '无参数。接入后首先调用。'},
    {'name': 'inno_search_projects', 'group': 'discovery', 'summary': '按关键词寻找项目ID与题录，不做语义优选。', 'args': 'query、offset、limit'},
    {'name': 'inno_search_methods', 'group': 'discovery', 'summary': '在64种方法中寻找ID、作用和版本。', 'args': 'query、offset、limit'},
    {'name': 'inno_read_project', 'group': 'read', 'summary': '分层读取项目总览、记录、解释与版本。', 'args': 'project_id、section、revision、record_id、entity、fields、offset、limit'},
    {'name': 'inno_read_method', 'group': 'read', 'summary': '读取方法的输入、步骤、来源与适用边界。', 'args': 'method_id、section、offset、limit'},
    {'name': 'inno_search_fields', 'group': 'read', 'summary': '逐字检索已发布事实字段，保留版本与证据。', 'args': 'query、project_ids、entity、field、offset、limit、snapshot；后续页传回snapshot固定版本。'},
    {'name': 'inno_read_evidence', 'group': 'read', 'summary': '按明确研究版本读取实际引用的逐字证据。', 'args': 'project_id、source_id、revision、offset、limit、chunks_sha256'},
    {'name': 'inno_prepare_research', 'group': 'prepare', 'summary': '组装版本绑定的研究上下文，不保存、不执行。', 'args': 'problem、project_ids、method_ids、keywords'},
    {'name':'inno_read_claim_evidence','group':'read','summary':'核对单条来源陈述与冻结引文、来源及读取范围。','args':'project_id、revision、record_id、field；追溯通过不等语义支持。'},
    {'name':'inno_read_mechanism','group':'read','summary':'读取同记录的问题、机制、取舍、验证和边界，缺项明确。','args':'project_id、revision、record_id；仅明确关联，不重建历史设计过程。'},
    {'name':'inno_read_method_asset','group':'read','summary':'显式选择冻结、深化或标杆方法资产。','args':'method_id、profile：frozen / deep / benchmark；缺标杆不自动回退。'},
    {'name':'inno_prepare_transfer','group':'prepare','summary':'准备源案例与目标需求的迁移核对工作表。','args':'project_id、revision、record_id、requirement（id、revision、text）；关系待审，不自动证明适用。'},
]


def tool_rows():
    rows = []
    for tool in TOOLS:
        rows.append(f'<details class="mcp-tool" data-tool-group="{tool["group"]}" data-tool-name="{tool["name"]}"><summary><code>{E(tool["name"])}</code><span>{E(tool["summary"])}</span><small>参数</small></summary><div class="mcp-tool-args"><strong>主要参数与使用方式</strong><p>{E(tool["args"])}</p></div></details>')
    return ''.join(rows)


def page():
    prompt = '使用 gooddesign-innovation，研究“小型异形零件内腔抛光时，如何降低表面损伤并改善去除均匀性”。材料、尺寸、载荷和验收标准暂时未知。先调用inno_capabilities并核12项工具；检索相关项目与方法，查看覆盖与失败原因，固定研究版本或snapshot；对关键字段读取inno_read_claim_evidence，按需读取inno_read_mechanism和deep方法资产；用inno_prepare_transfer准备目标条件核对，说明选取理由；再用问题定义、功能分析和形态组合形成草稿。来源主张、分析与目标假设分开，每项关键判断标出项目版本、记录字段与方法版本。相关专利不能写成已采用。最后给我需要补充的数据、候选方向、验证计划和停止条件；如要保留过程，请由当前客户端保存研究包和报告，并保留引用的项目与方法版本。'
    onboard = json.dumps({'endpoint': ENDPOINT, 'tools': TOOLS, 'prompt': prompt}, ensure_ascii=False).replace('</', '<\\/')
    body = f'''<div class="mcp-center"><header class="mcp-hero"><div><span class="gd-kicker">GoodDesign 开发接入</span><h1>MCP 接入中心</h1><p>在一个入口配置客户端、查找工具，并保留有版本的研究上下文。</p></div><span class="mcp-readonly">远程只读</span></header><section class="mcp-facts" aria-label="服务摘要"><div><strong>HTTP</strong><span>Streamable 远程接入</span></div><div><strong>{len(TOOLS)}</strong><span>只读工具</span></div><div><strong>0</strong><span>模型调用与收费生成</span></div><div><strong>120KB</strong><span>单次返回上限</span></div></section>
    <section class="mcp-section" id="setup"><header class="mcp-section-heading"><div><h2>先完成一次接入</h2><p>无需下载数据库或连接移动硬盘。配置只用于你的客户端，不向本页服务器提交。</p></div><span class="mcp-section-index">接入配置</span></header><div class="mcp-setup-grid"><div class="mcp-config-form"><div class="mcp-endpoint"><div><label>服务地址</label><code>{ENDPOINT}</code></div><button class="gd-button gd-button--quiet" type="button" id="copy-endpoint">复制地址</button></div><div class="mcp-tabs" role="group" aria-label="客户端配置格式"><button type="button" data-format="json" aria-pressed="true">标准 MCP · JSON</button><button type="button" data-format="toml" aria-pressed="false">Codex · TOML</button></div><div class="mcp-field"><label for="mcp-token">私有访问密钥</label><input id="mcp-token" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="填写管理员提供的私有密钥" aria-describedby="token-note"><small id="token-note">仅用于本次复制。密钥不自动保存、不写入浏览器存储，也不向服务器提交；配置预览始终使用占位符。</small></div><button class="gd-button gd-button--primary" type="button" id="copy-config">复制 JSON 配置</button><button class="gd-button gd-button--quiet" type="button" id="copy-onboard">复制 Agent 接入包</button><p class="mcp-status" id="copy-status" role="status" aria-live="polite"></p><div class="mcp-env-note" id="codex-env-note" hidden><p>TOML通过 <code>bearer_token_env_var = "GOODDESIGN_MCP_TOKEN"</code> 读取密钥，不将密钥写进配置。先在运行Codex的环境中设置变量，再启动或重连客户端。</p><pre><code>export GOODDESIGN_MCP_TOKEN='替换为管理员提供的私有密钥'</code></pre></div></div><aside class="mcp-config-preview"><div><strong>配置预览</strong><span>真实密钥不会显示在这里</span></div><pre><code id="mcp-config">正在生成配置预览</code></pre></aside></div></section>
    <section class="mcp-section" id="tools"><header class="mcp-section-heading"><div><h2>{len(TOOLS)}项工具，按研究动作查找</h2><p>先发现对象，再深读上下文与证据，最后组装研究包。</p></div><span class="mcp-section-index">工具目录</span></header><div class="mcp-tool-controls"><label class="mcp-search">搜索工具<input id="tool-search" type="search" placeholder="搜索名称、用途或参数"></label><div class="mcp-tool-filters" role="group" aria-label="工具分组"><button type="button" data-tool-filter="all" aria-pressed="true">全部 {len(TOOLS)}</button><button type="button" data-tool-filter="discovery" aria-pressed="false">发现 3</button><button type="button" data-tool-filter="read" aria-pressed="false">深读 {sum(t["group"]=="read" for t in TOOLS)}</button><button type="button" data-tool-filter="prepare" aria-pressed="false">组包 {sum(t["group"]=="prepare" for t in TOOLS)}</button></div></div><p class="mcp-status" id="tool-count" role="status" aria-live="polite">显示 {len(TOOLS)} 项工具</p><div class="mcp-tool-list" id="tool-list">{tool_rows()}<div class="mcp-empty" id="tool-empty" hidden>没有匹配的工具，试试项目名称、方法或证据。</div></div></section>
    <section class="mcp-section" id="workflow"><header class="mcp-section-heading"><div><h2>从一个问题，到可追溯的研究上下文</h2><p>固定研究顺序用于组织工作，不代表自动优选或工程结论。</p></div><span class="mcp-section-index">调用顺序</span></header><div class="mcp-flow"><article><span>检索</span><code>inno_search_projects<br>inno_search_methods</code><p>先确认稳定ID和研究对象，查看实际检索覆盖；跳过、失败和零命中含义不同。</p></article><article><span>读取</span><code>inno_read_project<br>inno_read_method_asset</code><p>按层次读取档案与方法。</p></article><article><span>核证</span><code>inno_search_fields<br>inno_read_claim_evidence</code><p>保留明确版本和逐字引用。</p></article><article><span>组包</span><code>inno_read_mechanism<br>inno_prepare_transfer</code><p>列源与目标的同异和未知；工作表由Agent继续分析，不自动证明适用。</p></article></div></section>
    <section class="mcp-section" id="acceptance"><h2>接通后，先验证这一条读取链</h2><p>重新连接并刷新工具列表，依次完成初始化、工具列表、inno_capabilities、字段查询和证据包读取。当前为12项只读工具；只看到配置或页面不算接通。空查询结果不等于证据读取已成功。</p><p>字段查询返回coverage和snapshot；继续分页时传回同一snapshot。版本撤回或证据损坏会拒绝读取，不静默返回半份结果。校验和用于完整性检查，不是身份认证。</p><p>方法资产的frozen为冻结目录，deep为经审核的深化正文，benchmark为三类标杆候选。正文可读不代表有执行契约；局部深度与未审核提示应继续保留。</p><p>服务还提供固定质量状态资源 gooddesign://schemas/quality-envelope，以及 evidence_review / method_application 模板；客户端不支持资源或模板时，可继续使用读取工具。扩展召回仍在评测，默认字段检索为逐字匹配。</p></section>
    <section class="mcp-section" id="start"><div class="mcp-start-grid"><div><header class="mcp-section-heading"><div><h2>把这段任务交给你的AI</h2><p>客户端负责分析与撰写，远程入口只读提供知识与研究包。</p></div></header><blockquote id="task-prompt">{E(prompt)}</blockquote><button class="gd-button" type="button" id="copy-prompt">复制任务描述</button></div><details class="mcp-example"><summary>查看组包请求示例</summary><pre><code>{{
  "tool": "inno_prepare_research",
  "arguments": {{
    "problem": "降低内腔抛光表面损伤，材料、载荷和验收阈值未知。",
    "project_ids": ["2025-04"],
    "method_ids": ["R48", "R14", "R17"],
    "keywords": ["抛光", "表面"]
  }}
}}</code></pre></details></div></section>
    <section class="mcp-bottom-grid" id="troubleshooting"><article><h2>权限与数据边界</h2><ul><li>远程{len(TOOLS)}项工具全部只读，不提供源档案写入。</li><li>研究组包一次最多3个项目、5个方法、5个关键词；其他工具按各自参数范围读取，统一返回上限120KB。</li><li>证据仅返回发布版本实际引用的片段，不开放整份原件。</li><li>不创建或回读研究历史，研究包和报告由当前客户端保存。</li></ul></article><article><h2>遇到问题时</h2><ul><li>无法连接：先检查远程MCP支持与服务地址，再调用 <code>inno_capabilities</code>。</li><li>提示401：使用管理员安全交付的当前有效Bearer私有密钥，网页登录密码不能替代。旧密钥被撤销或轮换后需更新客户端，不要恢复暴露的旧密钥。</li><li>向管理员提供失败响应的 request_id 或 X-Request-ID 及脱敏阶段信息；不要发送密钥、配置截图或Authorization头。页面可读和缓存题录不代表鉴权成功。</li><li>Codex未读取密钥：在可见该变量的环境启动或重连客户端。</li><li>不知道ID或版本：先检索和读取总览，不猜编号。</li><li>返回过大：缩小项目、方法和关键词范围。</li></ul><a href="/about/">查看项目库、方法库和资料管理的分工</a></article></section></div><script type="application/json" id="mcp-onboard-data">{onboard}</script><dialog class="mcp-copy-dialog" id="copy-dialog" aria-labelledby="copy-dialog-title"><div class="mcp-copy-head"><h2 id="copy-dialog-title">复制内容</h2><button class="gd-button gd-button--quiet" type="button" id="copy-dialog-close">关闭</button></div><p>浏览器未允许自动复制。内容已全选，请使用 Command+C 或 Ctrl+C。</p><textarea id="copy-dialog-text" readonly aria-label="待复制内容"></textarea></dialog>'''
    return shell('MCP 接入中心', body, '<link rel="stylesheet" href="/inno/portal/mcp-center.css"><script src="/inno/portal/mcp-guide.js"></script>', active='mcp')
