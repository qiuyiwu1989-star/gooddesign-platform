"""Explicit client-request bridge. Does not verify customer facts, identity or write back to an app."""
from method_engine import Engine, digest


def prepare_request(request, object_name, boundary, stage='frame'):
    if not isinstance(request,dict):raise ValueError('request_must_be_object')
    if request.get('scenario_type') not in {'simulated','customer_supplied'}:
        raise ValueError('declare_simulated_or_customer_supplied_scope')
    for key in ('task_id','title'):
        if not isinstance(request.get(key),str) or not request[key].strip() or len(request[key])>200:
            raise ValueError('invalid_request:'+key)
    for key in ('needs','functions','constraints','unknowns'):
        rows=request.get(key,[])
        if not isinstance(rows,list) or len(rows)>100 or any(not isinstance(x,str) or not x.strip() or len(x)>2000 for x in rows):
            raise ValueError('invalid_request_terms:'+key)
    if not request.get('needs') and not request.get('functions'):raise ValueError('missing_need_or_function')
    if not isinstance(object_name,str) or not object_name.strip() or not isinstance(boundary,str) or not boundary.strip():
        raise ValueError('object_and_boundary_must_be_explicit_not_inferred_from_title')
    if request.get('expert_certified') is True or request.get('engineering_validated') is True:
        raise ValueError('client_request_cannot_self_certify')
    fingerprint=digest(request)
    task={'task_id':'app-'+digest(request['task_id'])[:24],'revision':'request-'+fingerprint[:24],
          'object':object_name,'desired_outcome':request['title'],'boundary':boundary,'stage':stage,'delivery_level':'concept',
          'source_request':{'task_id':request['task_id'],'sha256':fingerprint,'scenario_type':request['scenario_type'],
                            'nature':'client_statements_not_observed_engineering_facts','identity_verification':'host_responsibility_not_performed_here'},
          'needs':request.get('needs',[]),'requested_functions':request.get('functions',[]),
          'declared_constraints':request.get('constraints',[]),'declared_unknowns':request.get('unknowns',[])}
    check=Engine().match(task)
    if check['issues']:return {'status':'blocked','issues':check['issues'],'task':task}
    return {'status':'prepared_unverified_client_context','task':task,'source_request_sha256':fingerprint,
            'source_facts_modified':False,'expert_certified':False}


def application_envelope(run_state):
    source=run_state['task'].get('source_request')
    if not source:raise ValueError('run_has_no_application_request_binding')
    artifacts=[x['artifact'] for x in run_state['submissions']]
    unknowns=[]
    for artifact in artifacts:
        p=artifact['payload']
        unknowns.extend(p.get('unknowns',p.get('uncovered_questions',p.get('validation_questions',[]))))
    return {'schema':'method-application-result-0.2','run_id':run_state['run_id'],'run_revision':run_state['revision'],
            'source_request':source,'task_revision':run_state['task']['revision'],'artifacts':artifacts,
            'unknowns':list(dict.fromkeys(unknowns)),'status':'research_drafts_pending_review',
            'expert_certified':False,'engineering_validated':False,'writeback_performed':False,
            'note':'应用负责权限、确认与版本化保存；此结果不写回案例事实或修改旧应用运行。'}
