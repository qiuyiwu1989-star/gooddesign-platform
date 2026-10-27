import urllib.request,urllib.error,socket,json
old=socket.getaddrinfo
socket.getaddrinfo=lambda h,p,*a,**kw:old('127.0.0.1'if h in ['opendesign.cc','gooddesign.qiuyiwu.com']else h,p,*a,**kw)
r=[]
for path,want in [('/inno/',200),('/inno/projects/',200),('/inno/about/',200),('/inno/portal/portal.css',200),('/inno/portal/portal.js',200),('/inno/portal/catalog.json',200),('/inno/portal/covers/case-2025-00.jpg',200),('/inno/dossier/?project=2025-04',200),('/inno/methods/',200),('/inno/api/projects',401),('/inno/asset?project=2025-00',401),('/inno/admin/',401),('/inno/portal/secret.json',404)]:
 try:
  with urllib.request.urlopen('https://opendesign.cc'+path,timeout=30)as x:status=x.status;b=x.read()
 except urllib.error.HTTPError as e:status=e.code;b=e.read()
 assert status==want,(path,status,want)
 if path=='/inno/':assert b'pp-search'in b
 if path.startswith('/inno/dossier'):assert b'pp-nav'in b
 if path=='/inno/methods/':assert b'href="/inno/projects/"'in b
 if path.endswith('catalog.json'):assert len(json.loads(b))==560 and b'"token"'not in b
 r.append(dict(path=path,status=status,bytes=len(b)))
for path in ['/industry-demo/','/hall.html','/learn.html','/award.html']:
 with urllib.request.urlopen('https://gooddesign.qiuyiwu.com'+path,timeout=30)as x:assert x.status==200;r.append(dict(platform_path=path,status=x.status))
print(json.dumps(r))
