<div align="center">

# 📚 AI Bookstore — Multi-Agent E-Commerce

**A production-ready AI-powered bookstore with a 7-agent LangGraph pipeline,
streaming chat, PostgreSQL backend, and full order management.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.55-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.1-1C3C3C?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

[🌐 Live Demo](https://ai-bookstore06.streamlit.app) · [📡 API Docs](https://ai-bookstore-ai.onrender.com/docs) · [🐛 Report Bug](https://github.com/Priyanshukv06/multi-agent-ecommerce/issues)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **7-Agent AI Pipeline** | Planner → Search → Research → Comparison → Recommendation → Critic → Action |
| 💬 **Streaming Chat** | Real-time token-by-token AI responses via SSE |
| 📚 **103 Books** | Across 15 CS/ML categories with cover images |
| 🛒 **Full Order Flow** | Browse → Buy → Track → Return |
| 👤 **Auth System** | Session-based login with role access (user/admin) |
| 🖼️ **Cover Images** | Dual-source fetch: Open Library + Google Books API |
| 🔧 **Admin Panel** | Live stats, stock manager, order status updater |
| 🚀 **Production Deploy** | FastAPI on Render + Streamlit on Streamlit Cloud |

---

## 🏗️ Architecture

```mermaid
flowchart TD
    A["🖥️ Streamlit Frontend\nBrowse | Chat | Orders | Admin"] 
    B["⚡ FastAPI Backend\n/chat/stream | /products | /order | /track | /return"]
    C["🧠 Planner Agent\nintent classification + routing"]
    D["🔍 Search Agent\nqueries PostgreSQL"]
    E["🔬 Research Agent\ndeep book analysis"]
    F["⚖️ Comparison Agent\ncompares options"]
    G["🎯 Recommendation Agent\nranks results"]
    H["🎭 Critic Agent\nquality check"]
    I["⚡ Action Agent\nplace / track orders"]
    J["🗄️ Supabase PostgreSQL\nproducts | orders | users | memory"]

    A -->|REST / SSE| B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    D & E & F & G & H & I --> J
```

## 🗂️ Project Structure


```
multi-agent-ecommerce/
│
├── api/ # FastAPI application
│ ├── main.py # App entry point, lifespan, CORS
│ └── routes.py # All API endpoints
│
├── agents/ # LangGraph agent definitions
│ ├── planner.py # Intent classification + routing
│ ├── search.py # Product search agent
│ ├── research.py # Deep book research agent
│ ├── comparison.py # Side-by-side comparison agent
│ ├── recommendation.py # Personalised ranking agent
│ ├── critic.py # Response quality checker
│ └── action.py # Order/return execution agent
│
├── graph/ # LangGraph pipeline
│ ├── pipeline.py # Node wiring + conditional edges
│ └── runner.py # Graph executor + streaming
│
├── tools/ # DB tool functions for agents
│ └── db_tool.py # search_products, place_order, etc.
│
├── memory/ # Conversation persistence
│ └── conversation_store.py # save_turn, get_history, get_last_context
│
├── auth/ # Authentication
│ └── auth.py # bcrypt hashing, user/order queries
│
├── state/ # LangGraph state schema
│ └── schema.py # AgentState, ProductItem TypedDicts
│
├── db/ # Database connection
│ └── connection.py # get_connection(), get_cursor()
│
├── config/ # Configuration
│ ├── _init_.py # Exports all settings
│ └── settings.py # Reads from .env + st.secrets
│
├── data/ # Database seeding
│ ├── seed_products.py # Seeds 103 books + 4 users
│ ├── seed_schema.sql # PostgreSQL table definitions
│ └── fetch_missing_covers.py # Patches missing cover images
│
├── frontend/ # Streamlit application
│ ├── app.py # Entry point + auth gate
│ ├── pages/
│ │ ├── browse.py # Book catalog with filters
│ │ ├── chat.py # AI assistant with streaming
│ │ ├── orders.py # Order history
│ │ ├── book_detail.py # Single book view + buy button
│ │ ├── cart.py # Cart management
│ │ └── admin.py # Admin dashboard
│ └── utils/
│ ├── api.py # All API call wrappers
│ └── session.py # Login/logout, session state
│
├── render.yaml # Render deployment config
├── runtime.txt # Python 3.11.9
├── requirements.txt # Production dependencies
├── .env.example # Template — copy to .env
└── .gitignore
```
---

## 🤖 The 7-Agent Pipeline in Action

User: "recommend a machine learning book under ₹800"

    🧠 Planner → intent: "recommendation", budget: 800, category: "ml"

    🔍 Search → queries PostgreSQL → returns 8 matching books

    🔬 Research → fetches descriptions, reviews, ratings for each

    ⚖️ Comparison → scores books on price / rating / relevance

    🎯 Recommend → ranks + selects top 3 with reasoning

    🎭 Critic → validates response, checks for hallucinations

    ⚡ Action → streams final response token by token

User: "buy it"

    🧠 Planner → intent: "purchase", recalls product from memory

    ⚡ Action → places order in DB → returns order ID ORD-00001


---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- PostgreSQL database — free tier on [Supabase](https://supabase.com)
- [NVIDIA AI API key](https://build.nvidia.com) — free
- [Groq API key](https://console.groq.com) — free

### 1. Clone
```bash
git clone https://github.com/Priyanshukv06/multi-agent-ecommerce.git
cd multi-agent-ecommerce
```

### 2. Virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
NVIDIA_API_KEY=nvapi-...
GROQ_API_KEY=gsk_...
SECRET_KEY=your-random-secret-key-here
APP_ENV=development
DEBUG=true
API_URL=http://localhost:8000
```

### 5. Set up database
```bash
# Create all tables
psql $DATABASE_URL -f data/seed_schema.sql

# Seed 103 books + 4 users (takes ~2 min, fetches cover images)
python data/seed_products.py

# Optional: patch any missing cover images
python data/fetch_missing_covers.py
```

### 6. Run backend
```bash
uvicorn api.main:app --reload --port 8000
```

### 7. Run frontend (new terminal)
```bash
streamlit run frontend/app.py
```

### 8. Open
```bash
Frontend → http://localhost:8501
API Docs → http://localhost:8000/docs
```



---

## 🔑 Default Accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Admin — full dashboard |
| `user1` | `user123` | Regular user |
| `user2` | `user123` | Regular user |
| `user3` | `user123` | Regular user |

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check + agent list |
| `POST` | `/api/v1/chat` | Single-shot AI response |
| `POST` | `/api/v1/chat/stream` | Streaming AI response (SSE) |
| `GET` | `/api/v1/products` | List products with filters |
| `GET` | `/api/v1/products/{id}` | Single product detail |
| `GET` | `/api/v1/products/meta/categories` | All categories |
| `GET` | `/api/v1/products/meta/price-range` | Price stats |
| `POST` | `/api/v1/order` | Place an order |
| `GET` | `/api/v1/track/{order_id}` | Track order status |
| `POST` | `/api/v1/return` | Initiate a return |
| `GET` | `/api/v1/history/{session_id}` | Conversation history |
| `DELETE` | `/api/v1/history/{session_id}` | Clear history |

Full interactive docs → **[https://ai-bookstore-ai.onrender.com/docs](https://ai-bookstore-ai.onrender.com/docs)**

---

## ☁️ Deployment

### Backend on Render

1. Push repo to GitHub
2. [render.com](https://render.com) → New Web Service → Connect repo
3. Fill settings:

| Field | Value |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| Python Version | `3.11.9` (via `runtime.txt`) |

4. Add all `.env` variables as environment variables
5. Deploy ✅

### Frontend on Streamlit Cloud

1. [share.streamlit.io](https://share.streamlit.io) → New app → Connect repo
2. Main file path: `frontend/app.py`
3. Add secrets:
```toml
API_URL        = "https://your-app.onrender.com"
SECRET_KEY     = "your-secret-key"
NVIDIA_API_KEY = "nvapi-..."
GROQ_API_KEY   = "gsk_..."
```
4. Deploy ✅

---

## 📚 Book Categories

| Category | Books | Category | Books |
|---|---|---|---|
| Machine Learning | 8 | Algorithms | 8 |
| Deep Learning | 8 | NLP | 7 |
| Computer Vision | 7 | Data Science | 7 |
| Databases | 7 | Distributed Systems | 7 |
| Mathematics | 7 | System Design | 7 |
| Python | 7 | Computer Networks | 6 |
| Operating Systems | 6 | MLOps | 6 |
| Reinforcement Learning | 5 | | |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit 1.55 |
| **Backend** | FastAPI 0.135 + Uvicorn 0.42 |
| **AI Orchestration** | LangGraph 1.1 + LangChain 1.2 |
| **LLM — Reasoning** | NVIDIA AI Endpoints (Llama 3.1 70B) |
| **LLM — Speed** | Groq (Llama 3 8B) |
| **Database** | PostgreSQL via Supabase |
| **Auth** | bcrypt + session tokens |
| **Streaming** | Server-Sent Events (SSE) |
| **Deployment** | Render (API) + Streamlit Cloud (UI) |

---

## 🤝 Contributing

```bash
git checkout -b feature/your-feature
git commit -m "feat: your feature"
git push origin feature/your-feature
# Open a Pull Request
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ by <a href="https://github.com/Priyanshukv06">Priyanshu Verma</a>
</div>
