"""Version-pinned private research proposals. No customer confirmation or remote access."""
import copy
import hashlib
import json
from pathlib import Path
from innovation_loop_decision import validate_requirement,compare_routes,validate_research_action
ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'output/innovation-loop-024/decision/tasks-v1'
IDS=('rubber-v1','gear-v1','polish-v1')
def _sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def _check(bundle):
    validate_requirement(bundle['requirement']);compare_routes(bundle['requirement'],bundle['routes'])
    route_refs={(r['id'],r['revision']) for r in bundle['routes']}
    for action in bundle['actions']:
        validate_research_action(action)
        if (action['route_ref']['id'],action['route_ref']['revision']) not in route_refs:raise ValueError('action from different task')
    if len(bundle['routes'])!=3 or len(bundle['actions'])!=3:raise ValueError('three routes/actions required')
    for ref in bundle['source_refs']:
        path=(ROOT/ref['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or _sha(path)!=ref['sha256']:raise ValueError('source_missing_or_changed')
    return bundle

def list_tasks():
    return [{'task_id':i,'title':load_task(i)['title'],'input_status':'research_proposal_not_customer_confirmed'} for i in IDS]

def load_task(task_id):
    if task_id not in IDS:raise ValueError('unknown_task')
    return copy.deepcopy(_check(json.loads((DIRECTORY/(task_id+'.json')).read_text())))
