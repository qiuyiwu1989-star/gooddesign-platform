"""Verify paired run configuration and provider usage without inferring expert quality."""
import json
from method_engine import ROOT


def summarize():
    base=ROOT/'output/method-engine-ML003/paired-comparison'
    status=json.loads((base/'status.json').read_text());rows=[];usage={}
    for task in status['tasks']:
        if not task['paired']:continue
        configs={}
        for condition in ('engine','ordinary'):
            folder=base/'private'/(task['id']+'-'+condition)
            execution=json.loads((folder/'execution.json').read_text())
            cmd=execution['command'];settings=[cmd[i+1] for i,x in enumerate(cmd[:-1]) if x=='-c']
            configs[condition]={'settings':settings,'timeout':execution['timeout_seconds'],'tools_disabled':execution['tools_disabled']}
            total=usage.setdefault(condition,{'input_tokens':0,'cached_input_tokens':0,'output_tokens':0,'completed_calls':0})
            events=[json.loads(line) for line in (folder/'model-events.jsonl').read_text().splitlines()]
            completed=[e['usage'] for e in events if e.get('type')=='turn.completed' and isinstance(e.get('usage'),dict)]
            if len(completed)!=1:raise ValueError('unexpected_completed_event_count')
            for key in ('input_tokens','cached_input_tokens','output_tokens'):total[key]+=completed[0].get(key,0)
            total['completed_calls']+=1
        rows.append({'task':task['id'],'configuration_equal':configs['engine']==configs['ordinary'],'configuration':configs['engine']})
    report={'status':'execution_configuration_checked_not_quality_assessed','paired_tasks':len(rows),'pairs':rows,
            'all_pair_configurations_equal':all(r['configuration_equal'] for r in rows) if rows else None,
            'provider_reported_usage':usage,'expert_preference':None,'expert_acceptance':None,
            'note':'Token counts are reported model usage, not billing or quality. Catalog context increases input; output length must not be a quality proxy.'}
    (base/'execution-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'paired_tasks':len(rows),'configuration_equal':report['all_pair_configurations_equal']},ensure_ascii=False))


if __name__=='__main__':summarize()
