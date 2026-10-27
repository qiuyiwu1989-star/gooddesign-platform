import json,urllib.request,urllib.error,sys
base='http://127.0.0.1:'+sys.argv[1];results=[]
for path in ['/api/projects','/dossier/?project=2025-04','/dossier/?project=2025-05','/dossier/?project=2025-00','/app.js','/style.css']:
 with urllib.request.urlopen(base+path,timeout=30)as r:
  b=r.read();assert r.status==200
  if path.startswith('/dossier'):assert '2026-10-27发布'.encode()in b
  results.append(dict(path=path,status=r.status,bytes=len(b)))
try:urllib.request.urlopen(urllib.request.Request(base+'/api/upload?project=2025-00',data=b'x'),timeout=10);raise AssertionError('write accepted')
except urllib.error.HTTPError as e:assert e.code==403;results.append(dict(write='POST',status=e.code))
print(json.dumps(results))
