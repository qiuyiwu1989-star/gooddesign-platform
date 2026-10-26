"""ML-007 actual local HTTP -> worker -> MCP pilot. One proposal per remaining node."""
import json
import time
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8788'
OUT=ROOT/'output/method-workbench-check/ml007'
OUT.mkdir(parents=True,exist_ok=True)
if (OUT/'actual-execution.json').exists():
    raise ValueError('Archived pilot exists; create a new explicit experiment instead of rerunning it')
TOKEN=json.load(urlopen(BASE+'/api/session'))['csrf']

def call(path,body=None):
    h={'Content-Type':'application/json','X-CSRF-Token':TOKEN}
    return json.load(urlopen(Request(BASE+path,headers=h,data=json.dumps(body).encode() if body is not None else None)))

def enqueue(action,artifact=None):
    body={'id':'RUBBER-20261026','revision':1,'action':action}
    if artifact:body['artifact']=artifact
    j=call('/api/execute',body)['job_id']
    deadline=time.time()+290
    while time.time()<deadline:
        s=call('/api/execution/RUBBER-20261026')
        job=next(x for x in s['jobs'] if x['id']==j)
        if job['state'] not in ('queued','running'):
            print(job['method'],action,job['state'],flush=True)
            return job
        time.sleep(3)
    raise TimeoutError(j)

s=call('/api/execution/RUBBER-20261026')
done={x['method'] for x in s['state']['submissions']}
if not done:
    draft=next(j for j in s['jobs'] if j['method']=='R48' and j['result'] and j['result'].get('artifact'))['result']['artifact']
    baseline={r['id']:r for r in s['state']['task']['demand_snapshot']['requirements']}
    changes=[]
    for r in draft['payload']['requirements']:
        if r['id'] in baseline:
            old=r['acceptance'];r['acceptance']=baseline[r['id']]['acceptance_proposal']
            if old!=r['acceptance']:changes.append({'id':r['id'],'before':old,'after':r['acceptance']})
    draft['revision']+='-host-baseline-restored'
    (OUT/'R48-host-repair.json').write_text(json.dumps({'reason':'restore original acceptance wording; no evidence or approval invented','changes':changes,'artifact':draft},ensure_ascii=False,indent=2))
    result=enqueue('submit',draft)
    if result['state']!='submitted':raise ValueError(result)
for method in ['R14','R17','R36','R44','R42']:
    s=call('/api/execution/RUBBER-20261026')
    if method in {x['method'] for x in s['state']['submissions']}:continue
    job=enqueue('propose')
    if job['state']!='draft':
        print('Stopped for review; no automatic model retry',flush=True);break
    print('Draft retained for Host/user semantic review before submission',flush=True)
    break
s=call('/api/execution/RUBBER-20261026')
(OUT/'actual-execution.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
print('submitted',len(s['state']['submissions']),'expert_certified',s['state']['expert_certified'],flush=True)
