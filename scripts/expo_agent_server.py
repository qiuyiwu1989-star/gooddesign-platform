# coding: utf-8
"""123 产业创新 Agent 真实后端：模型起草 + 真实检索 + 确定性校验，SSE 推流。

纪律（与 098/108 一致）：
- 模型只起草提议（画像/需求/映射），输出一律标"模型生成·待核"。
- 机制关联的项目必须来自项目库真实检索；模型挑选的项目不在候选集内一律丢弃并如实记录。
- 映射必须有迁移点与差异（transfer 契约）；推荐永远为空。
- 模型失败如实记录并降级（有静态数据包的地方走静态包，没有则如实报错）。
- 只读：不写库、不改任何研究数据。

运行：从运行时 release 启动（scripts 与 04-知识库/项目库 同级）。
  /var/www/innovation-design/venv/bin/python scripts/expo_agent_server.py --port 18792
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import httpx  # noqa: E402
import innovation_knowledge as ik  # noqa: E402
import project_pipeline as pp  # noqa: E402
import project_portal  # noqa: E402

SCHEMA = 'expo-agent-123-1'
MODEL_TIMEOUT = 100
DEPTHS = ('scan', 'standard', 'deep')
DEPTH_NAMES = {'scan': '速览', 'standard': '标准', 'deep': '深研'}
MAX_PLACE_LEN = 24
REPORT_STORE = Path(os.environ.get('EXPO_REPORT_STORE', '/var/lib/innovation-design/expo-reports'))


def safe_place_name(place):
    return re.sub(r'[^0-9A-Za-z\u4e00-\u9fff-]', '', place)[:MAX_PLACE_LEN]


PLACE_SLUGS = {'玉环': 'yuhuan', '嘉善': 'jiashan', '绍兴': 'shaoxing',
               '嘉兴': 'jiaxing', '天台': 'tiantai', '台州': 'taizhou',
               '杭州市西湖区': 'hangzhou-xihu', '南昌市西湖区': 'nanchang-xihu'}
PLACE_LABELS = {slug: label for label, slug in PLACE_SLUGS.items()}


def place_label(place):
    return PLACE_LABELS.get(place, place)


def report_slug(place, proposed=''):
    place = place_label(place)
    if isinstance(proposed, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', proposed):
        return proposed
    if place in PLACE_SLUGS:
        return PLACE_SLUGS[place]
    return 'report-' + hashlib.sha256(place.encode('utf-8')).hexdigest()[:12]


def read_reports():
    records = []
    if not REPORT_STORE.is_dir():
        return records
    for path in REPORT_STORE.glob('*.json'):
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            data['place'] = place_label(data['place'])
            data['pack']['label'] = place_label(data['pack'].get('label', data['place']))
            data['slug'] = data.get('slug') or report_slug(data['place'], data['pack'].get('slug', ''))
            data['id'] = data.get('id') or data['pack'].get('report_id') or 'legacy-' + hashlib.sha256(
                (path.name + str(data['ts'])).encode('utf-8')).hexdigest()[:12]
            records.append((path, data))
        except (ValueError, KeyError):
            continue
    records.sort(key=lambda item: (item[1].get('ts', 0), item[0].stat().st_mtime_ns), reverse=True)
    return records


def store_report(place, pack, curated=False):
    place = place_label(place)
    pack['label'] = place
    pack['slug'] = report_slug(place, pack.get('slug', ''))
    report_id = pack.get('report_id', '')
    if not isinstance(report_id, str) or not re.fullmatch(r'[a-z0-9-]{3,96}', report_id):
        report_id = ''
    if not report_id:
        report_id = f"{pack['slug']}-{time.strftime('%Y%m%d-%H%M%S')}-{time.time_ns() % 0xffffff:x}"
    pack['report_id'] = report_id
    REPORT_STORE.mkdir(parents=True, exist_ok=True)
    target = REPORT_STORE / (safe_place_name(place) + '--' + report_id + '.json')
    body = json.dumps({'schema': 'expo-report-123-2', 'place': place, 'id': report_id,
                       'ts': int(time.time()), 'depth': pack.get('depth', 'standard'),
                       'curated': curated, 'slug': pack['slug'],
                       'counts': {'sectors': len(pack.get('sectors', [])),
                                  'companies': len(pack.get('companies', [])),
                                  'requirements': len(pack.get('requirements', [])),
                                  'matches': sum(len(m['projects']) for m in pack.get('matches', [])),
                                  'opportunities': len(pack.get('opportunities', []))},
                       'pack': pack}, ensure_ascii=False, indent=1)
    target.write_text(body + '\n', encoding='utf-8')
    return target


def list_reports():
    return [{'place': data['place'], 'id': data['id'], 'ts': data['ts'],
             'depth': data.get('depth') or data['pack'].get('depth', 'standard'),
             'industry': (data['pack'].get('target') or {}).get('industry', ''),
             'counts': data['counts'], 'curated': data.get('curated', False),
             'slug': data['slug']} for path, data in read_reports()]


def load_report(place, report_id=None):
    place = place_label(place)
    for path, data in read_reports():
        place_match = data['place'] == place or data['slug'] == place
        if place_match and (report_id is None or data['id'] == report_id):
            return data
    return None


def archive_report(place, report_id=None):
    current = load_report(place, report_id)
    if current is None:
        return None
    for path, data in read_reports():
        if data['id'] == current['id']:
            data['curated'] = True
            path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
            return data
    return None

SYS_JSON = ('你是产业研究助手。只输出严格 JSON，不要输出其他文字。'
            '内容面向地方政府领导与产业部门决策者，使用简洁、稳重、可论证的咨政语言；'
            '避免算法、字段和工程内部术语，重点写产业判断、依据、案例启示和试点建议。'
            '不得编造企业名称、数据或链接；不确定的写"待核"；'
            '所有内容均为智能分析初稿，不能替代实地调研和专题论证。')


def load_env(path='/etc/innovation-expo.env'):
    env = {}
    p = Path(path)
    if p.is_file():
        for line in p.read_text(encoding='utf-8').splitlines():
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def ark_chat(env, user_text, system=SYS_JSON, temperature=0.2, on_token=None, web=False):
    """流式 chat 调用：模型输出随收随报（on_token 收到累计文本尾部）。
    失败抛异常由上层如实记录。"""
    url = env['LLM_BASE_URL'].rstrip('/') + '/chat/completions'
    headers = {'Authorization': 'Bearer ' + env['LLM_API_KEY'], 'Content-Type': 'application/json'}
    body = {
        'model': env.get('LLM_MODEL_PRO') or env['LLM_MODEL'],
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user_text},
        ],
        'temperature': temperature,
        'response_format': {'type': 'json_object'},
        'stream': True,
    }
    if web:
        body['enable_search'] = True
    text = ''
    last_push = 0.0
    with httpx.Client(timeout=MODEL_TIMEOUT) as client:
        with client.stream('POST', url, json=body, headers=headers) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line.startswith('data:'):
                    continue
                data = line[5:].strip()
                if data == '[DONE]':
                    break
                try:
                    chunk = json.loads(data)
                    delta = chunk['choices'][0].get('delta') or {}
                    piece = delta.get('content') or ''
                except (ValueError, KeyError, IndexError):
                    continue
                if not piece:
                    continue
                text += piece
                if on_token and time.time() - last_push > 0.12:
                    last_push = time.time()
                    on_token(text)
    if on_token:
        on_token(text)
    return json.loads(text)


def valid_place(place):
    return isinstance(place, str) and 1 <= len(place.strip()) <= MAX_PLACE_LEN and '\\' not in place


def prompt_theses(place):
    return (
        f'作为产业研究顾问，为「{place}产业 × 获奖设计机制迁移」这项研究起草 2-3 条初始假设，输出 JSON：\n'
        '{"theses": [{"id": "H1", "text": "假设(具体、可证伪)", "angle": "切入角度"}]}\n'
        '要求：假设必须能被证据推翻（不写"前景广阔"这类空话）；'
        '至少 1 条是关于当地产业现状的可核验判断（如结构、集群、升级约束的客观存在），公开资料可以支撑或部分支撑；'
        '其余围绕机制迁移可能（可以暂无公开证据）。')


def prompt_verify(place, theses):
    return (
        f'「{place}」的研究假设：{json.dumps(theses, ensure_ascii=False)}\n'
        '请结合公开资料逐条核证，输出 JSON：\n'
        '{"theses": [{"id": "H1", "status": "supported|partial|unknown", "note": "证据说明"}], '
        '"requirements": [{"id":"N1","text":"需求(具体、可验证、面向产品技术)","from":"来源画像"}]}\n'
        '要求：status 只能三选一，不确定就是 unknown；note 写明依据；requirements 5-8 条面向产品与工艺。')


def prompt_verify_one(place, thesis):
    return (
        f'「{place}」的研究假设：{json.dumps(thesis, ensure_ascii=False)}\n'
        '请联网检索公开资料，专项核证这一条假设，输出 JSON：\n'
        '{"thesis": {"id": "' + str(thesis.get('id', 'H1')) + '", "status": "supported|partial|unknown", "note": "证据与出处（机构/文件/时间）"}}\n'
        '要求：只核证这一条；证据写具体出处；不确定就是 unknown。')


def prompt_overview(place, deep=False):
    return (
        f'请为「{place}」写产业界定与概况，输出 JSON：\n'
        '{"slug": "地名全拼小写，只用字母和连字符", '
        '"headline": "一句话定位(不超过26字)", "intro": "两句产业概况", '
        '"sectors": ["板块1","板块2","板块3"], '
        '"drivers": ["驱动因素1","驱动因素2","驱动因素3"], '
        '"summary_points": ["核心观点1","核心观点2","核心观点3"], '
        '"boundary": "产业界定：本次研究包含什么、不包含什么", '
        '"sources": [{"title": "资料名", "url": "公开链接"}], '
        '"note": "数据边界说明"}\n'
        '要求：观点要具体可讨论，不写空话；不确定的写"待核"；'
        'boundary 一句话说明研究口径；sources 列出联网检索实际参考的公开资料（政府统计、行业协会、权威媒体），2-6 条，只写真实看到的来源'
        + ('，url 必须附上实际检索到的链接' if deep else '，url 不确定就留空') + '。')


def prompt_facts(place, overview):
    return (
        f'请联网深研「{place}」产业的关键事实与对标地区。已知界定：{json.dumps(overview, ensure_ascii=False)}\n'
        '输出 JSON：{"facts": [{"label":"指标或事实名","value":"数值或定性判断",'
        '"note":"年份、口径与证据说明","source":"来源机构或文件","url":"实际公开链接","status":"supported|partial|unknown"}], '
        '"benchmarks": [{"place":"对标地区","similarity":"与本地产业结构的可比性",'
        '"lesson":"值得验证的经验，不是可直接照搬的结论","source":"来源","url":"实际公开链接"}]}\n'
        '要求：facts 3-5 条，优先近三年统计公报、政府或企业年报；数字必须有口径，无证据标 unknown，url 不确定留空；'
        'benchmarks 2-3 个，必须解释可比性和不可照搬部分；不得编造数字或链接。')


def prompt_chain(place, overview):
    return (
        f'基于「{place}」产业概况：{json.dumps(overview, ensure_ascii=False)}\n'
        '请联网拆解产业链并深读代表企业，输出 JSON：\n'
        '{"chain": [{"tier": "上游", "links": ["环节1(说明)","环节2"]}, '
        '{"tier": "中游", "links": ["环节1","环节2"]}, '
        '{"tier": "下游", "links": ["环节1","环节2"]}], '
        '"companies": [{"name":"真实代表企业","field":"领域","reads":["要点1","要点2"],'
        '"proof":"这家企业在研究中证明什么","source":"实际公开资料","url":"实际链接"}], '
        '"personas": [{"name":"画像名","from":"代表企业","profile":"一句画像","pains":["痛点1","痛点2","痛点3"]}]}\n'
        '要求：links 每级 3-5 个；companies 3-6 家，优先真实龙头/专精特新企业，不要无故退回企业群；'
        'proof 必须与本研究问题相关；来源只写实际检索到的资料，不确定留空；personas 2-3 份。')


def prompt_profile(place):
    return (
        f'请为「{place}」做产业画像，输出 JSON：\n'
        '{"headline": "一句话定位(不超过26字)", "intro": "两句产业概况", '
        '"sectors": ["板块1","板块2","板块3"], '
        '"companies": [{"name":"代表性企业或企业群","field":"领域","reads":["要点1","要点2"]}], '
        '"personas": [{"name":"画像名","from":"代表企业","profile":"一句画像","pains":["痛点1","痛点2","痛点3"]}], '
        '"note": "数据边界说明"}\n'
        '要求：companies 3-6 家，personas 2-3 份；不知道的企业不要编，用"XX企业群"表述；'
        '只给产业结构信息，不要给建议。')


def prompt_requirements(place, profile):
    return (
        f'基于「{place}」的产业链与客户画像：{json.dumps(profile, ensure_ascii=False)}\n'
        '把典型客户在产业链各环节的真实痛点转成结构化需求，输出 JSON：\n'
        '{"requirements": [{"id":"N1","text":"需求描述(具体、可验证、面向产品技术)","from":"来源画像"}]}\n'
        '要求 5-8 条；面向产品与工艺，少写财务合规类；每条是具体、可验证的需求；不要给解决方案。')


def prompt_query_terms(place, requirements):
    return (
        f'「{place}」的需求：{json.dumps(requirements, ensure_ascii=False)}\n'
        '为每条需求提议 1-3 个用于检索获奖项目档案的短词（2-6 字，必须是行业通用词，不要地名），输出 JSON：\n'
        '{"queries": [{"question": "需求主题", "terms": ["短词1","短词2"]}]}\n'
        '示例：密封、齿轮、减振、机床、抛光、检测、传动、焊接。')


def prompt_mapping(place, requirements, candidates):
    brief = [{'id': c['id'], 'name': c['name'], 'award': c['award'], 'summary': c['summary'][:80]} for c in candidates[:6]]
    return (
        f'「{place}」的需求：{json.dumps(requirements, ensure_ascii=False)}\n'
        f'候选获奖项目（真实存在，只能从这里选）：{json.dumps(brief, ensure_ascii=False)}\n'
        '为每组需求与项目写双侧映射，输出 JSON：\n'
        '{"matches": [{"question": "需求主题", "projects": [{"id": "项目ID", '
        '"link": "迁移点(只能说是一种解/可类比/一种路径)", '
        '"diff": "差异与不可迁移部分"}]}]}\n'
        '要求：只允许使用候选项目 ID；每条必须有 link 和 diff；不需要的候选可以不选；不要给推荐排序。')


GENERIC_WAVE = ['机器人', '装备', '密封', '传动', '材料', '加工', '检测', '制造', '柔性', '抛光']


def retrieve_candidates(catalog, library, terms, limit_per_term=3, cap=8, found=None, on_hit=None, on_scan=None):
    """真实检索：逐候选与逐已扫描档案报告绝对数量。"""
    found = {} if found is None else found
    scanned = 0
    for pid, idx_cache in library.items():
        pid, idx = pid, idx_cache
        for term in terms:
            hit = ik.search(idx, functions=[term], limit=limit_per_term)
            for m in hit['matches']:
                node = m['node']
                if pid in catalog and pid not in found:
                    found[pid] = {'id': pid, 'term': term}
                    if on_hit:
                        on_hit(pid, term, len(found))
            if len(found) >= cap:
                break
        scanned += 1
        if on_scan:
            on_scan(pid, scanned)
        if len(found) >= cap:
            return found
    return found


def build_indexes(library_root, project_ids):
    out = {}
    for pid in project_ids:
        try:
            out[pid] = ik.build_index(library_root, pid)
        except Exception:
            continue
    return out


def validate_profile(data):
    if not isinstance(data, dict):
        raise ValueError('profile_not_object')
    data.setdefault('headline', '产业基础有待进一步核实')
    data.setdefault('intro', '')
    data.setdefault('note', '本部分为公开资料辅助整理，尚需结合最新资料与企业走访核实。')
    for key in ('sectors', 'companies', 'personas'):
        if not isinstance(data.get(key), list):
            data[key] = []
    data['sectors'] = [str(s)[:30] for s in data['sectors'][:8]]
    companies = []
    for c in data['companies'][:6]:
        if isinstance(c, dict) and c.get('name'):
            companies.append({'name': str(c['name'])[:40], 'field': str(c.get('field', ''))[:40],
                              'reads': [str(r)[:60] for r in (c.get('reads') or [])][:3]})
    personas = []
    for p in data['personas'][:3]:
        if isinstance(p, dict) and p.get('name'):
            personas.append({'name': str(p['name'])[:24], 'from': str(p.get('from', ''))[:40],
                             'profile': str(p.get('profile', ''))[:80],
                             'pains': [str(x)[:40] for x in (p.get('pains') or [])][:4]})
    data['companies'], data['personas'] = companies, personas
    slug = str(data.get('slug', '')).lower()
    data['slug'] = slug if re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', slug) else ''
    return data


def validate_chain(data):
    chain = []
    for tier in (data or {}).get('chain') or []:
        if isinstance(tier, dict) and tier.get('tier'):
            links = [str(x)[:60] for x in (tier.get('links') or [])][:5]
            if links:
                chain.append({'tier': str(tier['tier'])[:8], 'links': links})
    companies = []
    for c in (data or {}).get('companies') or []:
        if isinstance(c, dict) and c.get('name'):
            url = str(c.get('url', ''))[:200]
            companies.append({'name': str(c['name'])[:40], 'field': str(c.get('field', ''))[:40],
                              'reads': [str(r)[:60] for r in (c.get('reads') or [])][:3],
                              'proof': str(c.get('proof', ''))[:120],
                              'source': str(c.get('source', ''))[:80],
                              'url': url if url.startswith('http') else ''})
    personas = []
    for ps in (data or {}).get('personas') or []:
        if isinstance(ps, dict) and ps.get('name'):
            personas.append({'name': str(ps['name'])[:24], 'from': str(ps.get('from', ''))[:40],
                             'profile': str(ps.get('profile', ''))[:80],
                             'pains': [str(x)[:40] for x in (ps.get('pains') or [])][:4]})
    return {'chain': chain[:3], 'companies': companies[:6], 'personas': personas[:3]}


def validate_research(data):
    facts = []
    for f in (data or {}).get('facts') or []:
        if not isinstance(f, dict) or not f.get('label') or not f.get('value'):
            continue
        url = str(f.get('url', ''))[:200]
        status = f.get('status') if f.get('status') in THESIS_STATUS else 'unknown'
        facts.append({'label': str(f['label'])[:50], 'value': str(f['value'])[:90],
                      'note': str(f.get('note', ''))[:140], 'source': str(f.get('source', ''))[:80],
                      'url': url if url.startswith('http') else '', 'status': status})
    benchmarks = []
    for b in (data or {}).get('benchmarks') or []:
        if not isinstance(b, dict) or not b.get('place'):
            continue
        url = str(b.get('url', ''))[:200]
        benchmarks.append({'place': str(b['place'])[:30],
                           'similarity': str(b.get('similarity', ''))[:140],
                           'lesson': str(b.get('lesson', ''))[:140],
                           'source': str(b.get('source', ''))[:80],
                           'url': url if url.startswith('http') else ''})
    return {'facts': facts[:5], 'benchmarks': benchmarks[:3]}


THESIS_STATUS = ('supported', 'partial', 'unknown')


def validate_theses(data):
    out = []
    for x in (data or {}).get('theses') or []:
        if not isinstance(x, dict) or not x.get('text'):
            continue
        status = x.get('status') if x.get('status') in THESIS_STATUS else 'unknown'
        out.append({'id': str(x.get('id') or f'H{len(out) + 1}')[:8], 'text': str(x['text'])[:120],
                    'angle': str(x.get('angle', ''))[:40], 'status': status,
                    'note': str(x.get('note', ''))[:120]})
    return out[:4]


def validate_sources(data):
    out = []
    for s in (data or {}).get('sources') or []:
        if isinstance(s, dict) and s.get('title'):
            url = str(s.get('url', ''))[:200]
            out.append({'title': str(s['title'])[:80], 'url': url if url.startswith('http') else ''})
    return out[:6]


def validate_requirements(data):
    reqs = []
    for i, r in enumerate((data or {}).get('requirements') or [], 1):
        if isinstance(r, dict) and r.get('text'):
            reqs.append({'id': str(r.get('id') or f'N{i}')[:8], 'text': str(r['text'])[:80],
                         'from': str(r.get('from', ''))[:24]})
    return reqs[:8]


def validate_matches(data, catalog, candidate_ids):
    """transfer 契约：只用真实候选；link/diff 必填；丢弃一律记录。"""
    matches, dropped = [], []
    for m in (data or {}).get('matches') or []:
        if not isinstance(m, dict) or not m.get('question'):
            continue
        projs = []
        for ref in m.get('projects') or []:
            if not isinstance(ref, dict):
                continue
            pid, link, diff = ref.get('id'), (ref.get('link') or '').strip(), (ref.get('diff') or '').strip()
            if pid not in candidate_ids or pid not in catalog:
                dropped.append({'id': pid, 'reason': '不在真实候选集'})
                continue
            if not link or not diff:
                dropped.append({'id': pid, 'reason': '迁移点或差异为空，契约拒收'})
                continue
            projs.append({'id': pid, 'link': link[:120], 'diff': diff[:120]})
        if projs:
            matches.append({'question': str(m['question'])[:60], 'projects': projs[:3]})
    return matches[:6], dropped


def event(stream, event_type, **payload):
    body = json.dumps({'schema': SCHEMA, 'type': event_type, **payload}, ensure_ascii=False)
    stream.write(f'data: {body}\n\n'.encode('utf-8'))
    stream.flush()


INDEX_CACHE = {}


def research_indexes(library_root):
    if not INDEX_CACHE:
        lib = Path(library_root)
        seeds = [d.name for d in lib.iterdir() if d.is_dir() and (d / '研究工作区/版本').is_dir()]
        INDEX_CACHE.update(build_indexes(library_root, seeds))
    return INDEX_CACHE


def normalize_target(place, target=None):
    target = target if isinstance(target, dict) else {}
    region = place_label(str(target.get('region') or place).strip())[:40]
    industry = str(target.get('industry') or '').strip()[:40]
    label = region + industry
    question = str(target.get('question') or '').strip()[:120] or f'研究{label}产业的关键约束、企业需求、案例借鉴与试点路径'
    return {'region': region, 'industry': industry, 'label': label, 'question': question}


class Agent:
    def __init__(self, env, library_root):
        self.env = env
        self.library_root = library_root
        self.catalog = {p['id']: p for p in project_portal.catalog(Path(library_root))}

    def run(self, place, stream, depth='standard', target=None):
        target = normalize_target(place, target)
        place = target['label']
        target_brief = ('\n研究对象边界：地区=' + target['region'] + '；产业=' + (target['industry'] or '地方产业整体')
                        + '；问题=' + target['question']
                        + '。外部产业趋势只能作外部参照，本地事实必须针对该地区；'
                          '企业需求须对应具体环节，案例检索由需求驱动，不得把外部案例写成当地已采用。')
        if depth not in DEPTHS:
            depth = 'standard'
        t0 = time.time()
        calls = {'n': 0, 'web': 0}
        def chat(*args, **kw):
            calls['n'] += 1
            if kw.get('web'):
                calls['web'] += 1
            args = list(args)
            args[1] = args[1] + target_brief
            return ark_chat(*args, **kw)
        def log(text, cls=''):
            event(stream, 'log', text=text, cls=cls, t=round(time.time() - t0, 1))
        def activity(stage, kind, n, label):
            event(stream, 'activity', stage=stage, kind=kind, n=n, label=label)

        log(f'收到{DEPTH_NAMES[depth]}研究任务：「{place}」× 好设计创新')
        log('智能分析仅作研究辅助，重要判断均需结合公开资料和实际调研核查', 'warn')

        # S0 破题：初始假设
        event(stream, 'stage', i=0, s='doing')
        log('破题：形成初步判断，并明确需要核查的问题…', 'run')
        def pump0(text):
            event(stream, 'think', stage=0, tail=text[-260:])
        try:
            theses = validate_theses(chat(self.env, prompt_theses(place), on_token=pump0))
        except Exception as exc:
            log(f'破题失败：{type(exc).__name__}，如实记录并中止本次运行', 'warn')
            event(stream, 'error', reason='model_unavailable', detail=type(exc).__name__)
            return
        if not theses:
            log('未产出可证伪的假设，本次运行无法继续（不编造假设）', 'warn')
            event(stream, 'error', reason='empty_theses')
            return
        for k, thesis in enumerate(theses):
            activity(0, 'theses', k + 1, f'形成假设 {thesis["id"]}')
        event(stream, 'blk', i=0, data={'theses': theses})
        log(f'初始假设 {len(theses)} 条，全部待证', 'ok')
        event(stream, 'stage', i=0, s='done')

        # S1 侦察：联网取证 + 产业界定
        event(stream, 'stage', i=1, s='doing')
        log('联网侦察：检索公开资料，起草产业界定与来源…', 'run')
        def pump1(text):
            event(stream, 'think', stage=1, tail=text[-260:])
        try:
            overview = validate_profile(chat(self.env, prompt_overview(place, deep=(depth == 'deep')), on_token=pump1, web=True))
            overview.setdefault('drivers', [])
            overview.setdefault('summary_points', [])
            sources = validate_sources(overview)
            overview.setdefault('boundary', '')
            for k, sector in enumerate(overview['sectors']):
                activity(1, 'sectors', k + 1, f'界定板块 · {sector}')
            for k, source in enumerate(sources):
                activity(1, 'sources', k + 1, f'登记来源 · {source.get("title") or "公开资料"}')
            research = {'facts': [], 'benchmarks': []}
            if depth != 'scan':
                log('追加深研：核查关键事实、指标口径与可比地区…', 'run')
                try:
                    research = validate_research(chat(self.env, prompt_facts(place, overview), on_token=pump1, web=True))
                except Exception as exc:
                    log(f'事实与对标研究失败：{type(exc).__name__}，本段保留为空', 'warn')
            for k, fact in enumerate(research['facts']):
                activity(1, 'facts', k + 1, f'核查事实 · {fact["label"]}')
            for k, benchmark in enumerate(research['benchmarks']):
                activity(1, 'benchmarks', k + 1, f'对标研究 · {benchmark["place"]}')
            event(stream, 'blk', i=1, data={'headline': overview['headline'], 'intro': overview['intro'],
                                            'sectors': overview['sectors'], 'drivers': overview['drivers'],
                                            'boundary': overview['boundary'], 'sources': sources,
                                            'facts': research['facts'], 'benchmarks': research['benchmarks'],
                                            'note': overview['note']})
            log(f'产业界定完成：{len(overview["sectors"])} 板块、{len(sources)} 条来源（公开资料·待核）', 'ok')
        except Exception as exc:
            log(f'模型调用失败：{type(exc).__name__}，如实记录并中止本次运行', 'warn')
            event(stream, 'error', reason='model_unavailable', detail=type(exc).__name__)
            return
        event(stream, 'stage', i=1, s='done')

        # S2 拆解：产业链 + 企业深读
        event(stream, 'stage', i=2, s='doing')
        log('联网拆解产业链，并核查代表企业的研究意义与公开依据…' if depth != 'scan' else '拆解产业链上中下游与代表企业（速览不追加联网）…', 'run')
        def pump2c(text):
            event(stream, 'think', stage=2, tail=text[-260:])
        try:
            chain_data = chat(self.env, prompt_chain(place, overview), on_token=pump2c, web=(depth != 'scan'))
            chain = validate_chain(chain_data)
            profile = {'companies': chain['companies'], 'personas': chain['personas']}
            link_count = 0
            for tier in chain['chain']:
                for link in tier['links']:
                    link_count += 1
                    activity(2, 'links', link_count, f'拆解{tier["tier"]}环节 · {link[:24]}')
            for k, company in enumerate(chain['companies']):
                activity(2, 'companies', k + 1, f'深读企业 · {company["name"]}')
            event(stream, 'blk', i=2, data={'chain': chain['chain'], 'companies': chain['companies']})
            log(f'产业链拆解完成：{len(chain["chain"])} 级 {sum(len(x["links"]) for x in chain["chain"])} 环节', 'ok')
        except Exception as exc:
            log(f'产业链拆解失败：{type(exc).__name__}，如实记录并中止', 'warn')
            event(stream, 'error', reason='model_unavailable', detail=type(exc).__name__)
            return
        event(stream, 'stage', i=2, s='done')

        # S3 求证：假设核证 + 需求
        event(stream, 'stage', i=3, s='doing')
        log('求证：联网核证每条假设，并登记需求…' if depth != 'scan' else '求证：登记需求（速览模式不联网核证，假设如实保持未知）…', 'run')
        def pump2(text):
            event(stream, 'think', stage=3, tail=text[-260:])
        try:
            vdata = chat(self.env, prompt_verify(place, theses), on_token=pump2, web=(depth != 'scan'))
            theses = validate_theses({'theses': [dict(x, **(next((v for v in (vdata or {}).get('theses') or [] if v.get('id') == x['id']), {}))) for x in theses]}) or theses
            if depth == 'scan':
                theses = [dict(x, status='unknown', note='速览模式未联网核证') for x in theses]
            reqs = validate_requirements(vdata)
        except Exception as exc:
            log(f'求证失败：{type(exc).__name__}，如实记录并中止', 'warn')
            event(stream, 'error', reason='model_unavailable', detail=type(exc).__name__)
            return
        if not reqs:
            log('模型未产出有效需求，本次运行无法继续（不编造需求）', 'warn')
            event(stream, 'error', reason='empty_requirements')
            return
        for k, req in enumerate(reqs):
            activity(3, 'requirements', k + 1, f'登记需求 {req["id"]}')
        if depth == 'standard':
            for k, th in enumerate(theses):
                activity(3, 'checked', k + 1, f'核证 {th["id"]} · {th["status"]}')
        if depth == 'deep':
            for k, th in enumerate(theses):
                log(f'逐条核证 {th["id"]}（{k + 1}/{len(theses)}）：专项检索公开资料…', 'run')
                try:
                    vd = chat(self.env, prompt_verify_one(place, th), on_token=pump2, web=True)
                    one_in = (vd or {}).get('thesis') or {}
                    one_in.setdefault('id', th['id'])
                    one_in.setdefault('text', th['text'])
                    one = validate_theses({'theses': [one_in]})
                    if one:
                        th['status'] = one[0]['status']
                        if one[0]['note']:
                            th['note'] = one[0]['note']
                except Exception as exc:
                    log(f'{th["id"]} 专项核证失败：{type(exc).__name__}，保留批量核证结果', 'warn')
                activity(3, 'checked', k + 1, f'完成专项核证 {th["id"]}')
        n_sup = sum(1 for x in theses if x['status'] == 'supported')
        n_par = sum(1 for x in theses if x['status'] == 'partial')
        n_unk = sum(1 for x in theses if x['status'] == 'unknown')
        event(stream, 'blk', i=3, data={'requirements': reqs, 'theses': theses})
        log(f'核查完成：依据较充分 {n_sup} / 部分印证 {n_par} / 待核实 {n_unk}；整理需求 {len(reqs)} 条，均需企业确认', 'ok')
        event(stream, 'stage', i=3, s='done')

        # S4 映射：检索词 + 真实检索 + 双侧映射
        event(stream, 'stage', i=4, s='doing')
        log('根据企业需求形成案例检索线索…', 'run')
        def pump3(text):
            event(stream, 'think', stage=4, tail=text[-200:])
        try:
            qdata = chat(self.env, prompt_query_terms(place, reqs), on_token=pump3)
            qgroups = [(str(q.get('question', ''))[:60],
                        [str(x)[:12] for x in (q.get('terms') or []) if 2 <= len(str(x)) <= 12][:3])
                       for q in (qdata or {}).get('queries') or [] if isinstance(q, dict)]
        except Exception as exc:
            log(f'检索词提议失败：{type(exc).__name__}，改用板块词', 'warn')
            qgroups = [(s, [s]) for s in overview['sectors']]
        terms = sorted({x for _, ts in qgroups for x in ts}) or [place]
        for k, term in enumerate(terms):
            activity(4, 'terms', k + 1, f'形成检索线索 · {term}')
        indexes = research_indexes(self.library_root)
        log(f'在 {len(indexes)} 个研究版项目档案（全库 {len(self.catalog)} 项）里做真实逐字检索…', 'run')
        scan_state = {'n': 0}
        def archive_scanned(pid, n):
            scan_state['n'] += 1
            activity(4, 'scanned', scan_state['n'], f'完成档案检索 · {self.catalog[pid]["name"]}')
        def candidate_hit(pid, term, n):
            activity(4, 'candidates', n, f'召回项目 · {self.catalog[pid]["name"]}')
        found = retrieve_candidates(self.catalog, indexes, terms, cap=8, on_hit=candidate_hit, on_scan=archive_scanned)
        wave = 1
        if len(found) < 2:
            log('首轮召回不足，放宽到行业通用机制词再检一轮（仍为真实命中）', 'run')
            found = retrieve_candidates(self.catalog, indexes, GENERIC_WAVE, cap=10, found=found, on_hit=candidate_hit, on_scan=archive_scanned)
            wave = 2
        candidate_ids = set(found)
        log(f'真实召回 {len(candidate_ids)} 个候选项目（第 {wave} 轮检索词 {len(terms)} 个）', 'ok')
        if not candidate_ids:
            log('本次未找到合适的参考案例，如实保留研究缺口', 'warn')
            event(stream, 'blk', i=4, data={'matches': [], 'candidates': 0, 'terms': len(terms),
                                            'scanned': len(indexes), 'rounds': wave,
                                            'note': '本次未找到合适案例，建议补充资料后再研究。'})
            event(stream, 'stage', i=4, s='done')
        else:
            candidates = [dict(self.catalog[pid]) for pid in sorted(candidate_ids)]
            matches = []
            try:
                hinted = [{'id': r['id'], 'text': r['text']} for r in reqs]
                if qgroups:
                    hinted = [{'id': r['id'], 'text': r['text'], 'topic': qgroups[i % len(qgroups)][0]}
                              for i, r in enumerate(reqs)]
                def pump4(text):
                    event(stream, 'think', stage=4, tail=text[-260:])
                raw = chat(self.env, prompt_mapping(place, hinted, candidates), on_token=pump4)
                matches, dropped = validate_matches(raw, self.catalog, candidate_ids)
                for d in dropped:
                    log(f"丢弃：{d['id']}（{d['reason']}）", 'warn')
                match_count = 0
                for group in matches:
                    for ref in group['projects']:
                        match_count += 1
                        activity(4, 'matches', match_count, f'完成案例对照 · {self.catalog[ref["id"]]["name"]}')
                event(stream, 'blk', i=4, data={'matches': matches, 'candidates': len(candidate_ids),
                                                'terms': len(terms), 'scanned': len(indexes), 'rounds': wave})
                log(f'形成 {sum(len(m["projects"]) for m in matches)} 条案例关联（适用条件与差异已列）', 'ok')
            except Exception as exc:
                log(f'案例对照暂时中断：{type(exc).__name__}，本段保留为空', 'warn')
                event(stream, 'blk', i=4, data={'matches': [], 'candidates': len(candidate_ids),
                                                'terms': len(terms), 'scanned': len(indexes), 'rounds': wave,
                                                'note': '案例对照暂时中断，本段保留为空。'})
            event(stream, 'stage', i=4, s='done')

        # S5 综合：机会方向与核心观点
        event(stream, 'stage', i=5, s='doing')
        log('结合案例启示形成创新方向，并提出试点验证建议…', 'run')
        try:
            op_prompt = (f'基于「{place}」的需求 {json.dumps(reqs, ensure_ascii=False)} 与案例关联，'
                         '面向地方政府领导，以简洁咨政语言形成创新方向。'
                         '输出 JSON：{"opportunities": [{"title":"方向","text":"一句说明",'
                         '"basis":"关联需求与案例名称（奖项）","verify":"试点第一步",'
                         '"falsify":"出现什么结果就需要调整或停止该方向"}]}，'
                         '2-3 个；写清依据与试点前提；不做推荐排序；不要使用内部技术术语。')
            def pump5(text):
                event(stream, 'think', stage=5, tail=text[-260:])
            ops = (chat(self.env, op_prompt, on_token=pump5) or {}).get('opportunities') or []
            ops = [{'title': str(o.get('title', ''))[:40], 'text': str(o.get('text', ''))[:120],
                    'basis': str(o.get('basis', ''))[:100], 'verify': str(o.get('verify', ''))[:80],
                    'falsify': str(o.get('falsify', ''))[:100]}
                   for o in ops[:3] if isinstance(o, dict) and o.get('title')]
        except Exception as exc:
            log(f'方向研究暂时中断：{type(exc).__name__}，本段保留为空', 'warn')
            ops = []
        for k, opportunity in enumerate(ops):
            activity(5, 'opportunities', k + 1, f'形成方向 · {opportunity["title"]}')
        event(stream, 'blk', i=5, data={'opportunities': ops})
        log(f'形成 {len(ops)} 个可供论证的方向，均附试点建议', 'ok')
        event(stream, 'stage', i=5, s='done')

        # S6 成稿：装配研究报告
        event(stream, 'stage', i=6, s='doing')
        log('整理形成正式研究报告…', 'run')
        risks = ['企业情况主要来自公开资料，具体需求与合作意向需通过走访确认',
                 '案例做法需结合本地工艺、成本和应用环境开展试点验证',
                 '平台检索可能存在尚未覆盖的相关案例，必要时可补充专题检索']
        if depth == 'scan':
            risks.insert(0, '本次为快速梳理，初步判断尚未逐项联网核查，使用时应以进一步核实为前提')
        if not candidate_ids:
            risks.insert(0, '本次未检索到合适的参考案例，建议补充资料后开展专题研究')
        used_projects = {ref['id'] for group in matches for ref in group['projects']} if candidate_ids else set()
        project_cards = {}
        for pid in used_projects:
            item = self.catalog[pid]
            cover = str(item.get('cover', ''))
            if cover and not cover.startswith('http'):
                cover = 'https://haoshejiguan.com/inno/portal/' + cover.lstrip('/')
            project_cards[pid] = {'name': item['name'], 'award': item['award'], 'unit': item.get('unit', ''),
                                  'summary': item.get('summary', ''), 'research': bool(item.get('research')),
                                  'cover': cover}
        metrics = {'depth': depth, 'theses': len(theses),
                   'theses_status': {'supported': n_sup, 'partial': n_par, 'unknown': n_unk},
                   'sources': len(sources), 'sectors': len(overview['sectors']),
                   'facts': len(research['facts']), 'benchmarks': len(research['benchmarks']),
                   'chain_links': sum(len(x['links']) for x in chain['chain']),
                   'companies': len(profile['companies']), 'personas': len(profile['personas']),
                   'requirements': len(reqs), 'terms': len(terms), 'retrieval_rounds': wave,
                   'scanned': len(indexes), 'catalog': len(self.catalog),
                   'candidates': len(candidate_ids),
                   'matches': sum(len(m['projects']) for m in matches) if candidate_ids else 0,
                   'opportunities': len(ops),
                   'model_calls': calls['n'], 'web_calls': calls['web'],
                   'elapsed_s': round(time.time() - t0)}
        pack = {'label': place, 'target': target, 'slug': report_slug(place, overview.get('slug', '')),
                'depth': depth, 'headline': overview['headline'], 'intro': overview['intro'],
                'sectors': overview['sectors'], 'drivers': overview['drivers'],
                'summary_points': overview['summary_points'], 'theses': theses,
                'boundary': overview.get('boundary', ''), 'sources': sources,
                'facts': research['facts'], 'benchmarks': research['benchmarks'],
                'chain': chain['chain'], 'companies': profile['companies'],
                'note': overview['note'], 'personas': profile['personas'],
                'requirements': reqs, 'projects': project_cards,
                'matches': matches if candidate_ids else [],
                'opportunities': ops, 'risks': risks, 'metrics': metrics}
        try:
            store_report(place, pack)
            log('报告已冻结存档，可在首页地图点亮查看', 'ok')
        except Exception as exc:
            log(f'报告存档失败：{type(exc).__name__}（不影响本次展示）', 'warn')
        event(stream, 'pack', data=pack)
        event(stream, 'done')
        event(stream, 'stage', i=6, s='done')
        log('研究完成：报告可打印，引用项目可回查档案', 'ok')


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    env = None
    library_root = None

    def log_message(self, *args):
        pass

    def do_POST(self):
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path != '/api/archive':
            self.send_error(404)
            return
        origin = self.headers.get('Origin')
        if origin and urllib.parse.urlsplit(origin).netloc != self.headers.get('Host'):
            self.send_error(403)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length <= 0 or length > 2048:
                raise ValueError('invalid_length')
            payload = json.loads(self.rfile.read(length).decode('utf-8'))
            place = payload.get('place', '').strip() if isinstance(payload, dict) else ''
            report_id = payload.get('id', '').strip() if isinstance(payload, dict) else ''
            if not valid_place(place) or (report_id and not re.fullmatch(r'[a-z0-9-]{3,96}', report_id)):
                raise ValueError('invalid_place')
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_error(400)
            return
        report = archive_report(place, report_id or None)
        if report is None:
            self.send_error(404)
            return
        body = json.dumps({'ok': True, 'report': {'place': report['place'], 'id': report['id'],
                                                  'ts': report['ts'], 'curated': report['curated'],
                                                  'counts': report['counts']}}, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path = parsed.path
        if path == '/api/places':
            body = json.dumps({'schema': SCHEMA, 'places': list_reports()}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == '/api/report':
            query = urllib.parse.parse_qs(parsed.query)
            place_q = query.get('place', [''])[0].strip()
            report_id = query.get('id', [''])[0].strip()
            if report_id and not re.fullmatch(r'[a-z0-9-]{3,96}', report_id):
                report_id = 'invalid'
            report = load_report(place_q, report_id or None) if valid_place(place_q) else None
            if report is None:
                self.send_error(404)
                return
            body = json.dumps(report, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path in ('/health', '/api/health'):
            body = json.dumps({'ok': True, 'service': 'expo-agent', 'model': bool(self.env.get('LLM_API_KEY'))}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path != '/api/run':
            self.send_error(404)
            return
        query = urllib.parse.parse_qs(parsed.query)
        place = query.get('place', [''])[0].strip()
        if not valid_place(place):
            self.send_error(400, 'invalid_place')
            return
        target = {'region': query.get('region', [''])[0].strip(),
                  'industry': query.get('industry', [''])[0].strip(),
                  'question': query.get('question', [''])[0].strip()}
        depth = query.get('depth', ['standard'])[0].strip()
        if depth not in DEPTHS:
            depth = 'standard'
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Accel-Buffering', 'no')
        self.send_header('Connection', 'close')
        self.end_headers()
        try:
            Agent(self.env, self.library_root).run(place, self.wfile, depth=depth, target=target)
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=18792)
    parser.add_argument('--library', default=str(ROOT / '04-知识库/项目库'))
    args = parser.parse_args()
    Handler.env = load_env()
    Handler.library_root = args.library
    if not Handler.env.get('LLM_API_KEY'):
        print('warning: 无模型密钥，模型调用将如实失败', flush=True)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print('expo agent server on loopback', args.port, flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
