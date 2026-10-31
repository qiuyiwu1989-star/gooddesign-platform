"""ML024 local-only explicit private study loop; not remote production MCP."""
from mcp.server.fastmcp import FastMCP
from innovation_loop_store import LoopStore,ROOT
from innovation_loop_evidence import verify_experience_files
from innovation_loop_experience import load_experiences,search_experiences
from innovation_loop_decision import compare_routes
from method_engine_cognition import read_deep_method
MCP=FastMCP('gooddesign-loop-024')
SAMPLE=ROOT/'output/innovation-loop-024/experience/active-experience-catalog-v1.json'
READ={'readOnlyHint':True,'destructiveHint':False,'openWorldHint':False}
@MCP.tool(annotations=READ)
def loop_capabilities()->dict:
 return {'scope':'local_private_research','engineering_approved':False,'model_calls':0,'only_write':'loop_save_record','source_archives_modified':False}
@MCP.tool(annotations=READ)
def loop_tasks()->dict:
 from innovation_loop_tasks import list_tasks
 return {'tasks':list_tasks(),'domain_validated':False}
@MCP.tool(annotations=READ)
def loop_task_bundle(task_id:str)->dict:
 from innovation_loop_server import bundle
 return bundle(task_id)
@MCP.tool(annotations=READ)
def loop_experiences(query:str,limit:int=5)->dict:
 records=load_experiences(SAMPLE)
 for record in records:verify_experience_files(record)
 return search_experiences(records,query,limit)
@MCP.tool(annotations=READ)
def loop_read_record(kind:str,record_id:str,revision:int)->dict:
 return LoopStore().get(kind,record_id,revision)
@MCP.tool(annotations=READ)
def loop_read_method(method_id:str)->dict:
 return read_deep_method(method_id)
@MCP.tool(annotations=READ)
def loop_compare(requirement_id:str,revision:int,route_refs:list[dict])->dict:
 s=LoopStore();rq=s.get('requirement',requirement_id,revision)
 return compare_routes(rq,[s.get('route',r['id'],r['revision']) for r in route_refs])
@MCP.tool(annotations={'readOnlyHint':False,'destructiveHint':False,'openWorldHint':False})
def loop_save_record(kind:str,record:dict,expected_revision:int=0)->dict:
 """Explicit local persistence of study proposals/feedback only; never source facts or ratings."""
 return LoopStore().put(kind,record,expected_revision)
if __name__=='__main__':MCP.run(transport='stdio')
