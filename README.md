# 🤖 AI Chatbot — FastAPI + OpenRouter

A **production-grade, multi-user AI chatbot** built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery**, powered by **OpenRouter AI** (NVIDIA Nemotron model). Features JWT authentication, multi-session chat management, Redis caching, Prometheus monitoring, rate limiting, and a sleek dark-themed frontend.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-8.0-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A?logo=celery&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [API Endpoints](#-api-endpoints)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Running the Application](#-running-the-application)
- [Frontend](#-frontend)
- [Monitoring & Observability](#-monitoring--observability)

---

## ✨ Features

### Authentication & Security
- **JWT-based authentication** with access tokens (30 min) and refresh tokens (7 days)
- **Bcrypt password hashing** via `passlib` with constant-time comparison
- **Separate secret keys** for access and refresh tokens
- **OAuth2 Bearer** token scheme with auto-refresh flow
- **Role-based access control** — `is_active`, `is_verified`, `is_superuser` flags
- **Rate limiting** — 3 signups/min, 5 logins/min, 20 chat messages/min (per user)

### Chat & AI
- **OpenRouter AI integration** via the OpenAI SDK (compatible API)
- **Default model**: `nvidia/nemotron-3-ultra-550b-a55b:free`
- **Configurable LLM parameters** — temperature, max tokens, top-p, frequency penalty
- **Full conversation history** persisted in PostgreSQL per session
- **System prompt** support for controlling AI behavior
- **Token usage tracking** for analytics

### Multi-User & Session Management
- **Full CRUD** for chat sessions (create, list, get, rename, delete)
- **User-level data isolation** — users can only access their own sessions
- **Automatic session resolution** — latest session used if none specified
- **Cascade deletion** — deleting a session removes all its messages

### Infrastructure & Performance
- **Redis caching** with Cache-Aside pattern and graceful degradation
- **Celery task queue** with Redis broker for background processing
- **Prometheus metrics** — HTTP request count/duration, cache hit/miss, LLM metrics
- **Connection pooling** — SQLAlchemy (pool_size=10, max_overflow=20) and Redis (max_connections=20)
- **Health check endpoint** — aggregated status of PostgreSQL, Redis, and Celery workers
- **Alembic migrations** for database schema versioning

### Developer Experience
- **Colorful structured logging** — ANSI-colored request/response lifecycle banners
- **Request ID tracking** via `ContextVar` across all layers
- **Swagger UI** auto-generated at `/docs`
- **Dependency injection** throughout — repositories, services, auth

---

## 🏗 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vanilla JS)                     │
│  static/index.html  ·  static/script.js  ·  static/style.css    │
│  Auth screens (Login/Signup) + Chat UI + Session Sidebar         │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP (JSON + Bearer Token)
┌──────────────────────────▼───────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  Auth Routes  │  │  Chat Routes │  │  Session Routes        │  │
│  │  /auth/*      │  │  /chat       │  │  /sessions/*           │  │
│  │  /auth/signup │  │  /health     │  │  /sessions/{id}/msgs   │  │
│  │  /auth/login  │  │  /history    │  │                        │  │
│  │  /auth/me     │  │  /reset      │  │                        │  │
│  │  /auth/refresh│  │  /metrics    │  │                        │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘  │
│         │                 │                       │               │
│  ┌──────▼─────────────────▼───────────────────────▼────────────┐  │
│  │               SERVICE LAYER (Business Logic)                │  │
│  │  AuthService · ChatbotService · SessionService · JWTService │  │
│  │  UserService · CacheService · HealthService                 │  │
│  └──────┬──────────────┬─────────────────────┬─────────────────┘  │
│         │              │                     │                    │
│  ┌──────▼──────┐ ┌─────▼─────┐  ┌───────────▼───────────────┐   │
│  │ Repositories│ │  OpenAI   │  │  Redis (Cache/Rate Limit)  │   │
│  │ User/Session│ │  SDK →    │  │  Celery (Task Queue)       │   │
│  │ /Message    │ │ OpenRouter│  │  Prometheus (Metrics)      │   │
│  └──────┬──────┘ └───────────┘  └────────────────────────────┘   │
│         │                                                         │
│  ┌──────▼───────────────────────────────────────────────────────┐ │
│  │              PostgreSQL (via SQLAlchemy 2.0 ORM)             │ │
│  │         users · chat_sessions · messages                     │ │
│  └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | FastAPI 0.139 | Async web framework with auto-docs |
| **AI Provider** | OpenRouter (OpenAI SDK) | LLM API gateway |
| **Database** | PostgreSQL + SQLAlchemy 2.0 | Persistent storage with ORM |
| **Migrations** | Alembic | Database schema versioning |
| **Auth** | python-jose + passlib + bcrypt | JWT tokens + password hashing |
| **Caching** | Redis 8.0 | Cache-Aside pattern, rate limiting storage |
| **Rate Limiting** | SlowAPI + Redis | Per-user and per-IP throttling |
| **Task Queue** | Celery 5.6 + Redis | Background job processing |
| **Monitoring** | prometheus_client | HTTP, cache, LLM, Celery metrics |
| **Validation** | Pydantic V2 + pydantic-settings | Request/response schemas, config |
| **Server** | Uvicorn | ASGI server |
| **Frontend** | HTML + CSS + Vanilla JS | Dark-themed responsive chat UI |

---

## 📁 Project Structure

```
.
├── app/                          # Application core
│   ├── main.py                   # FastAPI app, lifespan, middleware, route registration
│   ├── config.py                 # App name, version, description constants
│   ├── dependencies.py           # Dependency injection (repos, services, auth guards)
│   └── middleware.py             # RequestLifecycleMiddleware (request/response logging)
│
├── api/                          # Route handlers (controllers)
│   ├── routes.py                 # /health, /chat, /reset, /history, /metrics
│   ├── auth_routes.py            # /auth/signup, /auth/login, /auth/refresh, /auth/logout, /auth/me
│   └── session_routes.py         # /sessions CRUD + /sessions/{id}/messages
│
├── services/                     # Business logic layer
│   ├── chatbot_service.py        # AI chat (OpenRouter API calls, history, session resolution)
│   ├── auth_service.py           # Signup, login, token refresh logic
│   ├── jwt_service.py            # JWT create/verify (access + refresh tokens)
│   ├── user_service.py           # Profile get/update with cache invalidation
│   ├── session_service.py        # Session CRUD with ownership enforcement
│   ├── cache_service.py          # Redis cache abstraction (get/set/delete/invalidate)
│   └── health_service.py         # Aggregated health checks (DB, Redis, Celery)
│
├── database/                     # Data access layer
│   ├── base.py                   # SQLAlchemy DeclarativeBase
│   ├── session.py                # Engine, SessionLocal, get_db dependency
│   ├── models/                   # ORM models
│   │   ├── user.py               # User model (UUID PK, auth fields, timestamps)
│   │   ├── session.py            # ChatSession model (FK → users, cascade messages)
│   │   └── message.py            # Message model (role, content, token_count, model_name)
│   └── repositories/             # Repository pattern (data access)
│       ├── user_repository.py    # CRUD for users table
│       ├── session_repository.py # CRUD for chat_sessions table
│       └── message_repository.py # CRUD for messages table
│
├── schemas/                      # Pydantic request/response schemas
│   ├── request.py                # ChatRequest (message + optional session_id)
│   ├── response.py               # ChatResponse, HealthResponse, HistoryResponse
│   ├── auth.py                   # Signup/Login/Refresh/Token/Profile schemas
│   └── session.py                # Session CRUD + message listing schemas
│
├── core/                         # Cross-cutting concerns
│   ├── settings.py               # Pydantic Settings (loads .env, all config)
│   ├── security.py               # Bcrypt hash_password / verify_password
│   └── limiter.py                # SlowAPI rate limiter (Redis-backed)
│
├── redis_client/                 # Redis connection management
│   └── client.py                 # RedisClientManager (connection pool, graceful degradation)
│
├── celery_app/                   # Celery configuration & tasks
│   ├── celery.py                 # Celery app factory (broker/backend config, task routing)
│   └── tasks.py                  # Example tasks (session cleanup, RAG processing)
│
├── monitoring/                   # Observability
│   └── metrics.py                # Prometheus counters, histograms, gauges
│
├── utils/                        # Utilities
│   └── helpers.py                # Colored logging, request ID, banner builders
│
├── static/                       # Frontend assets
│   ├── index.html                # Auth + Chat UI (Login/Signup/Sidebar/Chat)
│   ├── script.js                 # Auth manager, session management, chat logic
│   └── style.css                 # Dark theme with CSS variables, animations
│
├── alembic/                      # Database migrations
│   ├── env.py                    # Alembic environment (loads models + settings)
│   └── versions/                 # Migration scripts
│       ├── 8e307b53ddf2_initial_schema_users_sessions_messages.py
│       └── cefc8cffeb8d_phase3_add_auth_fields_to_users.py
│
├── .env                          # Environment variables (API keys, DB config, JWT secrets)
├── .gitignore                    # Git ignore rules
├── alembic.ini                   # Alembic configuration
├── requirements.txt              # Python dependencies (pinned versions)
└── README.md                     # This file
```

---

## 🗄 Database Schema

Three tables with UUID primary keys and cascading relationships:

```
┌─────────────────────────────────────┐
│              users                  │
├─────────────────────────────────────┤
│ id           UUID  PK  (auto)       │
│ username     VARCHAR(50) UNIQUE     │
│ email        VARCHAR(100) UNIQUE    │
│ hashed_password  VARCHAR(255) NULL  │
│ is_active    BOOLEAN  (default T)   │
│ is_verified  BOOLEAN  (default F)   │
│ is_superuser BOOLEAN  (default F)   │
│ last_login   TIMESTAMP WITH TZ      │
│ created_at   TIMESTAMP WITH TZ      │
│ updated_at   TIMESTAMP WITH TZ      │
└──────────────┬──────────────────────┘
               │ 1:N (cascade delete)
┌──────────────▼──────────────────────┐
│          chat_sessions              │
├─────────────────────────────────────┤
│ id           UUID  PK  (auto)       │
│ user_id      UUID  FK → users.id    │
│ title        VARCHAR(255)           │
│ created_at   TIMESTAMP WITH TZ      │
│ updated_at   TIMESTAMP WITH TZ      │
└──────────────┬──────────────────────┘
               │ 1:N (cascade delete)
┌──────────────▼──────────────────────┐
│            messages                 │
├─────────────────────────────────────┤
│ id           UUID  PK  (auto)       │
│ session_id   UUID  FK → sessions.id │
│ role         VARCHAR(20) (indexed)  │
│ content      TEXT                   │
│ token_count  INTEGER  (nullable)    │
│ model_name   VARCHAR(100)           │
│ created_at   TIMESTAMP WITH TZ      │
└─────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| `POST` | `/auth/signup` | ❌ | 3/min | Register a new account (returns tokens) |
| `POST` | `/auth/login` | ❌ | 5/min | Login with username/email + password |
| `POST` | `/auth/refresh` | ❌ | — | Refresh expired access token |
| `POST` | `/auth/logout` | ✅ | — | Logout (server-side logging) |
| `GET` | `/auth/me` | ✅ | — | Get current user profile (Redis cached) |
| `PUT` | `/auth/me` | ✅ | — | Update username/email |

### Chat (`/chat`, `/history`, `/reset`)

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| `POST` | `/chat` | ✅ | 20/min (per user) | Send message, receive AI reply |
| `GET` | `/history` | ✅ | — | Get conversation history |
| `POST` | `/reset` | ✅ | — | Clear latest session history |

### Sessions (`/sessions`)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/sessions` | ✅ | List all sessions (with message counts) |
| `POST` | `/sessions` | ✅ | Create a new session |
| `GET` | `/sessions/{id}` | ✅ | Get specific session |
| `PUT` | `/sessions/{id}` | ✅ | Rename a session |
| `DELETE` | `/sessions/{id}` | ✅ | Delete session + all messages |
| `GET` | `/sessions/{id}/messages` | ✅ | Get all messages in a session |

### System

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | ❌ | Aggregated health (DB + Redis + Celery) |
| `GET` | `/metrics` | ❌ | Prometheus metrics endpoint |
| `GET` | `/docs` | ❌ | Swagger UI (auto-generated) |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **PostgreSQL 15+**
- **Redis 7+**
- **pip** (Python package manager)

### 1. Clone the Repository

```bash
git clone https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend.git
cd AIChatbotFastAPIBackend
```

### 2. Create Virtual Environment

```bash
python -m venv vir_env
source vir_env/bin/activate  # Linux/macOS
# vir_env\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

```sql
CREATE DATABASE chatbot_db;
```

### 5. Configure Environment Variables

Create a `.env` file in the project root (see [Environment Variables](#-environment-variables) section).

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Start Redis (if not already running)

```bash
redis-server
```

### 8. Start the Application

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 9. (Optional) Start Celery Worker

```bash
celery -A celery_app.celery worker --loglevel=info
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# ── AI Configuration ──
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
MODEL_NAME=nvidia/nemotron-3-ultra-550b-a55b:free
BASE_URL=https://openrouter.ai/api/v1
TEMPERATURE=0.7
MAX_TOKENS=2048
TOP_P=0.9
FREQUENCY_PENALTY=0.2

# ── Database ──
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=chatbot_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# ── JWT Authentication ──
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=your-access-token-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-token-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── Redis & Celery ──
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# ── Caching & Rate Limiting ──
CACHE_DEFAULT_TTL=300
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_LOGIN_PER_MINUTE=5

# ── Monitoring ──
PROMETHEUS_ENABLED=true
ENVIRONMENT=development
```

---

## ▶ Running the Application

| Service | Command | URL |
|---------|---------|-----|
| **FastAPI Server** | `uvicorn app.main:app --reload` | `http://127.0.0.1:8000` |
| **Swagger Docs** | (auto) | `http://127.0.0.1:8000/docs` |
| **Chat UI** | (auto) | `http://127.0.0.1:8000/static/index.html` |
| **Redis** | `redis-server` | `localhost:6379` |
| **Celery Worker** | `celery -A celery_app.celery worker --loglevel=info` | — |

> **Note:** Redis is optional. If Redis is unavailable, the app runs in **graceful degradation** mode — caching and rate limiting are disabled, but core functionality continues to work.

---

## 🎨 Frontend

The frontend is a **single-page application** served as static files at `/static/`:

- **Dark theme** with CSS custom properties and smooth animations
- **Authentication screens** — Login/Signup with form validation
- **Session sidebar** — Create, select, rename, delete chat sessions
- **Chat interface** — Real-time messaging with typing indicators
- **Auto token refresh** — Transparent 401 → refresh → retry flow
- **Responsive design** — Collapsible sidebar on mobile
- **Google Fonts** — Inter font family for premium typography

### Auth Flow

```
1. User opens app → checks localStorage for tokens
2. If tokens exist → validate via GET /auth/me → show chat UI
3. If no tokens → show login screen
4. On 401 → auto-refresh via POST /auth/refresh → retry original request
5. If refresh fails → force logout → show login screen
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics (`GET /metrics`)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, http_status | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency |
| `cache_hits_total` | Counter | — | Redis cache hits |
| `cache_misses_total` | Counter | — | Redis cache misses |
| `llm_calls_total` | Counter | model, status | LLM API calls |
| `llm_response_time_seconds` | Histogram | model | LLM response latency |
| `celery_workers_active` | Gauge | — | Active Celery workers |
| `celery_tasks_total` | Counter | task_name, status | Celery task executions |

### Health Check (`GET /health`)

Returns aggregated status of all infrastructure components:

```json
{
  "status": "healthy",
  "environment": "development",
  "components": {
    "database": { "status": "healthy", "message": "Database connection successful" },
    "redis": { "status": "healthy", "message": "Redis connection successful" },
    "celery": { "status": "healthy", "message": "1 Celery worker(s) active" }
  }
}
```

Status values: `healthy` → `degraded` (non-critical component down) → `unhealthy` (database down → HTTP 503).

### Structured Logging

Every request/response is logged with colorful banners:

```
═══════════════════════════════════════════════════════
                FRONTEND  →  BACKEND
═══════════════════════════════════════════════════════
  Request ID  : REQ-a1b2c3d4
  Timestamp   : 2026-07-16 23:30:00
  Method      : POST
  Endpoint    : /chat
  Client IP   : 127.0.0.1
  User Message: "What is FastAPI?"
═══════════════════════════════════════════════════════
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ by <strong>Vaibhav Sharma</strong>
</p>