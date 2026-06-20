"""
main.py
=======
FastAPI entry point for PROTEGO.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import traceback
from pathlib import Path

from protego.api.schemas import (
    ChatRequest,
    ChatResponse,
    ChatResponseWithDebug,
)
from protego.api.chatbot_service import handle_message

# -----------------------------
# Paths (🔥 ADDED)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# App initialization
# -----------------------------
app = FastAPI(
    title="PROTEGO API",
    description="AI-powered safety & support chatbot for crisis prevention",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------------------
# CORS configuration
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# 🔥 SERVE FRONTEND (ADDED)
# -----------------------------
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "frontend"),
    name="static"
)

# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
async def startup_event():
    print("✅ PROTEGO API started successfully")

# -----------------------------
# 🔥 FRONTEND ROUTES (ADDED)
# -----------------------------
@app.get("/", tags=["UI"])
async def root_ui():
    return FileResponse(BASE_DIR / "frontend" / "login.html")


@app.get("/login", tags=["UI"])
async def login_ui():
    return FileResponse(BASE_DIR / "frontend" / "login.html")


@app.get("/signup", tags=["UI"])
async def signup_ui():
    return FileResponse(BASE_DIR / "frontend" / "signup.html")


@app.get("/user", tags=["UI"])
async def user_ui():
    return FileResponse(BASE_DIR / "frontend" / "index.html")


@app.get("/admin", tags=["UI"])
async def admin_ui():
    return FileResponse(BASE_DIR / "frontend" / "admin.html")

# -----------------------------
# Health check (KEEP SAME)
# -----------------------------
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "running",
        "service": "PROTEGO API",
        "message": "PROTEGO API is live 🛡️"
    }

# -----------------------------
# Chat endpoint (UNCHANGED)
# -----------------------------
@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Chat with PROTEGO"
)
async def chat_endpoint(request: ChatRequest):
    try:
        return handle_message(
            message=request.message,
            country=request.country,
            debug=False
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )

# -----------------------------
# Debug endpoint (UNCHANGED)
# -----------------------------
@app.post(
    "/chat/debug",
    response_model=ChatResponseWithDebug,
    tags=["Debug"],
    summary="Debug chatbot reasoning"
)
async def chat_debug_endpoint(request: ChatRequest):
    try:
        return handle_message(
            message=request.message,
            country=request.country,
            debug=True
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": "Debug endpoint failure",
                "details": str(e)
            }
        )