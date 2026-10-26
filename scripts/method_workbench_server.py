"""ML-006 local single-user workspace. Explicit single-node model execution; no public deployment."""
import argparse
import hashlib
import json
import mimetypes
import secrets
import sqlite3
import subprocess
import threading
from method_workbench_review import review as candidate_review
from method_workbench_execution import Execution
from method_workbench_morphology import progress as morphology_progress
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / '04-知识库/创新方法库/深度方法库-v0.1.0'
PILOT = ROOT / 'output/rubber-tapping-pilot'
WEB = ROOT / 'extensions/method-workbench'
DEFAULT_DB = ROOT / 'output/method-workbench-private/demands.sqlite'
EXECUTABLE = {'R48', 'R14', 'R17', 'R36', 'R44', 'R42'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


class Store:
    def __init__(self, path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT, rev INTEGER, result TEXT, PRIMARY KEY(id,rev))')
            db.execute('CREATE TABLE IF NOT EXISTS revisions (id TEXT, rev INTEGER, created TEXT, payload TEXT, sha TEXT, PRIMARY KEY(id,rev))')
        self.seed()

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def seed(self):
        with self.connect() as db:
            if db.execute("SELECT 1 FROM revisions WHERE id='RUBBER-20261026'").fetchone():
                return
        packet = json.loads((PILOT / '需求包.json').read_text())
        self.save({'id': 'RUBBER-20261026', 'expected_revision': 0, 'title': '割胶机器人改进研究',
                   'problem': '出胶效率、胶乳洁净与树体保护需要共同研究；现场工况与目标值待客户确认。',
                   'goal': '形成可验证的机械改进候选路线', 'conditions': ['', '', ''],
                   'requirements': packet['requirements'], 'selected_methods': ['R48', 'R14', 'R17', 'R36', 'R44', 'R42'],
                   'note': '从ML-005研究包导入；非客户批准。',
                   'baseline_packet_sha256': hashlib.sha256(canonical(packet).encode()).hexdigest()})

    def save(self, data):
        required = {'id', 'expected_revision', 'title', 'problem', 'goal', 'conditions', 'requirements', 'selected_methods', 'note'}
        if not isinstance(data, dict) or not required <= data.keys():
            raise ValueError('需求字段不完整')
        ident = data['id']
        if not isinstance(ident, str) or not ident or len(ident) > 80 or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in ident):
            raise ValueError('任务ID无效')
        if type(data['expected_revision']) is not int or data['expected_revision'] < 0:
            raise ValueError('版本号无效')
        for key, limit in [('title', 160), ('problem', 20000), ('goal', 4000), ('note', 4000)]:
            if not isinstance(data[key], str) or len(data[key]) > limit:
                raise ValueError('文字长度或类型无效：' + key)
        if not data['title'].strip() or not data['problem'].strip():
            raise ValueError('请填写研究名称和问题')
        if not isinstance(data['conditions'], list) or len(data['conditions']) != 3 or any(not isinstance(v, str) or len(v) > 8000 for v in data['conditions']):
            raise ValueError('条件必须为三项文字')
        methods = data['selected_methods']
        valid_ids = {m['research_id'] for m in json.loads((LIB / '目录.json').read_text())['methods']}
        if not isinstance(methods, list) or any(not isinstance(x, str) or x not in valid_ids for x in methods) or len(set(methods)) != len(methods):
            raise ValueError('方法ID无效')
        reqs = data['requirements']
        if not isinstance(reqs, list) or len(reqs) > 100:
            raise ValueError('需求条目数量无效')
        ids = set()
        for r in reqs:
            if not isinstance(r, dict) or not all(isinstance(r.get(k), str) and len(r[k]) <= 8000 for k in ['id', 'title', 'need', 'acceptance_proposal']):
                raise ValueError('需求条目格式无效')
            if not r['id'] or r['id'] in ids or not r['title'].strip():
                raise ValueError('需求ID须唯一，标题不能为空')
            ids.add(r['id'])
            if r.get('hard_proposal') is not None and type(r['hard_proposal']) is not bool:
                raise ValueError('硬约束只能为是、否或待确认')
            # This editor cannot promote research proposals into customer approval.
            r['status'] = 'research_proposed_not_customer_confirmed'
        payload = {k: data[k] for k in required - {'expected_revision'}}
        payload['approved'] = False
        payload['selected_methods'] = methods
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current = db.execute('SELECT MAX(rev) FROM revisions WHERE id=?', (ident,)).fetchone()[0] or 0
            if current != data['expected_revision']:
                raise FileExistsError('已有更新版本，请先导出当前草稿，再载入最新版本比较')
            # Preserve immutable original experiment lineage; never trust a client-supplied SHA.
            previous = db.execute('SELECT payload FROM revisions WHERE id=? ORDER BY rev LIMIT 1', (ident,)).fetchone()
            if previous:
                baseline = json.loads(previous[0]).get('baseline_packet_sha256')
            elif ident == 'RUBBER-20261026':
                baseline = data.get('baseline_packet_sha256')
            else:
                baseline = None
            if baseline:
                payload['baseline_packet_sha256'] = baseline
            raw = canonical(payload)
            db.execute('INSERT INTO revisions VALUES (?,?,?,?,?)', (ident, current + 1, datetime.now(timezone.utc).isoformat(), raw, hashlib.sha256(raw.encode()).hexdigest()))
        return self.get(ident)

    def get(self, ident, rev=None):
        with self.connect() as db:
            if rev is None:
                row = db.execute('SELECT * FROM revisions WHERE id=? ORDER BY rev DESC LIMIT 1', (ident,)).fetchone()
            else:
                row = db.execute('SELECT * FROM revisions WHERE id=? AND rev=?', (ident, rev)).fetchone()
            if not row:
                raise KeyError('找不到需求版本')
            history = [dict(r) for r in db.execute('SELECT rev,created,sha FROM revisions WHERE id=? ORDER BY rev DESC', (ident,))]
        return {'data': json.loads(row['payload']), 'revision': row['rev'], 'sha256': row['sha'], 'created': row['created'], 'history': history}

    def listing(self):
        with self.connect() as db:
            rows = db.execute('SELECT r.* FROM revisions r JOIN (SELECT id,MAX(rev) rev FROM revisions GROUP BY id) x ON r.id=x.id AND r.rev=x.rev ORDER BY created DESC').fetchall()
        return [{'id': r['id'], 'revision': r['rev'], 'title': json.loads(r['payload'])['title'], 'created': r['created']} for r in rows]


