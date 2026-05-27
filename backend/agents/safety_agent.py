from backend.agents.content_quality import clean_markdown_output
from backend.core.llm import quality_llm as llm


def safety_agent(state):
    content = clean_markdown_output(state["optimized_blog"])

    prompt = f"""
    You are the final accuracy and trust editor for a public-facing article.

    TOPIC:
    {state['topic']}

    ARTICLE:
    {content}

    Apply only changes needed for publication safety and quality:
    - Remove invented statistics, unverified quotes, unsupported named case studies,
      guaranteed results, and confident claims that cannot be established here.
    - Where a useful general claim remains, qualify it naturally rather than replacing
      it with vague filler.
    - Remove model notes, reviewer notes, or optimization commentary not requested by
      the topic. Preserve useful SEO or GEO discussion if that is the actual topic.
    - Preserve practical steps, meaningful limitations, readable structure, and Markdown.
    - Keep the article reader-facing and do not announce your edits.

    Return ONLY the complete final Markdown article body, beginning with its H1.
    Do not include frontmatter or any preface.
    """

    response = llm.invoke(prompt)

    return {
        "optimized_blog": clean_markdown_output(response.content)
    }
