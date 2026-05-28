from pathlib import Path


BLOG_DIRECTORY = Path("blogs")


def save_mdx_agent(state):
    BLOG_DIRECTORY.mkdir(exist_ok=True)
    file_path = BLOG_DIRECTORY / state["file_name"]
    file_path.write_text(state["mdx_content"], encoding="utf-8")

    print(f"--- [Node: save] Saved MDX file to: {file_path} ---\n")

    return state
