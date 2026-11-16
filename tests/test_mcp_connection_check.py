import asyncio,json,sys,unittest
from pathlib import Path
from unittest.mock import patch
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_mcp_connection as m
class CheckTests(unittest.TestCase):
 def test_urls(self):
  for u in ['http://example.com','https://user:secret@example.com','https://example.com/?token=secret']:
   with self.assertRaises(ValueError):m.validate_url(u)
 def test_tokens(self):
  for token in [' Bearer abc','Bearer abc','abc\ndef','']:
   with self.assertRaises(ValueError):asyncio.run(m.check(token=token))
 def test_response_redacts(self):
  r=httpx.Response(401,headers={'x-request-id':'safe-123'},text='secret')
  d=m.response_summary(r);self.assertNotIn('secret',str(d));self.assertEqual(d['request_id'],'safe-123')
 def test_bad_request_id(self):
  self.assertIsNone(m.response_summary(httpx.Response(401,headers={'x-request-id':'secret / bad'}))['request_id'])
 def test_denied_and_redirect_without_protocol_call(self):
  for code,status in [(401,'authentication_rejected'),(403,'authentication_rejected'),(308,'redirect_rejected'),(500,'http_failed')]:
   transport=httpx.MockTransport(lambda r:httpx.Response(code,text='TOPSECRET',headers={'location':'https://other.example'}))
   factory=httpx.AsyncClient
   with patch.object(m.httpx,'AsyncClient',side_effect=lambda **kw:factory(transport=transport,**kw)):
    d=asyncio.run(m.check(token='TOKEN-SECRET'))
   self.assertEqual(d['status'],status);self.assertNotIn('SECRET',json.dumps(d));self.assertFalse(d['authenticated'])
if __name__=='__main__':unittest.main()
