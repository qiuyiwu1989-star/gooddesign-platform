"""ML024 private, pure decision helpers. Validation checks structure, not truth."""
import copy
import json
import math
from datetime import datetime


def _base(r):
    if not isinstance(r, dict) or r.get('schema_version') != '0.1.0':
        raise ValueError('schema_version must be 0.1.0')
    if not isinstance(r.get('id'), str) or not r['id'].strip():
        raise ValueError('id required')
    if type(r.get('revision')) is not int or r['revision'] < 1:
        raise ValueError('positive integer revision required')
    try:
        json.dumps(r, allow_nan=False)
    except (ValueError, TypeError) as e:
        raise ValueError('finite JSON values required') from e


def _ref(r):
    if not isinstance(r, dict) or not isinstance(r.get('id'), str) or not r['id'].strip() or type(r.get('revision')) is not int or r['revision'] < 1:
        raise ValueError('exact id/revision reference required')


def validate_requirement(record):
    _base(record)
    if record.get('status') not in ('draft', 'proposed', 'confirmed'):
        raise ValueError('invalid requirement status')
    if not isinstance(record.get('goal'), str) or not record['goal'].strip():
        raise ValueError('goal required')
    for key in ('budget', 'operating_context', 'acceptance_threshold'):
        if key not in record:
            raise ValueError(key+' must be explicit')
        if record[key] is None and not record.get('missing_reason', {}).get(key):
            raise ValueError(key+' unknown needs missing_reason')
    budget = record['budget']
    if budget is not None:
        if not isinstance(budget, dict) or type(budget.get('value')) not in (int, float) or not math.isfinite(budget['value']) or budget['value'] < 0 or not isinstance(budget.get('unit'), str) or not budget['unit'].strip():
            raise ValueError('budget requires finite nonnegative value and unit')
    if record['status'] == 'confirmed':
        c = record.get('confirmation', {})
        if not all(isinstance(c.get(k), str) and c[k].strip() for k in ('actor', 'at')) or not c.get('evidence_ref'):
            raise ValueError('confirmation actor/time/evidence required')
        try:
            at = datetime.fromisoformat(c['at'].replace('Z','+00:00'))
            if at.tzinfo is None: raise ValueError('timezone required')
        except ValueError as e:
            raise ValueError('confirmation at must be timezone-aware ISO8601') from e
        _ref(c['evidence_ref'])
    return copy.deepcopy(record)


def diff_requirements(before, after):
    validate_requirement(before); validate_requirement(after)
    if before['id'] != after['id'] or after['revision'] <= before['revision']:
        raise ValueError('same id with strictly newer revision required')
    changes = [{'field': k, 'before': before.get(k), 'after': after.get(k)}
               for k in sorted(set(before)|set(after)) if k != 'revision' and before.get(k) != after.get(k)]
    return {'requirement_id': before['id'], 'from_revision': before['revision'],
            'to_revision': after['revision'], 'changes': changes,
            'route_review_required': bool(changes),
            'note': 'Existing routes remain bound to their original requirement revision.'}


def compare_routes(requirement, routes, preferences=None):
    validate_requirement(requirement)
    if not isinstance(routes, list) or len(routes) < 2:
        raise ValueError('at least two routes required')
    rows=[]; ids=set()
    for route in routes:
        _base(route)
        if route['id'] in ids: raise ValueError('duplicate route id')
        ids.add(route['id']); _ref(route.get('requirement_ref'))
        if route['requirement_ref'] != {'id': requirement['id'], 'revision': requirement['revision']}:
            raise ValueError('stale or different requirement reference')
        if not all(isinstance(route.get(k), str) and route[k].strip() for k in ('mechanism','next_action')) or not isinstance(route.get('conditions'), list) or not route['conditions'] or not all(isinstance(x,str) and x.strip() for x in route['conditions']):
            raise ValueError('mechanism, conditions and next_action required')
        if route.get('constraint_status') not in ('unknown','conflict','supported'):
            raise ValueError('explicit constraint_status required')
        costs=route.get('cost')
        if costs is None and not route.get('missing_reason',{}).get('cost'):
            raise ValueError('unknown cost needs reason')
        rows.append(copy.deepcopy(route))
    if preferences is not None:
        if not isinstance(preferences,dict) or not preferences.get('actor') or not preferences.get('criteria'):
            raise ValueError('preference actor and criteria required')
    suggestions=[{'route_ref':{'id':r['id'],'revision':r['revision']},'status':'blocked_by_constraint_conflict' if r['constraint_status']=='conflict' else 'conditional_research_only','conditions':copy.deepcopy(r['conditions']),'key_unknowns':copy.deepcopy(r.get('missing_reason',{})),'next_action':r['next_action'],'execution_authorized':False} for r in rows]
    return {'schema_version':'0.1.0', 'requirement_ref':{'id':requirement['id'],'revision':requirement['revision']},
            'routes':rows, 'conditional_suggestions':suggestions, 'preferences':copy.deepcopy(preferences), 'ranking':None,
            'recommendation_status':'requires_evidence_and_preference_review',
            'blocked_route_ids':[r['id'] for r in rows if r['constraint_status']=='conflict'],
            'research_ready':False,
            'note':'No calibrated utility model or engineering approval supplied; unknown values stay null.'}


