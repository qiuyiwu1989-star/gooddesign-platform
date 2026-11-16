(() => {
  'use strict';
  const $ = selector => document.querySelector(selector);
  const $$ = selector => [...document.querySelectorAll(selector)];
  const onboardDataEl = $('#mcp-onboard-data');
  const onboard = onboardDataEl ? JSON.parse(onboardDataEl.textContent) : null;
  const endpoint = onboard ? onboard.endpoint : 'https://haoshejiguan.com/inno/mcp/api';
  const token = $('#mcp-token');
  const output = $('#mcp-config');
  const status = $('#copy-status');
  const copyButton = $('#copy-config');
  const envNote = $('#codex-env-note');
  const copyDialog = $('#copy-dialog');
  const copyDialogText = $('#copy-dialog-text');
  let format = 'json';
  let toolGroup = 'all';
  let lastCopyTrigger = null;

  function config(key) {
    return format === 'json'
      ? JSON.stringify({ mcpServers: { 'gooddesign-innovation': { url: endpoint, headers: { Authorization: 'Bearer ' + key } } } }, null, 2)
      : '[mcp_servers.gooddesign-innovation]\nurl = ' + JSON.stringify(endpoint) + '\nbearer_token_env_var = "GOODDESIGN_MCP_TOKEN"';
  }

  function render() {
    output.textContent = config('<YOUR_PRIVATE_MCP_KEY>');
    copyButton.textContent = format === 'json' ? '复制 JSON 配置' : '复制 Codex TOML';
    envNote.hidden = format !== 'toml';
    $$('[data-format]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.format === format)));
    status.textContent = '';
  }

  function openCopyDialog(text, trigger) {
    lastCopyTrigger = trigger;
    copyDialogText.value = text;
    copyDialog.showModal();
    copyDialogText.focus();
    copyDialogText.select();
    copyDialogText.scrollTop = 0;
  }

  async function copyText(text, success, trigger) {
    try {
      if (!navigator.clipboard?.writeText) throw Error('clipboard_unavailable');
      await navigator.clipboard.writeText(text);
      status.textContent = success;
    } catch {
      openCopyDialog(text, trigger);
    }
  }

  function renderTools() {
    const query = $('#tool-search').value.trim().toLowerCase();
    let count = 0;
    $$('.mcp-tool').forEach(tool => {
      const matchesGroup = toolGroup === 'all' || tool.dataset.toolGroup === toolGroup;
      const matchesQuery = !query || tool.textContent.toLowerCase().includes(query) || tool.dataset.toolName.includes(query);
      const visible = matchesGroup && matchesQuery;
      tool.hidden = !visible;
      if (visible) count += 1;
    });
    $('#tool-count').textContent = count ? `显示 ${count} 项工具` : '没有匹配的工具';
    $('#tool-empty').hidden = count > 0;
  }

  $$('[data-format]').forEach(button => button.addEventListener('click', () => {
    format = button.dataset.format;
    render();
  }));

  copyButton.addEventListener('click', () => {
    const key = token.value.trim();
    if (format === 'json' && !key) {
      status.textContent = '请先填写私有访问密钥，或手动复制预览后在客户端替换密钥占位符。';
      token.focus();
      return;
    }
    copyText(config(key), format === 'json' ? '已复制 JSON 配置，其中包含你输入的私有密钥。' : '已复制 Codex TOML。请先设置 GOODDESIGN_MCP_TOKEN 再启动或重连客户端。', copyButton);
  });

  $('#copy-endpoint').addEventListener('click', event => copyText(endpoint, '已复制服务地址。', event.currentTarget));
  $('#copy-prompt').addEventListener('click', event => copyText($('#task-prompt').textContent, '已复制任务描述。', event.currentTarget));

  function onboardPack() {
    const groupName = { discovery: '发现', read: '深读', prepare: '组包' };
    const toolLines = onboard.tools.map(t =>
      `- ${t.name}（${groupName[t.group] || t.group}）：${t.summary} 参数：${t.args}`).join('\n');
    return `# 好设计创新知识库 MCP 接入包

## 接入配置（标准 MCP，JSON）

\`\`\`json
${JSON.stringify({ mcpServers: { 'gooddesign-innovation': { url: endpoint, headers: { Authorization: 'Bearer <YOUR_PRIVATE_MCP_KEY>' } } } }, null, 2)}
\`\`\`

Codex 用 TOML：url 同上，密钥经 bearer_token_env_var = "GOODDESIGN_MCP_TOKEN" 读取，不写进配置。

## 工具清单（全部只读）

${toolLines}

## 边界

- 一次最多 3 个项目、5 个方法、5 个关键词，单次返回上限 120KB。
- 证据仅返回发布版本实际引用的片段，不开放整份原件。
- 不创建或回读研究历史；研究包和报告由客户端保存。
- 接入后先调用 inno_capabilities 确认入口与边界；不知道 ID 或版本时先检索，不猜编号。

## 示例任务描述

${onboard.prompt}
`;
  }

  const copyOnboard = $('#copy-onboard');
  if (copyOnboard) copyOnboard.addEventListener('click', event =>
    copyText(onboardPack(), '已复制 Agent 接入包（配置 + 工具清单 + 边界 + 示例任务），直接粘贴给 Agent 即可。', event.currentTarget));
  $('#copy-dialog-close').addEventListener('click', () => copyDialog.close());
  copyDialog.addEventListener('close', () => lastCopyTrigger?.focus());

  $$('[data-tool-filter]').forEach(button => button.addEventListener('click', () => {
    toolGroup = button.dataset.toolFilter;
    $$('[data-tool-filter]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    renderTools();
  }));
  $('#tool-search').addEventListener('input', renderTools);
  token.addEventListener('input', () => { status.textContent = ''; });
  addEventListener('pagehide', () => {
    token.value = '';
    copyDialogText.value = '';
  });
  render();
  renderTools();
})();
