"""Build honest local acceptance view, preserving distinction between operation and expert quality."""
import hashlib
import html
import json
from pathlib import Path
from method_engine import ROOT, digest
from method_quality_gate import assess


def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def build():
    base=ROOT/'output/method-engine-ML003';base.mkdir(exist_ok=True)
    runs=sorted((base/'live-chain').glob('*/report.json'),key=lambda f:f.stat().st_mtime)
    live=json.loads(runs[-1].read_text()) if runs else None
    revisions=sorted((base/'live-revision').glob('*/report.json'),key=lambda f:f.stat().st_mtime)
    revised=json.loads(revisions[-1].read_text()) if revisions else None
    integration=json.loads((base/'mcp-integration.json').read_text())
    benchmarks=json.loads((base/'expert-review-pack/evaluation-status.json').read_text())
    model_protocol=json.loads((base/'live-model-mcp.json').read_text()) if (base/'live-model-mcp.json').exists() else None
    passport={'type':'research_run_quality_passport','expert_certified':False,'engineering_validated':False,
        'independent_review':'not_obtained','engineering_evidence':'not_provided',
        'live_chain_status':live['status'] if live else 'not_finished',
        'method_mcp_operational_checks':len(integration['checks']),
        'model_review_tasks':len(benchmarks['tasks']),
        'available_model_proposals':sum(x['status']=='available_model_proposal' for x in benchmarks['tasks']),
        'expert_pass_rate':None,'contract_snapshots':[]}
    passport['post_review_revision_status']=revised['status'] if revised else 'not_available'
    passport['post_review_revision_report']=str(revisions[-1]) if revisions else None
    if runs and (runs[-1].parent/'post-review-recheck.json').exists():
        passport['original_run_recheck']=json.loads((runs[-1].parent/'post-review-recheck.json').read_text())['status']
    if live:
        passport['task']=live['task'];passport['run_id']=live['run_id'];passport['source_refs']=live['evidence_refs']
        for step in live['steps']:
            call=ROOT/'04-知识库/创新方法库/运行数据-v0.2/model-calls'/step.get('call_id','')
            if (call/'input.json').exists():
                snapshot=json.loads((call/'input.json').read_text())['payload']['contract']
                passport['contract_snapshots'].append({'method':step['method'],'contract':snapshot,'sha256':digest(snapshot)})
        packet={'revision':'passport-1','task_revision':live['task']['revision'],
                'method_versions':[x['method'] for x in live['steps']], 'scope':live['task']['boundary'],
                'author_id':'model_generated_teaching_drafts','level':'concept',
                'claims':[{'kind':'hypothesis','critical':True,'text':'Concept drafts may guide later investigation',
                           'verification_question':'Independent domain review and actual task evaluation are still required'}],
                'evidence':[],'hard_constraints_checked':False,'reviews':[],'ratings':{},
                'issues':[{'severity':'major','status':'open','text':'No independent expert review; key customer conditions unknown'}]}
        passport['publication_gate']=assess(packet)
        dump(base/'live-quality-packet.json',packet)
    dump(base/'quality-passport.json',passport)
    cards=[]
    for row in benchmarks['tasks']:
        target=Path(row['result_path']) if row.get('result_path') else None
        proposal=json.loads(target.read_text())['proposal'] if target and target.exists() else None
        cards.append('<details><summary>'+html.escape(row['id']+' · '+row['status'])+'</summary>'+
                     ('<p>'+html.escape(proposal['rationale'])+'</p><p>方法：'+html.escape('、'.join(proposal['selected_methods']))+'</p>' if proposal else '<p>未执行</p>')+
                     '<p>独立专家评分：待评</p></details>')
    (base/'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>方法引擎技术验收与质量状态</title><style>body{font:15px/1.9 system-ui,sans-serif;background:#f4f5f8;color:#16181f;max-width:1000px;margin:40px auto;padding:24px}section,details{padding:22px;background:white;border:1px solid #dde0e9;border-radius:15px;margin:15px 0}summary{cursor:pointer}a{color:#5a4fe6}pre{white-space:pre-wrap;overflow-wrap:anywhere}.status{border-left:4px solid #c88620;padding-left:14px}</style>
<h1>方法引擎：技术能力与专家质量分开验收</h1><p class="status">本机研究版本 · 专家评审待完成 · 不作为工程已验证方案</p>
<section><h2>已运行能力</h2><p>六方法契约、输入绑定、规则匹配、可选真实模型、案例证据适配、版本化运行和质量必要条件门禁。18个独立stdio MCP工具。</p>
<p>真实案例/方法双服务 SDK检查：'''+str(len(integration['checks']))+'''项。模型经MCP调用：'''+html.escape(model_protocol['status'] if model_protocol else '未执行')+'''。</p>
<p>实时六节点模型链：'''+html.escape(passport['live_chain_status'])+'''。复读后修订状态：'''+html.escape(passport['post_review_revision_status'])+'''。原始记录不覆盖；这与预编写教学fixture的SDK检查分别保存。</p>
<a href="mcp-integration.json">SDK证据</a> · <a href="live-model-mcp.json">真实模型MCP</a> · <a href="quality-passport.json">质量护照</a> · <a href="mcp-config.local.json">Host本地配置</a></section>
<section><h2>尚不能宣称</h2><p>模型提案不是专家答案，结构与引用检查不证明语义正确，源案例成功不证明客户方案可行。独立领域评审、真实客户任务与相关工程证据仍未取得；专家达标率保持空值。</p></section>
<section><h2>十二题待评提案</h2><p>作者编写的标定任务；不是独立专家金标准，也不是留出测试。</p>
<a href="expert-review-pack/review-tasks.json">题目</a> · <a href="expert-review-pack/review-instructions.md">独立评审说明</a> · <a href="expert-review-pack/evaluation-status.json">执行与待评状态</a></section>'''+''.join(cards)+'</html>')
    print(json.dumps({'live_chain':passport['live_chain_status'],'proposals':passport['available_model_proposals'],
                      'publication_status':passport.get('publication_gate',{}).get('status'),'index':str(base/'index.html')},ensure_ascii=False))


if __name__=='__main__':build()
