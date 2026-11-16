"""Anonymous pilot adapter: signed browser scope, isolated records, no account dependency."""
import argparse,contextvars,hashlib,hmac,json,os,secrets,socketserver
from pathlib import Path
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer

scope=contextvars.ContextVar('guest_scope')
class GuestMixin:
    def _guest(self):
        if hasattr(self,'_guest_id'):return self._guest_id
        cookies=SimpleCookie()
        try:cookies.load(self.headers.get('Cookie',''))
        except Exception:pass
        token=cookies['gd_pilot'].value if 'gd_pilot' in cookies else ''
        ident,_,sig=token.partition('.')
        expected=hmac.new(KEY,ident.encode(),hashlib.sha256).hexdigest()
        if len(ident)!=48 or not hmac.compare_digest(sig,expected):
            ident=secrets.token_hex(24);sig=hmac.new(KEY,ident.encode(),hashlib.sha256).hexdigest()
            self._new_cookie=ident+'.'+sig
        self._guest_id=ident
        return ident
    def end_headers(self):
        self._guest()
        if hasattr(self,'_new_cookie'):self.send_header('Set-Cookie','gd_pilot='+self._new_cookie+'; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=2592000')
        super().end_headers()
    def do_GET(self):
        token=scope.set(self._guest())
        try:return super().do_GET()
        finally:scope.reset(token)
    def do_POST(self):
        origin=self.headers.get('Origin','')
        if origin not in ('https://haoshejiguan.com','https://www.haoshejiguan.com','https://opendesign.cc'):
            self.send_error(403,'same-origin browser required');return
        token=scope.set(self._guest())
        try:return super().do_POST()
        finally:scope.reset(token)

def main():
    global KEY
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['canvas','loop'],required=True);p.add_argument('--port',type=int,required=True);p.add_argument('--data',required=True);a=p.parse_args()
    data=Path(a.data);data.mkdir(parents=True,exist_ok=True);keyfile=data/'guest-signing.key'
    if not keyfile.exists():
        fd=os.open(keyfile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as f:f.write(secrets.token_bytes(32))
    KEY=keyfile.read_bytes()
    if a.kind=='canvas':
        import reasoning_canvas_server as mod
        mod.STATE_DB=data/'guest-canvas.sqlite3'
        class Handler(GuestMixin,mod.Handler):
            def _workspace(self,parsed):return self._guest()+':'+super()._workspace(parsed)
            def _read_body(self):
                obj=super()._read_body()
                if isinstance(obj,dict) and isinstance(obj.get('workspace_id'),str):obj['workspace_id']=self._guest()+':'+obj['workspace_id']
                return obj
        handler=lambda *args,**kw:Handler(*args,directory=str(mod.ROOT),**kw)
    else:
        import innovation_loop_server as mod
        from innovation_loop_store import LoopStore
        from innovation_loop_seed import seed
        def guest_store():
            db=data/(scope.get()+'.sqlite3');fresh=not db.exists();s=LoopStore(db)
            if fresh:seed(s)
            return s
        mod.LoopStore=guest_store
        class Handler(GuestMixin,mod.Handler):pass
        handler=Handler
    ThreadingHTTPServer.allow_reuse_address=True
    ThreadingHTTPServer(('127.0.0.1',a.port),handler).serve_forever()
if __name__=='__main__':main()
