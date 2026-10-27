from pathlib import Path
import os,json,subprocess,shutil
base=Path('/var/www/innovation-design');cur=base/'current';old=cur.resolve();assert old.name=='20261027-059','project release changed'
new=base/'releases/20261027-060';conf=Path('/etc/nginx/snippets/inno-readonly.conf');backup=Path('/var/lib/innovation-design/nginx-060-before.conf');shutil.copy2(conf,backup)
m=Path('/var/www/gooddesign-methods');mc=m/'current';mo=mc.resolve();assert mo.name=='20261027-ML013-inno','method release changed; preserve concurrent work'
mn=m/'releases/20261027-060-nav';assert not mn.exists();shutil.copytree(mo,mn);count=0
for p in mn.rglob('*.html'):
 s=p.read_text()
 if '<header>' in s and 'href="/inno/projects/"' not in s:s=s.replace('<header>','<header><a href="/inno/projects/">项目库</a>',1);p.write_text(s);count+=1

def point(link,target):
 temp=link.with_name(link.name+'.060');temp.unlink(missing_ok=True);temp.symlink_to(target);os.replace(temp,link)
try:
 point(cur,new);subprocess.run(['systemctl','restart','innovation-readonly'],check=True)
 subprocess.run(['curl','-fsS','--retry','8','--retry-connrefused','--retry-delay','1','http://127.0.0.1:18776/portal/catalog.json','-o','/var/lib/innovation-design/catalog-060.json'],check=True)
 assert len(json.loads(Path('/var/lib/innovation-design/catalog-060.json').read_text()))==560
 point(mc,mn);shutil.copy2(new/'deploy/nginx-inno-readonly.conf',conf);subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
except BaseException:
 point(cur,old);point(mc,mo);shutil.copy2(backup,conf);subprocess.run(['systemctl','restart','innovation-readonly']);subprocess.run(['nginx','-t']);subprocess.run(['systemctl','reload','nginx']);raise
(base/'backups/20261027-060.previous').write_text(str(old)+'\n');(m/'previous-060').write_text(str(mo)+'\n');print('Activated portal 060; method navigation only changed on',count,'pages')
