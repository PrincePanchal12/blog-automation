from langchain_groq import ChatGroq

from backend.core.config import GROQ_API_KEY


# MAIN WRITING MODEL
writer_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.35
)


# FAST MODEL FOR SOURCE CLEANUP
fast_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.1
)


# STRONG LOW-VARIANCE MODEL FOR EDITORIAL REVIEW
quality_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0.1
)
