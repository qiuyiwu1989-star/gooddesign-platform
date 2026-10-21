# coding: utf-8
"""Offline layered-read example; does not infer or modify project facts."""
import argparse,json,sys
sys.dont_write_bytecode=True
from pathlib import Path
from check import check,load,safe
ROOT=Path(__file__).resolve().parent
if __name__=='__main__':
 ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group();g.add_argument('--record');g.add_argument('--source');args=ap.parse_args();check(ROOT)
 data=load(ROOT/'研究版本/档案.json')
 if args.record:
  row=next((x for x in data['records']if x['id']==args.record),None)
  if row is None:ap.error('没有这个记录ID')
  result=dict(record=row,ai_interpretations=[x for x in data.get('interpretations',[])if x.get('record_id')==args.record])
 elif args.source:
  row=next((x for x in load(ROOT/'资料库/来源目录.json')['items']if x['id']==args.source),None)
  if row is None:ap.error('没有这个来源ID')
  result=dict(source=row,chunks=load(safe(ROOT,'资料库/'+row['chunks'])))
 else:
  guide=ROOT/'阅读导读/导读.json';result=dict(overview=load(ROOT/'交付概览.json'),reading_guide=load(guide)if guide.exists()else None,research_review=load(ROOT/'研究评估/评估.json')if (ROOT/'研究评估/评估.json').exists()else None,records=[dict(id=r['id'],entity=r['entity'],title=r['title'])for r in data['records']])
 print(json.dumps(result,ensure_ascii=False,indent=2))
