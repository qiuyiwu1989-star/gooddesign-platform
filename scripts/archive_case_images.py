# coding: utf-8
"""035: preserve images from already archived case sources; no semantic verification."""
import concurrent.futures,io,re,sys,urllib.parse,urllib.request,warnings
from html.parser import HTMLParser
from pathlib import Path
from PIL import Image
import fitz
import project_pipeline as pp
ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Images(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='img':self.images.append((a,'/'.join(x[1]for x in self.stack)))
  if tag not in VOID:self.stack.append((tag,a.get('id','')+' '+a.get('class','')))
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:self.stack=self.stack[:i];break

def candidates(p,sources):
 found={};skipped=[]
 for x in sources:
  if not x['original'].endswith(('.html','.htm')):continue
  sourceurl=x.get('origin',{}).get('url')
  if not sourceurl:continue
  parser=Images();parser.feed(pp.decode((p/x['original']).read_bytes()))
  for order,(a,context)in enumerate(parser.images,1):
   src=a.get('data-original')or a.get('data-src')or a.get('src','');url=urllib.parse.urljoin(sourceurl,src);ctx=context.lower()
   if not src or not url.startswith(('http:','https:')):continue
   if re.search(r'logo|icon|qrcode|qr-new|jiucuo|conac|visitcount|printicon|knowledge_map|readHtml|showEstimate|\.gif(?:\?|$)',url,re.I)or re.search(r'header|footer|nav-child|col-slide|share_list|weixin|gallery-thumbs',ctx):continue
   if 'cnsa.gov.cn'in sourceurl and '/part/'not in url:continue
   if 'cgd.cmes.org/about/'in sourceurl:continue
   location=dict(source_id=x['id'],source_url=sourceurl,image_url=url,html_image_order=order,alt=a.get('alt',''),method='download_original_image',semantic_status='candidate_not_semantically_verified')
   found.setdefault(url,[]).append(location)
 return found

def download(pair):
 url,locations=pair
 try:
  pp.public_url(url);opener=urllib.request.build_opener(pp.Redirect())
  with opener.open(urllib.request.Request(url,headers={'User-Agent':'GoodDesignSourceArchive/0.1'}),timeout=18)as r:data=r.read(pp.MAX_BYTES+1);final=r.url
  if len(data)>pp.MAX_BYTES:raise ValueError('图片超过30MB')
  with warnings.catch_warnings():
   warnings.simplefilter('error',Image.DecompressionBombWarning)
   im=Image.open(io.BytesIO(data));w,h=im.size;fmt=im.format;im.load()
  if min(w,h)<100 or max(w,h)<240:return dict(skip=url,reason='过小，作为网页装饰素材跳过')
  if fmt not in ['JPEG','PNG','WEBP','GIF','TIFF','BMP']:raise ValueError('暂不接收此图像格式')
  return dict(data=data,ext={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp','GIF':'.gif','TIFF':'.tif','BMP':'.bmp'}[fmt],width=w,height=h,kind='web_image',locations=[dict(v,final_image_url=final)for v in locations])
 except Exception as exc:return dict(error=url,reason=str(exc)[:500],locations=locations)

def run(pid='2025-00'):
 p=pp.project(pp.LIB,pid);folder=p/'图片素材';folder.mkdir(exist_ok=True);manifestfile=folder/'图片清单.json';old=pp.load(manifestfile)if manifestfile.exists()else dict(items=[]);assets={x['sha256']:x for x in old['items']};sources=list(pp.state(p)['sources'].values());failures=[];skipped=[]
 def preserve(data,ext,width,height,kind,locations):
  digest=pp.sha(data)
  if digest in assets:
   for loc in locations:
    keys=('source_id','image_url','page','xref','method','html_image_order')
    if not any(all(v.get(k)==loc.get(k)for k in keys)for v in assets[digest]['locations']):assets[digest]['locations'].append(loc)
   return
  title={'web_image':'网页图片','pdf_embedded':'PDF嵌入图片','scan_page':'扫描页图像','patent_drawing_page':'专利附图页'}[kind]+'-'+locations[0]['source_id']+(('-第'+str(locations[0]['page'])+'页')if locations[0].get('page')else '')+'-'+digest[:8]+ext
  path=pp.INBOX/pid/('image-'+digest[:16]+ext);origin=dict(kind='image_asset',filename=title,parent_source_id=locations[0]['source_id'],image_kind=kind,url=locations[0].get('image_url'),note='研究图片保存；语义待审核；PDF页图像为衍生件')
  with pp.lock(pp.LIB):
   pp.save(path.with_name(path.name+'.origin.json'),origin);part=path.with_name('.'+path.name+'.part');part.write_bytes(data);part.replace(path);result=pp.ingest(p,path,origin);meta=pp.state(p)['sources'][result['source_id']]
  assets[digest]=dict(preview_status='ready',id='IMG'+digest[:16],library_source_id=meta['id'],title=title,sha256=digest,original=meta['original'],width=width,height=height,bytes=len(data),kind=kind,locations=locations,review_status='pending_semantic_review',rights='仅私有研究留存；未取得公开再发布授权',created_at=pp.now())
 pairs=candidates(p,sources)
 with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:
  for result in pool.map(download,pairs.items()):
   if 'error'in result:failures.append(result)
   elif 'skip'in result:skipped.append(result)
   else:preserve(**result)
 print('web candidates',len(pairs),'saved',len(assets),'failed',len(failures),flush=True)
 # Limit PDF extraction to the case's explicitly indexed paper and patent originals.
 pdf_ids=set()
 for file in [p/'论文原文管理/论文原件清单.json',p/'专利原文管理/专利原件清单.json']:
  if file.exists():pdf_ids.update(x['library_source_id']for x in pp.load(file)['items']if x.get('original','').endswith('.pdf'))
 source_map={x['id']:x for x in sources}
 for sid in sorted(pdf_ids):
  x=source_map[sid]
  with fitz.open(str(p/x['original']))as doc:
   for number,page in enumerate(doc,1):
    text=page.get_text();compact=''.join(text.split());location=dict(source_id=sid,page=number,source_file=x['original'],semantic_status='unreviewed')
    if not compact or '说明书附图'in compact[:180]:
     scale=min(1.5,1600/max(page.rect.width,1),2000/max(page.rect.height,1));pix=page.get_pixmap(matrix=fitz.Matrix(scale,scale),alpha=False);kind='scan_page'if not compact else 'patent_drawing_page';preserve(pix.tobytes('png'),'.png',pix.width,pix.height,kind,[dict(location,method='render_pdf_page_not_individual_figure')]);continue
    for image in page.get_images(full=True):
     try:
      block=doc.extract_image(image[0]);w,h=block['width'],block['height']
      if min(w,h)<100 or max(w,h)<240:continue
      with Image.open(io.BytesIO(block['image']))as im:im.load()
      preserve(block['image'],'.'+block['ext'],w,h,'pdf_embedded',[dict(location,xref=image[0],method='extract_pdf_embedded_image')])
     except Exception as exc:failures.append(dict(source_id=sid,page=number,reason=str(exc)[:500]))
 manifest=dict(schema_version='case-images-1.0',project_id=pid,updated_at=pp.now(),items=list(assets.values()),failed=failures,skipped=skipped,limits=['网页候选图片语义待审核，部分可能是人物/背景或对照案例图','扫描页和附图页是原PDF的衍生图像，不称独立插图','未下载CSS背景/动态媒体，不宣称图片已穷尽','新增图像不代表原文OCR/专业核读或公开使用授权'])
 pp.save(manifestfile,manifest);(folder/'README.md').write_text('# 图片素材\n\n[打开图片后台](http://127.0.0.1:8776/?project='+pid+'&kind=image)\n\n原图/提取图与PDF整页衍生图分开标记；图片清单记录全部出处、页码、尺寸、哈希及失败项。语义关联和再发布授权未确认。\n');print('all images',len(assets),'failures',len(failures),flush=True);return manifest
if __name__=='__main__':run(sys.argv[1]if len(sys.argv)>1 else '2025-00')
