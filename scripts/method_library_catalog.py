"""ML-012 immutable base plus explicit research supplements. No solver contracts added."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'04-知识库/创新方法库/深度方法库-v0.1.0'
SUPPLEMENT=ROOT/'04-知识库/创新方法库/增补方法库-v0.1.0'

def catalog():
    rows=[];seen=set()
    for folder,collection in [(BASE,'frozen_0.1.0'),(SUPPLEMENT,'supplement_0.1.0')]:
        for original in json.loads((folder/'目录.json').read_text())['methods']:
            m=dict(original,collection=collection)
            if m['research_id'] in seen:raise ValueError('duplicate research ID')
            seen.add(m['research_id']);rows.append(m)
    return {'version':'base_0.1.0+supplement_0.1.0','status':'research_content_not_expert_certified','methods':rows}

def read(ident):
    rows=catalog()['methods'];row=next((x for x in rows if ident in (x['research_id'],x['method_id'])),None)
    if row is None:raise KeyError('unknown method')
    folder=BASE if row['collection']=='frozen_0.1.0' else SUPPLEMENT
    p=folder/row['path'];raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise ValueError('method checksum mismatch')
    return json.loads(raw)

def public_document_base(rid):
    row=next((x for x in catalog()['methods'] if x['research_id']==rid),None)
    if not row:raise KeyError('unknown method')
    return BASE if row['collection']=='frozen_0.1.0' else SUPPLEMENT

def supplemental_search(query='',limit=10):
    if not isinstance(limit,int) or not 1<=limit<=60:raise ValueError('limit must be 1..60')
    q=query.strip().lower();rows=[x for x in catalog()['methods'] if x['collection'].startswith('supplement')]
    rows=[x for x in rows if not q or q in json.dumps(x,ensure_ascii=False).lower()]
    return {'methods':rows[:limit],'total':len(rows),'execution_available':False,'scope':'supplement_content_only','expert_certified':False}
