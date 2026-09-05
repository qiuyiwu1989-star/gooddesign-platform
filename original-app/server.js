// “好设计”平台服务：静态托管 + 智能体问答 API（零依赖，Node 18+）
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PUBLIC_DIR = path.join(ROOT, 'public');
// 课件目录：预览环境在工作区根 ../courseware；部署包内则带 public/courseware 副本
const COURSEWARE_DIR = fs.existsSync(path.join(ROOT, '..', 'courseware'))
  ? path.join(ROOT, '..', 'courseware')
  : path.join(PUBLIC_DIR, 'courseware');
const AGENT_DEF_PATH = path.join(ROOT, 'agents', 'good-design-agent.md');
const KB_PATH = path.join(ROOT, 'knowledge', 'good-design-kb.md');
const CASES_KB_PATH = path.join(ROOT, 'knowledge', 'good-design-cases.md');
const NOTICE_KB_PATH = path.join(ROOT, 'knowledge', 'good-design-2026-notice.md');
const CASES_JSON_PATH = path.join(ROOT, 'public', 'cases.json');

// ---- .env 加载（本地调试可用 .env；生产环境优先使用部署环境变量）----
function loadEnv() {
  let fileVars = {};
  try {
    const raw = fs.readFileSync(path.join(ROOT, '.env'), 'utf8');
    for (const line of raw.split('\n')) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
      if (m) fileVars[m[1]] = m[2];
    }
  } catch (_) { /* .env 不存在则完全依赖环境变量 */ }
  return fileVars;
}
const fileVars = loadEnv();
const isProd = process.env.NODE_ENV === 'production';
const pick = (k, d) => isProd ? (process.env[k] || d) : (fileVars[k] || process.env[k] || d);

const BASE_URL = pick('LLM_BASE_URL', '').replace(/\/+$/, '');
const API_KEY = pick('LLM_API_KEY', '');
const MODEL = pick('LLM_MODEL', 'mimo-v2.5');
const MODEL_PRO = pick('LLM_MODEL_PRO', 'mimo-v2.5-pro');

// ---- 多身份讲解：同一项目，对公众讲故事 / 对学生讲原理 / 对设计师讲方法 / 对企业讲迁移 ----
const PERSONAS = {
  public: '【当前服务对象：公众参观者】讲故事、讲意义：用生活化语言，多打比方，少术语；先讲它解决了什么国家/产业/生活难题，再讲一个最动人的设计细节；长度照常。',
  student: '【当前服务对象：学生】讲原理、讲启发：把设计背后的科学/工程原理拆成可学习的知识点，解释"为什么这样做"，可适当提问引导思考；关联课内知识（物理/化学/生物/地理）时明确指出。',
  designer: '【当前服务对象：设计师/工程人员】讲方法、讲过程：重点讲设计理念与准则、走过的弯路与试错、顿悟时刻、可复用的设计方法；允许使用专业术语；按"问题→约束→方法→验证"组织。',
  enterprise: '【当前服务对象：企业】讲迁移、讲价值：重点讲该技术/方法可迁移到哪些产业场景、解决什么企业问题、转化路径与门槛；输出尽量结构化（可迁移方向/适用条件/对接建议）。',
};
function personaSuffix(key) {
  return PERSONAS[key] ? '\n\n' + PERSONAS[key] : '';
}

// ---- 模型路由：默认 mimo-v2.5；显式指定 / 深度开关 / 深度推理意图 → mimo-v2.5-pro ----
const ALLOWED_MODELS = [MODEL, MODEL_PRO];
const DEEP_RE = /迁移|对接方案|企业画像|深度|推理|对比分析|评估|策划|提案|PPT|课程设计|挑战|再设计/;
function resolveModel(body, question) {
  if (body && typeof body.model === 'string' && ALLOWED_MODELS.includes(body.model)) return body.model;
  if (body && body.deep === true) return MODEL_PRO;
  if (DEEP_RE.test(question)) return MODEL_PRO;
  return MODEL;
}

