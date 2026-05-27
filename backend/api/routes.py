from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile

from backend.graph.workflow import graph


router = APIRouter()
BLOG_DIRECTORY = Path("blogs")
UPLOAD_DIRECTORY = Path("uploads")
MAX_PDF_BYTES = 25 * 1024 * 1024


# =========================
# HEALTH CHECK
# =========================

@router.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =========================
# REQUEST MODEL
# =========================

class BlogRequest(BaseModel):

    topic: str


# =========================
# GENERATE BLOG
# =========================

@router.post("/generate-blog")
async def generate_blog(request: Request):

    input_type = "topic"
    pdf_path = ""

    if request.headers.get("content-type", "").startswith("multipart/form-data"):
        form = await request.form()
        uploaded = form.get("file")

        if not isinstance(uploaded, UploadFile) or not uploaded.filename:
            raise HTTPException(status_code=422, detail="A PDF source file is required")

        if not uploaded.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF source files are supported")

        source = await uploaded.read(MAX_PDF_BYTES + 1)

        if len(source) > MAX_PDF_BYTES:
            raise HTTPException(status_code=413, detail="PDF source exceeds the 25 MB limit")

        UPLOAD_DIRECTORY.mkdir(exist_ok=True)
        saved_pdf = UPLOAD_DIRECTORY / f"{uuid4().hex}-{Path(uploaded.filename).name}"
        saved_pdf.write_bytes(source)
        pdf_path = str(saved_pdf)
        input_type = "pdf"
        topic = str(form.get("topic") or Path(uploaded.filename).stem).strip()
    else:
        try:
            payload = BlogRequest(**await request.json())
        except Exception as exc:
            raise HTTPException(status_code=422, detail="A blog topic is required") from exc

        topic = payload.topic.strip()

    if not topic:
        raise HTTPException(status_code=422, detail="A blog topic is required")

    try:
        result = await run_in_threadpool(graph.invoke, {

            "input_type": input_type,

            "topic": topic,

            "pdf_path": pdf_path,

            "raw_content": "",
            "outline": "",
            "blog": "",
            "analysis": "",
            "optimized_blog": "",
            "quality_report": "",
            "mdx_content": "",
            "file_name": ""
        })
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "message": "Draft generated successfully",
        "file_name": result["file_name"],
        "draft_path": f"blogs/{result['file_name']}",
        "quality_report": result["quality_report"],
    }

class PublishRequest(BaseModel):

    file_name: str


class DraftContentRequest(BaseModel):

    content: str


def get_draft_path(file_name: str):

    if Path(file_name).name != file_name or not file_name.endswith(".mdx"):
        raise HTTPException(status_code=400, detail="Invalid MDX file name")

    return BLOG_DIRECTORY / file_name


@router.get("/drafts/{file_name}")
def get_draft(file_name: str):

    path = get_draft_path(file_name)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Draft not found")

    return {
        "file_name": file_name,
        "content": path.read_text(encoding="utf-8")
    }


@router.put("/drafts/{file_name}")
def update_draft(file_name: str, request: DraftContentRequest):

    path = get_draft_path(file_name)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Draft not found")

    path.write_text(request.content, encoding="utf-8")

    return {
        "message": "Draft saved successfully",
        "file_name": file_name
    }


@router.post("/publish-blog")
def publish_blog(request: PublishRequest):

    from backend.agents.github_agent import github_push_agent

    path = get_draft_path(request.file_name)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Draft not found")

    github_push_agent({
        "file_name": request.file_name
    })

    return {
        "message": "Blog published successfully"
    }
