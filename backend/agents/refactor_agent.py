from backend.agents.content_quality import clean_markdown_output
from backend.core.llm import writer_llm as llm


def refactor_agent(state):
    print("--- [Node: refactor] Revising draft based on editorial feedback ---")
    content = clean_markdown_output(state.get("blog") or state.get("raw_content") or "")
    source_instruction = (
        "The input originated in a PDF. Preserve supported details and attribution, "
        "but do not add claims that are absent from the source."
        if state["input_type"] == "pdf"
        else "No research sources were supplied. Avoid statistics, named success "
        "stories, or factual performance claims unless expressed cautiously as examples."
    )

    prompt = f"""
    You are a senior human editor producing the publication-ready version of an article.

    TOPIC:
    {state['topic']}

    SOURCE POLICY:
    {source_instruction}

    DRAFT:
    {content}

    EDITORIAL AUDIT:
    {state['analysis']}

    REVISION STANDARD:
    - Resolve every item under Must Fix.
    - Start with one descriptive H1 and a concise answer-first introduction.
    - Provide useful, concrete steps, decisions, examples, risks, and evaluation advice.
    - Prefer qualified and accurate claims over impressive but unsupported claims.
    - Use H2/H3 headings that reflect reader questions and actions.
    - Remove repetition, filler, hype, invented authority, and internal review commentary.
    - Maintain a natural professional voice and substantial depth.
    - SEO should come from clear intent coverage, not keyword repetition.
    - GEO means clear, self-contained explanations suited to accurate AI summarization;
      do not write about GEO or SEO unless the article topic requires it.

    OUTPUT RULES:
    - Return only the final Markdown article body.
    - Begin directly with the H1.
    - Do not include frontmatter, editorial notes, citations you invented, or commentary.
    """

    response = llm.invoke(prompt)

    return {
        "optimized_blog": clean_markdown_output(response.content)
    }
