# 🤖 AI Chatbot — FastAPI + OpenRouter + RAG (pgvector)

A **production-grade, multi-user AI chatbot and RAG (Retrieval-Augmented Generation) system** built with **FastAPI**, **PostgreSQL (pgvector)**, **Redis**, and **Celery**, powered by **OpenRouter AI** (NVIDIA Nemotron LLM & Embedding models). 

Features end-to-end RAG document ingestion & vector search retrieval, JWT authentication with auto-refresh tokens, multi-session chat management, Redis caching, Prometheus monitoring, rate limiting, and a sleek dark-themed Web UI.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-0.8.5-blue?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-8.0-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A?logo=celery&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📑 Table of Contents

- [📌 Project Introduction](#-project-introduction)
- [✨ Features](#-features)
- [🛠 Technology Stack](#-technology-stack)
- [🏗 Project Architecture](#-project-architecture)
- [📁 Folder Structure](#-folder-structure)
- [🗄 Database & Schema](#-database--schema)
- [🔐 Authentication & Security](#-authentication--security)
- [💬 Chat System](#-chat-system)
- [📄 RAG Pipeline Architecture](#-rag-pipeline-architecture)
- [⚡ Celery & Redis Infrastructure](#-celery--redis-infrastructure)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🔌 API Documentation](#-api-documentation)
- [🚀 Installation & Setup Guide](#-installation--setup-guide)
- [🔑 Environment Variables](#-environment-variables)
- [▶ Running the Application](#-running-the-application)
- [🖼 Screenshots](#-screenshots)
- [🔮 Future Roadmap](#-future-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👨‍💻 Author](#-author)

---

## 📌 Project Introduction

### What is this project?
This project is an enterprise-grade AI Chatbot backend and Web application designed to demonstrate modern asynchronous Python backend development, production-ready AI integration (via OpenRouter & OpenAI SDK), and high-performance Document Retrieval-Augmented Generation (RAG) using PostgreSQL `pgvector`.

### Why does it exist?
Traditional generic LLM applications lack domain-specific context and user document grounding. This application bridges that gap by enabling users to upload PDF, Word, CSV, Markdown, or Text documents, automatically processing and indexing them as vector embeddings, and retrieving relevant document context during live chat conversations to produce grounded, hallucination-free AI responses.

### Key Real-World Use Cases
* **Personalized AI Resume / Portfolio Assistant**: Upload your resume or CV and have an AI answer detailed experience questions on your behalf.
* **Document Question Answering**: Query lengthy reports, research papers, contracts, or documentation.
* **Internal Enterprise Knowledge Base**: Store and search company manuals, FAQs, and policies securely per user.

---

## ✨ Features

### 🔐 Authentication & Security
- **JWT Authentication**: Short-lived access tokens (30 mins) and long-lived refresh tokens (7 days).
- **Bcrypt Password Hashing**: Secure password storage using `passlib` with constant-time verification.
- **Token Isolation**: Separate secret keys for access and refresh tokens.
- **Role-Based Access Control**: `is_active`, `is_verified`, and `is_superuser` status flags.
- **Throttling & Rate Limiting**: Redis-backed SlowAPI rate limiting (3 signups/min, 5 logins/min, 20 messages/min).

### 💬 Chat & AI Engine
- **OpenRouter AI Integration**: Native OpenAI SDK integration with OpenRouter API gateway.
- **Default LLM**: `nvidia/nemotron-3-ultra-550b-a55b:free`.
- **Configurable Parameters**: Dynamic temperature, max tokens, top-p, and frequency penalty tuning.
- **Persistent Conversation History**: Multi-turn chat history stored per session in PostgreSQL.

### 📄 RAG (Retrieval-Augmented Generation) & Document Processing
- **Multi-Format Ingestion**: Supports `.pdf`, `.docx`, `.txt`, `.csv`, `.md`.
- **OCR Support**: Extensible document loaders with text extraction fallbacks.
- **Smart Chunking**: Text split into configurable chunk sizes with overlap (e.g., 1000 chars, 200 overlap).
- **Matryoshka Vector Embeddings**: Generates embeddings using `nvidia/nemotron-3-embed-1b:free`, truncated and L2-normalized to 2000 dimensions for `pgvector` HNSW/IVFFlat index compliance.
- **Vector Similarity Search**: Cosine distance similarity search (`1 - (vector <=> query_vector)`) filtered by authenticated user ownership and completion status.
- **Context Injection**: Retrieved document chunks are automatically formatted and injected into the LLM system prompt.

### ⚡ Infrastructure & Background Processing
- **Redis Caching**: Cache-Aside pattern for user profiles and sessions with graceful degradation.
- **Celery Task Queue**: Async background worker processing for document ingestion and heavy operations.
- **Alembic Migrations**: Fully tracked schema migrations including `pgvector` extension and index management.

### 📊 Monitoring & Observability
- **Prometheus Metrics (`/metrics`)**: Latency histograms, HTTP counters, Redis cache hits/misses, and LLM call metrics.
- **Aggregated Health Checks (`/health`)**: Status checks for PostgreSQL, Redis, and Celery workers.
- **Structured Colorful Logging**: ANSI-colored request/response banners with `ContextVar` Request ID tracking.

---

## 🛠 Technology Stack

| Domain | Technology | Description / Purpose |
|--------|-----------|-----------------------|
| **Core Framework** | FastAPI 0.139 | High-performance async REST API framework |
| **Language** | Python 3.12+ | Strongly typed modern Python |
| **Database** | PostgreSQL 15+ | Relational database storage |
| **Vector DB** | pgvector 0.8.5 | Native PostgreSQL vector extension for similarity search |
| **ORM** | SQLAlchemy 2.0 | Async-compatible Python SQL Toolkit & Object Relational Mapper |
| **Migrations** | Alembic | Version-controlled database schema migrations |
| **AI Gateway** | OpenRouter (OpenAI SDK) | Unified LLM & Embedding API gateway |
| **Embedding Model** | `nvidia/nemotron-3-embed-1b:free` | 2000-dim truncated L2-normalized vector embeddings |
| **LLM Model** | `nvidia/nemotron-3-ultra-550b-a55b:free` | Primary conversational AI model |
| **Caching** | Redis 8.0 | Cache-Aside pattern & rate limit storage |
| **Task Queue** | Celery 5.6 | Background document processing worker pool |
| **Authentication** | python-jose + passlib + bcrypt | JWT creation/validation & password hashing |
| **Rate Limiting** | SlowAPI | Redis-backed endpoint throttling |
| **Monitoring** | Prometheus Client | Application metrics and observability |
| **Frontend** | Vanilla JS + HTML5 + CSS3 | Dark-mode single page interface |

---

## 🏗 Project Architecture

### High-Level System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Single Page App)                  │
│   static/index.html   ·   static/script.js   ·   static/style.css│
│   Auth Forms  ·  Chat UI  ·  Session Sidebar  ·  Doc Upload      │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP / JSON / Bearer JWT
┌──────────────────────────▼───────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Auth Routes  │  │ Chat Routes  │  │ Document / Session     │  │
│  │ /auth/*      │  │ /chat        │  │ /documents, /sessions  │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬────────────┘  │
│         │                 │                      │               │
│  ┌──────▼─────────────────▼──────────────────────▼────────────┐  │
│  │                    SERVICE LAYER                           │  │
│  │ AuthService · ChatbotService · RetrievalService            │  │
│  │ DocumentService · CacheService · HealthService             │  │
│  └──────┬──────────────┬──────────────────┬───────────────────┘  │
│         │              │                  │                      │
│  ┌──────▼──────┐ ┌─────▼───────┐  ┌───────▼───────────────┐      │
│  │ Repositories│ │ OpenRouter  │  │ Redis (Cache/Limits)  │      │
│  │ User / Chat │ │ API Gateway │  │ Celery (Task Broker)  │      │
│  │ Document    │ └─────────────┘  │ Prometheus (Metrics)  │      │
│  │ Embedding   │                  └───────────────────────┘      │
│  └──────┬──────┘                                                 │
│         │                                                        │
│  ┌──────▼──────────────────────────────────────────────────────┐ │
│  │         PostgreSQL Database (pgvector Extension)            │ │
│  │ users · chat_sessions · messages · documents ·              │ │
│  │ document_chunks · chunk_metadata · embeddings (HNSW Index)  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
.
├── app/                          # Core application setup
│   ├── config.py                 # App metadata & constants
│   ├── dependencies.py           # Dependency Injection container (repos, services, auth)
│   ├── main.py                   # FastAPI app entry point, middleware, routes
│   └── middleware.py             # Request lifecycle logging & context ID injection
│
├── api/                          # Route handlers (controllers)
│   ├── auth_routes.py            # Signup, Login, Refresh, Logout, Profile routes
│   ├── document_routes.py        # Upload, List, and Delete document endpoints
│   ├── routes.py                 # /chat, /history, /reset, /health, /metrics
│   └── session_routes.py         # Chat session CRUD and message history
│
├── services/                     # Business logic layer
│   ├── auth_service.py           # Signup/Login credential validation
│   ├── cache_service.py          # Redis caching implementation
│   ├── chatbot_service.py        # Chat processing & RAG prompt orchestration
│   ├── chunking_service.py       # Recursive text splitting logic
│   ├── document_service.py       # File upload validation & lifecycle tracking
│   ├── embedding_service.py      # Embedding provider & Matryoshka dimension truncation
│   ├── health_service.py         # Subsystem status aggregations
│   ├── jwt_service.py            # JWT token encoding, decoding & verification
│   ├── loader_service.py         # Factory router for file loaders
│   ├── metadata_service.py       # Chunk metadata extraction
│   ├── retrieval_service.py      # Vector similarity retrieval & context builder
│   ├── session_service.py        # Chat session management
│   ├── storage_service.py        # File persistence interface
│   └── user_service.py           # User management service
│
├── database/                     # Data access & persistence layer
│   ├── base.py                   # SQLAlchemy Base class
│   ├── session.py                # Database connection pool setup
│   ├── models/                   # ORM database models
│   │   ├── user.py               # User table definition
│   │   ├── session.py            # ChatSession table definition
│   │   ├── message.py            # Message table definition
│   │   ├── document.py           # Document table definition
│   │   ├── chunk.py              # DocumentChunk table definition
│   │   ├── chunk_metadata.py     # ChunkMetadata table definition
│   │   └── embedding.py          # Embedding table definition (pgvector Column)
│   └── repositories/             # Data Access Repositories
│       ├── user_repository.py    # User queries
│       ├── session_repository.py # Chat session queries
│       ├── message_repository.py # Message history queries
│       ├── document_repository.py# Document status queries
│       ├── chunk_repository.py   # Chunk persistence
│       └── embedding_repository.py# Cosine similarity vector search queries
│
├── loaders/                      # Extensible document extractors
│   ├── base.py                   # Abstract Base Loader
│   ├── pdf.py                    # PDF Loader (pypdf/pdfplumber/OCR)
│   ├── docx.py                   # Word document loader
│   ├── csv.py                    # CSV spreadsheet loader
│   ├── txt.py                    # Plain text loader
│   └── markdown.py               # Markdown file loader
│
├── storage/                      # File storage implementations
│   ├── base.py                   # Storage Provider Interface
│   └── local.py                  # Disk storage provider implementation
│
├── celery_app/                   # Asynchronous task queue
│   ├── celery.py                 # Celery app configuration
│   └── tasks.py                  # Document ingestion background task
│
├── schemas/                      # Pydantic validation schemas
│   ├── auth.py                   # Auth requests/responses
│   ├── request.py                # Chat request schema
│   ├── response.py               # Chat & API responses
│   └── session.py                # Session schemas
│
├── core/                         # Configuration & security settings
│   ├── settings.py               # Pydantic Settings class (.env reader)
│   ├── security.py               # Password hashing utilities
│   └── limiter.py                # SlowAPI rate limiter
│
├── redis_client/                 # Redis connection manager
│   └── client.py                 # Redis client singleton
│
├── monitoring/                   # Prometheus metrics setup
│   └── metrics.py                # Prometheus metric counters & gauges
│
├── utils/                        # System helpers
│   └── helpers.py                # ANSI colorful logger & helper functions
│
├── static/                       # Web UI assets
│   ├── index.html                # Main SPA interface
│   ├── script.js                 # Frontend application logic
│   └── style.css                 # Custom CSS dark theme
│
├── alembic/                      # Database migration scripts
├── .env                          # Local environment variables
├── alembic.ini                   # Alembic configuration file
├── requirements.txt              # Pinned Python package dependencies
└── README.md                     # Project documentation
```

---

## 🗄 Database & Schema

The application uses **PostgreSQL** with the **`pgvector`** extension enabled.

```
┌──────────────────────────────────────┐
│                users                 │
├──────────────────────────────────────┤
│ id            UUID (PK)              │
│ username      VARCHAR(50) (Unique)   │
│ email         VARCHAR(100) (Unique)  │
│ hashed_pw     VARCHAR(255)           │
│ is_active     BOOLEAN                │
│ created_at    TIMESTAMPTZ            │
└──────────────────┬───────────────────┘
                   │ 1:N
     ┌─────────────┴──────────────┐
     │                            │
┌────▼─────────────┐     ┌────────▼───────────┐
│  chat_sessions   │     │     documents      │
├──────────────────┤     ├────────────────────┤
│ id        UUID PK│     │ id          UUID PK│
│ user_id   UUID FK│     │ user_id     UUID FK│
│ title     VARCHAR│     │ filename    VARCHAR│
└────────┬─────────┘     │ status      VARCHAR│
         │ 1:N           └────────┬───────────┘
┌────────▼─────────┐              │ 1:N
│    messages      │     ┌────────▼───────────┐
├──────────────────┤     │  document_chunks   │
│ id        UUID PK│     ├────────────────────┤
│ session_id UUID FK│     │ id          UUID PK│
│ role      VARCHAR│     │ document_id UUID FK│
│ content   TEXT   │     │ content     TEXT   │
└──────────────────┘     └────────┬───────────┘
                                  │ 1:N
                         ┌────────▼───────────┐
                         │    embeddings      │
                         ├────────────────────┤
                         │ id          UUID PK│
                         │ chunk_id    UUID FK│
                         │ vector      VECTOR │
                         └────────────────────┘
```

### Database Migration Commands (Alembic)

```bash
# Run all pending database migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Generate a new migration script
alembic revision --autogenerate -m "description_of_changes"
```

> [!NOTE]
> `pgvector` requires creating the vector column with dimension matching your setting (`2000` dimensions for truncated Nemotron embeddings) and creating an HNSW index for fast nearest-neighbor lookups.

---

## 🔐 Authentication & Security

The system uses standard **OAuth2 Bearer Token Authentication** with dual JWTs:

1. **Access Token**: Short-lived (30 minutes) used to authenticate API requests.
2. **Refresh Token**: Long-lived (7 days) used to retrieve new access tokens seamlessly.

```
Client                        Backend                      Redis / DB
  │                              │                              │
  ├─ 1. POST /auth/login ───────►│                              │
  │                              ├─ Verify Password ───────────►│
  │◄─ 2. Return Tokens ──────────┤                              │
  │  (Access + Refresh)          │                              │
  │                              │                              │
  ├─ 3. GET /chat (Bearer token)►│                              │
  │                              ├─ Validate JWT Token ────────►│
  │◄─ 4. Response ───────────────┤                              │
  │                              │                              │
  ├─ 5. Token Expired (401) ────►│                              │
  ├─ 6. POST /auth/refresh ─────►│                              │
  │◄─ 7. Return New Access Token ┴──────────────────────────────┘
```

---

## 💬 Chat System

The chat system guarantees state isolation per user and session:

- **Automatic Session Resolution**: If no `session_id` is supplied in `/chat`, the backend automatically resolves or creates the active chat session for the authenticated user.
- **Conversation Persistence**: Incoming user messages and generated AI replies are saved into the `messages` table synchronously before returning to the frontend.
- **Full History Context**: Prior turns in the session are loaded and supplied to OpenRouter to maintain conversation context.

---

## 📄 RAG Pipeline Architecture

### End-to-End RAG Ingestion & Retrieval Flow

```
========================================================================================
1. INGESTION PIPELINE (Background Celery Task)
========================================================================================
[User Uploads File] ──► [DocumentService] ──► [Celery Task: process_document_task]
                                                      │
 ┌────────────────────────────────────────────────────┘
 ▼
[LoaderService (PDF/DOCX/TXT)] ──► Text Extraction
 ▼
[ChunkingService] ──► Recursive Split (Size: 1000, Overlap: 200)
 ▼
[EmbeddingService] ──► Call OpenRouter Embedding API (`nemotron-3-embed-1b:free`)
                       │
                       ▼ Matryoshka Truncation (2048 → 2000 Dims) + L2 Normalization
                       │
[EmbeddingRepository] ──► Store Vectors into PostgreSQL `embeddings` table

========================================================================================
2. RETRIEVAL & PROMPT INJECTION PIPELINE (Live Chat Request)
========================================================================================
[User Question] ──► [ChatbotService] ──► [RetrievalService]
                                                │
                                                ▼ Embed Query Vector (2000 Dims)
                                                │
                                                ▼ [EmbeddingRepository.search_similar]
                                                │ Pgvector Cosine Search: (1 - (vector <=> q))
                                                │ Filter: user_id & status == 'COMPLETED'
                                                │
                                                ▼ Top K Matching Chunks (relevance >= 5%)
                                                │
                                                ▼ System Prompt Augmented with Doc Context
                                                │
                                         [OpenRouter LLM API] ──► Grounded Answer to User
```

---

## ⚡ Celery & Redis Infrastructure

- **Redis**: Acts as the cache store (DB 0), rate limit tracker, Celery message broker (DB 1), and Celery result backend (DB 2).
- **Celery Workers**: Process document text extraction, chunking, and embedding generation asynchronously without blocking FastAPI HTTP threads.

### Available Celery Tasks
1. `process_document_task`: Processes uploaded files into vector embeddings.
2. `cleanup_expired_sessions_task`: Periodic maintenance cleanup.
3. `simulate_heavy_rag_processing_task`: Test/benchmarking background job.

---

## 📊 Monitoring & Observability

### Prometheus Metrics (`GET /metrics`)
Metrics tracked include:
- `http_requests_total`: Total request counts grouped by method, endpoint, status.
- `http_request_duration_seconds`: Histogram of latency across API endpoints.
- `cache_hits_total` & `cache_misses_total`: Redis cache efficiency.
- `llm_calls_total` & `llm_response_time_seconds`: LLM provider metrics.

### System Health (`GET /health`)
Example Response:
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

---

## 🔌 API Documentation

### Authentication (`/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/signup` | ❌ | Register new account |
| `POST` | `/auth/login` | ❌ | Authenticate and return JWT tokens |
| `POST` | `/auth/refresh` | ❌ | Refresh expired access token |
| `POST` | `/auth/logout` | ✅ | Log out current session |
| `GET` | `/auth/me` | ✅ | Get user profile |
| `PUT` | `/auth/me` | ✅ | Update profile information |

### Chat (`/chat`, `/history`, `/reset`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/chat` | ✅ | Send message & receive document-grounded AI reply |
| `GET` | `/history` | ✅ | Fetch active session history |
| `POST` | `/reset` | ✅ | Clear current session messages |

### Document Management (`/documents`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/documents/upload` | ✅ | Upload document for background RAG processing |
| `GET` | `/documents` | ✅ | List user uploaded documents and status |
| `DELETE` | `/documents/{id}` | ✅ | Delete document & cascade delete embeddings |

### Sessions (`/sessions`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/sessions` | ✅ | List user chat sessions |
| `POST` | `/sessions` | ✅ | Create new chat session |
| `GET` | `/sessions/{id}` | ✅ | Get session details |
| `PUT` | `/sessions/{id}` | ✅ | Rename session |
| `DELETE` | `/sessions/{id}` | ✅ | Delete session and messages |
| `GET` | `/sessions/{id}/messages` | ✅ | Fetch all messages in a session |

### System & Health
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | ❌ | Component health status |
| `GET` | `/metrics` | ❌ | Prometheus metrics |

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites
- **Python 3.12+**
- **PostgreSQL 15+** (with `pgvector` extension installed)
- **Redis 7+**

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend.git
cd AIChatbotFastAPIBackend

python -m venv vir_env
source vir_env/bin/activate  # On Linux/macOS
# vir_env\Scripts\activate   # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database
```sql
CREATE DATABASE chatbot_db;
\c chatbot_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Configure Environment Variables
Copy `.env` and adjust your credentials:
```bash
cp .env .env.local
```

### 6. Apply Database Migrations
```bash
alembic upgrade head
```

---

## 🔑 Environment Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` | API Key for OpenRouter LLM & Embedding services |
| `MODEL_NAME` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Chat LLM model |
| `BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter base URL |
| `DATABASE_HOST` | `localhost` | PostgreSQL host |
| `DATABASE_PORT` | `5432` | PostgreSQL port |
| `DATABASE_NAME` | `chatbot_db` | Database name |
| `DATABASE_USER` | `postgres` | Database username |
| `DATABASE_PASSWORD` | `your_password` | Database password |
| `JWT_SECRET_KEY` | *(secret)* | Secret key for access token signing |
| `JWT_REFRESH_SECRET_KEY` | *(secret)* | Secret key for refresh token signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifespan in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan in days |
| `REDIS_HOST` | `localhost` | Redis server host |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_URL` | `redis://localhost:6379/0` | Primary Redis connection string |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery task broker URL |
| `CELERY_RESULT_BACKEND` | `redis://localhost:6379/2` | Celery task results store URL |
| `UPLOAD_DIRECTORY` | `./uploaded_files` | Directory where uploaded files reside |
| `EMBEDDING_MODEL` | `nvidia/nemotron-3-embed-1b:free` | Text embedding model |
| `VECTOR_DIMENSION` | `2000` | Matryoshka target dimension for pgvector HNSW index |
| `CHUNK_SIZE` | `1000` | Document chunking character size |
| `CHUNK_OVERLAP` | `200` | Character overlap between chunks |

---

## ▶ Running the Application

### Start Redis Server
```bash
redis-server
```

### Start Celery Background Worker
```bash
celery -A celery_app.celery worker --loglevel=info --concurrency=2
```

### Start FastAPI Application Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Chat Web Interface**: `http://127.0.0.1:8000`
- **Swagger Interactive API Docs**: `http://127.0.0.1:8000/docs`
- **Prometheus Metrics**: `http://127.0.0.1:8000/metrics`

---

## 🖼 Screenshots

| Interface | Preview |
|-----------|---------|
| **Authentication Screen** | *(Screenshot Placeholder: Login / Signup Form)* |
| **Main Chat Interface** | *(Screenshot Placeholder: Dark Mode Chat UI & Sidebar)* |
| **Document Upload & RAG** | *(Screenshot Placeholder: PDF Upload & Vector Ingestion)* |
| **Swagger API Documentation**| *(Screenshot Placeholder: OpenAPI /docs)* |

---

## 🔮 Future Roadmap

### Phase 6: Advanced Retrieval & Search Enhancements
- [ ] **Hybrid Search**: Combining Sparse BM25 text search with Dense `pgvector` embeddings.
- [ ] **Re-ranking**: Cross-encoder re-ranking for higher precision context scoring.
- [ ] **Source Citation**: Direct snippet highlighting and page number attribution in UI.
- [ ] **Framework Integration**: LangChain & LangGraph workflow orchestration options.

### Phase 7: AI Agents & Tool Calling
- [ ] **Multi-Agent Systems**: Task-specialized autonomous agents (Researcher, Coder, Writer).
- [ ] **MCP Integration**: Model Context Protocol client & server integration.
- [ ] **Voice Interface**: WebRTC real-time voice input and speech synthesis.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:
1. Fork the Repository.
2. Create a Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ by <strong>Vaibhav Sharma</strong>
</p>