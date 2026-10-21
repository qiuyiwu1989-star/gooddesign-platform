# coding: utf-8
import sys,io,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_file_admin_033 as base
import project_pipeline as pp,archive_case_images as images
import fitz
from PIL import Image
class RelatedImagesTests(unittest.TestCase):
 setUp=base.FileAdminTests.setUp
 tearDown=base.FileAdminTests.tearDown
 request=base.FileAdminTests.request
 def test_related_pdf_image_keeps_parent_and_is_idempotent(self):
  buffer=io.BytesIO();Image.new('RGB',(400,300),'navy').save(buffer,format='PNG')
  doc=fitz.open();page=doc.new_page();page.insert_text((40,30),'article full text');page.insert_image(fitz.Rect(40,40,440,340),stream=buffer.getvalue());pdf=self.root/'paper.pdf';doc.save(pdf);doc.close();p=self.lib/'demo-01';x=pp.ingest(p,pdf)
  pp.save(p/'论文原文管理/论文原件清单.json',dict(items=[dict(paper_id='A01',library_source_id='HTML-main',original='来源/HTML-main/原件.html',related_source_ids=[x['source_id']])]))
  with patch.object(pp,'LIB',self.lib),patch.object(pp,'INBOX',self.inbox):
   first=images.run('demo-01',source_ids={x['source_id']});second=images.run('demo-01',source_ids={x['source_id']})
  self.assertEqual(len(first['items']),1);self.assertEqual(len(second['items']),1);a=first['items'][0];self.assertEqual(a['locations'][0]['source_id'],x['source_id']);self.assertEqual(a['locations'][0]['page'],1);self.assertEqual(a['review_status'],'pending_semantic_review');self.assertEqual(a['kind'],'pdf_embedded')
if __name__=='__main__':unittest.main()
