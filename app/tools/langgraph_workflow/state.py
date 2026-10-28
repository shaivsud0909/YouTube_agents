from __future__ import annotations

from typing_extensions import TypedDict


class ScriptState(TypedDict):
    topic: str
    existing_script: str
    structure: dict | None        # serialized ScriptStructure
    analysis: dict | None         # serialized ScriptAnalysis
    qa_pairs: list[dict]
    pending_questions: list[dict]  # serialized Question dicts
    remaining_gaps: list[str]
    batch_counter: int
    total_tokens: int
    final_script: dict | None     # serialized FinalScript
    current_answers: dict[str, str]
    needs_more_questions: bool
