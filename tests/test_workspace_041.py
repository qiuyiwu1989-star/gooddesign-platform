# coding: utf-8
"""041 read routes, strict HTML policy, project isolation and immutable historical render."""
import re,sys,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import test_file_admin_033 as base
import project_pipeline as pp,innovation_methods as im,workspace_ui
class WorkspaceTests(base.FileAdminTests):
 def add_case(self):
  p=self.root/'second.json';pp.save(p,dict(projects=[dict(id='2025-00',name='隔离嫦娥')]))
  pp.bootstrap(self.lib,self.inbox,p,self.root/'no-original')
 def test_admin_is_html_not_json_and_navigation_is_project_bound(self):
  code,body,head=self.request('/?project=demo-01');self.assertEqual(code,200);self.assertTrue(body.startswith(b'<!doctype html>'));self.assertNotIn(b'\\n<header',body)
  text=body.decode();self.assertIn('/dossier/?project=demo-01',text);self.assertIn('data-admin-view="review" hidden',text)
  self.assertEqual(self.request('/workspace.js')[0],200);self.assertEqual(self.request('/workspace.css')[0],200)
  nonce=re.search(r'<style nonce="([^"]+)"',text)[1];self.assertIn("'nonce-"+nonce+"'",head['Content-Security-Policy']);self.assertNotIn("unsafe-inline",head['Content-Security-Policy'])
  self.assertNotEqual(nonce,re.search(r'<style nonce="([^"]+)"',self.request('/?project=demo-01')[1].decode())[1])
 def test_unresearched_project_does_not_receive_chang_e_contents(self):
  for route in ['/dossier/','/methods/']:
   status,body,_=self.request(route+'?project=demo-01');self.assertEqual(status,200);self.assertIn('本项目'.encode(),body);self.assertNotIn('具有层次差异的颗粒材料'.encode(),body);self.assertNotIn('filename'.encode(),body)
 def test_dossier_is_same_baseline_and_source_remains_unchanged(self):
  self.add_case();source=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样/档案.html';before=pp.sha(source.read_bytes());status,body,_=self.request('/dossier/?project=2025-00');self.assertEqual(status,200);text=body.decode();self.assertIn('workspace-header',text);self.assertIn('人工整合档案',text);self.assertIn('55',text);self.assertIn('资料与解读',text);self.assertIn('档案评估',text);self.assertEqual(before,pp.sha(source.read_bytes()))
  self.assertEqual(self.request('/dossier/?project=../bad')[0],400);self.assertEqual(self.request('/dossier/?project=missing')[0],400)
 def test_no_generic_private_file_server(self):
  self.assertEqual(self.request('/dossier/../../AGENTS.md')[0],404);self.assertEqual(self.request('/dossier/raw/data.json')[0],404)
 def test_fresh_environment_shows_an_empty_research_state(self):
  missing=self.root/'empty-runs';missing.mkdir()
  with patch.object(im,'RUNS',missing):
   code,body,_=self.request('/methods/');self.assertEqual(code,200);self.assertIn('还没有生成应用研究记录'.encode(),body);self.assertNotIn('取到样品'.encode(),body)
 def test_report_retains_methods_evidence_and_fixed_scenario_boundary(self):
  from render_method_demo import render
  run=im.read_run('latest','full');before=pp.sha((im.RUNS/run['run_id']/'run.json').read_bytes());text=render(run)
  self.assertIn('evidence-dialog',text);self.assertIn('id="questions"',text);self.assertIn('id="tests"',text);self.assertEqual(text.count('role="tab"'),6);self.assertIn('尚待企业现场核对',text);self.assertIn('不会对新需求自动推理',text)
  self.assertEqual(before,pp.sha((im.RUNS/run['run_id']/'run.json').read_bytes()))
if __name__=='__main__':unittest.main()
