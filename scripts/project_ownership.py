# coding: utf-8
"""036: explicit document ownership, separate from semantic fact verification."""
import json
SCOPES={'project','shared','reassigned','pending'}
def registry(p):
 f=p/'资料归属.json'
 return json.loads(f.read_text())if f.exists()else {'version':0,'assignments':{},'url_rules':{}}
def assignment(p,sid,sources,reg=None,seen=None):
 reg=reg if reg is not None else registry(p);seen=set()if seen is None else seen
 if sid in seen:raise ValueError('资料归属存在循环')
 seen.add(sid)
 if sid in reg['assignments']:return reg['assignments'][sid]
 origin=sources.get(sid,{}).get('origin',{})
 parent=origin.get('parent_source_id')
 if parent and parent in sources:
  if parent in reg.get('image_parent_rules',{}):return reg['image_parent_rules'][parent]
  return assignment(p,parent,sources,reg,seen)
 url=origin.get('url')or origin.get('requested_url')
 if url in reg.get('url_rules',{}):return reg['url_rules'][url]
 return dict(scope='project',relation='project_submission_unreviewed',owner_project=p.name,reason='按已选择项目提交，语义关联尚待核对')
def select(p,sources,scope='project',reg=None):
 if scope not in SCOPES:raise ValueError('资料范围无效')
 reg=registry(p)if reg is None else reg
 return {sid:x for sid,x in sources.items()if assignment(p,sid,sources,reg)['scope']==scope}
