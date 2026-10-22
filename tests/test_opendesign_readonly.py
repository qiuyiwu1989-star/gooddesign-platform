import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import opendesign_readonly as cloud
class CloudTests(unittest.TestCase):
 def test_prefixes(self):
  for path in ['/api/files?project=x','/asset?project=x','/dossier/?project=x','/methods/','/app.js','/workspace.css','/?project=x']:
   for quote in ['"',"'",'`']:
    self.assertEqual(cloud.prefixed(quote+path+quote),quote+'/inno'+path+quote)
 def test_no_external_or_evidence_change(self):
  for text in ['https://example.org/api/file','S01:chunk1','来源/原件.pdf','"/unrelated"','"/inno/api/files"']:
   self.assertEqual(cloud.prefixed(text),text)
 def test_write_verbs_denied(self):
  for name in ['do_POST','do_PUT','do_PATCH','do_DELETE']:
   calls=[];fake=type('Fake',(),{'send':lambda *args:calls.append(args)})()
   getattr(cloud.Handler,name)(fake);self.assertEqual(calls[0][1],403)
 def test_no_background_watcher(self):
  import inspect
  self.assertNotIn('start_watch(',inspect.getsource(cloud.main))
 def test_nginx_auth_all_routes(self):
  text=(Path(__file__).resolve().parents[1]/'deploy/nginx-inno-readonly.conf').read_text()
  self.assertIn('location ^~ /inno/',text);self.assertIn('auth_basic_user_file /etc/nginx/inno.htpasswd',text)
  self.assertIn('limit_except GET HEAD { deny all; }',text)
if __name__=='__main__':unittest.main()
