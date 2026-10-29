from __future__ import annotations

from app.llm import llm_call
from app.tools.retriever_tool import retrieve_context
from app.tools.script_tool import prompts
from app.tools.script_tool.schemas import (
    AnswerBatch,
    FinalScript,
    GapAssessment,
    QuestionBatch,
    ScriptAnalysis,
    ScriptStructure,
    SectionDraft,
)
from app.tools.langgraph_workflow.state import ScriptState
from core.logs import logger

# Hard cap on question/answer rounds so the loop always terminates.
MAX_BATCHES = 3


def analyze_topic(state: ScriptState) -> dict:
    """Build ScriptStructure + ScriptAnalysis and collect initial gaps."""
    topic = state["topic"]
    existing_script = state["existing_script"]

    logger.info("Node analyze_topic: building structure for '%s'", topic)
    r1 = llm_call(ScriptStructure, prompts.STRUCTURE_PROMPT, {"topic": topic})
    structure: ScriptStructure = r1["response"]

    logger.info("Node analyze_topic: analysing existing script")
    r2 = llm_call(
        ScriptAnalysis,
        prompts.ANALYSIS_PROMPT,
        {
            "topic": topic,
            "structure_json": structure.model_dump_json(indent=2),
            "existing_script": existing_script or "(none)",
        },
    )
    analysis: ScriptAnalysis = r2["response"]

    remaining_gaps = (
        analysis.missing_concepts
        + analysis.weak_explanations
        + analysis.logical_gaps
        + analysis.needs_examples_for
    )

    return {
        "structure": structure.model_dump(),
        "analysis": analysis.model_dump(),
        "remaining_gaps": remaining_gaps,
        "total_tokens": state["total_tokens"] + r1["token_used"] + r2["token_used"],
    }


def generate_questions(state: ScriptState) -> dict:
    """Generate the next prioritised batch of questions from remaining gaps."""
    topic = state["topic"]
    analysis = ScriptAnalysis.model_validate(state["analysis"])
    qa_pairs = state["qa_pairs"]

    answered_so_far = (
        "\n".join(f"Q: {p['question']}\nA: {p['answer']}" for p in qa_pairs)
        if qa_pairs
        else "None yet."
    )

    logger.info("Node generate_questions: batch %d for '%s'", state["batch_counter"] + 1, topic)
    r = llm_call(
        QuestionBatch,
        prompts.QUESTIONS_PROMPT,
        {
            "topic": topic,
            "analysis_json": analysis.model_dump_json(indent=2),
            "answered_so_far": answered_so_far,
        },
    )
    batch: QuestionBatch = r["response"]

    return {
        "pending_questions": [q.model_dump() for q in batch.questions],
        "batch_counter": state["batch_counter"] + 1,
        "total_tokens": state["total_tokens"] + r["token_used"],
    }