let agentDef = '';
try { agentDef = fs.readFileSync(AGENT_DEF_PATH, 'utf8'); } catch (_) {
  agentDef = '你是「好设计馆」的智能导览员,负责向参观者介绍中国好设计奖获奖项目。当前知识库未加载,请如实说明并引导访问好设计馆页面。';
}
let kb = '';
try { kb = fs.readFileSync(KB_PATH, 'utf8'); } catch (_) { kb = ''; }
let casesKb = '';
try { casesKb = fs.readFileSync(CASES_KB_PATH, 'utf8'); } catch (_) { /* 案例库可选 */ }
let noticeKb = '';
try { noticeKb = fs.readFileSync(NOTICE_KB_PATH, 'utf8'); } catch (_) { /* 通知库可选 */ }
let caseNames = [];
try {
  caseNames = JSON.parse(fs.readFileSync(CASES_JSON_PATH, 'utf8')).map(c => ({ name: c.name, year: c.year }));
} catch (_) { /* 用于来源标注，可选 */ }

const SYSTEM_PROMPT = agentDef +
  '\n\n---\n\n# 随附知识库（回答的唯一依据）\n\n' + kb +
  (casesKb ? '\n\n---\n\n' + casesKb : '') +
  (noticeKb ? '\n\n---\n\n' + noticeKb : '');

// ---- 来源标注：根据问题与回答内容推断依据了哪些知识库 ----
function computeRefs(question, reply) {
  const refs = [];
  const text = question + '\n' + (reply || '');
  if (caseNames.some(c => c.name && text.includes(c.name)) || /金奖|银奖|获奖|案例/.test(question)) {
    refs.push('历届获奖案例库');
  }
  if (/提名|申报|报名|怎么报|如何报|时间|截止|流程|材料|资格|2026/.test(question)) {
    refs.push('2026 第十一届提名通知');
  }
  if (/路甬祥|潘云鹤|中国工程院|中国制造2025|红点|iF|发起|背景|是什么|内涵/.test(text)) {
    refs.push('奖项背景知识库');
  }
  return [...new Set(refs)];
}

// ---- 规则式兜底：API 不可用时基于知识库关键词检索回答 ----
function buildMessages(question, history) {
  const messages = [];
  if (Array.isArray(history)) {
    for (const h of history.slice(-8)) {
      if (h && (h.role === 'user' || h.role === 'assistant') && typeof h.content === 'string') {
        messages.push({ role: h.role, content: h.content.slice(0, 2000) });
      }
    }
  }
  messages.push({ role: 'user', content: question });
  return messages;
}
function fallbackAnswer(question) {
  const sourceBlocks = [
    { label: '奖项背景知识库', text: kb },
    { label: '历届获奖案例库', text: casesKb },
    { label: '2026 第十一届提名通知', text: noticeKb },
  ].filter(x => x.text);
  const paras = [];
  for (const block of sourceBlocks) {
    for (const raw of block.text.split(/\n{2,}/)) {
      const text = raw.trim();
      if (text.length > 20 && !text.startsWith('#')) paras.push({ source: block.label, text });
    }
  }
  const q = question.replace(/[？?！!，,。.\s]/g, '');
  const terms = new Set();
  for (let i = 0; i < q.length - 1; i++) terms.add(q.slice(i, i + 2));
  const stop = ['的', '是', '了', '在', '和', '与', '什么', '怎么', '哪些', '一个', '我们', '你们'];
  const scored = paras.map(p => {
    let score = 0;
    for (const t of terms) {
      if (stop.some(s => t === s)) continue;
      const hits = p.text.split(t).length - 1;
      score += hits;
    }
    return { p, score };
  }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);
  if (!scored.length) {
    return '这个问题超出了我目前掌握的资料范围。我主要解答“好设计奖”的发起背景、奖项定位、“好设计”内涵、评奖导向和发展脉络等问题；更细的信息（如申报流程、获奖名单）建议查阅好设计官网（cgd.cmes.org）或中国机械工程学会官网（cmes.org）的最新通知。';
  }
  const top = scored.slice(0, 3).map(x => {
    const text = x.p.text.replace(/\n/g, ' ').replace(/^>\s*/gm, '');
    return '【' + x.p.source + '】' + text;
  });
  return top.join('\n\n') + '\n\n（当前为离线知识库模式：大模型接口暂不可用，以上回答直接摘自平台知识库。）';
}
function llmUnavailableMessage() {
  if (!BASE_URL || !API_KEY) return 'MIMO 模型服务未配置，请在部署环境变量中配置 LLM_BASE_URL 和 LLM_API_KEY。';
  return 'MIMO 模型服务暂时不可用，请稍后重试。';
}

