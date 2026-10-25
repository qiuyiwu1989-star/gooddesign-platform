"""Export authored model artifacts for review, excluding case source bodies and private model logs."""
import json
import sqlite3
from method_engine import ROOT, digest
from method_quality_gate import DIMENSIONS


def export():
    base=ROOT/'output/method-engine-ML003'
    reports=[p for p in (base/'live-revision').glob('*/report.json')
             if json.loads(p.read_text()).get('status')=='corrected_draft_pending_review']
    source=max(reports,key=lambda p:p.stat().st_mtime)
    report=json.loads(source.read_text())
    with sqlite3.connect('file:'+str(source.parent/'run.sqlite3')+'?mode=ro',uri=True) as db:
        task,plan=db.execute('SELECT task,plan FROM runs WHERE id=?',(report['run_id'],)).fetchone()
        task,plan=json.loads(task),json.loads(plan)
        submissions=[json.loads(r[0]) for r in db.execute('SELECT data FROM submissions WHERE run_id=? ORDER BY rowid',(report['run_id'],))]
    artifacts=plan['inputs_snapshot']['artifacts']+[r['artifact'] for r in submissions]
    assert len(artifacts)==6 and len({a['type'] for a in artifacts})==6
    evidence={e['id']:{k:v for k,v in e.items() if k!='text'}
              for e in plan['inputs_snapshot']['evidence']+[e for r in submissions for e in r['evidence']]}
    dest=base/'six-node-review';dest.mkdir(exist_ok=True)
    manifest=[]
    for artifact in artifacts:
        filename=artifact['type']+'.json'
        (dest/filename).write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n')
        manifest.append({'file':filename,'artifact_id':artifact['artifact_id'],'revision':artifact['revision'],'content_sha256':digest(artifact)})
    bundle={'status':'awaiting_independent_domain_review','scenario':'teaching_not_customer',
            'run_id':report['run_id'],'task':task,'artifacts':manifest,'evidence_index':list(evidence.values()),
            'source_bodies_included':False,'expert_certified':False,'engineering_validated':False,
            'source_review_instruction':'Use authorized case MCP to re-read the specified frozen source/chunk/revision. Metadata hashes are not a substitute for reading and assessing support.'}
    (dest/'review-manifest.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2)+'\n')
    template={'reviewer_id':None,'professional_scope':None,'qualification_verified_by':None,'conflicts_of_interest':None,
              'packet_sha256':digest(bundle),'outcome':None,
              'ratings':{d:{'score':None,'basis':None} for d in DIMENSIONS},
              'hard_gate_findings':[],'source_support_findings':[],'issues':[],
              'note':'空白表，不代表已评审；两名评审者各自保存，提交后再讨论。'}
    (dest/'blank-independent-review.json').write_text(json.dumps(template,ensure_ascii=False,indent=2)+'\n')
    (dest/'README.md').write_text('''# 六节点草稿独立评审包

这是夹具教学任务的实际模型产物，含前五份原始草稿及新运行中修订的验证计划。不是客户案例，不是已执行工程试验。原始失败与修订记录另存，未覆盖。

先读review-manifest.json的任务与证据索引，再按ProblemBrief、FunctionModel、ConceptSet、ComparisonRecord、PrototypePlan、VerificationPlan顺序评阅。重点检查硬约束未知时的方案推荐、功能与候选ID交接、需求基线版本、计划覆盖与未验证的区别，以及来源案例的迁移边界。

外部原文未打入此包。证据相关判断必须经授权案例MCP重新读取指定版本，不能仅凭指纹接受。暂时无法取得原文时，把证据支持维度留为待核，不能自动给3分。

两名领域评审者分别复制空白表；不填写虚构姓名或资质。一般AI意见只可作为编辑线索。评审执行与指标口径见平台规划同名文档。
''')
    print(json.dumps({'artifacts':len(artifacts),'evidence_records':len(evidence),'status':bundle['status']},ensure_ascii=False))


if __name__=='__main__':export()
