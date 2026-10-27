from pathlib import Path
import urllib.request,json,hashlib,shutil,re
P=Path(__file__).parent;B=P.parent;ROOT=P.parents[2]
for name,sid,url in [('MD-046-R50','NNG','https://www.nngroup.com/articles/service-blueprints-definition/'),('MD-049-R07','NIST-DFSS','https://www.nist.gov/baldrige/lean-iso-and-six-sigma'),('MD-049-R07','NIST-GAUGE','https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc46.htm')]:
 d=B/name;r={'id':sid,'url':url,'date':'2026-10-27'}
 try:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25).read();p=d/'private-sources'/(sid+'.html');p.write_bytes(raw);p.with_suffix('.txt').write_text(re.sub('<[^>]+>',' ',raw.decode(errors='replace')));r.update(status='acquired',sha256=hashlib.sha256(raw).hexdigest())
 except Exception as e:r.update(status='failed',error=str(e))
 (d/('取得记录-'+sid+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));print(r)
for name,sid in [('MD-047-R51','e469186f8f8337'),('MD-048-R52','02426f074883c4')]:
 d=B/name
 for ext in ['pdf','txt']:
  p=ROOT/'output/method-deepening-ML017/private-sources'/(sid+'.'+ext)
  if p.exists():shutil.copy2(p,d/'private-sources'/p.name)
 (d/'已有来源再核读.json').write_text(json.dumps({'source_id':sid,'original_context':'ML017 private primary material','reviewed_date':'2026-10-27','read_scope':'selected original passages; see source claim locators','not_new_download':True},ensure_ascii=False,indent=2))
for n in ['MD-046-R50','MD-047-R51','MD-048-R52','MD-049-R07']:(B/n/'.gitignore').write_text('private-sources/\n__pycache__/\n')
