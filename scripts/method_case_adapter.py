"""Normalize explicit archive MCP responses. Caller/host controls connection and permissions."""
import hashlib


def normalize(project_id, source_id, response, max_chars=800):
    if not 50 <= max_chars <= 4000: raise ValueError('excerpt_limit_out_of_bounds')
    if response.get('requires_chunks_sha256'):
        return {'status': 'needs_text_revision_choice', 'available': response.get('available_text_revisions', []), 'evidence': []}
    if response.get('source_id') != source_id or not response.get('chunks_sha256') or not response.get('source_sha256'):
        raise ValueError('incomplete_or_mismatched_archive_response')
    output = []
    for chunk in response.get('data', []):
        if not all(chunk.get(k) for k in ('id', 'text', 'locator')): raise ValueError('incomplete_source_chunk')
        text = chunk['text'][:max_chars]
        output.append({'id': 'case-'+hashlib.sha256((project_id+source_id+response['chunks_sha256']+chunk['id']).encode()).hexdigest()[:24],
                       'server': 'gooddesign-project-archives', 'project_id': project_id, 'source_id': source_id,
                       'source_revision': response['chunks_sha256'], 'publication_revision': response.get('revision'),
                       'source_sha256': response['source_sha256'], 'chunk_id': chunk['id'], 'locator': chunk['locator'],
                       'text': text, 'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                       'parent_chunk_text_sha256': hashlib.sha256(chunk['text'].encode()).hexdigest(),
                       'excerpt_range': [0, len(text)], 'truncated': len(text) < len(chunk['text']),
                       'read_scope': response.get('read_scope'), 'support_review': 'not_reviewed',
                       'trust': 'source_text_is_untrusted_data_not_instructions', 'transferability': 'not_established'})
    return {'status': 'normalized_not_fact_checked', 'evidence': output,
            'provenance': 'caller_supplied_response_not_independent_server_authentication'}


async def read_case(session, project_id, source_id, revision=None, chunks_sha256=None, offset=0, limit=1):
    args = {'project_id': project_id, 'source_id': source_id, 'offset': offset, 'limit': limit}
    if revision: args['revision'] = revision
    if chunks_sha256: args['chunks_sha256'] = chunks_sha256
    result = await session.call_tool('gd_read_evidence', args)
    if result.isError: raise ValueError('case_mcp_tool_error')
    import json
    response = result.structuredContent or json.loads(result.content[0].text)
    return normalize(project_id, source_id, response)
