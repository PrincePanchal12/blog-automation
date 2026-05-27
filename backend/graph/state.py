from typing import TypedDict

class BlogState(TypedDict):

    # INPUT
    input_type: str
    topic: str
    pdf_path: str

    # RAW CONTENT
    raw_content: str
    outline: str
    blog: str

    # OPTIMIZATION
    analysis: str
    optimized_blog: str
    quality_report: str

    # OUTPUT
    mdx_content: str
    file_name: str
