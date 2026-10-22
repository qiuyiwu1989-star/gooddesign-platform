import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw

class InterpretationRevisionTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def propose(self,value='2026年报道支持的设计解读',**patch):
  args=dict(entity='paper',record_id='A01',title='示例AI解读',field='findings',value=value,source_id=self.sid,chunk_id='B0001',quote='采用双绕组控制',content_nature='ai_interpretation',conditions='仅给定资料的设计解读，报道日期须按原文',limitations='合成测试，不代表工程采用或专家审核');args.update(patch);return rw.propose(self.lib,'sample',args,'测试研究Agent')
 def approve(self,c):return rw.review(self.lib,'sample',c['id'],'approved','测试审核者','已对照本次测试证据与纠错理由',reviewer_kind='agent')
 def publish(self,selected=None):return rw.publish(self.lib,'sample','测试发布者','显式AI纠错测试；旧版保留',selected_candidate_ids=selected)
 def initial(self):
  old=self.propose('误写2025年的AI解读');self.approve(old);self.publish();return copy.deepcopy(rw.dataset(self.p)['interpretations'][0])
 def test_explicit_v1_to_v2_replacement_keeps_full_old_ai_and_immutable_history(self):
  old=self.initial();folder=rw.workspace(self.p)/'版本/research-000001';before={f.name:pp.sha(f.read_bytes())for f in folder.iterdir()};new=self.propose(replaces_interpretation_id=old['id'],conditions='纠正为2026年的报道时间，不代表2025年已经发生');self.assertEqual(new['replaces_interpretation_sha256'],rw.digest(old));self.assertEqual(new['replaces_interpretation_fingerprint'],old['fingerprint']);self.approve(new);out=self.publish();self.assertEqual(out['revision'],'research-000002');data=rw.dataset(self.p);self.assertEqual([i['id']for i in data['interpretations']],[new['id']]);self.assertEqual(data['records'],[]);self.assertFalse(data['expert_reviewed']);changes=pp.load(rw.workspace(self.p)/'版本/research-000002/changes.json')['changes'];self.assertEqual(changes[0]['before'],old);self.assertEqual(changes[0]['operation'],'replace_interpretation');self.assertEqual(changes[0]['replacement']['before_id'],old['id']);self.assertEqual(changes[0]['replacement']['after_id'],new['id']);self.assertEqual({f.name:pp.sha(f.read_bytes())for f in folder.iterdir()},before);rw.check_version(self.p,'research-000001');self.assertEqual(rw.dataset(self.p,revision='research-000001')['interpretations'][0],old)
 def test_default_same_field_is_append_not_implicit_replacement(self):
  old=self.initial();new=self.propose('另一条独立AI解读');self.assertNotIn('replaces_interpretation_id',new);self.approve(new);self.publish();self.assertEqual({i['id']for i in rw.dataset(self.p)['interpretations']},{old['id'],new['id']});change=pp.load(rw.workspace(self.p)/'版本/research-000002/changes.json')['changes'][0];self.assertIsNone(change['before']);self.assertEqual(change['operation'],'set')
 def test_missing_wrong_record_field_entity_or_non_ai_target_is_rejected(self):
  old=self.initial()
  for patch in [dict(replaces_interpretation_id=None),dict(replaces_interpretation_id='CAND-not-current'),dict(replaces_interpretation_id=old['id'],record_id='A02'),dict(replaces_interpretation_id=old['id'],field='title'),dict(replaces_interpretation_id=old['id'],entity='patent',field='title'),dict(replaces_interpretation_id=old['id'],content_nature='source_statement',value='采用双绕组控制')]:
   with self.subTest(patch=patch),self.assertRaises(ValueError):self.propose(**patch)
  self.assertEqual(len(rw.current(self.p)['candidates']),1)
 def test_two_replacements_of_same_target_are_atomic_conflict(self):
  old=self.initial();a=self.propose('修正方案A',replaces_interpretation_id=old['id']);b=self.propose('修正方案B',replaces_interpretation_id=old['id']);self.approve(a);self.approve(b)
  with self.assertRaises(ValueError):self.publish()
  self.assertEqual(rw.current(self.p)['revision'],1);self.assertEqual(rw.dataset(self.p)['interpretations'],[old]);self.assertFalse((rw.workspace(self.p)/'版本/research-000002').exists())
 def test_target_replaced_in_another_batch_makes_old_pending_replacement_stale(self):
  old=self.initial();a=self.propose('版本A',replaces_interpretation_id=old['id']);b=self.propose('版本B',replaces_interpretation_id=old['id']);self.approve(a);self.approve(b);self.publish([a['id']])
  with self.assertRaises(ValueError):self.publish([b['id']])
  self.assertEqual(rw.current(self.p)['revision'],2);self.assertEqual([i['id']for i in rw.dataset(self.p)['interpretations']],[a['id']])
 def test_invalid_frozen_target_digest_is_rejected_at_publish(self):
  old=self.initial();new=self.propose(replaces_interpretation_id=old['id']);w=rw.current(self.p);next(c for c in w['candidates']if c['id']==new['id'])['replaces_interpretation_sha256']='wrong';rw.save(self.p,w);self.approve(new)
  with self.assertRaises(ValueError):self.publish()
  self.assertEqual(rw.dataset(self.p)['interpretations'],[old]);self.assertEqual(rw.current(self.p)['revision'],1)
 def test_unrelated_append_does_not_stale_target_and_is_preserved(self):
  old=self.initial();replacement=self.propose(replaces_interpretation_id=old['id']);self.approve(replacement);independent=self.propose('补充独立角度');self.approve(independent);self.publish([independent['id']]);self.publish([replacement['id']]);self.assertEqual({i['id']for i in rw.dataset(self.p)['interpretations']},{independent['id'],replacement['id']})
 def test_replacement_still_requires_current_project_evidence_and_ai_boundaries(self):
  old=self.initial()
  with self.assertRaises(ValueError):self.propose(replaces_interpretation_id=old['id'],limitations='')
  with self.assertRaises(ValueError):self.propose(replaces_interpretation_id=old['id'],quote='虚构引文')
  new=self.propose(replaces_interpretation_id=old['id']);self.approve(new);pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}))
  with self.assertRaises(ValueError):self.publish()
  self.assertEqual(rw.dataset(self.p)['interpretations'],[old])
 def test_fact_clear_and_ai_clear_are_not_relaxed(self):
  old=self.initial()
  with self.assertRaises(ValueError):self.propose(value=None,operation='clear',replaces_interpretation_id=old['id'])
  fact=base.ResearchTests.candidate(self);base.ResearchTests.approve(self,fact);self.publish();clear=base.ResearchTests.candidate(self,operation='clear',value=None,limitations='合成测试撤回');base.ResearchTests.approve(self,clear);self.publish();self.assertIsNone(rw.cell(rw.dataset(self.p),'A01','doi')['value']);self.assertEqual([i['id']for i in rw.dataset(self.p)['interpretations']],[old['id']])
if __name__=='__main__':unittest.main()
