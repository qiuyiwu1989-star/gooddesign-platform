"""ML-012 opt-in 22-tool entrypoint; original 18/20 entrypoints unchanged."""
from method_engine_incremental_mcp import MCP
from method_library_catalog import supplemental_search,read,catalog
READ={'readOnlyHint':True,'destructiveHint':False,'idempotentHint':True,'openWorldHint':False}

@MCP.tool(annotations=READ)
def method_supplement_search(query: str = '', limit: int = 10) -> dict:
    """Keyword search ONLY the 4 research supplements. Not semantic routing, execution or expert approval."""
    return supplemental_search(query,limit)

@MCP.tool(annotations=READ)
def method_supplement_get(method_id: str) -> dict:
    """Read one supplemental research dossier after checksum verification. No executable contract or certification."""
    valid={x['research_id'] for x in supplemental_search('',60)['methods']}|{x['method_id'] for x in supplemental_search('',60)['methods']}
    if method_id not in valid:raise ValueError('not a supplemental method ID; use original method_get for frozen methods')
    return {'method':read(method_id),'execution_available':False,'expert_certified':False,'scope':'supplement_research_content_only'}

if __name__=='__main__':MCP.run(transport='stdio')
