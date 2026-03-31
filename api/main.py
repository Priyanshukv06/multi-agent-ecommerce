import os
import asyncio                                               # ← ADDED
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.settings import APP_ENV, DEBUG, print_config_summary
from api.routes import router

print_config_summary()

app = FastAPI(
    title="Multi-Agent E-commerce AI",
    description="""
Multi-Agent AI Book Store — LangGraph-powered 7-agent system.

**Agents**: Planner → Search → Research → Comparison → Recommendation → Critic → Action

**Features**:
- Conversation memory across sessions
- Self-correcting critic-retry loop
- Full order lifecycle (place / track / return)
- NVIDIA NIM + Groq LLMs
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup DB health check ───────────────────────────────────────────────────
@app.on_event("startup")                                     # ← ADDED
async def startup_db_check():
    """Fail fast on startup if PostgreSQL is unreachable."""
    try:
        from db.connection import get_connection
        conn = get_connection()
        conn.close()
        print("✅ PostgreSQL connection OK")
    except Exception as e:
        print(f"🔴 PostgreSQL connection FAILED on startup: {e}")
        # Don't crash the app — just warn so uvicorn still starts


# ════════════════════════════════════════════════════════════════════════════
# GLOBAL EXCEPTION HANDLERS
# ════════════════════════════════════════════════════════════════════════════

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " → ".join(str(e) for e in err["loc"])
        errors.append(f"{field}: {err['msg']}")

    return JSONResponse(
        status_code=422,
        content={
            "error":  "Validation Error",
            "detail": "Request body has invalid or missing fields.",
            "fields": errors,
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error":  _http_status_label(exc.status_code),
            "detail": exc.detail,
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"\n🔴 UNHANDLED EXCEPTION on {request.method} {request.url}\n{tb}")

    if DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "error":     "Internal Server Error",
                "detail":    str(exc),
                "traceback": tb.splitlines()[-5:],
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "error":  "Internal Server Error",
                "detail": "Something went wrong. Please try again.",
            }
        )


@app.exception_handler(TimeoutError)                         # built-in (Python 3.11+)
@app.exception_handler(asyncio.TimeoutError)                 # ← ADDED: Python ≤ 3.10
async def timeout_exception_handler(request: Request, exc: Exception):
    print(f"⏱️  Timeout on {request.method} {request.url}")
    return JSONResponse(
        status_code=504,
        content={
            "error":  "Gateway Timeout",
            "detail": "The AI pipeline took too long. Please try again.",
        }
    )


# ── Helper ────────────────────────────────────────────────────────────────────
def _http_status_label(code: int) -> str:
    labels = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
        504: "Gateway Timeout",
    }
    return labels.get(code, f"HTTP Error {code}")


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Multi-Agent E-commerce AI",
        "docs":    "/docs",
        "health":  "/api/v1/health",
    }