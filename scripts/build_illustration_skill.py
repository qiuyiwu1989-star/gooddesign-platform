# -*- coding: utf-8 -*-
"""Build a public, portable illustration skill and download page from its source."""
from pathlib import Path
import hashlib,json,shutil,zipfile,html
ROOT=Path(__file__).resolve().parents[1]
NAME='gooddesign-pixel-illustrations';VERSION='1.0.0'
def build(target):
 source=ROOT/'skills'/NAME
 files=[p for p in sorted(source.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts]
 manifest={'name':NAME,'version':VERSION,'files':[{'path':p.relative_to(source).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]}
 (source/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 target=Path(target);target.mkdir(parents=True,exist_ok=True);dest=target/NAME;shutil.copytree(source,dest,dirs_exist_ok=True)
 archive=target/(NAME+'-v'+VERSION+'.zip')
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for p in [*files,source/'manifest.json']:z.write(p,NAME+'/'+p.relative_to(source).as_posix())
 digest=hashlib.sha256(archive.read_bytes()).hexdigest();(target/(archive.name+'.sha256')).write_text(digest+'  '+archive.name+'\n')
 prompt='请读取 https://haoshejiguan.com/inno/portal/skills/gooddesign-pixel-illustrations/SKILL.md，并按其中引用的文件学习好设计“像素工业志”风格。核心要求是原型准确优先、风格统一其次：有原图须先看图并用作参考。请为我指定的项目补充插画，提交原图对照、提示词、版本与审核记录；不要修改正式数据或自行上线。'
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>像素工业志 · Agent绘画Skill</title><style>body{margin:0;background:#f4f5fa;color:#1d2440;font:16px/1.8 system-ui}main{max-width:960px;margin:auto;padding:56px 24px}h1{font-size:clamp(30px,5vw,48px);line-height:1.2}h2{margin-top:40px;font-size:22px}a{color:#5144cb}nav{display:flex;gap:16px;flex-wrap:wrap}.button{display:inline-block;padding:10px 18px;border-radius:12px;background:#5c4be1;color:white;text-decoration:none}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:22px;border-radius:16px;font:15px/1.8 system-ui}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.grid img{width:100%;border-radius:12px}small{overflow-wrap:anywhere;color:#626c85}@media(max-width:600px){.grid{grid-template-columns:1fr}main{padding-top:32px}}</style><main><a href="/museum/zones">← 好设计馆</a><p>GOODDESIGN · AGENT SKILL · vVERSION</p><h1>像素工业志</h1><p>好设计平台的科技复古项目插画规范。<strong>原型准确优先，风格统一其次。</strong></p><nav><a class="button" href="../ARCHIVE">下载完整 Skill</a><a href="SKILL.md">读取 SKILL.md</a><a href="references/review.md">查看验收标准</a></nav><h2>把这段交给其他 Agent</h2><pre>PROMPT</pre><p>可直接按链接读取；支持文件型 Skill 的客户端可下载ZIP，解压后将整个 gooddesign-pixel-illustrations 文件夹放入该客户端的技能目录。客户端仍需具备图像生成/编辑工具；本包不含模型、API密钥或自动部署权限。</p><h2>这套规范包含什么</h2><ul><li>原图重绘、用途场景、无图概念和批量补图流程</li><li>轮廓、比例、部件、配色优先的绘画规则与提示词</li><li>逐件验收表、任务与交付JSON模板</li><li>三张风格示例及本地完整性检查脚本</li></ul><div class="grid"><img src="examples/rover-reference-redraw.webp" alt="金色星球车原图约束重绘"><img src="examples/jiaolong-reference-redraw.webp" alt="红白蛟龙号原图约束重绘"><img src="examples/wing-sail-usage-scene.webp" alt="翼帆船用途概念场景"></div><p>样图只用于学习风格，不替代目标项目原图。原型项未经核对，不能因出图完成就写成通过。</p><h2>包校验</h2><small>ZIP SHA256：DIGEST</small><p><a href="../ARCHIVE.sha256">下载校验值</a> · <a href="manifest.json">文件清单</a></p></main></html>'''.replace('VERSION',VERSION).replace('ARCHIVE',archive.name).replace('PROMPT',html.escape(prompt)).replace('DIGEST',digest)
 (dest/'index.html').write_text(page)
 return {'files':len(manifest['files']),'zip_bytes':archive.stat().st_size,'zip_sha256':digest,'target':str(target)}
if __name__=='__main__':
 import sys
 print(json.dumps(build(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'output/illustration-skill-20261116/public'),ensure_ascii=False))