def make_server(port=8786, db_path=DEFAULT_DB):
    store = Store(Path(db_path))
    token = secrets.token_urlsafe(32)
    run_lock = threading.Lock()
    execution = Execution(Path(db_path).resolve().parent / 'execution.sqlite')
    engine_db = str(Path(db_path).resolve().parent / 'engine.sqlite')

    def bridge(request):
        runtime = ROOT / '.runtime/pipeline/bin/python'
        if not runtime.is_file():
            raise ValueError('缺少固定MCP运行环境，请检查.runtime/pipeline')
        request['db'] = engine_db
        process = subprocess.run([str(runtime), str(ROOT / 'scripts/method_workbench_bridge.py')],
                                 input=json.dumps(request), text=True, capture_output=True, timeout=45, cwd=ROOT)
        if process.returncode:
            raise ValueError('MCP连接失败，未启动模型调用，请稍后重试')
        return json.loads(process.stdout)


    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code, value, content_type='application/json; charset=utf-8'):
            body = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def trusted(self):
            host = self.headers.get('Host', '')
            allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            origin = self.headers.get('Origin')
            return host in allowed and (not origin or origin == 'http://' + host) and self.headers.get('Sec-Fetch-Site') not in {'cross-site'}

        def do_GET(self):
            if not self.trusted():
                return self.send(403, {'error': '仅允许本机同源访问'})
            path = unquote(urlsplit(self.path).path)
            try:
                if path == '/api/session':
                    return self.send(200, {'csrf': token, 'mode': 'local_single_user', 'model_connected': None, 'model_execution_available': (ROOT / '.runtime/pipeline/bin/python').is_file(), 'model_connection_status': 'checked_on_explicit_generation_not_preverified'})
                if path == '/api/methods':
                    data = json.loads((LIB / '目录.json').read_text())
                    for m in data['methods']:
                        m['executable_contract'] = m['research_id'] in EXECUTABLE
                    return self.send(200, data)
                if path == '/api/demands':
                    return self.send(200, store.listing())
                if path.startswith('/api/demands/'):
                    parts = path.split('/')
                    if len(parts) not in (4, 5):
                        raise KeyError()
                    return self.send(200, store.get(parts[3], int(parts[4]) if len(parts) == 5 else None))
                if path.startswith('/api/execution/'):
                    ident = path[len('/api/execution/'):]
                    with store.connect() as db:
                        row = db.execute('SELECT result FROM runs WHERE id=? ORDER BY rev DESC LIMIT 1', (ident,)).fetchone()
                    if not row:
                        raise KeyError()
                    meta = json.loads(row[0])
                    rid = meta['created']['run_id']
                    state = bridge({'action': 'get_run', 'run_id': rid})
                    jobs=execution.listing(rid); evidence=execution.evidence(rid)
                    kinds={s['artifact']['type'] for s in state['submissions']}
                    morph=morphology_progress(state,evidence,jobs) if {'ProblemBrief','FunctionModel'}<=kinds else None
                    return self.send(200, {'meta':meta, 'state':state, 'jobs':jobs, 'evidence':evidence, 'notes':execution.notes(rid),'morphology':morph,'candidate_review':candidate_review(state,evidence)})
                if path.startswith('/api/run/'):

                    ident = path[len('/api/run/'):]
                    with store.connect() as db:
                        row = db.execute('SELECT result FROM runs WHERE id=? ORDER BY rev DESC LIMIT 1', (ident,)).fetchone()
                    return self.send(200, json.loads(row[0]) if row else None)
                if path == '/api/pilot':
                    r = json.loads((PILOT / 'engine-report.json').read_text())
                    return self.send(200, {'run_id': r['run_id'], 'mode': r['mode'], 'task': r['task'], 'demand_packet_sha256': r['demand_packet_sha256'], 'expert_certified': False})
                if path.startswith('/library/'):
                    base, rel = LIB, path[len('/library/'):]
                    if not (rel.startswith('methods/') or '/' not in rel) or Path(rel).suffix not in {'.html', '.css', '.js'}:
                        raise KeyError()
                elif path.startswith('/reports/'):
                    base, rel = PILOT, path[len('/reports/'):]
                    if rel not in {'index.html', '需求报告.html', '创新方案报告.html', '推理记录.html', 'reports.css', 'vendor/tokens.css', 'vendor/design-system.css'}:
                        raise KeyError()
                else:
                    base, rel = WEB, 'app/index.html' if path == '/' else path.lstrip('/')
                    if not (rel.startswith('app/') or rel in {'workbench.css', 'vendor/tokens.css', 'vendor/design-system.css'}):
                        raise KeyError()
                target = (base / rel).resolve()
                if base.resolve() not in target.parents or not target.is_file():
                    raise KeyError()
                return self.send(200, target.read_bytes(), mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
            except (KeyError, ValueError):
                return self.send(404, {'error': '未找到该资源'})
            except Exception:
                return self.send(500, {'error': '读取失败，请重试或检查本地文件'})

        def do_POST(self):
            if not self.trusted() or self.headers.get('X-CSRF-Token') != token:
                return self.send(403, {'error': '访问校验失败，请刷新后重试'})
            if urlsplit(self.path).path not in {'/api/demands', '/api/cases/search', '/api/runs', '/api/execute', '/api/cases/sources', '/api/evidence/attach', '/api/evidence/preview', '/api/execution/note'}:
                return self.send(404, {'error': '不存在该操作'})
            try:
                length = int(self.headers.get('Content-Length', 0))
                if length <= 0 or length > 300000:
                    return self.send(413, {'error': '内容大小无效'})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('请求必须是JSON对象')
                path = urlsplit(self.path).path
                if path == '/api/cases/sources':
                    if not isinstance(data.get('project_id'), str) or len(data['project_id']) > 100:
                        raise ValueError('案例ID无效')
                    return self.send(200, bridge({'action': 'case_sources', 'project_id': data['project_id']}))
                if path in ('/api/execute', '/api/evidence/attach', '/api/evidence/preview', '/api/execution/note'):
                    if not isinstance(data.get('id'), str) or type(data.get('revision')) is not int:
                        raise ValueError('需求版本无效')
                    with store.connect() as db:
                        row = db.execute('SELECT result FROM runs WHERE id=? AND rev=?', (data['id'], data['revision'])).fetchone()
                    if not row:
                        raise ValueError('请先建立对应版本的运行计划')
                    meta = json.loads(row[0]); rid = meta['created']['run_id']
                    if path == '/api/execution/note':
                        return self.send(201, {'notes':execution.notes(rid,data.get('text'))})
                    if path in ('/api/evidence/attach','/api/evidence/preview'):
                        if path=='/api/evidence/attach' and data.get('preview_id'):
                            if not isinstance(data['preview_id'],str) or len(data['preview_id'])>80:
                                raise ValueError('预览ID无效')
                            evidence=execution.preview(rid,ident=data['preview_id'])
                            return self.send(200,{'evidence':execution.attach(rid,evidence),'read_scope':'selected_frozen_excerpt_not_full_source'})
                        for field in ('project_id','source_id'):
                            if not isinstance(data.get(field), str) or len(data[field]) > 100:
                                raise ValueError('案例/来源ID无效')
                        if data.get('chunks_sha256') and (not isinstance(data['chunks_sha256'], str) or len(data['chunks_sha256']) != 64):
                            raise ValueError('文本修订指纹无效')
                        offset=data.get('offset',0); maximum=data.get('max_chars',800)
                        if type(offset) is not int or not 0<=offset<=100000 or type(maximum) is not int or not 50<=maximum<=4000:
                            raise ValueError('文本块位置须为0—100000整数，摘录长度须为50—4000整数')
                        revision=data.get('research_revision')
                        if revision is not None and (not isinstance(revision,str) or len(revision)>100):
                            raise ValueError('研究版本无效')
                        if data.get('chunks_sha256') and not revision:
                            raise ValueError('选择冻结文本指纹时还需指定研究版本')
                        result = bridge({'action':'case_evidence','project_id':data['project_id'],'source_id':data['source_id'],'chunks_sha256':data.get('chunks_sha256'),'research_revision':revision,'offset':offset,'max_chars':maximum,'preview':path=='/api/evidence/preview'})
                        if path=='/api/evidence/preview':
                            if result.get('status')=='needs_text_revision_choice':return self.send(200,result)
                            if not result.get('evidence'):raise ValueError('该位置没有文本块，请调整位置')
                            return self.send(200,{**result,'preview_id':execution.preview(rid,result['evidence'])})
                        if not result.get('evidence'):
                            return self.send(422, {'error':'该来源没有可直接选择的摘录，请明确文本修订SHA。'+json.dumps(result.get('available',[]),ensure_ascii=False),'details':result})
                        return self.send(200, {'evidence':execution.attach(rid, result['evidence']), 'read_scope':'first_chunk_excerpt_not_full_source'})
                    if data.get('action') not in ('propose','submit'):
                        raise ValueError('执行动作无效')
                    state = bridge({'action':'get_run','run_id':rid})
                    done = {x['method'] for x in state['submissions']}
                    node = next((n for n in state['plan']['nodes'] if n['node_id'] not in done), None)
                    if not node:
                        raise ValueError('所有节点已提交，请阅读报告；修改需求请保存新版本')
                    request = {'action':data['action'], 'method':node['node_id'], 'db':engine_db, 'run_id':rid,
                               'expected_revision':state['revision'], 'evidence':execution.evidence(rid), 'notes':execution.notes(rid)}
                    if data['action']=='propose' and node['node_id']=='R17':
                        morph=morphology_progress(state,request['evidence'],execution.listing(rid))
                        request.update(input_fingerprint=morph['input_fingerprint'])
                        if morph['next_function']:
                            request.update(action='morph_option',function_id=morph['next_function'])
                        else:
                            request.update(action='morph_assemble',parts=morph['parts'])
                    if data['action'] == 'submit':
                        if not isinstance(data.get('artifact'),dict):
                            raise ValueError('请提供待校验的产物JSON对象')
                        request['artifact'] = data['artifact']
                        note=data.get('review_note','')
                        if not isinstance(note,str) or len(note)>4000:
                            raise ValueError('评审说明格式无效')
                        request['review_note']=note
                    return self.send(202, execution.enqueue(request))
                if path == '/api/cases/search':
                    query = data.get('query')
                    if not isinstance(query, str) or not query.strip() or len(query) > 300:
                        raise ValueError('请填写1—300字符的案例关键词')
                    return self.send(200, bridge({'action': 'case_search', 'query': query}))
                if path == '/api/runs':
                    if not isinstance(data.get('id'), str) or type(data.get('revision')) is not int:
                        raise ValueError('任务版本无效')
                    saved = store.get(data['id'], data['revision'])
                    with run_lock:
                        with store.connect() as db:
                            row = db.execute('SELECT result FROM runs WHERE id=? AND rev=?', (data['id'], data['revision'])).fetchone()
                        if row:
                            return self.send(200, json.loads(row[0]))
                        d = saved['data']
                        task = {'task_id': d['id'], 'revision': 'workbench-v' + str(saved['revision']),
                                'object': d['title'], 'desired_outcome': d['goal'] or d['problem'],
                                'boundary': '研究提案，未客户确认；' + d['conditions'][2],
                                'delivery_level': 'concept', 'stage': 'frame', 'demand_packet_sha256': saved['sha256'],
                                'demand_snapshot': d, 'input_status': 'research_proposed_not_customer_confirmed'}
                        created = bridge({'action': 'create_run', 'task': task})
                        result = {'demand_id': d['id'], 'demand_revision': saved['revision'], 'demand_sha256': saved['sha256'],
                                  'created': created, 'automatic_generation': False,
                                  'note': '实际方法MCP计划，尚无执行产物；所选内容方法不等同六节点参考执行链'}
                        if created.get('status') == 'blocked':
                            return self.send(422, {'error':'运行计划被阻断，请检查任务条件','details':result})
                        with store.connect() as db:
                            db.execute('INSERT INTO runs VALUES (?,?,?)', (d['id'], saved['revision'], json.dumps(result, ensure_ascii=False)))
                        return self.send(201, result)
                return self.send(201, store.save(data))
            except FileExistsError as e:
                return self.send(409, {'error': str(e)})
            except (ValueError, TypeError) as e:
                return self.send(400, {'error': str(e)})
            except Exception:
                return self.send(500, {'error': '保存失败，当前输入仍保留，请导出草稿并重试'})

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    return server


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=8786)
    p.add_argument('--db', type=Path, default=DEFAULT_DB)
    args = p.parse_args()
    server = make_server(args.port, args.db)
    print(f'创新工作台 http://127.0.0.1:{server.server_port}', flush=True)
    server.serve_forever()
