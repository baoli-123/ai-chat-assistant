# AI Chat Assistant

A lightweight AI chat web application built with FastAPI + SQLite + Vue3 (CDN).
Supports multi-turn conversations, RAG-style knowledge base, and streaming responses.

## Features

- Multi-turn conversation with context memory
- Knowledge base upload (PDF / TXT) and retrieval-augmented generation
- Real-time streaming response via WebSocket
- User authentication (JWT)
- Docker one-click deployment

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11 + FastAPI |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Vue 3 + Tailwind CSS (CDN, no build step) |
| Auth | JWT |
| Deploy | Docker + docker-compose |
| LLM | OpenAI-compatible API (any provider) |

## Quick Start

```bash
# Clone
git clone https://github.com/yourname/ai-chat-assistant.git
cd ai-chat-assistant

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000 in your browser.

## Docker

```bash
docker-compose up -d
```

## Project Structure

```
├── main.py              # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── app/
│   ├── __init__.py
│   ├── database.py      # DB connection
│   ├── models.py        # SQLAlchemy models
│   ├── routers/
│   │   ├── chat.py      # Chat & WebSocket
│   │   └── users.py     # Auth
│   ├── templates/
│   │   └── index.html   # Frontend
│   └── static/
└── sql/
    └── init.sql
```

## API Docs

- `POST /api/auth/register` — Register
- `POST /api/auth/login` — Login, returns JWT
- `POST /api/chat/send` — Send a message, get reply
- `WS /api/chat/ws/{token}` — WebSocket streaming chat
- `POST /api/kb/upload` — Upload knowledge base file
- `GET /api/history/{user_id}` — Get chat history

## License

MIT
