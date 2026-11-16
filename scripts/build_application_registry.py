import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / 'extensions/application-center/apps.json'
CASES = ROOT / 'extensions/application-center/cases.json'
SCHEMA = ROOT / 'extensions/application-center/application.schema.json'

FORBIDDEN_CLAIMS = {
    'approved',
    'confirmed',
    'customer_confirmed',
    'engineering_validated',
    'expert_reviewed',
    'model_called',
    'remote_write',
    'recommendations',
    'public',
    'training_authorized',
}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_apps(apps, cases):
    jsonschema.validate(apps, load_json(SCHEMA))
    case_ids = {case['id'] for case in cases}
    app_ids = [app['id'] for app in apps]
    if len(app_ids) != len(set(app_ids)):
        raise ValueError('duplicate_app_id')
    for app in apps:
        missing = [case_id for case_id in app['evidence']['case_ids'] if case_id not in case_ids]
        if missing:
            raise ValueError(f'unknown_case_id:{app["id"]}:{",".join(missing)}')
        unknown_claims = set(app['evidence']['forbidden_claims']) - FORBIDDEN_CLAIMS
        if unknown_claims:
            raise ValueError(f'unknown_forbidden_claims:{app["id"]}')
        if app['status'] in {'planned', 'deprecated'} and app['permissions']['requires_login']:
            raise ValueError(f'planned_or_deprecated_app_requires_login:{app["id"]}')
        if app['capabilities']['mcp_status'] == 'not_connected' and app['capabilities']['mcp_tools']:
            raise ValueError(f'not_connected_app_lists_mcp_tools:{app["id"]}')
    return apps


def build_registry():
    apps = load_json(APPS)
    cases = load_json(CASES)
    validate_apps(apps, cases)
    case_map = {case['id']: {'id': case['id'], 'title': case['title'], 'status': case['status'], 'status_label': case['status_label'], 'summary': case['summary'], 'route': f'/inno/cases/{case["id"]}/'} for case in cases}
    return {
        'registry_schema_version': 'gd-app-registry-0.1',
        'app_schema_version': 'gd-app-0.1',
        'apps': apps,
        'cases': case_map,
        'agent_onboarding': [
            'read_registry',
            'read_application_manifest',
            'call_inno_capabilities',
            'search_projects_or_methods',
            'read_versioned_evidence',
            'prepare_research_context',
            'validate_gdrp_package',
            'submit_for_review',
        ],
        'boundaries': {
            'mcp': 'remote_read_only',
            'source_archive_writes': 'forbidden',
            'research_history': 'client_side',
            'model_calls': 'not_provided_by_registry',
        },
    }


def main():
    print(json.dumps(build_registry(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
