import urllib.request,urllib.error,socket,json
old=socket.getaddrinfo
socket.getaddrinfo=lambda host,port,*a,**kw:old('127.0.0.1' if host=='opendesign.cc' else host,port,*a,**kw)
results=[]
for path,want in [('/inno/',200),('/inno/projects/',200),('/inno/dossier/?project=2025-04',200),('/inno/dossier/?project=2025-00',200),('/inno/admin/',401),('/inno/api/projects',401),('/inno/api/files?project=2025-00',401),('/inno/asset?project=2025-00',401),('/inno/api/pdf-page?project=2025-00',401),('/',200)]:
 try:
  with urllib.request.urlopen('https://opendesign.cc'+path,timeout=30)as r:status=r.status;body=r.read()
 except urllib.error.HTTPError as e:status=e.code;body=e.read()
 assert status==want,(path,status,want)
 results.append(dict(path=path,status=status,bytes=len(body)))
print(json.dumps(results))
