"""ML-008 additive entrypoint: existing 18 tools plus 2 bounded R17 tools.
Use the pinned project runtime. Original frozen MCP entrypoint remains unchanged.
"""
from pathlib import Path
from method_engine_mcp import MCP, ENGINE
from method_engine_store import Store
from method_workbench_morphology import generate_function, assemble, PartGenerationError

MODEL = {'readOnlyHint':False,'destructiveHint':False,'idempotentHint':False,'openWorldHint':True}


def context(run_id, evidence):
    store=Store()
    state=store.get(run_id)
    prior=[s['artifact'] for s in state['submissions'] if s['artifact']['type'] in ('ProblemBrief','FunctionModel')]
    ready=ENGINE.check_inputs('R17',state['task'],prior,evidence)
    if ready['status']=='blocked':
        raise ValueError('R17输入不足；先提交需求和功能模型，并提供其引用的证据：'+str(ready['issues']))
    return state,prior,store.path.parent/'model-parts'


@MCP.tool(annotations=MODEL)
def method_generate_function_options(run_id: str, function_id: str, evidence: list[dict] | None = None) -> dict:
    """Spend ONE model call (90s limit) for 2-3 options of one actual FunctionModel function.
    Requires existing submitted ProblemBrief/FunctionModel and their evidence. Returns a fingerprinted fragment;
    caller must persist it. No automatic retry, combination, submission or expert certification.
    """
    evidence=evidence or []
    state,_,folder=context(run_id,evidence)
    try:
        return generate_function(state,evidence,function_id,folder)
    except PartGenerationError as exc:
        return exc.record


@MCP.tool(annotations=MODEL)
def method_assemble_function_options(run_id: str, parts: dict, evidence: list[dict] | None = None) -> dict:
    """Spend ONE model call to assemble complete same-fingerprint function fragments.
    parts maps every FunctionModel ID to its returned fragment. Checks a full ConceptSet with the frozen engine.
    Returns a draft or blocked record, never auto-submits or certifies compatibility/expertise.
    """
    evidence=evidence or []
    state,prior,folder=context(run_id,evidence)
    try:
        result=assemble(state,evidence,parts,folder)
    except PartGenerationError as exc:
        return exc.record
    checked=ENGINE.check_output('R17',result['artifact'],state['task'],prior,evidence)
    result['check']=checked
    result['status']='blocked' if checked['status']=='blocked' else 'draft_requires_semantic_and_domain_review'
    return result


if __name__=='__main__':
    MCP.run(transport='stdio')