// ---- 调用 Anthropic 兼容接口（非流式） ----
async function askLLM(question, history, model, persona) {
  const messages = buildMessages(question, history);

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), model === MODEL_PRO ? 120000 : 30000);
  try {
    const resp = await fetch(BASE_URL + '/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model,
        max_tokens: 2048,
        system: SYSTEM_PROMPT + personaSuffix(persona),
        messages,
      }),
      signal: controller.signal,
    });
    if (!resp.ok) throw new Error('LLM HTTP ' + resp.status + ': ' + (await resp.text()).slice(0, 300));
    const data = await resp.json();
    const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('').trim();
    if (!text) throw new Error('LLM 返回空内容');
    return text;
  } finally {
    clearTimeout(timer);
  }
}

// ---- 调用 Anthropic 兼容接口（SSE 流式，转发给浏览器） ----
async function askLLMStream(question, history, res, model, persona) {
  const messages = buildMessages(question, history);
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), model === MODEL_PRO ? 180000 : 60000);
  let full = '';
  try {
    const resp = await fetch(BASE_URL + '/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model,
        max_tokens: 2048,
        system: SYSTEM_PROMPT + personaSuffix(persona),
        messages,
        stream: true,
      }),
      signal: controller.signal,
    });
    if (!resp.ok || !resp.body) throw new Error('LLM HTTP ' + resp.status);

    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buf = '';
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop();
      for (const line of lines) {
        const t = line.trim();
        if (!t.startsWith('data:')) continue;
        const payload = t.slice(5).trim();
        if (!payload || payload === '[DONE]') continue;
        try {
          const ev = JSON.parse(payload);
          if (ev.type === 'content_block_delta' && ev.delta && ev.delta.type === 'text_delta' && ev.delta.text) {
            full += ev.delta.text;
            res.write('data: ' + JSON.stringify({ text: ev.delta.text }) + '\n\n');
          }
        } catch (_) { /* 忽略无法解析的行 */ }
      }
    }
    if (!full.trim()) throw new Error('LLM 流式返回空内容');
    res.write('data: ' + JSON.stringify({ done: true, refs: computeRefs(question, full), source: 'llm', model }) + '\n\n');
    res.end();
  } finally {
    clearTimeout(timer);
  }
}