def validate_feedback(record):
    _base(record)
    for key in ('requirement_ref','route_ref','claim_ref'): _ref(record.get(key))
    if record.get('kind') not in ('opinion','reported_observation','reported_trial'):
        raise ValueError('invalid feedback kind')
    if not all(isinstance(record.get(k),str) and record[k].strip() for k in ('actor_role','basis')):
        raise ValueError('actor_role and basis required')
    auth=record.get('authorization')
    if not isinstance(auth,dict) or set(auth) != {'internal_research','public','training'} or any(type(v) is not bool for v in auth.values()):
        raise ValueError('explicit boolean authorization required')
    if record.get('apply_to_facts',False) or record.get('change_score',False):
        raise ValueError('feedback cannot automatically change facts or scores')
    result=copy.deepcopy(record); result['processing_status']='pending_review'
    return result


def _strings(value, label):
    if not isinstance(value, list) or not value or not all(isinstance(x,str) and x.strip() for x in value):
        raise ValueError(label+' must be nonempty string list')

def validate_route_transfer(record):
    """Validate proposed analogy discipline, never certify semantic equivalence."""
    _base(record)
    for key in ('source_anchor','target_anchor'):
        anchor=record.get(key)
        _ref(anchor)
        if not isinstance(anchor.get('locator'),str) or not anchor['locator'].strip():
            raise ValueError(key+' requires locator')
    for key in ('differences','assumptions','falsification'):
        _strings(record.get(key),key)
    if record.get('transfer_kind') != 'structure_hypothesis' or record.get('copy_parameter') is not False:
        raise ValueError('only structural hypothesis, explicit no parameter copying')
    if record.get('nature') != 'hypothesized':
        raise ValueError('transfer remains hypothesized')
    result=copy.deepcopy(record);result['semantic_review_status']='pending'
    return result

def validate_research_action(record):
    _base(record)
    _ref(record.get('route_ref'))
    for key in ('question','observation','decision_rule','stop_condition'):
        if not isinstance(record.get(key),str) or not record[key].strip():
            raise ValueError(key+' required')
    _strings(record.get('hypotheses'),'hypotheses')
    for key in ('resources','responsible_actor'):
        value=record.get(key)
        if value is None:
            if not isinstance(record.get('missing_reason',{}).get(key),str) or not record['missing_reason'][key].strip():
                raise ValueError(key+' unknown needs reason')
        elif key=='resources':_strings(value,key)
        elif not isinstance(value,str) or not value.strip():raise ValueError(key+' must be string')
    approval=record.get('professional_approval')
    if not isinstance(approval,dict) or approval.get('status') not in ('pending','required','not_required_with_reason','approved'):
        raise ValueError('professional approval status required')
    if approval['status']=='approved':
        if not isinstance(approval.get('actor'),str) or not approval['actor'].strip():raise ValueError('approval actor required')
        _ref(approval.get('evidence_ref'))
    elif approval['status']=='not_required_with_reason' and not approval.get('reason'):
        raise ValueError('approval exemption needs reason')
    result=copy.deepcopy(record)
    result['execution_authorized']=False
    result['note']='Structure validation does not authorize physical testing or establish approval authenticity.'
    return result
