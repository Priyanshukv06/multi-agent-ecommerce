from config.settings import NVIDIA_API_KEY, GROQ_API_KEY
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_groq import ChatGroq


nvidia_llm = ChatNVIDIA(
    model="meta/llama-4-maverick-17b-128e-instruct",
    nvidia_api_key=NVIDIA_API_KEY,
    temperature=0.3,
    max_completion_tokens=2048,
)

nvidia_fast = ChatNVIDIA(
    model="meta/llama3-70b-instruct",
    nvidia_api_key=NVIDIA_API_KEY,
    temperature=0.1,
    max_completion_tokens=1024,
)

# No timeout param — not valid for ChatGroq, causes UserWarning
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.0,
    max_tokens=1024,
)
