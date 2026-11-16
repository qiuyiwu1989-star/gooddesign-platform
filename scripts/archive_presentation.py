# coding: utf-8
"""Shared human-reading projections; research truth stays unchanged."""
EVIDENCE_KEYS = ('source_id', 'source_sha256', 'chunk_id', 'chunks_path', 'chunks_sha256', 'quote', 'quote_sha256', 'source_read_scope')


def known_cells(record):
    return [(key, cell) for key, cell in record.get('cells', {}).items()
            if cell.get('value_state') == 'known' and cell.get('value') is not None]


def fact_cells(record):
    return [(key, cell) for key, cell in known_cells(record)
            if cell.get('content_nature') == 'source_statement']


def complete_evidence(cell, sources):
    evidence = cell.get('evidence') or {}
    return (all(evidence.get(key) for key in EVIDENCE_KEYS)
            and (evidence.get('locator') or cell.get('locator'))
            and evidence.get('source_id') in sources)
