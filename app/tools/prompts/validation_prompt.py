from langchain_core.prompts import PromptTemplate


VALIDATION_PROMPT = PromptTemplate(
    input_variables=["topic", "question", "answer", "retrieved_context"],
    template="""You are a strict fact-checker reviewing a question and answer pair for a YouTube script.

Topic: {topic}

Question:
{question}

Answer:
{answer}

Retrieved context from the research database:
{retrieved_context}

Check:
1. Is the question relevant to the topic, specific, and clearly worded?
2. Does the answer actually address the question?
3. Is every claim in the answer supported by the retrieved context? List unsupported claims.

Set is_valid to true only if all three checks pass.
""",
)
