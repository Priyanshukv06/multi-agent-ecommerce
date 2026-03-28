from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Multi-Agent E-commerce AI",
    description="""
## 🤖 Multi-Agent AI Book Store

A LangGraph-powered multi-agent system for intelligent book recommendations.

### Agents
- **Planner** — classifies intent, extracts budget/category
- **Search** — finds matching products from database
- **Research** — analyzes reviews and extracts insights
- **Comparison** — scores and ranks products
- **Recommendation** — generates personalized responses
- **Critic** — validates quality with retry loop
- **Action** — handles orders, tracking, returns

### Key Features
- 🧠 Conversation memory across sessions
- 🔁 Self-correcting critic-retry loop
- 📦 Full order lifecycle (place → track → return)
- ⚡ Groq + NVIDIA NIM LLMs
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Multi-Agent E-commerce AI",
        "docs":    "/docs",
        "health":  "/api/v1/health"
    }
