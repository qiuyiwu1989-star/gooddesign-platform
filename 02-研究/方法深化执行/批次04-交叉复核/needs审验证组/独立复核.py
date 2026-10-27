# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,runpy,shutil,copy,contextlib,io
D=Path(__file__).resolve().parent;ROOT=D.parents[3];BASE=ROOT/'02-研究/方法深化执行'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def review(dest,names,script,probes,dependencies=[]):
 before={str(p):sha(p)for n in names for p in(BASE/n).rglob('*')if p.is_file()};S=dest/'sandbox/02-研究/方法深化执行';S.mkdir(parents=True,exist_ok=True)
 for n in names+dependencies:shutil.copytree(BASE/n,S/n,dirs_exist_ok=True)
 buf=io.StringIO()
 with contextlib.redirect_stdout(buf):m=runpy.run_path(str(S/names[0]/script))
 rows=[]
 for name,key,fn,mut in probes:
  q=copy.deepcopy(m[key]);mut(q)
  try:out=m[fn](q);state='accepted'
  except Exception as e:out={'error':type(e).__name__+': '+str(e)};state='rejected'
  rows.append({'name':name,'input':q,'actual':state,'output':out})
 assert all(sha(Path(p))==h for p,h in before.items())
 result={'original_files_unchanged':len(before),'manifest_sha256':{n:sha(BASE/n/'manifest.json')for n in names},'replayed':buf.getvalue(),'probes':rows}
 (dest/'.gitignore').write_text('sandbox/\n');(dest/'实际复核.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print([(r['name'],r['actual'])for r in rows]);return result
D2=BASE/'批次02-修订复核/needs审验证修订'
r=review(D2,['修订版/MD-014-R13-v0.1.1'],'教学与反例.py',[
('empty','base13','check13',lambda x:x.update(representations={})),('onlyA','base13','check13',lambda x:x['representations'].pop('B')),('onlyB','base13','check13',lambda x:x['representations'].pop('A')),('missing-state','base13','check13',lambda x:x['representations']['B'].pop('S-STALE')),('empty-string-states','base13','check13',lambda x:x['representations'].update(B={'S-CURRENT':'','S-STALE':''})),('invent-human-result','base13','check13',lambda x:x.update(records=[{'reaction_time':0.1}]))],['MD-001-R48','MD-005-R36','MD-006-R44','MD-007-R42'])
review(D,['MD-036-R05','MD-037-R47'],'教学与反例.py',[
('bool-command','base05','check05',lambda x:x['command'].update(software_value=True)),('nan-command','base05','check05',lambda x:x['command'].update(software_value=float('nan'))),('other-frame','base05','check05',lambda x:x['software'].update(frame='other')),('future-time','base05','check05',lambda x:x['sample'].update(timestamp_ms=101)),('timeout-boundary','base05','check05',lambda x:x['sample'].update(now_ms=110)),('duplicate-control-owner','base05','check05',lambda x:x['command'].update(other_writers=['motion_controller'])),('lost-constraint','base47','check47',lambda x:x['constraints'].pop()),('bool-grid','base47','check47',lambda x:x['mass_grid'].__setitem__(0,True)),('fake-evidence','base47','check47',lambda x:x['constraints'][0].update(status='measured')),('unknown-pass','base47','check47',lambda x:x.update(real_latex_boundary='pass'))])
