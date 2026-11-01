"""ML024 separate private append-only records. No writes to source archives."""
import copy
import hashlib
import json
import sqlite3
from pathlib import Path
from innovation_loop_decision import validate_requirement, compare_routes, validate_feedback, validate_route_transfer, validate_research_action

ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'output/innovation-loop-024/integration/loop.sqlite3'

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()

class LoopStore:
    def __init__(self,path=DEFAULT):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS records(kind TEXT,id TEXT,revision INTEGER,payload TEXT,sha TEXT,PRIMARY KEY(kind,id,revision))')
    def connect(self):
        return sqlite3.connect(self.path,timeout=15)
    def get(self,kind,ident,revision):
        if type(revision) is not int or revision<1:raise ValueError('exact positive revision required')
        with self.connect() as db:
            row=db.execute('SELECT payload,sha FROM records WHERE kind=? AND id=? AND revision=?',(kind,ident,revision)).fetchone()
        if not row:raise ValueError('record_not_found')
        obj=json.loads(row[0])
        if digest(obj)!=row[1]:raise ValueError('record_hash_mismatch')
        return obj
    def put(self,kind,obj,expected_revision=0):
        obj=copy.deepcopy(obj)
        if kind=='requirement':obj=validate_requirement(obj)
        elif kind=='route':
            ref=obj.get('requirement_ref',{});rq=self.get('requirement',ref.get('id'),ref.get('revision'))
            # The decision API compares multiple routes. Validate a candidate alongside a distinct structural copy.
            twin=copy.deepcopy(obj);twin['id']=str(obj.get('id'))+'-validation-only'
            compare_routes(rq,[obj,twin])
        elif kind=='feedback':
            obj=validate_feedback(obj)
            if not obj['authorization']['internal_research']:raise ValueError('internal_processing_not_authorized')
            for key,target in [('requirement_ref','requirement'),('route_ref','route'),('claim_ref','claim')]:
                ref=obj[key];linked=self.get(target,ref['id'],ref['revision'])
                if target=='route' and linked['requirement_ref']!=obj['requirement_ref']:raise ValueError('feedback_requirement_mismatch')
                if target=='claim' and linked['route_ref']!=obj['route_ref']:raise ValueError('feedback_claim_mismatch')
        elif kind=='clarification':
            from innovation_loop_tasks import load_task
            task=load_task(obj.get('task_id'));rq=task['requirement'];ref={'id':rq['id'],'revision':rq['revision']}
            if obj.get('requirement_ref')!=ref:raise ValueError('clarification_requirement_mismatch')
            self.get('requirement',ref['id'],ref['revision'])
            if obj.get('schema_version')!='0.1.0' or type(obj.get('revision')) is not int or obj['revision']<1 or not isinstance(obj.get('id'),str) or not obj['id']:raise ValueError('invalid_clarification_identity')
            if obj.get('field') not in ('budget','operating_context','acceptance_threshold') or obj.get('status')!='pending_review':raise ValueError('clarification_is_pending_only')
            if not all(isinstance(obj.get(k),str) and obj[k].strip() and len(obj[k])<=maxlen for k,maxlen in [('value',8000),('actor',200)]):raise ValueError('clarification_text_required')
        elif kind=='experience':
            from innovation_loop_experience import validate_experience
            obj=validate_experience(obj)
        elif kind=='transfer':
            obj=validate_route_transfer(obj)
            for key,target in [('source_anchor','experience'),('target_anchor','requirement')]:
                ref=obj[key];self.get(target,ref['id'],ref['revision'])
        elif kind=='action':
            obj=validate_research_action(obj)
            ref=obj['route_ref'];self.get('route',ref['id'],ref['revision'])
        elif kind=='claim':
            if obj.get('schema_version')!='0.1.0' or type(obj.get('revision')) is not int or obj['revision']<1 or not obj.get('id'):raise ValueError('invalid claim')
            if obj.get('nature') not in ('source_statement','inferred','hypothesized') or not all(isinstance(obj.get(k),str) and obj[k].strip() for k in ['text','basis']):raise ValueError('claim nature/text/basis required')
            ref=obj.get('route_ref',{});self.get('route',ref.get('id'),ref.get('revision'))
        else:raise ValueError('unsupported kind')
        if type(expected_revision) is not int or expected_revision<0:raise ValueError('expected_revision required')
        sha=digest(obj)
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing=db.execute('SELECT sha FROM records WHERE kind=? AND id=? AND revision=?',(kind,obj['id'],obj['revision'])).fetchone()
            if existing:
                if existing[0]==sha:return {'status':'already_saved','sha256':sha}
                raise ValueError('immutable_revision_conflict')
            current=db.execute('SELECT COALESCE(MAX(revision),0) FROM records WHERE kind=? AND id=?',(kind,obj['id'])).fetchone()[0]
            if current!=expected_revision or obj['revision']!=current+1:raise ValueError('revision_conflict')
            db.execute('INSERT INTO records VALUES(?,?,?,?,?)',(kind,obj['id'],obj['revision'],json.dumps(obj,ensure_ascii=False,allow_nan=False),sha))
        return {'status':'saved','sha256':sha}
    def list_records(self,kind):
        with self.connect() as db:rows=db.execute('SELECT id,revision FROM records WHERE kind=? ORDER BY id,revision',(kind,)).fetchall()
        return [self.get(kind,*r) for r in rows]