def _format_chunks(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant context found in the research database."
    return "\n\n".join(
        f"[{i+1}] {c.get('text') or c.get('content') or str(c)}"
        for i, c in enumerate(chunks)
    )


def auto_answer(state: ScriptState) -> dict:
    """Answer the pending questions from the research database."""
    pending = state["pending_questions"]

    logger.info("Node auto_answer: retrieving context for %d questions", len(pending))
    seen: set[str] = set()
    chunks: list[dict] = []
    for q in pending:
        results = retrieve_context(topic=f"{state['topic']} {q['text']}", top_k=3).get("results", [])
        for c in results:
            key = c.get("text") or c.get("content") or str(c)
            if key not in seen:
                seen.add(key)
                chunks.append(c)

    r = llm_call(
        AnswerBatch,
        prompts.ANSWER_PROMPT,
        {
            "topic": state["topic"],
            "questions": "\n".join(f"{q['id']}: {q['text']}" for q in pending),
            "retrieved_context": _format_chunks(chunks),
        },
    )
    batch: AnswerBatch = r["response"]

    valid_ids = {q["id"] for q in pending}
    return {
        "current_answers": {a.id: a.answer for a in batch.answers if a.id in valid_ids},
        "total_tokens": state["total_tokens"] + r["token_used"],
    }


def process_answers(state: ScriptState) -> dict:
    """Ingest user answers, retrieve grounding context, reassess gaps."""
    answers = state["current_answers"]
    pending = state["pending_questions"]
    id_to_text = {q["id"]: q["text"] for q in pending}

    new_qa_pairs = [
        {"question": id_to_text.get(qid, qid), "answer": ans.strip()}
        for qid, ans in answers.items()
    ]
    new_answers_text = "\n".join(
        f"Q ({qid}): {id_to_text.get(qid, qid)}\nA: {ans}"
        for qid, ans in answers.items()
    )
    remaining_gaps_text = (
        "\n".join(f"- {g}" for g in state["remaining_gaps"]) or "None."
    )

    # Build a focused retrieval query from the topic + unresolved gaps
    retrieval_query = state["topic"]
    if state["remaining_gaps"]:
        retrieval_query += " " + " ".join(state["remaining_gaps"][:3])

    logger.info("Node process_answers: retrieving context for reassessment")
    retrieval = retrieve_context(topic=retrieval_query, top_k=5)
    retrieved_context = _format_chunks(retrieval.get("results", []))

    logger.info("Node process_answers: reassessing after %d answers", len(answers))
    r = llm_call(
        GapAssessment,
        prompts.REASSESS_PROMPT,
        {
            "topic": state["topic"],
            "remaining_gaps": remaining_gaps_text,
            "new_answers": new_answers_text,
            "retrieved_context": retrieved_context,
        },
    )
    assessment: GapAssessment = r["response"]

    return {
        "qa_pairs": state["qa_pairs"] + new_qa_pairs,
        "remaining_gaps": assessment.remaining_gaps,
        "pending_questions": [q.model_dump() for q in assessment.next_questions],
        "needs_more_questions": assessment.needs_more_questions,
        "current_answers": {},
        "total_tokens": state["total_tokens"] + r["token_used"],
    }


def write_script(state: ScriptState) -> dict:
    """Generate the final ready-to-record script from all collected Q&A."""
    topic = state["topic"]
    qa_pairs = state["qa_pairs"]
    structure = ScriptStructure.model_validate(state["structure"])
    all_qa = (
        "\n".join(f"Q: {p['question']}\nA: {p['answer']}" for p in qa_pairs)
        if qa_pairs
        else "None."
    )

    sections: list[dict] = []
    tokens = 0
    for i, section in enumerate(structure.sections, start=1):
        logger.info(
            "Node write_script: section %d/%d '%s'", i, len(structure.sections), section.name
        )
        r = llm_call(
            SectionDraft,
            prompts.SECTION_SCRIPT_PROMPT,
            {
                "topic": topic,
                "section_json": section.model_dump_json(indent=2),
                "section_index": i,
                "section_count": len(structure.sections),
                "previous_text": sections[-1]["content"] if sections else "",
                "existing_script": state["existing_script"] or "(none)",
                "all_qa": all_qa,
            },
        )
        content = r["response"].content.strip()
        tokens += r["token_used"]
        sections.append(
            {"name": section.name, "content": content, "word_count": len(content.split())}
        )

    total_words = sum(s["word_count"] for s in sections)
    final = FinalScript(
        title=structure.topic,
        sections=sections,
        total_word_count=total_words,
        estimated_duration_minutes=round(total_words / 150, 1),
        production_notes="",
    )

    return {
        "final_script": final.model_dump(),
        "total_tokens": state["total_tokens"] + tokens,
    }


def route_after_assessment(state: ScriptState) -> str:
    """Conditional edge: loop back for more questions or proceed to write."""
    if state["needs_more_questions"] and state["batch_counter"] < MAX_BATCHES:
        return "generate_questions"
    return "write_script"