// ---- HTTP 服务 ----
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.webp': 'image/webp', '.ico': 'image/x-icon', '.md': 'text/markdown; charset=utf-8',
};
const API_HEADERS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'GET,POST,OPTIONS',
  'access-control-allow-headers': 'content-type',
};
function writeApiHead(res, status, headers = {}) {
  res.writeHead(status, { ...API_HEADERS, ...headers });
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', c => { data += c; if (data.length > 64 * 1024) req.destroy(); });
    req.on('end', () => resolve(data));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost');
  // 兼容平台预览子路径前缀:/preview/<会话>/<端口>/xxx → /xxx(无前缀时原样)
  let pathname = url.pathname;
  const pm = pathname.match(/^\/preview\/[^/]+\/[^/]+\//);
  if (pm) pathname = pathname.slice(pm[0].length - 1);

  if (pathname.startsWith('/api/') && req.method === 'OPTIONS') {
    writeApiHead(res, 204);
    return res.end();
  }

  if (pathname === '/api/chat' && req.method === 'POST') {
    try {
      const body = JSON.parse(await readBody(req) || '{}');
      const question = String(body.message || '').trim().slice(0, 2000);
      if (!question) {
        writeApiHead(res, 400, { 'content-type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: '消息不能为空' }));
      }
      const model = resolveModel(body, question);
      const persona = typeof body.persona === 'string' ? body.persona : '';
      if (!BASE_URL || !API_KEY) {
        writeApiHead(res, 503, { 'content-type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: llmUnavailableMessage(), source: 'llm_unavailable' }));
      }

      // SSE 流式通道
      if (body.stream) {
        writeApiHead(res, 200, {
          'content-type': 'text/event-stream; charset=utf-8',
          'cache-control': 'no-cache',
          'connection': 'keep-alive',
        });
        try {
          await askLLMStream(question, body.history, res, model, persona);
        } catch (e) {
          console.error('[chat] MIMO 流式调用失败：', e.message);
          res.write('data: ' + JSON.stringify({ done: true, error: llmUnavailableMessage(), source: 'llm_error' }) + '\n\n');
          res.end();
        }
        return;
      }

      // 普通 JSON 通道
      let reply;
      try {
        reply = await askLLM(question, body.history, model, persona);
      } catch (e) {
        console.error('[chat] MIMO 调用失败：', e.message);
        writeApiHead(res, 502, { 'content-type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: llmUnavailableMessage(), source: 'llm_error' }));
      }
      writeApiHead(res, 200, { 'content-type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ reply, source: 'llm', model, refs: computeRefs(question, reply) }));
    } catch (e) {
      writeApiHead(res, 500, { 'content-type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ error: '服务内部错误' }));
    }
    return;
  }

  if (pathname === '/health') {
    res.writeHead(200, { 'content-type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify({ ok: true }));
  }

  // ---- 企业问题留资：产业板块合作意向入口（MVP：JSONL 落盘 .build/）----
  if (pathname === '/api/inquiry' && req.method === 'POST') {
    try {
      const body = JSON.parse(await readBody(req) || '{}');
      const rec = {
        company: String(body.company || '').trim().slice(0, 100),
        industry: String(body.industry || '').trim().slice(0, 50),
        contact: String(body.contact || '').trim().slice(0, 100),
        question: String(body.question || '').trim().slice(0, 2000),
        page: String(body.page || '').slice(0, 100),
        at: new Date().toISOString(),
      };
      if (!rec.company || !rec.question) {
        writeApiHead(res, 400, { 'content-type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify({ error: '企业名称与问题描述为必填项' }));
      }
      rec.id = 'IN-' + Date.now().toString(36).toUpperCase();
      const dir = process.env.DATA_DIR || path.join(ROOT, '.build');
      try { fs.mkdirSync(dir, { recursive: true }); } catch (_) { /* 已存在 */ }
      fs.appendFileSync(path.join(dir, 'inquiries.jsonl'), JSON.stringify(rec) + '\n');
      writeApiHead(res, 200, { 'content-type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify({ ok: true, id: rec.id }));
    } catch (e) {
      writeApiHead(res, 500, { 'content-type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify({ error: '提交失败，请稍后重试' }));
    }
  }

  if (pathname === '/api/health') {
    writeApiHead(res, 200, { 'content-type': 'application/json; charset=utf-8' });
    return res.end(JSON.stringify({ ok: true, llm: Boolean(BASE_URL && API_KEY), model: MODEL, modelPro: MODEL_PRO, personas: Object.keys(PERSONAS) }));
  }

  if (pathname === '/courseware' || pathname.startsWith('/courseware/')) {
    let p = decodeURIComponent(url.pathname.replace(/^\/courseware\/?/, '/'));
    if (p === '/') p = '/index.html';
    const file = path.normalize(path.join(COURSEWARE_DIR, p));
    if (!file.startsWith(COURSEWARE_DIR)) { res.writeHead(403); return res.end(); }
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(404); return res.end('Not Found'); }
      res.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' });
      res.end(buf);
    });
    return;
  }

  // 静态资源
  let p = decodeURIComponent(pathname);
  if (p.endsWith('/')) p += 'index.html';
  const file = path.normalize(path.join(PUBLIC_DIR, p));
  if (!file.startsWith(PUBLIC_DIR)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, buf) => {
    if (err) {
      // SPA 兜底：非资源请求回退到首页；缺失的 .js/.css 必须真 404
      if (!/\.[a-z0-9]+$/i.test(p)) {
        fs.readFile(path.join(PUBLIC_DIR, 'index.html'), (e2, html) => {
          if (e2) { res.writeHead(404); return res.end('Not Found'); }
          res.writeHead(200, { 'content-type': MIME['.html'], 'cache-control': 'no-cache' });
          res.end(html);
        });
      } else {
        res.writeHead(404); res.end('Not Found');
      }
      return;
    }
    res.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream', 'cache-control': 'no-cache' });
    res.end(buf);
  });
});

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';
server.listen(PORT, HOST, () => console.log(`好设计平台已启动: http://${HOST}:${PORT} (LLM: ${BASE_URL && API_KEY ? MODEL : '未配置，规则兜底'})`));
