import urllib.request,urllib.error,socket,json
old=socket.getaddrinfo;socket.getaddrinfo=lambda h,p,*a,**kw:old('127.0.0.1'if h=='opendesign.cc'else h,p,*a,**kw)
r=[]
for path,want in [('/inno/report/',200),('/inno/portal/data-report.css',200),('/inno/portal/data-report.js',200),('/inno/',200),('/inno/mcp/',200),('/inno/api/projects',401),('/inno/asset?project=2025-00',401),('/inno/admin/',401)]:
 try:
  with urllib.request.urlopen('https://opendesign.cc'+path,timeout=30)as x:s=x.status;b=x.read()
 except urllib.error.HTTPError as e:s=e.code;b=e.read()
 assert s==want,(path,s)
 if path=='/inno/report/':assert b'dr-kpis'in b and b'data-panel="projects"'in b and b'data-panel="methods"'in b
 if path=='/inno/':assert b'href="/inno/report/"'in b
 r.append(dict(path=path,status=s))
print(json.dumps(r))
