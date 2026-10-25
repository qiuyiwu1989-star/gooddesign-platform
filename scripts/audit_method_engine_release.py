"""Evidence audit with separate technical and independent-validation outcomes."""
import hashlib
import json
import re
from jsonschema import Draft202012Validator
from method_engine import ROOT, Engine
from method_engine_contracts import META, OVERLAY, CONTRACT_VERSION, contract
from method_quality_gate import assess


def audit():
    engine=Engine();library=engine.library;manifest=json.loads((library/'manifest.json').read_text())
    file_checks={name:hashlib.sha256((library/name).read_bytes()).hexdigest()==sha for name,sha in manifest['files'].items()}
    catalog=json.loads((library/'目录.json').read_text())['methods']
    dossiers=[engine.get(r['research_id'],'full') for r in catalog]
    contracts=[]
    for rid in META:
        current=contract(rid);Draft202012Validator.check_schema(current['schema'])
        saved=json.loads((OVERLAY/rid/'contract.json').read_text())
        contracts.append({'method':rid,'saved_contract_matches':all(saved.get(k)==v for k,v in current.items())})
    base=ROOT/'output/method-engine-ML003'/('v'+CONTRACT_VERSION)
    log=(base/'final-tests.txt').read_text();tests=re.search(r'Ran (\d+) tests',log)
    sdk=json.loads((base/'mcp-integration.json').read_text())
    reports=[p for p in base.glob('run-*/report.json') if json.loads(p.read_text()).get('status')=='six_artifacts_cross_checked_pending_domain_review']
    live=json.loads(max(reports,key=lambda p:p.stat().st_mtime).read_text()) if reports else None
    gate=assess({'level':'concept'})
    technical={'frozen_library_manifest':all(file_checks.values()),'all_60_dossiers_readable':len(dossiers)==60,
               'six_schemas_and_saved_contracts':len(contracts)==6 and all(c['saved_contract_matches'] for c in contracts),
               'method_tests':bool(tests and int(tests[1])>=65 and '\nOK\n' in log),
               'two_mcp_sdk':sdk.get('contract_version')==CONTRACT_VERSION and len(sdk['checks'])==16 and all(c['passed'] for c in sdk['checks']),
               'real_model_six_artifact_cross_checks':bool(live and len(live['all_six_checks'])==6 and all(x['check']['status']!='blocked' for x in live['all_six_checks'])),
               'quality_gate_rejects_incomplete_packet':gate['status']=='blocked' and gate['expert_certified'] is False}
    result={'contract_version':CONTRACT_VERSION,'technical_checks':technical,'technical_checks_passed':all(technical.values()),
            'library_files_verified':len(file_checks),'contracts':contracts,'method_tests':int(tests[1]) if tests else None,
            'live_run_id':live['run_id'] if live else None,'expert_certified':False,'overall_expert_goal_complete':False,
            'remaining_required_evidence':{'independent_domain_review':'not_obtained','real_customer_pilot':'not_obtained',
                'expert_reference_and_held_out_tasks':'not_completed','engineering_validation':'not_performed'},
            'scope':'Checks explicitly listed above only; no factual accuracy, expert equivalence, universal method coverage or engineering validation inferred.'}
    (base/'completion-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'technical_checks_passed':result['technical_checks_passed'],'overall_expert_goal_complete':False,'library_files':len(file_checks)},ensure_ascii=False))


if __name__=='__main__':audit()
