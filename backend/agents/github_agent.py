from github import Github
from github import Auth

from backend.core.config import (
    GITHUB_TOKEN,
    GITHUB_REPO
)

def github_push_agent(state):

    auth = Auth.Token(GITHUB_TOKEN)

    g = Github(auth=auth)

    repo = g.get_repo(GITHUB_REPO)

    local_file = f"blogs/{state['file_name']}"

    github_path = f"data/{state['file_name']}"

    with open(local_file, "r", encoding="utf-8") as file:
        content = file.read()

    try:

        existing_file = repo.get_contents(
            github_path,
            ref="main"
        )

        repo.update_file(
            github_path,
            f"Update {state['file_name']}",
            content,
            existing_file.sha,
            branch="main"
        )

        print("Updated existing blog.")

    except:

        repo.create_file(
            github_path,
            f"Create {state['file_name']}",
            content,
            branch="main"
        )

        print("Created new blog.")

    return state