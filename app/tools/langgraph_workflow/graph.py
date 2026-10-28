from __future__ import annotations

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.tools.langgraph_workflow.nodes import (
    analyze_topic,
    generate_questions,
    process_answers,
    route_after_assessment,
    write_script,
)
from app.tools.langgraph_workflow.state import ScriptState


def build_graph():
    builder = StateGraph(ScriptState)

    builder.add_node("analyze_topic", analyze_topic)
    builder.add_node("generate_questions", generate_questions)
    builder.add_node("process_answers", process_answers)
    builder.add_node("write_script", write_script)

    builder.add_edge(START, "analyze_topic")
    builder.add_edge("analyze_topic", "generate_questions")
    builder.add_edge("generate_questions", "process_answers")
    builder.add_conditional_edges(
        "process_answers",
        route_after_assessment,
        {"generate_questions": "generate_questions", "write_script": "write_script"},
    )
    builder.add_edge("write_script", END)

    return builder.compile(
        checkpointer=MemorySaver(),
        interrupt_before=["process_answers"],
    )


@lru_cache(maxsize=1)
def get_graph():
    """Return the singleton compiled graph (lazy-initialised)."""
    return build_graph()
