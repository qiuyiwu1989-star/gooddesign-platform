"""Safe auth diagnostics. Inputs are classifications, never request headers/body.

Server-generated IDs avoid trusting attacker-controlled correlation identifiers.
Audit failure never changes the deny decision and never exposes exception text.
"""
import json
import re
import secrets
from datetime import datetime, timezone

REASONS = frozenset({'unknown', 'revoked', 'expired', 'malformed', 'registry_unavailable'})
ID_PATTERN = re.compile(r'mcp-[0-9a-f]{32}\Z')


def new_request_id():
    return 'mcp-' + secrets.token_hex(16)


def valid_request_id(value):
    return isinstance(value, str) and bool(ID_PATTERN.fullmatch(value))


def public_denial(request_id):
    if not valid_request_id(request_id):
        raise ValueError('invalid_request_id')
    return {'error': 'access_key_required', 'request_id': request_id,
            'message': 'Configure a valid private MCP access key; contact the administrator with request_id. Never send the key in chat.'}


def denial_event(request_id, reason):
    if not valid_request_id(request_id):
        raise ValueError('invalid_request_id')
    # Unknown input cannot smuggle arbitrary text into logs.
    safe_reason = reason if isinstance(reason, str) and reason in REASONS else 'registry_unavailable'
    return {'event': 'mcp_auth_denied', 'request_id': request_id,
            'reason': safe_reason, 'http_status': 401,
            'at': datetime.now(timezone.utc).isoformat(timespec='seconds')}


def deny(reason, log=None, request_id=None):
    """Return deny response and audit status. log receives one JSON line string.

    Optional request_id is for a server-generated identifier from new_request_id;
    middleware must not populate it from incoming headers. No token, key owner,
    URL, headers, body or exception may be passed to this API.
    """
    rid = request_id if valid_request_id(request_id) else new_request_id()
    event = denial_event(rid, reason)
    written = False
    if log is not None:
        try:
            log(json.dumps(event, ensure_ascii=True, separators=(',', ':')))
            written = True
        except Exception:
            # Do not leak logger exceptions (they may contain configuration).
            pass
    return {'allowed': False, 'http_status': 401, 'body': public_denial(rid),
            'headers': {'X-Request-ID': rid, 'Cache-Control': 'no-store',
                        'WWW-Authenticate': 'Bearer realm="OpenDesign MCP"'},
            'audit_written': written}
