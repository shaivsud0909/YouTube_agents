from __future__ import annotations

from app.tools.script_tool.schemas import Question, ScriptAnalysis, ScriptStructure


class WorkflowState:
    def __init__(self, topic: str, existing_script: str) -> None:
        self.topic = topic
        self.existing_script = existing_script
        self.structure: ScriptStructure | None = None
        self.analysis: ScriptAnalysis | None = None
        self.qa_pairs: list[dict] = []
        self.pending_questions: list[Question] = []
        self.remaining_gaps: list[str] = []
        self.batch_counter: int = 0
        self.total_tokens: int = 0
        self.ready_to_finalize: bool = False

    def record_tokens(self, n: int) -> None:
        self.total_tokens += n

    def qa_summary(self) -> str:
        if not self.qa_pairs:
            return "None yet."
        return "\n".join(
            f"Q: {pair['question']}\nA: {pair['answer']}" for pair in self.qa_pairs
        )

    def remaining_gaps_text(self) -> str:
        return "\n".join(f"- {g}" for g in self.remaining_gaps) or "None."
