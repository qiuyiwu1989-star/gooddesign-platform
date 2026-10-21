# coding: utf-8
import json,sys,tempfile,threading,time,unittest,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import file_admin as fa,project_pipeline as pp
class FileAdminTests(unittest.TestCase):
 def setUp(self):
  (ROOT/'tmp/admin-tests').mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=str(ROOT/'tmp/admin-tests'));self.root=Path(self.tmp.name);self.lib=self.root/'lib';self.lib.mkdir();self.inbox=self.root/'inbox';cat=self.root/'catalog.json';pp.save(cat,dict(projects=[dict(id='demo-01',name='测试项目',year=2025,award='待核对',unit='测试单位')]))
  pp.bootstrap(self.lib,self.inbox,cat,self.root/'archive');self.srv=fa.server(self.lib,self.inbox,0);self.thread=threading.Thread(target=self.srv.serve_forever,daemon=True);self.thread.start();self.base='http://127.0.0.1:'+str(self.srv.server_port);self.token=self.request('/api/projects')[1]['token']
 def tearDown(self):
  self.srv.shutdown();self.srv.server_close();self.srv.store.pool.shutdown(wait=True);self.thread.join();self.tmp.cleanup()
 def request(self,path,body=None,method=None,headers=None):
  h={'Origin':self.base,'X-CSRF-Token':self.srv.store.token};h.update(headers or {})
  req=urllib.request.Request(self.base+path,data=body,method=method,headers=h)
  try:r=urllib.request.urlopen(req,timeout=5)
  except urllib.error.HTTPError as e:r=e
  data=r.read();ctype=r.headers.get('Content-Type','');return r.status,json.loads(data)if 'application/json'in ctype else data,r.headers
 def wait(self,j):
  for _ in range(100):
   row=next(x for x in self.srv.store.jobs if x['id']==j['id'])
   if row['status']not in ('queued','running'):return row
   time.sleep(.02)
  self.fail('task did not finish')
 def test_upload_persist_preview_and_dedup(self):
  status,j,_=self.request('/api/upload?project=demo-01&name=research.txt','原始资料 12mm'.encode());self.assertEqual(status,202);self.assertEqual(self.wait(j)['status'],'completed')
  d=self.request('/api/files?project=demo-01')[1];self.assertEqual(len(d['files']),1);sid=d['files'][0]['id'];self.assertEqual(d['files'][0]['name'],'research.txt')
  preview=self.request('/api/preview?project=demo-01&source='+sid)[1];self.assertIn('12mm',preview['blocks'][0]['text'])
  _,j,_=self.request('/api/upload?project=demo-01&name=again.txt','原始资料 12mm'.encode());self.assertEqual(self.wait(j)['result']['status'],'duplicate');self.assertEqual(len(pp.load(self.lib/'.file-admin/jobs.json')),2)
 def test_xss_and_original_attachment(self):
  _,j,_=self.request('/api/upload?project=demo-01&name=page.html',b'<script>BAD()</script><p>real text</p>');j=self.wait(j);sid=j['result']['source_id'];status,body,headers=self.request('/asset?project=demo-01&source='+sid+'&kind=original');self.assertEqual(status,200);self.assertIn('attachment',headers['Content-Disposition']);self.assertEqual(headers['Content-Type'],'application/octet-stream');self.assertIn(b'<script>',body)
  d=self.request('/api/preview?project=demo-01&source='+sid)[1];self.assertNotIn('BAD()',str(d));self.assertIn('real text',str(d))
 def test_security_rejects_csrf_host_paths_and_private_urls(self):
  path='/api/upload?project=demo-01&name=a.txt'
  for headers in [{'X-CSRF-Token':'wrong'},{'Origin':'https://bad.example'},{'Host':'bad.example'}]:self.assertEqual(self.request(path,b'x',headers=headers)[0],403)
  self.assertEqual(self.request('/api/upload?project=demo-01&name=../escape.txt',b'x')[0],400)
  self.assertEqual(self.request('/api/files?project=../demo-01')[0],400)
  self.assertEqual(self.request('/asset?project=demo-01&source=../../secret')[0],400)
  with patch.object(pp,'public_url',side_effect=ValueError('不允许内网地址')):self.assertEqual(self.request('/api/fetch?project=demo-01',json.dumps({'url':'http://local.invalid/x'}).encode())[0],400)
 def test_unsupported_original_retained_and_retry(self):
  _,j,_=self.request('/api/upload?project=demo-01&name=image.png',b'fake image');j=self.wait(j);self.assertEqual(j['status'],'needs_attention');d=self.request('/api/files?project=demo-01')[1];self.assertEqual(d['files'][0]['status'],'unsupported_needs_conversion')
  _,retry,_=self.request('/api/retry?project=demo-01',json.dumps({'job_id':j['id']}).encode());self.assertEqual(self.wait(retry)['status'],'needs_attention');self.assertNotEqual(self.wait(retry)['result']['source_id'],j['result']['source_id'])
 def test_invalid_large_and_project(self):
  self.assertEqual(self.request('/api/upload?project=missing&name=a.txt',b'x')[0],400)
  self.assertEqual(self.request('/api/upload?project=demo-01&name=noextension',b'x')[0],202)
  self.assertEqual(self.request('/api/fetch?project=demo-01',b'not-json')[0],400)
 def test_network_octet_stream_pdf_is_preserved(self):
  import io
  from email.message import Message
  from pypdf import PdfWriter
  writer=PdfWriter();writer.add_blank_page(width=200,height=200);buff=io.BytesIO();writer.write(buff)
  class Response:
   headers=Message();headers['Content-Type']='application/octet-stream';url='https://public.example/download'
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,n):return buff.getvalue()
  class Opener:
   def open(self,*args,**kwargs):return Response()
  with patch.object(pp,'public_url',return_value='https://public.example/download'),patch.object(pp.urllib.request,'build_opener',return_value=Opener()):result=pp.fetch(self.lib,self.inbox,'demo-01','https://public.example/download')
  meta=pp.state(self.lib/'demo-01')['sources'][result['source_id']];self.assertTrue(meta['original'].endswith('.pdf'));self.assertEqual(meta['status'],'needs_ocr')
  url='?project=demo-01&source='+meta['id'];self.assertEqual(self.request('/api/pdf-info'+url)[1]['pages'],1);status,png,headers=self.request('/api/pdf-page'+url+'&page=0');self.assertEqual(status,200);self.assertTrue(png.startswith(b'\x89PNG'));self.assertEqual(self.request('/api/pdf-page'+url+'&page=9')[0],400)
 def test_job_restart_marks_interrupted(self):
  pp.save(self.lib/'.file-admin/jobs.json',[dict(id='fake',status='running')]);store=fa.Store(self.lib,self.inbox)
  try:self.assertEqual(store.jobs[0]['status'],'interrupted')
  finally:store.pool.shutdown()
if __name__=='__main__':unittest.main()
