"""Check distributed skill file integrity; does not evaluate visual fidelity."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'manifest.json').read_text())
errors=[]
for entry in manifest['files']:
 p=root/entry['path']
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append(entry['path'])
if errors:
 print(json.dumps({'status':'failed','files':errors}));sys.exit(1)
print(json.dumps({'status':'passed','version':manifest['version'],'checked_files':len(manifest['files']),'visual_review':'not_performed'}))
