import os
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai_service import get_gemini_api_key
from qna import router as qa_router
from explanation_module import router as explain_router
from quiz_module import router as quiz_router
from summary_module import router as summary_router
from learning_path import router as learn_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

load_dotenv(override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = get_gemini_api_key()
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set.")
    else:
        logger.info("GEMINI_API_KEY configured")
    logger.info("EduGenie starting")
    yield
    logger.info("EduGenie shutting down")


app = FastAPI(
    title="EduGenie",
    description="AI-Powered Educational Assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(qa_router)
app.include_router(explain_router)
app.include_router(quiz_router)
app.include_router(summary_router)
app.include_router(learn_router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
@app.get("/api/diagnostic")
async def health_check():
    has_api_key = bool(get_gemini_api_key())
    return {
        "status": "ok",
        "service": "EduGenie",
        "version": "1.0.0",
        "gemini_api_key_configured": has_api_key,
        "ai_configured": has_api_key,
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        "platform": "vercel" if os.getenv("VERCEL") else "serverless/standard",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "The requested resource was not found."},
    )