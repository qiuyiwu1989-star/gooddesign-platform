from pathlib import Path
import os,subprocess,json,hashlib,urllib.request,urllib.error
release=Path('/var/www/innovation-design/releases/20261027-057');base=release.parent.parent;current=base/'current';previous=current.resolve();assert str(previous).endswith('20261022-049'),'current changed; manual inspection required'
for pid,d in json.loads((release/'dataset-check.json').read_text()).items():
 f=release/'04-知识库/项目库'/pid/'研究工作区/版本'/d['revision']/'档案.json';assert hashlib.sha256(f.read_bytes()).hexdigest()==d['sha256'],pid
(base/'backups').mkdir(exist_ok=True);(base/'backups/20261027-057.previous').write_text(str(previous)+'\n')
def point(dest):
 temp=base/'current.057';temp.unlink(missing_ok=True);temp.symlink_to(dest);os.replace(temp,current)
try:
 point(release);subprocess.run(['sudo','systemctl','restart','innovation-readonly'],check=True)
 subprocess.run(['curl','-fsS','--retry','8','--retry-connrefused','--retry-delay','1','http://127.0.0.1:18776/api/projects','-o','/var/lib/innovation-design/projects-057.json'],check=True)
 subprocess.run(['/var/www/innovation-design/venv/bin/python','/var/lib/innovation-design/verify-057.py','18776'],check=True)
except BaseException:
 point(previous);subprocess.run(['sudo','systemctl','restart','innovation-readonly'],check=True);raise
print('ACTIVATED 20261027-057; rollback '+str(previous))
