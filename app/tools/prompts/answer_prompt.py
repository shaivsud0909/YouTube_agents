from langchain_core.prompts import PromptTemplate


ANSWER_PROMPT = PromptTemplate(
    input_variables=["question", "retrieved_context"],
    template="""You are a subject-matter researcher helping complete a YouTube script.

Answer the question below using ONLY the retrieved research context.
If the context does not cover the question, say so plainly instead of inventing facts.

Question:
{question}

Retrieved context from the research database:
{retrieved_context}

Set answered to false when the context is not enough to answer the question.
""",
)
