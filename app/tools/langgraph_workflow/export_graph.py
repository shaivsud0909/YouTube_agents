"""
Regenerate graph.png from the current graph definition:
    uv run python -m app.tools.langgraph_workflow.export_graph
"""
from __future__ import annotations

from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from typing_extensions import TypedDict


# Minimal state mirror — avoids importing app.llm (needs API keys)
class ScriptState(TypedDict):
    topic: str
    existing_script: str
    structure: dict | None
    analysis: dict | None
    qa_pairs: list[dict]
    pending_questions: list[dict]
    remaining_gaps: list[str]
    batch_counter: int
    total_tokens: int
    final_script: dict | None
    current_answers: dict
    needs_more_questions: bool


def _stub(state: ScriptState) -> dict:
    return {}


def _route(state: ScriptState) -> str:
    return "generate_questions" if state["needs_more_questions"] else "write_script"


def _build_visual_graph():
    """Build graph with stub nodes so no LLM/API keys are needed."""
    builder = StateGraph(ScriptState)
    builder.add_node("analyze_topic", _stub)
    builder.add_node("generate_questions", _stub)
    builder.add_node("process_answers", _stub)
    builder.add_node("write_script", _stub)

    builder.add_edge(START, "analyze_topic")
    builder.add_edge("analyze_topic", "generate_questions")
    builder.add_edge("generate_questions", "process_answers")
    builder.add_conditional_edges(
        "process_answers",
        _route,
        {"generate_questions": "generate_questions", "write_script": "write_script"},
    )
    builder.add_edge("write_script", END)

    return builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["process_answers"],
    )


if __name__ == "__main__":
    graph = _build_visual_graph()
    out = Path(__file__).parent / "graph.png"
    out.write_bytes(graph.get_graph().draw_mermaid_png())
    print(f"Saved → {out}")
