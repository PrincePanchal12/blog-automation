from backend.agents.content_quality import clean_markdown_output
from backend.core.llm import quality_llm as llm


def analyzer_agent(state):
    content = clean_markdown_output(state.get("blog") or state.get("raw_content") or "")
    source_context = (
        "This article is derived from uploaded PDF source material. Flag claims that "
        "need source attribution or that go beyond that material."
        if state["input_type"] == "pdf"
        else "No external sources were supplied. Flag factual, quantitative, or named "
        "outcome claims that should be removed, qualified, or sourced."
    )

    prompt = f"""
    You are the editorial quality auditor for a professional blog.

    TOPIC:
    {state['topic']}

    SOURCE RULE:
    {source_context}

    DRAFT:
    {content}

    Audit the draft rigorously. SEO here means satisfying real search intent with a
    clear title, useful coverage, natural headings, and a good reader experience.
    GEO means Generative Engine Optimization: direct definitions, unambiguous entities,
    well-scoped statements, and answer-ready passages that can be summarized accurately.
    GEO does not mean location-based marketing.

    Evaluate:
    - usefulness, specificity, completeness, and reader intent
    - unsupported facts, statistics, quotations, case studies, or implied guarantees
    - SEO clarity without keyword stuffing or optimization filler
    - GEO answer clarity and factual qualification
    - structure, repetition, tone, risks, and actionable guidance
    - any internal model/reviewer language that must not be published

    Return a compact editorial brief with these headings:
    ## Verdict
    ## Must Fix
    ## Improve If Useful
    ## Required Structure

    Do not rewrite the article in this response.
    """

    response = llm.invoke(prompt)

    return {
        "blog": content if state["input_type"] == "topic" else state.get("blog", ""),
        "raw_content": content if state["input_type"] == "pdf" else state.get("raw_content", ""),
        "analysis": response.content.strip(),
    }
