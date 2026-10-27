(()=>{'use strict';
  const endpoint='https://opendesign.cc/inno/mcp/api';
  const token=document.querySelector('#mcp-token');
  const out=document.querySelector('#mcp-config');
  const status=document.querySelector('#copy-status');
  const copyButton=document.querySelector('#copy-config');
  const envNote=document.querySelector('#codex-env-note');
  let format='json';
  function config(key){
    return format==='json'
      ?JSON.stringify({mcpServers:{'gooddesign-innovation':{url:endpoint,headers:{Authorization:'Bearer '+key}}}},null,2)
      :'[mcp_servers.gooddesign-innovation]\nurl = '+JSON.stringify(endpoint)+'\nbearer_token_env_var = "GOODDESIGN_MCP_TOKEN"';
  }
  function render(){
    // Never render the actual key into the visible configuration preview.
    out.textContent=config('<YOUR_PRIVATE_MCP_KEY>');
    copyButton.textContent=format==='json'?'复制 JSON 配置':'复制 Codex TOML';
    if(envNote)envNote.hidden=format!=='toml';
    document.querySelectorAll('[data-format]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.format===format)));
    status.textContent='';
  }
  async function copy(text,success){
    try{await navigator.clipboard.writeText(text);status.textContent=success;}
    catch{status.textContent='浏览器未允许复制。请手动复制预览；JSON 中的密钥占位符需在客户端替换。';}
  }
  document.querySelectorAll('[data-format]').forEach(b=>b.onclick=()=>{format=b.dataset.format;render();});
  copyButton.onclick=()=>{
    const key=token.value.trim();
    if(format==='json'&&!key){status.textContent='请先填写私有访问密钥，或手动复制预览后在客户端替换密钥占位符。';token.focus();return;}
    copy(config(key),format==='json'?'已复制 JSON 配置，其中包含你输入的私有密钥。':'已复制 Codex TOML。请先设置 GOODDESIGN_MCP_TOKEN 再启动或重连客户端。');
  };
  document.querySelector('#copy-prompt').onclick=()=>copy(document.querySelector('#task-prompt').textContent,'已复制任务描述。');
  // No storage, network requests, form submission, or key-bearing URL parameters.
  token.addEventListener('input',()=>{status.textContent='';});
  addEventListener('pagehide',()=>{token.value='';});
  render();
})();
