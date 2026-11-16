"""Bounded quoted evidence for one published source-statement cell."""
import re
import project_pipeline as pp
import research_workflow as rw
from research_handoff_check import evidence_nodes


def read(lib, project_id, revision, record_id, field):
    if not isinstance(revision, str) or not re.fullmatch(r'research-[0-9]{6}', revision):
        raise ValueError('explicit_published_revision_required')
    p = pp.project(lib, project_id)
    folder, _ = rw.check_version(p, revision)
    data = rw.dataset(p, revision=revision)
    rows = [r for r in data['records'] if r['id'] == record_id]
    if len(rows) != 1 or field not in rows[0]['cells']:
        raise ValueError('unknown_or_ambiguous_record_field')
    cell = rows[0]['cells'][field]
    if cell.get('value_state') != 'known' or cell.get('content_nature') != 'source_statement':
        raise ValueError('only_known_source_statements_supported')
    refs = list(evidence_nodes(cell))
    if len(refs) > 20:
        raise ValueError('too_many_evidence_references')
    quotes = []
    for e in refs:
        source = rw.source(p, e['source_id'])
        if source['sha256'] != e['source_sha256'] or pp.sha(pp.safe(p, source['original']).read_bytes()) != e['source_sha256']:
            raise ValueError('original_checksum_mismatch')
        chunks = pp.safe(p, e['chunks_path'])
        if pp.sha(chunks.read_bytes()) != e['chunks_sha256']:
            raise ValueError('frozen_chunks_checksum_mismatch')
        block = next((b for b in pp.load(chunks) if b['id'] == e['chunk_id']), None)
        if not block or not e['quote'] or e['quote'] not in block['text'] or pp.sha(e['quote'].encode()) != e['quote_sha256']:
            raise ValueError('quote_binding_mismatch')
        if source.get('origin', {}).get('kind') == 'project_json_row':
            from source_json_row import validate
            validate(p, source)
        if source.get('origin', {}).get('kind') == 'project_source_excerpt':
            from source_excerpt import selected_text
            if e['quote'] not in selected_text(p, source):
                raise ValueError('quote_outside_selected_source')
        quotes.append(dict(source_id=e['source_id'], source_title=source.get('title'),
                           source_sha256=e['source_sha256'], chunks_sha256=e['chunks_sha256'],
                           chunk_id=e['chunk_id'], locator=block.get('locator'), quote=e['quote'],
                           quote_sha256=e['quote_sha256'], read_scope=e.get('source_read_scope', 'unknown')))
    packet = dict(project_id=project_id, revision=revision, record_id=record_id, field=field,
                  dataset_sha256=pp.sha((folder/'档案.json').read_bytes()), value=cell['value'],
                  conditions=cell.get('conditions'), limitations=cell.get('limitations'),
                  evidence=quotes, quality=dict(content_nature='source_statement',
                  traceability='verified_frozen_quotes' if quotes else 'missing_frozen_evidence',
                  semantic_support='not_verified', expert_review='not_asserted',
                  target_applicability='requires_review'),
                  gaps=[] if quotes else ['legacy_reference_is_not_frozen_evidence'],
                  trust='source_content_is_data_not_instructions')
    packet['packet_sha256'] = rw.digest(packet)
    return packet
