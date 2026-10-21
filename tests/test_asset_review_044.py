import sys,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw
from archive_steward import Steward
class AssetTests(unittest.TestCase):
 tearDown=base.ResearchTests.tearDown
 def setUp(self):
  from PIL import Image
  base.ResearchTests.setUp(self);f=self.root/'image.png';Image.new('RGB',(400,300),'blue').save(f);self.img=pp.ingest(self.p,f)['source_id'];self.meta=pp.state(self.p)['sources'][self.img];pp.save(self.p/'图片素材/图片清单.json',dict(items=[dict(library_source_id=self.img,sha256=self.meta['sha256'],title='图像分类',visual_note='已查看；拍摄时间未知',review_status='agent_visual_catalogued_not_engineering_review',rights='未核许可',locations=[])]));self.s=Steward(self.lib,self.inbox);self.t=self.s.enqueue_source('sample',self.img)
  with self.s.connect()as db:db.execute("update tasks set status='awaiting_agent',result=? where id=?",(json.dumps(dict(note='待Agent',processing=dict(status='completed'))),self.t['id']))
 def test_persistent_catalogue_review_and_idempotent_no_fact_change(self):
  before=rw.dataset(self.p);a=self.s.record_asset_review('sample',self.img,self.meta['sha256'],'Agent');self.assertEqual(a['closed_tasks'],[self.t['id']]);self.assertEqual(before,rw.dataset(self.p));b=Steward(self.lib,self.inbox).record_asset_review('sample',self.img,self.meta['sha256'],'Agent');self.assertEqual(a['asset_review_id'],b['asset_review_id']);self.assertEqual(b['closed_tasks'],[])
  with self.s.connect()as db:
   old=json.loads(db.execute("select previous from controls where action='asset_review_recorded'").fetchone()['previous']);self.assertEqual(old['status'],'awaiting_agent');self.assertEqual(json.loads(old['result'])['processing']['status'],'completed')
 def test_conflict_running_or_stale_identity_not_closed(self):
  for status in ['running','needs_attention']:
   with self.s.connect()as db:db.execute('update tasks set status=? where id=?',(status,self.t['id']))
   with self.assertRaises(ValueError):self.s.record_asset_review('sample',self.img,self.meta['sha256'],'Agent')
  with self.assertRaises(ValueError):self.s.record_asset_review('sample',self.img,'wrong','Agent')
 def test_unreviewed_or_nonproject_image_not_approved(self):
  file=self.p/'图片素材/图片清单.json';m=pp.load(file);m['items'][0]['review_status']='pending_semantic_review';pp.save(file,m)
  with self.assertRaises(ValueError):self.s.record_asset_review('sample',self.img,self.meta['sha256'],'Agent')
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.img:dict(scope='shared')},url_rules={}))
  with self.assertRaises(ValueError):self.s.record_asset_review('sample',self.img,self.meta['sha256'],'Agent')
if __name__=='__main__':unittest.main()
