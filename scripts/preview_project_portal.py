"""060 local preview of the exact cloud reading shell, with /inno prefix."""
import argparse
from http.server import ThreadingHTTPServer
import opendesign_readonly as cloud
class Handler(cloud.Handler):
 def do_GET(self):
  if self.path.startswith('/inno/methods/'):
   self.send_response(302);self.send_header('Location','https://opendesign.cc'+self.path);self.end_headers();return
  if self.path.startswith('/inno/admin/'):
   self.send_response(302);self.send_header('Location','http://127.0.0.1:8776/');self.end_headers();return
  if self.path.startswith('/inno/'):self.path=self.path[len('/inno'):]
  super().do_GET()
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--port',type=int,default=8775);o=a.parse_args();s=ThreadingHTTPServer(('127.0.0.1',o.port),Handler);s.store=cloud.app.Store(cloud.app.pipe.LIB,cloud.app.pipe.INBOX)
 try:s.serve_forever()
 finally:s.store.steward.close();s.store.pool.shutdown(wait=True);s.server_close()
