import asyncio,contextlib,hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from innovation_gateway_http import BearerAuth
import project_pipeline as pp
class AuthIntegration(unittest.TestCase):
 def exercise(self,kind):
  with tempfile.TemporaryDirectory(dir=pp.ROOT/'output') as t:
   p=Path(t);token='TEST-only-sensitive-token';keys=p/'keys.json';keys.write_text(json.dumps({'keys':[{'enabled':True,'sha256':hashlib.sha256(token.encode()).hexdigest()}]}));registry=p/'registry.sqlite'
   if kind=='corrupt':registry.write_text('invalid sqlite')
   entered=[];sent=[];log=io.StringIO()
   async def app(*args):entered.append(True)
   async def receive():raise AssertionError('denial must not consume body')
   async def send(x):sent.append(x)
   headers=[] if kind=='malformed' else [(b'authorization',('Bearer '+token).encode()),(b'x-request-id',b'caller-secret-id')]
   with contextlib.redirect_stderr(log):asyncio.run(BearerAuth(app,keys,registry)({'type':'http','headers':headers},receive,send))
   self.assertFalse(entered);self.assertEqual(sent[0]['status'],401)
   body=json.loads(sent[1]['body']);response_headers=dict(sent[0]['headers']);event=json.loads(log.getvalue())
   self.assertEqual(response_headers[b'x-request-id'].decode(),body['request_id']);self.assertEqual(event['request_id'],body['request_id'])
   self.assertEqual(event['reason'],'malformed' if kind=='malformed' else 'registry_unavailable')
   self.assertNotIn(token,log.getvalue()+json.dumps(body));self.assertNotIn('caller-secret-id',log.getvalue()+json.dumps(body));self.assertEqual(response_headers[b'cache-control'],b'no-store')
 def test_missing_registry_asgi_fail_closed(self):self.exercise('missing')
 def test_corrupt_registry_asgi_fail_closed(self):self.exercise('corrupt')
 def test_malformed_asgi_correlation(self):self.exercise('malformed')
if __name__=='__main__':unittest.main()
