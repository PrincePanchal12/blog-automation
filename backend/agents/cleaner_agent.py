from backend.core.llm import fast_llm as llm


def content_cleaner_agent(state):
    print("--- [Node: clean] Cleaning extracted PDF text ---")

    prompt = f"""
    You are cleaning extracted PDF text for an editor. The PDF is the source material.

    TASKS:
    - Remove repeated headers, footers, page numbers, and broken spacing.
    - Restore obvious paragraph and heading breaks.
    - Preserve the source meaning, qualifications, names, dates, and attribution.
    - Do not invent facts, expand arguments, or add optimization language.
    - If text is unreadable or incomplete, retain it rather than guessing.

    EXTRACTED CONTENT:
    {state['raw_content']}

    Return cleaned source text in Markdown only, without a preface.
    """

    response = llm.invoke(prompt)

    return {
        "raw_content": response.content
    }
