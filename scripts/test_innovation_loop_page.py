import unittest
from innovation_loop_page import page
class PageTests(unittest.TestCase):
 def test_escape(self):
  s=page({'requirement':{'goal':'</pre><script>alert(1)</script>'}})
  self.assertIn('&lt;/pre&gt;&lt;script&gt;',s);self.assertNotIn('</pre><script>alert',s)
 def test_interfaces(self):
  s=page({});self.assertIn('/inno/portal/system.css',s);self.assertIn("fetch('/api/bundle'+window.location.search",s);self.assertIn("fetch('/api/feedback'",s);self.assertIn('aria-live="polite"',s);self.assertIn('type="button"',s);self.assertIn('textContent=JSON.stringify',s)
 def test_feedback_form_and_action(self):
  s=page({'claims':[],'research_action':{'question':'构造研究'},'transfer':{'assumptions':['待验证']}})
  for token in ('route-select','internal-consent','feedback-kind','结构迁移假设','研究行动与停止条件','该路线尚无可绑定的主张记录'):
   self.assertIn(token,s)
  self.assertIn('claim_ref:{id:claim.id,revision:claim.revision}',s)
 def test_inert_json_escape(self):
  import re,json
  value={'notice':'</script><script>bad</script>'}
  s=page(value);encoded=re.search(r'id="initial-bundle">(.*?)</script>',s).group(1)
  self.assertNotIn('<',encoded);self.assertEqual(json.loads(encoded),value)
 def test_nested_reading_and_refresh_equivalence(self):
  import re,json,ast
  from pathlib import Path
  from innovation_loop_page import friendly
  self.assertEqual(friendly({'value':'原文','nature':'source_statement'}),'原文（来源陈述）')
  self.assertEqual(friendly({'status':'required'}),'状态：需要专业批准')
  source=Path(__file__).with_name('innovation_loop_page.py').read_text()
  static=ast.literal_eval(re.search(r'        labels=(\{.*\})',source).group(1))
  dynamic=json.loads(re.search(r'const labels=(\{.*?\});for\(const row',source).group(1))
  self.assertEqual(static,dynamic)
  s=page({'experiences':[{'object_scope':'特定设备','mechanism':{'value':'过程','nature':'source_statement'}}],'requirement':{'status':'proposed'}})
  self.assertIn('经验对象',s);self.assertIn('过程（来源陈述）',s);self.assertIn('待确认提案',s)
 def test_task_selector(self):
  s=page({'tasks':[{'task_id':'rubber-v1','title':'割胶'}],'current_task_id':'rubber-v1'})
  self.assertIn('task-select',s);self.assertIn("url.searchParams.set('task'",s);self.assertIn('研究行动与停止条件',s);self.assertIn('本任务方法',s)
 def test_bad_bundle(self):
  with self.assertRaises(ValueError):page([])
 def test_decision_overview_and_side_panel(self):
  s=page({'routes':[{'id':'R','mechanism':'unsafe </script>'}],'clarifications':[]})
  for token in ['decision-overview','route-grid','evidence-panel','showModal()','反馈这条路线','/api/clarifications','待确认补充','clarify-records']:
   self.assertIn(token,s)
  self.assertIn('不自动改写需求',s)
  self.assertNotIn('unsafe </script>',s)
if __name__=='__main__':unittest.main()
