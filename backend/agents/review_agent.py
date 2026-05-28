from backend.agents.content_quality import clean_markdown_output, quality_issues
from backend.core.llm import quality_llm as llm


def review_agent(state):
    print("--- [Node: review] Checking for quality issues and preparing report ---")
    content = clean_markdown_output(state["optimized_blog"])
    issues = quality_issues(content)

    if issues:
        issue_list = "\n".join(f"- {issue}" for issue in issues)
        prompt = f"""
        Perform a final editorial repair of this Markdown article.

        TOPIC:
        {state['topic']}

        ISSUES TO FIX:
        {issue_list}

        ARTICLE:
        {content}

        Return only a reader-facing Markdown article beginning with one H1.
        Do not invent sources, numbers, outcomes, quotations, or review commentary.
        Preserve useful content while resolving every listed issue.
        """
        content = clean_markdown_output(llm.invoke(prompt).content)

    remaining_issues = quality_issues(content)
    if remaining_issues:
        report = "Human review recommended before publishing: " + "; ".join(remaining_issues)
    else:
        report = "Automated editorial checks passed; human approval is still recommended."

    return {
        "optimized_blog": content,
        "quality_report": report,
    }
