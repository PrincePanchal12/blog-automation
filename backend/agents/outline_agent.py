from backend.core.llm import writer_llm as llm


def outline_agent(state):

    prompt = f"""
    You are a senior content strategist planning an evidence-conscious article.

    Create an outline for this topic:

    TOPIC:
    {state['topic']}

    AUDIENCE AND PURPOSE:
    - Infer one clear reader audience and their practical goal.
    - Satisfy that goal before thinking about discovery or ranking.

    SEO REQUIREMENTS:
    - Use a descriptive H1 aligned with the reader's intent.
    - Use natural H2 sections that fully answer the topic.
    - Cover key related questions only when useful to the reader.
    - Avoid keyword stuffing and sections about "SEO optimization."

    GEO REQUIREMENTS:
    - GEO means Generative Engine Optimization, not geographic targeting.
    - Plan clear definitions, concise answer-first passages, and concrete steps.
    - Prefer information that can be accurately summarized or cited by an AI answer.

    TRUST REQUIREMENTS:
    - Do not plan statistics, quotations, studies, or named results unless a source
      is supplied in the topic itself.
    - Use hypothetical examples when illustrating implementation.
    - Include risks, limitations, and a practical evaluation checklist.

    OUTPUT:
    - Markdown outline only.
    - Include one H1 and useful H2/H3 sections.
    - Do not include commentary about this instruction.

    """

    response = llm.invoke(prompt)

    return {
        "outline": response.content
    }
