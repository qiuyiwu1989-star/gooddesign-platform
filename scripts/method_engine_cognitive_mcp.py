"""Opt-in ML022 entrypoint; existing 18/20/22-tool entrypoints stay unchanged."""
from method_engine_library_mcp import MCP, READ
from method_engine_cognition import read_deep_method, prepare_context, feedback_summary


@MCP.tool(annotations=READ)
def method_deep_content(method_id: str) -> dict:
    """Read hash-checked ML021 teaching content and partial source-depth ratings."""
    return read_deep_method(method_id)


@MCP.tool(annotations=READ)
def innovation_reasoning_context(task: dict, claims: list[dict], method_ids: list[str],
                                 conflicts: list[dict] | None = None,
                                 associations: list[dict] | None = None) -> dict:
    """Prepare explicit evidence-scoped Host context; no LLM, case fetch or memory write.

    Validates supplied anchors and proposal shapes, not truth or structural analogy.
    Each claim: id,text,scope,epistemic(observed/inferred/associated/hypothesized),
    evidence[{source_id,locator,scope}]. Selected methods: 1..5 IDs.
    """
    return prepare_context(task, claims, method_ids, conflicts, associations)


@MCP.tool(annotations=READ)
def innovation_feedback_summary(records: list[dict]) -> dict:
    """Count caller-labelled prediction outcomes with anchors; no accuracy claim or writeback."""
    return feedback_summary(records)


if __name__ == '__main__':
    MCP.run(transport='stdio')
