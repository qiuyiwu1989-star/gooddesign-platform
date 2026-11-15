"""Read-only research projections. No implicit model calls or source writes."""
import copy
import json
import uuid
import innovation_knowledge as ik
import research_workflow as rw
from research_handoff_check import evidence_nodes

VERSION = 'innovation-services-1.0'


def quality_envelope(data, tool_name):
    """Add conservative metadata without upgrading supplied review states."""
    result = copy.deepcopy(data)
    result['service_metadata'] = dict(request_id='read-'+uuid.uuid4().hex,
        service_version=VERSION, schema_version='quality-envelope-1', tool=tool_name,
        quality=dict(semantic_review='not_asserted_by_gateway', expert_review='not_asserted',
                     engineering_validation='not_asserted', target_applicability='requires_review'),
        content_policy='source_statements_AI_and_hypotheses_retain_their_own_labels',
        context_policy='bounded_response_no_silent_truncation',
        coverage_scope='see_payload_coverage_or_project_scope_not_whole_library')
    return result


def mechanism_packet(library, project_id, revision, record_id):
    index = ik.build_index(library, project_id, revision)
    nodes = [n for n in index['nodes'] if n['record_id'] == record_id]
    if not nodes:
        raise ValueError('record_has_no_indexed_mechanism_context')
    groups = {}
    for dimension in ('problem', 'mechanism', 'choice', 'verification', 'boundary', 'constraint'):
        groups[dimension] = []
        for n in nodes:
            if dimension not in n['dimensions']:
                continue
            e = [{k: v for k, v in r.items() if k in ('source_id','source_sha256',
                 'chunks_sha256','chunk_id','quote','quote_sha256','source_read_scope')}
                 for r in n.get('evidence', [])]
            groups[dimension].append(dict(node_id=n['id'], record_id=record_id,
                field=n['field'], value=n['value'], content_nature=n['nature'],
                traceability=n['evidence_state'], evidence=e,
                conditions=n.get('conditions'), limitations=n.get('limitations'),
                sidecar_binding_sha256=n.get('sidecar_binding_sha256'),
                validation_status=n.get('validation_status','not_asserted'),
                review_status=n.get('review_status','not_asserted')))
    return dict(schema_version='mechanism-packet-1', project_id=project_id,
        revision=index['revision'], index_sha256=index['index_sha256'], record_id=record_id,
        source_bindings=index.get('source_bindings',[]),
        membership_policy='sidecar_AI_is_separately_hashed_not_part_of_research_revision',
        sections=groups, missing_dimensions=[k for k,v in groups.items() if not v],
        explicit_relations=[e for e in index['edges'] if e['source']==record_id or e['target']==record_id],
        relation_policy='same_record_and_explicit_references_only_not_reconstructed_design_history',
        scope='bounded_record_context_not_complete_case_or_validated_transfer')


def transfer_check(library, project_id, revision, record_id, requirement):
    """Return a structured comparison task, never infer target equivalence."""
    if not isinstance(requirement, dict):
        raise ValueError('requirement_object_required')
    for key in ('id', 'revision', 'text'):
        if not isinstance(requirement.get(key), str) or not requirement[key].strip():
            raise ValueError('requirement_id_revision_text_required')
    if len(json.dumps(requirement,ensure_ascii=False)) > 12000:
        raise ValueError('requirement_too_large')
    source = mechanism_packet(library, project_id, revision, record_id)
    comparisons = [dict(dimension=k, source_items=source['sections'][k],
         target_evidence='not_supplied_or_not_reviewed', relationship='unknown',
         next_action='identify_target_evidence_and_compare_conditions')
         for k in ('problem','mechanism','constraint','verification','boundary')]
    return dict(schema_version='transfer-review-1',requirement=requirement,
        source_context=source, comparisons=comparisons,
        method_route_proposal=[
            dict(method_id='R48',reason='clarify_unconfirmed_requirements', readiness='needs_host_review'),
            dict(method_id='R14',reason='represent_functions_and_interfaces_after_problem_brief',readiness='requires_ProblemBrief'),
            dict(method_id='R42',reason='plan_evidence_for_claims_and_intended_use',readiness='requires_upstream_artifacts')],
        route_kind='explicit_template_not_semantic_method_optimization',
        status='comparison_worksheet_not_completed_inference',
        prohibited_transfers=['source_parameter_as_target_specification',
                              'source_success_as_target_validation'],
        research_action_contract=['competing_hypotheses','configuration','independent_measurement',
                                  'decision_changed_by_result','stop_or_return_condition'],
        source_projects_modified=False, model_calls=0)
