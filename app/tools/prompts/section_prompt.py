from langchain_core.prompts import PromptTemplate


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

Use this researched information:
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
