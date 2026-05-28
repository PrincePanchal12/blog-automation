import fitz


def pdf_extractor_agent(state):
    print(f"--- [Node: extract] Extracting text from PDF: {state.get('pdf_path')} ---")

    pdf_path = state["pdf_path"]

    with fitz.open(pdf_path) as doc:
        pages = [page.get_text().strip() for page in doc]

    text = "\n\n".join(page for page in pages if page)

    if not text.strip():
        raise ValueError("The PDF does not contain selectable text to convert into a draft.")

    return {
        "raw_content": text
    }
