"""ML-008 bounded explicit HTTP pilot; reuse current fragments, zero automatic retries.
Dedicated local test server only; no automatic artifact submission or certification.
"""
import json
import time
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/method-workbench-check/ml008'
BASE='http://127.0.0.1:8790'

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'morphology-pilot.json').exists():raise ValueError('Archived pilot exists: create a new explicit test version')
    token=json.load(urlopen(BASE+'/api/session'))['csrf']
    def call(path,body=None):
        return json.load(urlopen(Request(BASE+path,data=json.dumps(body).encode() if body else None,headers={'Content-Type':'application/json','X-CSRF-Token':token})))
    for attempt in range(15):
        state=call('/api/execution/RUBBER-20261026')
        prior=[j for j in state['jobs'] if j['action']=='morph_assemble' and j['state']=='draft']
        if prior:break
        job_id=call('/api/execute',{'id':'RUBBER-20261026','revision':1,'action':'propose'})['job_id']
        for poll in range(120):
            state=call('/api/execution/RUBBER-20261026')
            job=next(j for j in state['jobs'] if j['id']==job_id)
            if job['state'] not in ('queued','running'):break
            time.sleep(1)
        print(job['action'],job['state'],'parts',state['morphology']['ready'],'/',state['morphology']['total'],flush=True)
        if job['state'] not in ('part','draft'):
            print('Stopped: no automatic retry or replacement',flush=True);break
        if job['state']=='draft':break
    state=call('/api/execution/RUBBER-20261026')
    (OUT/'morphology-pilot.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
    print('saved pilot, no R17 auto submission',flush=True)

if __name__=='__main__':run()
