"""Single-user local run persistence; no remote/multitenant authorization claim."""
import json
import os
import sqlite3
import uuid
from pathlib import Path
from method_engine import Engine, ROOT, digest, implementation_hashes
from method_engine_contracts import contract


class Store:
    def __init__(self, path=None, engine=None):
        self.path = Path(path or os.environ.get('METHOD_ENGINE_DB') or ROOT/'04-知识库/创新方法库/运行数据-v0.2/runs.sqlite3')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = engine or Engine()
        with self.connect() as db:
            db.executescript('CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, task TEXT NOT NULL, plan TEXT NOT NULL, revision INTEGER NOT NULL);'
                             'CREATE TABLE IF NOT EXISTS submissions(run_id TEXT, key TEXT, hash TEXT NOT NULL, data TEXT NOT NULL, response TEXT NOT NULL, PRIMARY KEY(run_id,key));')

    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        return db

    def create(self, task, target='R42', artifacts=None, evidence=None):
        plan = self.engine.plan(task, target, artifacts, evidence)
        if plan['status'] == 'blocked': return plan
        rid = 'run-'+uuid.uuid4().hex
        with self.connect() as db:
            db.execute('INSERT INTO runs VALUES(?,?,?,0)', (rid, json.dumps(task), json.dumps(plan)))
        return {'run_id': rid, 'revision': 0, 'status': 'planned_not_executed', 'plan': plan}

    def get(self, run_id):
        with self.connect() as db:
            row = db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
            if row is None: raise ValueError('run_not_found')
            submissions = [json.loads(x['data']) for x in db.execute('SELECT data FROM submissions WHERE run_id=? ORDER BY rowid', (run_id,))]
        return {'run_id': run_id, 'revision': row['revision'], 'task': json.loads(row['task']),
                'plan': json.loads(row['plan']), 'submissions': submissions, 'expert_certified': False}

    def submit(self, run_id, expected_revision, key, method, artifact, evidence=None):
        if not isinstance(key, str) or not 1 <= len(key) <= 100: raise ValueError('invalid_idempotency_key')
        data = {'method': method, 'artifact': artifact, 'evidence': evidence or []}
        fingerprint = digest(data)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT * FROM submissions WHERE run_id=? AND key=?', (run_id, key)).fetchone()
            if previous:
                if previous['hash'] != fingerprint: raise ValueError('idempotency_payload_conflict')
                return json.loads(previous['response'])
            row = db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
            if row is None: raise ValueError('run_not_found')
            if row['revision'] != expected_revision: raise ValueError('stale_run_revision')
            plan, task = json.loads(row['plan']), json.loads(row['task'])
            if plan.get('implementation_hashes')!=implementation_hashes():raise ValueError('engine_implementation_changed_replan_required')
            node = next((n for n in plan['nodes'] if n['node_id'] == method), None)
            if node is None: raise ValueError('method_not_in_plan')
            if node['contract_sha256'] != digest(contract(method)): raise ValueError('contract_changed_replan_required')
            current = self.engine.get(method, 'overview')
            if current['content_sha256'] != node['method_content_sha256']: raise ValueError('method_changed_replan_required')
            prior = [json.loads(x['data']) for x in db.execute('SELECT data FROM submissions WHERE run_id=?', (run_id,))]
            if any(x['method'] == method for x in prior): raise ValueError('method_already_submitted_create_new_run_for_revision')
            done = {x['method'] for x in prior}
            if not set(node['depends_on']) <= done: raise ValueError('dependencies_not_submitted')
            inputs=list(plan['inputs_snapshot']['artifacts'])+[x['artifact'] for x in prior]
            evmap={}
            evrows=list(plan['inputs_snapshot']['evidence'])+[e for x in prior for e in x['evidence']]+list(evidence or [])
            for ev in evrows:
                key_id=ev.get('id')
                if key_id in evmap and digest(evmap[key_id])!=digest(ev):raise ValueError('evidence_identity_conflict')
                evmap[key_id]=ev
            checked = self.engine.check_output(method,artifact,task,inputs,list(evmap.values()))
            if checked['status'] == 'blocked': return checked
            revision = expected_revision+1
            response = {'run_id': run_id, 'revision': revision, 'artifact_id': artifact['artifact_id'],
                        'status': 'recorded_not_expert_approved', 'artifact_sha256': checked['artifact_sha256'], 'expert_certified': False}
            db.execute('INSERT INTO submissions VALUES(?,?,?,?,?)', (run_id, key, fingerprint, json.dumps(data), json.dumps(response)))
            db.execute('UPDATE runs SET revision=? WHERE id=?', (revision, run_id))
            return response
