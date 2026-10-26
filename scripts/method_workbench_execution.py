"""ML-007 durable single-node jobs. Worker survives UI/server disconnection."""
import argparse
import hashlib
import json
import os
import signal
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def alignment(task, method, artifact):
    if method != 'R48':
        return []
    baseline = task.get('demand_snapshot', {}).get('requirements', [])
    actual = artifact.get('payload', {}).get('requirements', [])
    found = {r.get('id'): r for r in actual}
    issues = []
    for r in baseline:
        a = found.get(r['id'])
        if not a:
            issues.append({'code': 'baseline_requirement_missing', 'id': r['id']})
            continue
        if a.get('hard') is not r.get('hard_proposal'):
            issues.append({'code': 'baseline_requirement_hardness_changed', 'id': r['id']})
        if a.get('status') == 'confirmed':
            issues.append({'code': 'research_requirement_promoted_without_customer_confirmation', 'id': r['id']})
        if r.get('acceptance_proposal') and a.get('acceptance') != r['acceptance_proposal']:
            issues.append({'code': 'baseline_acceptance_changed', 'id': r['id']})
    return issues


class Execution:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, run_id TEXT, method TEXT, action TEXT, state TEXT,
                created REAL, updated REAL, request TEXT, result TEXT, pid INTEGER);
                CREATE UNIQUE INDEX IF NOT EXISTS active_run ON jobs(run_id) WHERE state IN ('queued','running');
                CREATE TABLE IF NOT EXISTS evidence (run_id TEXT,id TEXT,payload TEXT,PRIMARY KEY(run_id,id));
                CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY,run_id TEXT,created REAL,text TEXT);
                CREATE TABLE IF NOT EXISTS previews (id TEXT PRIMARY KEY,run_id TEXT,payload TEXT,created REAL);''')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def evidence(self, run_id):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT payload FROM evidence WHERE run_id=? ORDER BY id', (run_id,))]

    def notes(self, run_id, text=None):
        with self.connect() as db:
            if text is not None:
                if not isinstance(text,str) or not text.strip() or len(text)>4000:
                    raise ValueError('评审备注需为1—4000字符')
                db.execute('INSERT INTO notes VALUES (?,?,?,?)',('note-'+uuid.uuid4().hex,run_id,time.time(),text))
            return [dict(r) for r in db.execute('SELECT id,created,text FROM notes WHERE run_id=? ORDER BY created',(run_id,))]

    def preview(self, run_id, evidence=None, ident=None):
        with self.connect() as db:
            if ident is not None:
                row=db.execute('SELECT payload FROM previews WHERE id=? AND run_id=?',(ident,run_id)).fetchone()
                if not row:raise ValueError('预览不存在或不属于当前运行，请重新预览')
                return json.loads(row[0])
            ident='preview-'+uuid.uuid4().hex
            db.execute('INSERT INTO previews VALUES (?,?,?,?)',(ident,run_id,json.dumps(evidence,ensure_ascii=False),time.time()))
            return ident

    def attach(self, run_id, evidence):
        with self.connect() as db:
            if db.execute("SELECT 1 FROM jobs WHERE run_id=? AND state IN ('queued','running')", (run_id,)).fetchone():
                raise FileExistsError('执行中不能修改证据，请等待当前任务结束')
            stored=[json.loads(r[0]) for r in db.execute('SELECT payload FROM evidence WHERE run_id=?',(run_id,))]
            def signature(e):return tuple(e.get(k) for k in ('project_id','source_id','source_revision','chunk_id','text_sha256'))
            signatures={signature(e) for e in stored}; identities={e['id']:e for e in stored}
            for e in evidence:
                if hashlib.sha256(e['text'].encode()).hexdigest() != e['text_sha256']:
                    raise ValueError('证据指纹不匹配')
                if e['id'] in identities and identities[e['id']]['text_sha256']!=e['text_sha256']:
                    raise ValueError('相同证据ID已有不同摘录，请使用预览选择新摘录')
                if signature(e) in signatures:continue
                signatures.add(signature(e));identities[e['id']]=e
                db.execute('INSERT OR IGNORE INTO evidence VALUES (?,?,?)', (run_id, e['id'], json.dumps(e, ensure_ascii=False)))
        return self.evidence(run_id)

    def listing(self, run_id):
        with self.connect() as db:
            rows = db.execute('SELECT * FROM jobs WHERE run_id=? ORDER BY created', (run_id,)).fetchall()
            output = []
            for row in rows:
                r = dict(row)
                if r['state'] in ('queued', 'running') and time.time() - r['updated'] > 300:
                    # No automatic resume: a prior model call might already have consumed quota.
                    db.execute("UPDATE jobs SET state='interrupted',updated=? WHERE id=? AND state IN ('queued','running')", (time.time(), r['id']))
                    r['state'] = 'interrupted'
                r.pop('request')
                r['result'] = json.loads(r['result']) if r['result'] else None
                output.append(r)
        return output

    def enqueue(self, request, spawn=True):
        if request['action'] not in ('propose', 'submit', 'morph_option', 'morph_assemble'):
            raise ValueError('不支持的执行动作')
        ident = 'job-' + uuid.uuid4().hex
        now = time.time()
        try:
            with self.connect() as db:
                db.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,NULL)', (ident, request['run_id'], request['method'], request['action'], 'queued', now, now, json.dumps(request, ensure_ascii=False), None))
        except sqlite3.IntegrityError:
            raise FileExistsError('该运行已有任务正在执行，请等待结果')
        if spawn:
            try:
                process = subprocess.Popen([str(ROOT / '.runtime/pipeline/bin/python'), str(Path(__file__).resolve()), '--worker', str(self.path), ident], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                with self.connect() as db:
                    db.execute('UPDATE jobs SET pid=? WHERE id=?', (process.pid, ident))
            except Exception:
                self.finish(ident, 'failed', {'error': '后台进程启动失败，请检查固定运行环境'})
                raise
        return {'job_id': ident, 'status': 'queued'}

    def finish(self, ident, state, result):
        with self.connect() as db:
            db.execute('UPDATE jobs SET state=?,updated=?,result=? WHERE id=?', (state, time.time(), json.dumps(result, ensure_ascii=False), ident))

    def worker(self, ident):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT request,state FROM jobs WHERE id=?', (ident,)).fetchone()
            if not row or row['state'] != 'queued':
                return
            db.execute("UPDATE jobs SET state='running',updated=? WHERE id=?", (time.time(), ident))
            request = json.loads(row['request'])
        request['key'] = ident
        try:
            p = subprocess.Popen([sys.executable, str(ROOT / 'scripts/method_workbench_bridge.py')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT, start_new_session=True)
            try:
                stdout, stderr = p.communicate(json.dumps(request), timeout=240)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGTERM)
                try:
                    p.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.communicate()
                raise
            if p.returncode:
                # Raw provider stderr stays out of UI; details remain in existing model-call audit logs.
                self.finish(ident, 'failed', {'error': '模型或MCP执行失败（可能为额度、超时或检查错误）；未自动重试。可查看本机模型调用审计记录。'})
                return
            result = json.loads(stdout)
            if request['action']=='submit':
                result['artifact'] = request['artifact']
            if request.get('review_note'):
                result['host_or_user_review_note'] = request['review_note']
                result['review_scope'] = 'not_independent_domain_expert_review'
            state = 'failed' if result.get('status')=='model_call_failed' else ('blocked' if result.get('status') == 'blocked' else ('part' if request['action']=='morph_option' else ('draft' if request['action'] in ('propose','morph_assemble') else 'submitted')))
            self.finish(ident, state, result)
        except subprocess.TimeoutExpired:
            self.finish(ident, 'failed', {'error': '执行超过240秒，未自动重试。请先检查运行与模型审计记录。'})
        except Exception:
            self.finish(ident, 'failed', {'error': '后台执行异常；未自动重试，请检查本地数据及运行环境'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker', nargs=2)
    args = parser.parse_args()
    if args.worker:
        Execution(args.worker[0]).worker(args.worker[1])
