from langchain_core.prompts import PromptTemplate


STRUCTURE_PROMPT = PromptTemplate(
    input_variables=["topic"],
    template="""You are an expert educational video scriptwriter.

Define an ideal structure for an 8-minute YouTube educational video about:
"{topic}"

Guidelines:
- Assume 120-150 words per minute (960-1200 words total).
- Adapt the section breakdown to the topic; do not force a rigid template.
- Typical sections: hook/intro, background/context, core concepts, examples/applications, key insights, conclusion.
- Allocate more time to the sections that matter most for this specific topic.
- For each section specify: name, duration_seconds, word_count_range, description, key_points.
""",
)


ANALYSIS_PROMPT = PromptTemplate(
    input_variables=["topic", "structure_json", "existing_script"],
    template="""You are reviewing a partially written YouTube script.

Topic: {topic}

Ideal 8-minute structure (JSON):
{structure_json}

Existing script (may be empty or incomplete):
\"\"\"
{existing_script}
\"\"\"

Analyse the existing script against the ideal structure.
For each section state whether coverage is 'adequate', 'partial', or 'missing'.
Also identify:
- Concepts mentioned but poorly explained
- Logical gaps or missing transitions
- Places that need concrete examples
- Any factual claims that need supporting detail
""",
)


QUESTIONS_PROMPT = PromptTemplate(
    input_variables=["topic", "analysis_json", "answered_so_far"],
    template="""You are helping a content creator gather information to complete their script.

Topic: {topic}

Script analysis (JSON):
{analysis_json}

Information already collected from the creator:
{answered_so_far}

Generate a prioritised batch of 3-5 questions that:
- Fill the most important remaining gaps first
- Are specific and actionable (not vague like "tell me more")
- Progress from foundational context to deeper insights
- Do NOT ask about anything already adequately covered or already answered
- Include a brief note on which gap each question addresses

Assign each question a unique id like q1, q2, ...
""",
)


ANSWER_PROMPT = PromptTemplate(
    input_variables=["topic", "questions", "retrieved_context"],
    template="""You are a subject-matter researcher helping complete a YouTube script.

Topic: {topic}

Answer each question below using ONLY the retrieved research context.
If the context does not cover a question, say so plainly instead of inventing facts.

Questions:
{questions}

Retrieved context from the research database:
{retrieved_context}

Return one answer per question, using the same question id.
""",
)


REASSESS_PROMPT = PromptTemplate(
    input_variables=["topic", "remaining_gaps", "new_answers", "retrieved_context"],
    template="""You are tracking progress on completing a YouTube script.

Topic: {topic}

Remaining gaps before this round:
{remaining_gaps}

New answers from the creator:
{new_answers}

Relevant context retrieved from research database:
{retrieved_context}

Assess:
1. Which gaps have been resolved by the new answers or the retrieved context?
2. Which gaps are still unresolved?
3. Are more questions needed, or is there now enough information to write the full script?
4. If more questions are needed, list the next batch (max 4).
""",
)


FINAL_SCRIPT_PROMPT = PromptTemplate(
    input_variables=["topic", "structure_json", "existing_script", "all_qa"],
    template="""You are a professional YouTube scriptwriter.

Write a complete, ready-to-record ~8-minute educational script about:
"{topic}"

Use this structure as the blueprint:
{structure_json}

Preserve and improve this existing draft where useful:
\"\"\"
{existing_script}
\"\"\"

Incorporate this information gathered from the creator:
{all_qa}

Requirements:
- Natural spoken delivery — no bullet points inside the spoken text
- Smooth transitions between sections
- Concrete examples and analogies where helpful
- Engaging hook and memorable close
- Do NOT invent statistics, quotes, or sources; flag any uncertainty explicitly
- Target 960-1200 words total
- Return each section separately with its word count
""",
)


SECTION_SCRIPT_PROMPT = PromptTemplate(
    input_variables=[
        "topic", "section_json", "section_index", "section_count",
        "previous_text", "existing_script", "all_qa",
    ],
    template="""You are a professional YouTube scriptwriter writing an educational video about:
"{topic}"

You are writing section {section_index} of {section_count}. Write ONLY this section:
{section_json}

Text of the previous section, for continuity (empty for the first section):
\"\"\"
{previous_text}
\"\"\"

Preserve and improve this existing draft where useful:
\"\"\"
{existing_script}
\"\"\"

Incorporate this information gathered from the creator:
{all_qa}

Requirements:
- Natural spoken delivery, no bullet points inside the spoken text
- Stay within the section's word_count_range
- Open with a smooth transition from the previous section (skip for the first section)
- Concrete examples and analogies where helpful
- Do NOT invent statistics, quotes, or sources; flag any uncertainty explicitly
- Do not repeat material from other sections
""",
)
