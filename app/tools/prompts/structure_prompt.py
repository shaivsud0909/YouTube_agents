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
