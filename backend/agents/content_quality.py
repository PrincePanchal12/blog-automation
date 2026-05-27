import json
import re


EDITORIAL_LEAKS = (
    "here's the reviewed blog post",
    "here is the reviewed blog post",
    "here's the revised",
    "here is the revised",
    "fake statistics",
    "hallucinations",
    "as an ai",
)


def clean_markdown_output(content: str) -> str:
    """Normalize an LLM article body and remove non-article commentary."""
    text = content.strip()
    text = re.sub(r"\A```(?:markdown|md|mdx)?\s*\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n```\s*\Z", "", text)
    text = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, flags=re.DOTALL)

    title_match = re.search(r"(?m)^#\s+.+$", text)
    if title_match:
        text = text[title_match.start():]

    return text.strip()


def quality_issues(content: str) -> list[str]:
    text = clean_markdown_output(content)
    lower_text = text.lower()
    words = re.findall(r"\b[\w'-]+\b", text)
    h2_count = len(re.findall(r"(?m)^##\s+.+$", text))
    issues: list[str] = []

    if not re.match(r"^#\s+.+$", text, flags=re.MULTILINE):
        issues.append("The article must begin with one clear H1 title.")
    if len(words) < 700:
        issues.append("The article is thin; add concrete guidance and useful detail.")
    if h2_count < 4:
        issues.append("Use at least four meaningful H2 sections for reader navigation.")
    if any(phrase in lower_text for phrase in EDITORIAL_LEAKS):
        issues.append("Remove internal review commentary or model-facing language.")
    if re.search(
        r"(?im)^#{1,4}\s+.*(?:semantic seo|featured snippet optimization|geo optimization)",
        text,
    ):
        issues.append("Remove sections written about ranking tactics instead of the reader's task.")
    if "game-changer" in lower_text:
        issues.append("Replace promotional buzzwords with a descriptive, specific title.")

    return issues


def yaml_string(value: str) -> str:
    return json.dumps(" ".join(value.split()), ensure_ascii=True)


def article_title(topic: str, content: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", content)
    return match.group(1).strip() if match else " ".join(topic.split()).strip()


def meta_description(title: str) -> str:
    description = (
        f"A practical guide to {title}, covering useful applications, "
        "implementation steps, risks, and ways to evaluate results."
    )
    if len(description) <= 160:
        return description
    return f"A practical guide to {title}, including applications, risks, and next steps."[:160]


def topic_tags(topic: str) -> list[str]:
    lower_topic = topic.lower()
    tags: list[str] = []

    if "ai" in lower_topic or "artificial intelligence" in lower_topic:
        tags.append("AI")
    if "automat" in lower_topic:
        tags.append("Automation")
    if "business" in lower_topic:
        tags.append("Business")

    return tags or ["Insights"]
