# coding: utf-8
"""046 read-only, version-bound update ledger; evidence counts are not quality scores."""
import html,json,re,urllib.parse,sqlite3
from collections import Counter
import project_pipeline as pp,research_workflow as rw
LABELS={'added':'新增事实','corrected':'修正事实','withdrawn':'撤回事实','evidence_added':'补充依据','ai_added':'新增AI解读'}
def read(lib,pid,revision=None,offset=0,limit=20):
 if type(offset)is not int or type(limit)is not int or offset<0 or not 1<=limit<=50:raise ValueError('offset>=0，limit须1–50')
 p=pp.project(lib,pid);w=rw.current(p);latest='research-%06d'%w['revision']
 if not w['revision']:
  if revision:raise ValueError('尚未发布研究版本')
  return dict(project_id=pid,status='not_published',changes=[],counts={},quality_score_changed=False,expert_reviewed=False)
 revision=revision or latest;folder,manifest=rw.check_version(p,revision);delta=pp.load(folder/'changes.json');data=pp.load(folder/'档案.json');records={r['id']:r for r in data['records']};dictionary=rw.schema();rows=[]
 for c in delta['changes']:
  before=c.get('before')or{};old=before.get('value');nature=c.get('content_nature','source_statement')
  if nature!='source_statement':kind='ai_added'
  elif c.get('operation')=='clear':kind='withdrawn'
  elif old is None or before.get('value_state')!='known':kind='added'
  elif old==c['after']:kind='evidence_added'
  else:kind='corrected'
  record=records.get(c['record_id'],{});label=dictionary.get(record.get('entity'),{}).get(c['field'],{}).get('label',c['field'])
  rows.append(dict(kind=kind,label=LABELS[kind],record_id=c['record_id'],record_title=record.get('title',c['record_id']),field=c['field'],field_label=label,before=old,after=c['after'],source_id=c['source_id'],chunk_id=c['chunk_id'],quote=c['quote'],content_nature=nature,candidate_id=c['candidate_id']))
 counts=dict(Counter(c['kind']for c in rows));pending=[]
 if revision==latest:
  for c in w['candidates']:
   if c['status']in ('pending','needs_more','approved'):pending.append(dict(id=c['id'],record_id=c['record_id'],field=c['field'],status=c['status'],reason=c.get('review_reason')or'等待证据检查或判断'))
 return dict(project_id=pid,status='available',revision=revision,previous_revision=delta['previous_revision'],latest_revision=latest,actor=manifest['actor'],reason=manifest['reason'],published_at=data.get('published_at'),counts=counts,total=len(rows),changes=rows[offset:offset+limit],next_offset=offset+limit if offset+limit<len(rows)else None,pending_count=len(pending),pending=pending[:limit],pending_scope='current_queue_only'if revision==latest else'not_mixed_into_historical_revision',quality_score_changed=False,quality_note='更新不自动升分；新项目仍未评，人工标杆保留原量规和自评。',expert_reviewed=False)
def render(lib,pid):
 d=read(lib,pid,limit=8);h=lambda x:html.escape(str(x),quote=True)
 if d['status']!='available':return '<details class="reader-expand"><summary>版本更新记录</summary><p>尚未发布研究版本。</p></details>'
 def fmt(v):return '—'if v is None else json.dumps(v,ensure_ascii=False)if isinstance(v,(dict,list))else str(v)
 rows=[]
 for c in d['changes']:
  q=urllib.parse.urlencode(dict(project=pid,source=c['source_id'],kind='original'));before=fmt(c['before']);after=fmt(c['after'])
  rows.append('<details class="reader-expand"><summary>'+h(c['label'])+' · '+h(c['record_title'])+' / '+h(c['field_label'])+'</summary><dl class="reader-properties"><div><dt>更新前</dt><dd>'+h(before)+'</dd></div><div><dt>更新后</dt><dd>'+h(after)+'</dd></div></dl><details><summary>查看本次依据</summary><blockquote>'+h(c['quote'])+'</blockquote><a href="/asset?'+h(q)+'">查看来源原件</a></details></details>')
 download='/api/research-document?'+urllib.parse.urlencode(dict(project=pid,document='changes',revision=d['revision']))
 return '<details class="reader-expand archive-updates" id="archive-updates"><summary>本次档案更新 · '+h(d['revision'])+'</summary><p class="reader-note">'+h(d['previous_revision'])+' → '+h(d['revision'])+'。'+h(d['quality_note'])+'</p><p>'+h(' · '.join(LABELS[k]+str(v)+'项'for k,v in d['counts'].items()))+'</p>'+''.join(rows)+'<p class="reader-note">本次共'+str(d['total'])+'项更新，以上展示前8项；另有'+str(d['pending_count'])+'项候选待处理，未计入已发布内容。</p><a href="'+h(download)+'">下载完整更新记录</a></details>'
def semantic_attention(lib,pid):
 folder=pp.project(lib,pid).parent/'.file-admin/semantic-agent';dbfile=folder/'jobs.sqlite3'
 if not dbfile.exists():return ''
 h=lambda v:html.escape(str(v),quote=True);items=[]
 with sqlite3.connect('file:'+urllib.parse.quote(str(dbfile),safe='/')+'?mode=ro',uri=True)as db:
  rows=db.execute("SELECT id,snapshot,result_path FROM jobs WHERE project_id=? AND status='needs_review' ORDER BY id DESC LIMIT 5",(pid,)).fetchall()
 for job_id,snapshot,path in rows:
  try:
   snap=json.loads(snapshot);f=pp.safe(folder,path);response=pp.load(f.parent/'response.json')
   from semantic_agent import validate_bundle
   checked=validate_bundle(lib,snap,response);agent=checked['semantic_agent'];texts=agent['unresolved_conflicts']+agent['risks']
   items.append('<li><b>深读任务 #'+str(job_id)+'</b><ul>'+''.join('<li>'+h(t)+'</li>'for t in texts)+'</ul></li>')
  except (ValueError,KeyError,OSError,json.JSONDecodeError):items.append('<li>深读任务 #'+str(job_id)+' 的资料或状态已变化，请在资料管理中重新核对。</li>')
 return '<details class="reader-expand"><summary>资料深读中发现的疑点 · 待核对</summary><p class="reader-note">以下是当前Agent任务的风险提示，不是已发布事实或专家结论；不会据此自动改分。</p><ul>'+''.join(items)+'</ul></details>'if items else''

def inject(text,lib,pid):
 panel=render(lib,pid)+semantic_attention(lib,pid)
 return re.sub(r'(<(?:div|section)\b[^>]*\bid="assessment-view"[^>]*>)',lambda m:m.group(1)+panel,text,count=1)
