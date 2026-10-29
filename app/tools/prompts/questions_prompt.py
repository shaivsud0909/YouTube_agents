from langchain_core.prompts import PromptTemplate


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
