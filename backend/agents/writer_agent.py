from backend.core.llm import writer_llm as llm


def writer_agent(state):

    prompt = f"""
    You are a senior editor writing a trustworthy, practical article for a real reader.

    TOPIC:
    {state['topic']}

    APPROVED OUTLINE:
    {state['outline']}

    Write the complete article in Markdown.

    EDITORIAL REQUIREMENTS:
    - Begin with exactly one descriptive H1.
    - Give the reader a direct, useful answer in the introduction.
    - Prefer specific implementation advice, checklists, decisions, and tradeoffs.
    - Use a professional natural tone; avoid hype such as "game-changer."
    - Avoid repeating the same claimed benefits in multiple sections.
    - Target substantial useful coverage, normally 900-1400 words.

    EVIDENCE AND SAFETY:
    - Do not invent statistics, citations, studies, customer results, or expert quotes.
    - Do not claim that a tool improves costs, sales, accuracy, or satisfaction as a
      proven result unless the supplied outline contains a reliable cited source.
    - If giving a scenario, clearly make it an example rather than a factual case study.
    - Mention meaningful risks and human review requirements where relevant.

    SEO AND GEO:
    - SEO means accurately matching reader intent using clear headings and complete answers.
    - GEO means Generative Engine Optimization: make definitions and key steps clear
      enough to quote or summarize accurately in AI-assisted search.
    - Do not mention SEO, GEO, featured snippets, or ranking tactics in the article
      unless the topic specifically asks about them.

    OUTPUT:
    - Return only the finished Markdown article body beginning with the H1.
    - Do not include frontmatter, notes to the editor, or claims that the article
      has been reviewed or optimized.
    """

    response = llm.invoke(prompt)

    return {
        "blog": response.content
    }
