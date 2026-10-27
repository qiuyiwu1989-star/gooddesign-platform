from pathlib import Path
import os,subprocess,shutil
base=Path('/var/www/innovation-design');cur=base/'current';old=cur.resolve();assert old.name=='20261027-062'
new=base/'releases/20261027-063';conf=Path('/etc/nginx/snippets/inno-readonly.conf');backup=Path('/var/lib/innovation-design/nginx-063-before.conf');shutil.copy2(conf,backup)
def point(p):
 t=base/'current.063';t.unlink(missing_ok=True);t.symlink_to(p);os.replace(t,cur)
try:
 point(new);subprocess.run(['systemctl','restart','innovation-readonly'],check=True);subprocess.run(['curl','-fsS','--retry','8','--retry-connrefused','--retry-delay','1','http://127.0.0.1:18776/report/','-o','/var/lib/innovation-design/report-063.html'],check=True)
 assert b'dr-kpis'in Path('/var/lib/innovation-design/report-063.html').read_bytes()
 shutil.copy2(new/'deploy/nginx-inno-readonly.conf',conf);subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
except BaseException:
 point(old);shutil.copy2(backup,conf);subprocess.run(['systemctl','restart','innovation-readonly']);subprocess.run(['nginx','-t']);subprocess.run(['systemctl','reload','nginx']);raise
(base/'backups/20261027-063.previous').write_text(str(old)+'\n');print('063 reporting snapshot activated')
