from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_REPO = os.getenv("GITHUB_REPO")