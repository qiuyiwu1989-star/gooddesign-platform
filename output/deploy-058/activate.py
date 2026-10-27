from pathlib import Path
import os,subprocess,shutil,urllib.request
base=Path('/var/www/innovation-design');current=base/'current';old=current.resolve();assert old.name=='20261027-057'
new=base/'releases/20261027-058';conf=Path('/etc/nginx/snippets/inno-readonly.conf');backup=Path('/var/lib/innovation-design/nginx-058-before.conf');shutil.copy2(conf,backup)
def point(p):
 t=base/'current.058';t.unlink(missing_ok=True);t.symlink_to(p);os.replace(t,current)
try:
 point(new);subprocess.run(['systemctl','restart','innovation-readonly'],check=True)
 subprocess.run(['curl','-fsS','--retry','8','--retry-connrefused','--retry-delay','1','http://127.0.0.1:18776/','-o','/var/lib/innovation-design/public-home-058.html'],check=True)
 assert '探索项目'.encode() in Path('/var/lib/innovation-design/public-home-058.html').read_bytes()
 shutil.copy2(new/'deploy/nginx-inno-readonly.conf',conf);subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
except BaseException:
 shutil.copy2(backup,conf);point(old);subprocess.run(['systemctl','restart','innovation-readonly']);subprocess.run(['nginx','-t']);subprocess.run(['systemctl','reload','nginx']);raise
(base/'backups/20261027-058.previous').write_text(str(old)+'\n');print('activated 058 public reading; private routes remain authenticated')
