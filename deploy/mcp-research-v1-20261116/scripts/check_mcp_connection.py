"""Read-only MCP diagnostics. Never accepts a token argument or prints server bodies."""
import argparse
import asyncio
import getpass
import json
import logging
import os
import platform
import re
from urllib.parse import urlsplit
import httpx

DEFAULT_URL = 'https://haoshejiguan.com/inno/mcp/api'


def validate_url(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.query or p.fragment:
        raise ValueError('https_endpoint_without_credentials_query_or_fragment_required')
    return url


def response_summary(response):
    rid = response.headers.get('x-request-id', '')
    return {'http_status': response.status_code,
            'request_id': rid if re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}', rid) else None,
            'redirect_rejected': 300 <= response.status_code < 400}


async def check(url=DEFAULT_URL, token=None, timeout=15, query=None, project_id=None):
    validate_url(url)
    if not 1 <= timeout <= 120:
        raise ValueError('timeout_must_be_1_to_120_seconds')
    if token is not None and (not isinstance(token,str) or not token or token.strip()!=token or token.startswith('Bearer ') or any(c.isspace() for c in token)):
        raise ValueError('raw_token_without_whitespace_or_bearer_prefix_required')
    report = {'endpoint': url, 'platform': platform.system(), 'checks': [],
              'status': 'not_connected', 'authenticated': False, 'model_calls': 0}
    headers = {'Accept':'application/json, text/event-stream'}
    if token:headers['Authorization']='Bearer '+token
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            response = await client.post(url, headers=headers, json={'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'gooddesign-diagnostic','version':'1'}}})
        summary = response_summary(response)
        if token and summary['request_id'] and token in summary['request_id']:
            summary['request_id'] = None
        report['checks'].append({'stage':'http_auth', **summary})
        if summary['redirect_rejected']:
            report['status']='redirect_rejected';return report
        if response.status_code in (401,403):
            report['status']='authentication_rejected' if token else 'credential_required';return report
        if response.status_code != 200:
            report['status']='http_failed';return report
        if not token:
            report['status']='unexpected_unauthenticated_success';return report
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client
        def factory(headers=None, timeout=None, auth=None):
            return httpx.AsyncClient(headers=headers, timeout=timeout, auth=auth, follow_redirects=False)
        async with asyncio.timeout(timeout):
            async with streamablehttp_client(url, headers=headers, timeout=timeout, sse_read_timeout=timeout, httpx_client_factory=factory) as (r,w,_):
                async with ClientSession(r,w) as session:
                    await session.initialize()
                    report['checks'].append({'stage':'initialize','passed':True})
                    tools = await session.list_tools()
                    names = {t.name for t in tools.tools}
                    report['checks'].append({'stage':'tools_list','passed':bool(names),'tool_count':len(names)})
                    if not names or 'inno_capabilities' not in names:
                        report['status']='capabilities_tool_missing';return report
                    result = await session.call_tool('inno_capabilities',{})
                    if result.isError:
                        report['status']='capabilities_failed';return report
                    report['checks'].append({'stage':'capabilities','passed':True})
                    if query:
                        args={'query':query,'limit':1}
                        if project_id:args['project_ids']=[project_id]
                        result=await session.call_tool('inno_search_fields',args)
                        if result.isError:report['status']='query_failed';return report
                        data=result.structuredContent or json.loads(result.content[0].text)
                        report['checks'].append({'stage':'query','passed':True,'returned_count':len(data.get('data',[]))})
                        rows=data.get('data',[])
                        if rows and 'inno_read_claim_evidence' in names:
                            args={k:rows[0][k] for k in ('project_id','revision','record_id','field')}
                            result=await session.call_tool('inno_read_claim_evidence',args)
                            if result.isError:report['status']='evidence_failed';return report
                            report['checks'].append({'stage':'evidence_packet','passed':True})
                    report.update(status='connected',authenticated=True)
    except (TimeoutError,httpx.TimeoutException):report['status']='timeout'
    except Exception:
        # Exception text/groups may contain request headers or server content.
        report['status']='transport_or_protocol_failed'
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default=DEFAULT_URL)
    parser.add_argument('--timeout',type=int,default=15)
    parser.add_argument('--prompt-token',action='store_true')
    parser.add_argument('--query');parser.add_argument('--project-id')
    args=parser.parse_args()
    logging.disable(logging.CRITICAL)
    token=getpass.getpass('MCP access key: ') if args.prompt_token else os.environ.get('GOODDESIGN_MCP_TOKEN')
    try:report=asyncio.run(check(args.url,token,args.timeout,args.query,args.project_id))
    except Exception:report={'status':'invalid_configuration','authenticated':False}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['status']=='connected' else 1

if __name__=='__main__':raise SystemExit(main())
