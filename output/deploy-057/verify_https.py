import pathlib,secrets,subprocess,urllib.request,urllib.error,base64,json,hashlib,socket
getaddrinfo=socket.getaddrinfo
socket.getaddrinfo=lambda host,port,*a,**kw:getaddrinfo("127.0.0.1" if host=="opendesign.cc" else host,port,*a,**kw)
root=pathlib.Path('/var/lib/innovation-design');auth=pathlib.Path('/etc/nginx/inno.htpasswd');old=auth.read_bytes();password=secrets.token_urlsafe(28);user='inno057test'
hash_=subprocess.run(['openssl','passwd','-apr1','-stdin'],input=password+'\n',text=True,capture_output=True,check=True).stdout.strip()
results=[]
def get(path,login=True,method='GET'):
 headers={'Authorization':'Basic '+base64.b64encode((user+':'+password).encode()).decode()}if login else {}
 req=urllib.request.Request('https://opendesign.cc'+path,headers=headers,method=method)
 try:
  with urllib.request.urlopen(req,timeout=35)as r:return r.status,r.read(),dict(r.headers)
 except urllib.error.HTTPError as e:return e.code,e.read(),dict(e.headers)
try:
 auth.write_bytes(old+f'{user}:{hash_}\n'.encode())
 for path in ['/inno/','/inno/api/projects','/inno/app.js','/inno/dossier/?project=2025-00','/inno/asset?project=2025-00']:
  status,_,_=get(path,False);assert status==401,(path,status);results.append({'anonymous':path,'status':status})
 status,body,_=get('/inno/api/projects');assert status==200;assert len(json.loads(body)['projects'])==560
 for pid in ['2025-00','2015-02','2017-01','2019-s10','2021-00','2021-01','2021-02','2025-02']:
  status,body,headers=get('/inno/dossier/?project='+pid);assert status==200,(pid,status)
  text=body.decode();assert '/inno/dossier/' in text;assert '只读快照' in text
  assert 'nonce-' in headers.get('Content-Security-Policy','');results.append({'project':pid,'status':status,'bytes':len(body)})
 for path in ['/inno/','/inno/app.js','/inno/style.css','/inno/workflow.js','/inno/workspace.js','/inno/agent.js','/inno/api/files?project=2025-00','/inno/api/research?project=2021-02']:
  status,_,_=get(path);assert status==200,(path,status);results.append({'resource':path,'status':status})
 status,_,_=get('/inno/api/upload?project=2025-00',method='POST');assert status==403;results.append({'write':'POST','status':status})
 status,_,_=get('/',False);assert status==200;results.append({'main_site':'/','status':status})
 # A real managed original is downloadable through its ownership-checked API.
 _,body,_=get('/inno/api/files?project=2025-00');files=json.loads(body)['files'];item=next(x for x in files if x.get('bytes',0)>0)
 from urllib.parse import urlencode
 status,body,_=get('/inno/asset?'+urlencode({'project':'2025-00','source':item['id'],'kind':'original','scope':'project'}))
 results.append({'original_download':status,'bytes':len(body)})
 assert status==200,status
finally:auth.write_bytes(b''.join(line for line in auth.read_bytes().splitlines(keepends=True) if not line.startswith((user+':').encode())))
(root/'staging/http-acceptance-057.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));print(json.dumps(results,ensure_ascii=False))
