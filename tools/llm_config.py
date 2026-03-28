import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_groq import ChatGroq

load_dotenv()

# ── NVIDIA NIM — Deep Reasoning (Recommendation Agent) ─────────────────────
# Llama 4 Maverick: best reasoning quality on your free tier list
nvidia_llm = ChatNVIDIA(
    model="meta/llama-4-maverick-17b-128e-instruct",
    nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=0.3,
    max_tokens=1024,
    timeout=60,          # explicit timeout — prevents silent hanging [web:110]
)

# ── NVIDIA NIM — Structured JSON Output (Research + Comparison Agents) ──────
# llama3-70b: confirmed on your list, no cold-start issues, strong at JSON
nvidia_fast = ChatNVIDIA(
    model="meta/llama3-70b-instruct",
    nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=0.1,
    max_tokens=512,
    timeout=60,
)

# ── Groq — Ultra-fast Classification (Planner + Critic Agents) ──────────────
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0,
    max_tokens=256,
)
