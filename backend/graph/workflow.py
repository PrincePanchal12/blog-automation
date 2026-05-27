from langgraph.graph import StateGraph, END

from backend.graph.state import BlogState

# Topic Flow Agents
from backend.agents.outline_agent import outline_agent
from backend.agents.writer_agent import writer_agent

# PDF Flow Agents
from backend.agents.pdf_agent import pdf_extractor_agent
from backend.agents.cleaner_agent import content_cleaner_agent

# Shared Pipeline
from backend.agents.analyzer_agent import analyzer_agent
from backend.agents.refactor_agent import refactor_agent
from backend.agents.safety_agent import safety_agent

# Final Pipeline
from backend.agents.mdx_agent import mdx_agent
from backend.agents.save_agent import save_mdx_agent
from backend.agents.review_agent import review_agent


# =========================
# CREATE WORKFLOW
# =========================

workflow = StateGraph(BlogState)


# =========================
# ADD NODES
# =========================

# Topic Flow
workflow.add_node("outline", outline_agent)
workflow.add_node("writer", writer_agent)

# PDF Flow
workflow.add_node("extract", pdf_extractor_agent)
workflow.add_node("clean", content_cleaner_agent)

# Shared Pipeline
workflow.add_node("analyze", analyzer_agent)
workflow.add_node("refactor", refactor_agent)
workflow.add_node("safety", safety_agent)

# Final Pipeline
workflow.add_node("mdx", mdx_agent)
workflow.add_node("save", save_mdx_agent)
workflow.add_node("review", review_agent)


# =========================
# ROUTER
# =========================

def router(state):

    if state["input_type"] == "topic":
        return "outline"

    elif state["input_type"] == "pdf":
        return "extract"


# =========================
# CONDITIONAL ENTRY
# =========================

workflow.add_conditional_edges(
    "__start__",
    router,
    {
        "outline": "outline",
        "extract": "extract"
    }
)


# =========================
# TOPIC FLOW
# =========================

workflow.add_edge("outline", "writer")
workflow.add_edge("writer", "analyze")


# =========================
# PDF FLOW
# =========================

workflow.add_edge("extract", "clean")
workflow.add_edge("clean", "analyze")


# =========================
# SHARED FLOW
# =========================

workflow.add_edge("analyze", "refactor")
workflow.add_edge("refactor", "safety")


# =========================
# FINAL FLOW
# =========================

# Review the final article before packaging and saving it as a draft.
workflow.add_edge("safety", "review")
workflow.add_edge("review", "mdx")
workflow.add_edge("mdx", "save")

# Publishing is explicitly triggered through POST /publish-blog after human review.
workflow.add_edge("save", END)


# =========================
# COMPILE GRAPH
# =========================

graph = workflow.compile()
