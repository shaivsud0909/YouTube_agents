from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ScriptSection(BaseModel):
    name: str = Field(description="Section name, e.g. 'Hook & Introduction'")
    duration_seconds: int = Field(description="Target duration in seconds")
    word_count_range: str = Field(description="Target word range, e.g. '120-150'")
    description: str = Field(description="What this section should accomplish")
    key_points: list[str] = Field(description="Bullet points that should be covered")


class ScriptStructure(BaseModel):
    topic: str
    total_duration_minutes: int = 8
    sections: list[ScriptSection]
    rationale: str = Field(description="Why this structure fits the topic")


class SectionCoverage(BaseModel):
    section_name: str
    coverage: Literal["adequate", "partial", "missing"]
    notes: str = Field(description="What is present and what is lacking")


class ScriptAnalysis(BaseModel):
    section_coverages: list[SectionCoverage]
    missing_concepts: list[str]
    weak_explanations: list[str]
    logical_gaps: list[str]
    needs_examples_for: list[str]
    summary: str = Field(description="One-paragraph summary of what still needs to be written")


class Question(BaseModel):
    id: str = Field(description="Short unique id, e.g. 'q1'")
    text: str = Field(description="The question to ask the user")
    addresses: str = Field(description="Which gap or section this question fills")
    priority: int = Field(description="1 = highest priority", ge=1)


class QuestionBatch(BaseModel):
    batch_number: int
    questions: list[Question]
    note: str = Field(description="Brief explanation of why these questions were chosen")


class Answer(BaseModel):
    id: str = Field(description="Id of the question being answered, e.g. 'q1'")
    answer: str = Field(description="Answer grounded in the retrieved context")


class AnswerBatch(BaseModel):
    answers: list[Answer]


class GapAssessment(BaseModel):
    resolved_gaps: list[str] = Field(description="Gaps now filled by the user's answers")
    remaining_gaps: list[str] = Field(description="Gaps that still need information")
    needs_more_questions: bool
    next_questions: list[Question] = Field(
        default_factory=list,
        description="Next batch of questions; empty when needs_more_questions is False",
    )


class ScriptSectionContent(BaseModel):
    name: str
    content: str = Field(description="Full spoken text for this section")
    word_count: int


class SectionDraft(BaseModel):
    content: str = Field(description="Full spoken text for this section only")


class FinalScript(BaseModel):
    title: str
    sections: list[ScriptSectionContent]
    total_word_count: int
    estimated_duration_minutes: float
    production_notes: str = Field(
        description="Optional delivery or editing notes for the creator"
    )
