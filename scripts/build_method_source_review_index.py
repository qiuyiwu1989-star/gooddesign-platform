"""Index declared source support for review; extraction does not validate semantic support."""
import json
from method_engine import ROOT, digest


def build():
    library=ROOT/'04-知识库/创新方法库/深度方法库-v0.1.0'
    output=ROOT/'04-知识库/创新方法库/来源主张复核工作区-v0.1'
    output.mkdir(exist_ok=True)
    claims=[];methods=[];source_count=0
    for path in sorted((library/'档案').glob('*/档案.json')):
        dossier=json.loads(path.read_text());rid=dossier['research_id'];ids=[]
        for source in dossier['sources']:
            source_count+=1
            for index,text in enumerate(source.get('supports',[]),1):
                cid=rid+'-'+source['source_id']+'-C'+str(index);ids.append(cid)
                claims.append({'claim_id':cid,'method_id':rid,'declared_support_statement':text,
                    'source':{k:source.get(k) for k in ('source_id','title','authors','publisher','url','locator','read_scope','accessed_at','rights')},
                    'declared_evidence_note':source.get('evidence_note'),
                    'origin':'existing_dossier_source_supports_field_not_newly_verified_claim',
                    'dossier_sha256':digest(dossier),'semantic_support_review':None,'criticality_review':None,
                    'reviewer_id':None,'review_revision':None,'finding':None})
        methods.append({'method_id':rid,'name':dossier['name'],'kind':dossier['kind'],
            'claim_ids':ids,'declared_gaps':dossier['sections'].get('gaps'),
            'expert_review_status':dossier['review_status'],'engineering_validation_status':dossier['validation_status']})
    data={'status':'extracted_for_review_not_semantically_verified','method_count':len(methods),'source_records':source_count,
          'declared_support_statements':len(claims),'independently_verified_count':None,'methods':methods,'claims':claims,
          'limitations':['source supports fields are author assertions about scope, not original-source quotations',
                        'the index does not exhaust all claims in method principles or steps',
                        'shared URLs and author-dependent sources are not independent confirmations',
                        'unreviewed criticality must not be interpreted as noncritical']}
    (output/'来源主张待复核索引.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (output/'README.md').write_text('''# 来源主张复核工作区

此索引从60份冻结档案的sources.supports字段逐条抽取，保留原来源定位、实际核读范围、释义说明与档案指纹。它把分散记录整理为可分派的复核项；不增加任何已验证数量，也不替代原理、步骤和示例全文审查。

复核时先判断该陈述是否影响方法选择、执行或验收，再按所需范围读取原文，记录支持、部分支持、不支持或无法判断及定位。摘要和目录通常只能支持身份、主题或框架，不能自动支撑完整操作或公式。平台改编步骤要追查改编依据，不冒充原典规定。

关键程度、复核意见与评审人当前均为空。填写后仍需核验评审身份、专业范围与实际读到的版本；不得把作者填表视为独立审核。相同URL的多条记录不能按独立证据累加。
''')
    print(json.dumps({k:data[k] for k in ('method_count','source_records','declared_support_statements','independently_verified_count')},ensure_ascii=False))


if __name__=='__main__':build()
