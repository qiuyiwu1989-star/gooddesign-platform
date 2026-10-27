import urllib.request,urllib.error,socket,json
old=socket.getaddrinfo;socket.getaddrinfo=lambda h,p,*a,**kw:old('127.0.0.1'if h=='opendesign.cc'else h,p,*a,**kw)
r=[]
for path,want in [('/inno/mcp/',200),('/inno/portal/mcp-guide.js',200),('/inno/',200),('/inno/api/projects',401),('/inno/asset?project=2025-00',401),('/inno/admin/',401)]:
 try:
  with urllib.request.urlopen('https://opendesign.cc'+path,timeout=30)as x:s=x.status;b=x.read()
 except urllib.error.HTTPError as e:s=e.code;b=e.read()
 assert s==want,(path,s)
 if path=='/inno/':assert b'href="/inno/mcp/"'in b
 if path=='/inno/mcp/':assert b'mcp-config'in b and b'inno_start_research'in b
 r.append(dict(path=path,status=s))
print(json.dumps(r))
