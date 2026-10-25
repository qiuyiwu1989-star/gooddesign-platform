"""Authored teaching inputs, not customer research, measurements or expert reference answers."""


def teaching_task():
    return {'task_id': 'TEACH-CLAMP', 'revision': 't1', 'object': 'bench clamp',
            'desired_outcome': 'hold a workpiece without visible damage', 'boundary': 'bench teaching only; load and material unknown', 'stage': 'frame'}


def teaching_artifacts():
    payloads = {
      'R48': ('ProblemBrief', {'actor': 'operator', 'object': 'clamp', 'boundary': 'bench teaching only', 'desired_outcome': 'hold without damage',
             'requirements': [{'id': 'Q1', 'text': 'retain workpiece', 'hard': True, 'acceptance': 'representative load to be confirmed', 'status': 'proposed', 'evidence_refs': []}],
             'conditions': [], 'unknowns': ['load', 'material', 'damage criterion']}),
      'R14': ('FunctionModel', {'boundary': 'clamp and workpiece', 'functions': [
             {'id': 'F1', 'verb_object': 'locate workpiece', 'necessity': 'necessary', 'evidence_refs': []},
             {'id': 'F2', 'verb_object': 'apply holding force', 'necessity': 'necessary', 'evidence_refs': []}],
             'flows': [{'id': 'L1', 'from_function': 'F2', 'to_function': 'F1', 'flow_type': 'energy', 'description': 'hypothesized holding action, not proven cause', 'evidence_refs': []}],
             'interfaces': [], 'unknowns': ['force path and contact pressure']}),
      'R17': ('ConceptSet', {'function_ids': ['F1', 'F2'], 'options': [
             {'id': 'O1', 'function_id': 'F1', 'principle': 'reference surface', 'conditions': ['geometry to confirm'], 'evidence_refs': []},
             {'id': 'O2', 'function_id': 'F2', 'principle': 'manual screw with contact pad', 'conditions': ['pad friction and deformation unknown'], 'evidence_refs': []}],
             'combinations': [{'id': 'C1', 'option_ids': ['O1', 'O2'], 'status': 'unknown', 'reason': 'contact and load need tests'}],
             'compatibility': [{'option_ids': ['O1', 'O2'], 'status': 'unknown', 'reason': 'no actual geometry', 'evidence_refs': []}], 'unknowns': ['full motion and contact']}),
      'R36': ('ComparisonRecord', {'requirements_revision': 'a1', 'baseline_id': 'C1', 'candidate_ids': ['C1'], 'criteria': [{'id': 'K1', 'text': 'retain without damage', 'hard': True, 'requirement_ids':['Q1']}],
             'judgments': [{'candidate_id': 'C1', 'criterion_id': 'K1', 'value': 'unknown', 'basis': 'no representative load/material or test', 'evidence_refs': []}],
             'recommendations': [], 'sensitivity': ['material may change preferred contact'], 'unknowns': ['hard gate not established']}),
      'R44': ('PrototypePlan', {'hypothesis': 'a broader contact pad may reduce visible marking while retaining', 'learning_goal': 'test retention and marking jointly',
             'scope': 'contact coupon, not production clamp', 'procedure': ['confirm safe load and material', 'define damage and retention criteria', 'compare contact samples under approved conditions'],
             'measurements': [{'id': 'M1', 'observable': 'retention and surface condition', 'unit_or_scale': 'force unit and damage scale to be approved before test', 'criterion': 'must be specified before execution'}],
             'uncovered_questions': ['fatigue', 'manufacturing tolerances'], 'execution_status': 'planned'}),
      'R42': ('VerificationPlan', {'requirements_revision': 'a1', 'matrix': [{'requirement_id': 'Q1', 'purpose': 'verification', 'method': 'test',
             'criterion': 'load and acceptance require confirmation before test', 'configuration': 'coupon/material/contact configuration to freeze', 'evidence_status': 'planned', 'evidence_refs': []}],
             'validation_questions': ['can the intended operator load and release the workpiece safely?'], 'uncovered_requirements': [], 'execution_status': 'planned'}),
    }
    return {rid: {'artifact_id': 'A-'+rid, 'revision': 'a1', 'task_id': 'TEACH-CLAMP', 'task_revision': 't1',
                  'type': kind, 'scope': 'teaching_proposal_not_engineering_result', 'conditions': [], 'evidence_refs': [], 'payload': payload}
            for rid, (kind, payload) in payloads.items()}
