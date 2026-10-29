from langchain_core.prompts import PromptTemplate


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
