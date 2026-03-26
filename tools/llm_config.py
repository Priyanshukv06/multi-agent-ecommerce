import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_groq import ChatGroq

load_dotenv()

# NVIDIA NIM — for deep reasoning tasks
nvidia_llm = ChatNVIDIA(
    model="nvidia/llama-3.1-nemotron-70b-instruct",  # best free model on NIM
    nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=0.3,
    max_tokens=1024,
)

# NVIDIA NIM — for structured output tasks
nvidia_fast = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct",
    nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
    temperature=0.1,
    max_tokens=512,
)

# Groq — for ultra-fast classification tasks
groq_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0,    # zero temp for intent classification = deterministic
    max_tokens=256,
)
