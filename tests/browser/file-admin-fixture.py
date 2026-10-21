# coding: utf-8
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'));import file_admin as fa,project_pipeline as pp
folder=ROOT/'tmp/admin033-browser';lib=folder/'lib';inbox=folder/'inbox';lib.mkdir(parents=True,exist_ok=True);cat=folder/'catalog.json';pp.save(cat,dict(projects=[dict(id='demo-01',name='隔离测试项目',year=2025,award='待核对',unit='测试单位')]))
pp.bootstrap(lib,inbox,cat,folder/'archive')
def fetch_fixture(lib,inbox,pid,url):
 if url!='https://example.org/demo.html':raise ValueError('隔离测试只允许固定示例URL')
 target=inbox/pid/'示例网页.html';target.write_text('<h1>浏览器测试网页</h1><p>仅隔离库中的测试内容。</p>');return pp.ingest(pp.project(lib,pid),target,dict(kind='web',url=url))
pp.fetch=fetch_fixture;srv=fa.server(lib,inbox,8777);print('isolated browser fixture 8777',flush=True);srv.serve_forever()
