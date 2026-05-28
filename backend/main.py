import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import router


app = FastAPI(
    title="AI Blog Platform",
    version="1.0.0"
)

frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in frontend_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        
    error_msg = str(exc)
    if "Rate limit reached" in error_msg or "429" in error_msg:
        detail = "Groq AI Token Limit Reached! Please wait a few minutes or use a different API key."
    elif "AuthenticationError" in error_msg or "401" in error_msg:
        detail = "Invalid Groq API Key! Please check your environment variables."
    else:
        detail = f"Internal Server Error: {error_msg}"

    return JSONResponse(
        status_code=500,
        content={"detail": detail},
        headers=headers
    )


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
