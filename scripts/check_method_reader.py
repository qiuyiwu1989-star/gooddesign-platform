"""ML-011 generated content/route validation; does not validate method engineering truth."""
import hashlib
import json
import threading
import unittest
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from build_method_reader import LIB,OUT,build
from method_library_catalog import catalog
from method_workbench_server import make_server, ROOT

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag in ('a','img','link','script'):
            v=a.get('href',a.get('src',''))
            if v:self.links.append(v)

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in LIB.rglob('*') if p.is_file()}
        build()
        cls.server=make_server(0,ROOT/'output/method-workbench-check/ml011/demands.sqlite')
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def get(self,path):return urllib.request.urlopen(self.base+urllib.parse.quote(path,safe='/:#?')).read()
    def test_all_catalog_entries_and_frozen_unchanged(self):
        self.assertEqual(len(list((OUT/'methods').glob('*.html'))),len(catalog()['methods']))
        self.assertEqual(len(list((OUT/'icons').glob('*.svg'))),len(catalog()['methods']))
        self.assertEqual(self.hashes,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in LIB.rglob('*') if p.is_file()})
    def test_all_internal_links_and_anchors(self):
        for file in OUT.rglob('*.html'):
            path='/library/'+str(file.relative_to(OUT));parser=Links();parser.feed(self.get(path).decode())
            for href in parser.links:
                u=urlsplit(urljoin(self.base+path,href))
                if u.netloc!=urlsplit(self.base).netloc:continue
                if u.path in {'/inno/needs/','/inno/','/inno/projects/','/inno/report/','/inno/mcp/','/inno/admin/','/inno/about/'}:continue
                data=self.get(unquote(u.path))
                if u.fragment:
                    target=Links();target.feed(data.decode());self.assertIn(unquote(u.fragment),target.ids,(path,href))
    def test_categories_open_reading_no_counts(self):
        text=self.get('/library/index.html').decode()
        for x in 'ABCDEFG':self.assertIn('data-category="'+x+'"',text)
        for p in (OUT/'methods').glob('*.html'):
            text=p.read_text();self.assertNotIn('<details',text);self.assertIn('id="structure"',text)
            self.assertNotIn('个操作环节',text);self.assertNotIn('条来源',text)
    def test_attachment_whitelist_and_safe_render(self):
        self.assertIn('<h2>',self.get('/library/档案/R17/方法结构.md').decode())
        self.assertEqual(json.loads(self.get('/library/档案/R17/档案.json'))['research_id'],'R17')
        with self.assertRaises(urllib.error.HTTPError):self.get('/library/档案/R17/输入模板.json')
        with self.assertRaises(urllib.error.HTTPError):self.get('/library/../scripts/method_engine.py')
    def test_mcp_config_and_correct_tools(self):
        text=(OUT/'integration.html').read_text();parser=Links();parser.feed(text)
        self.assertIn('METHOD_ENGINE_DB',text);self.assertIn('method_generate_function_options',text)
        self.assertIn('method_run_submit',text)
        self.assertIn('22个工具',text);self.assertIn('method_supplement_get',text)

if __name__=='__main__':unittest.main(verbosity=2)
