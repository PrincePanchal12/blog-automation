import json
from datetime import datetime

from slugify import slugify

from backend.agents.content_quality import (
    article_title,
    clean_markdown_output,
    meta_description,
    topic_tags,
    yaml_string,
)


def mdx_agent(state):
    print("--- [Node: mdx] Creating MDX metadata frontmatter ---")
    content = clean_markdown_output(state["optimized_blog"])
    title = article_title(state["topic"], content)
    slug = slugify(title)
    description = meta_description(title)
    tags = json.dumps(topic_tags(state["topic"]), ensure_ascii=True)

    mdx_content = f"""---
title: {yaml_string(title)}
date: {yaml_string(str(datetime.now().date()))}
author: "Prince Panchal"
img: {yaml_string(f"/images/blog/{slug}.jpg")}
description: {yaml_string(description)}
tags: {tags}
coverImage: {yaml_string(f"/blog/{slug}.png")}
---

{content}
"""

    return {
        "mdx_content": mdx_content,
        "file_name": f"{slug}.mdx",
    }
