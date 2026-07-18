# 🤖 Nexus AI — Enterprise FastAPI RAG & Multi-User AI Chatbot Platform

A **production-grade, multi-user AI Chatbot and RAG (Retrieval-Augmented Generation) Platform** engineered with **FastAPI**, **PostgreSQL (`pgvector`)**, **Redis**, and **Celery**, powered by **OpenRouter AI Gateway** (NVIDIA Nemotron LLM & Embedding models).

Features an end-to-end multi-stage RAG document processing and vector search pipeline, intent detection grounding, token-budgeted context building, cross-encoder re-ranking, OAuth2 JWT authentication with auto-refresh tokens, multi-session chat isolation, Redis caching, Prometheus monitoring, rate limiting, and a modern, responsive, collapsible dark-mode Web UI.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.139-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-0.8.5-blue?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-8.0-DC382D?logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.6-37814A?logo=celery&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📑 Table of Contents

- [1. Project Title](#1-project-title)
- [2. Project Overview](#2-project-overview)
- [3. Features](#3-features)
- [4. Screenshots](#4-screenshots)
- [5. Technology Stack](#5-technology-stack)
- [6. Project Architecture](#6-project-architecture)
- [7. Project Folder Structure](#7-project-folder-structure)
- [8. Installation Guide](#8-installation-guide)
- [9. Environment Variables](#9-environment-variables)
- [10. Database & Vector Indexing](#10-database--vector-indexing)
- [11. Authentication & Security](#11-authentication--security)
- [12. Chat System](#12-chat-system)
- [13. Document Processing Pipeline](#13-document-processing-pipeline)
- [14. Retrieval Pipeline](#14-retrieval-pipeline)
- [15. AI & Prompt Pipeline](#15-ai--prompt-pipeline)
- [16. API Documentation](#16-api-documentation)
- [17. Structured Logging](#17-structured-logging)
- [18. Monitoring & Observability](#18-monitoring--observability)
- [19. Redis Integration](#19-redis-integration)
- [20. Celery Task Queue](#20-celery-task-queue)
- [21. Error Handling & Fallbacks](#21-error-handling--fallbacks)
- [22. Security Mechanisms](#22-security-mechanisms)
- [23. Configuration Management](#23-configuration-management)
- [24. Running the Project](#24-running-the-project)
- [25. Verification & Testing](#25-verification--testing)
- [26. Troubleshooting](#26-troubleshooting)
- [27. Performance Optimizations](#27-performance-optimizations)
- [28. Future Roadmap](#28-future-roadmap)
- [29. Contributing](#29-contributing)
- [30. License](#30-license)
- [31. Author](#31-author)

---

## 1. Project Title

**Nexus AI Chatbot Platform**  
*Enterprise-Grade Multi-User AI Assistant with Multi-Stage RAG Document Intelligence*

- **Version**: `1.0.0`
- **Status**: Production Ready (`Phase 7 RAG Completed`)

---

## 2. Project Overview

### What is this project?
Nexus AI is a high-performance, asynchronous Python AI Chatbot application built using FastAPI, PostgreSQL (`pgvector`), Redis, and Celery. It combines multi-user session management with advanced Retrieval-Augmented Generation (RAG) capabilities, allowing users to converse with an AI assistant grounded in their private uploaded documents.

### Why was it built?
Standard LLMs suffer from strict context window limitations, static knowledge cutoffs, and severe hallucinations when asked about private domain knowledge. Nexus AI solves this by integrating automated document ingestion, multi-format text extraction (PDF, Word, CSV, TXT, Markdown), vector embedding generation, pgvector similarity search, metadata re-ranking, and dynamic prompt injection.

### Real-World Use Cases
1. **Personal AI Resume / Career Portfolio**: Upload CVs and cover letters; allow hiring managers to ask detailed experience questions grounded directly in your resume.
2. **Legal & Contract Review**: Query contracts, policies, and legal documentation with exact source chunk attributions.
3. **Enterprise Knowledge Base**: Provide employees with instant document search and conversational Q&A isolated per user profile.

---

## 3. Features

### 🔐 Authentication & Security
- **OAuth2 JWT Authentication**: Short-lived Access Tokens (30 mins) and long-lived Refresh Tokens (7 days).
- **Bcrypt Hashing**: Password security using `passlib` with constant-time verification.
- **Strict User Isolation**: Data queries (sessions, messages, documents, embeddings) are scoped strictly to the authenticated user ID.
- **Rate Limiting**: Redis-backed SlowAPI throttling on auth and chat endpoints.

### 💬 Chat & Session Engine
- **Multi-Session Management**: Create, rename, search, and delete independent chat sessions.
- **Stateful History**: Persistent conversation history stored per session in PostgreSQL.
- **Native Non-Blocking UI**: Instant response rendering with typing indicators and smooth scrolling.

### 📄 Document Ingestion & Vector Processing
- **Multi-Format Loaders**: Ingestion support for `.pdf`, `.docx`, `.txt`, `.csv`, `.md` with OCR text extraction fallback.
- **Recursive Chunking**: Smart text splitting (e.g., 1000 characters with 200 character overlap).
- **Vector Embeddings**: High-dimensional embeddings via OpenRouter (`nomic-embed-text-v1.5` at 768 dimensions or `nemotron-3-embed-1b`).
- **HNSW Vector Indexing**: Cosine similarity search (`1 - (vector <=> query_vector)`) in PostgreSQL using `pgvector`.

### 🧠 Production RAG Pipeline (Phase 7)
- **Intent Grounding**: Automatic detection of query relevance to avoid unnecessary document retrieval on general greetings.
- **Metadata-Aware Re-ranking**: Score weighting based on similarity threshold, query keywords, and recency.
- **Token-Budgeted Context Builder**: Smart chunk concatenation respecting model token limits (default 3,000 tokens) with source citations (`[Doc: filename, Page N]`).
- **RAG Debug Endpoints**: API endpoints (`/rag/debug`, `/rag/context`, `/rag/prompt`, `/rag/rerank`) for deep pipeline inspection.

### 💻 Collapsible Responsive Web Interface
- **Collapsible Desktop Sidebar**: Smooth transitions between 280px expanded view and 68px icon-only mode with state persistence (`localStorage`).
- **Mobile & Tablet Drawer**: Slide-out drawer with backdrop overlay for mobile viewports.
- **Single Page Architecture**: Built with modular vanilla JavaScript ES modules and modern CSS design tokens.

---

## 4. Screenshots

| Interface | Preview |
|-----------|---------|
| **Login & Signup** | *(Placeholder: Dark Mode Auth Card)* |
| **Expanded Main Layout** | *(Placeholder: 3-Panel Chat View & Left Sidebar)* |
| **Collapsed Desktop Sidebar** | *(Placeholder: 68px Icon-Only Sidebar & Active Chat)* |
| **Knowledge Base Panel** | *(Placeholder: Document Upload & Retrieval Sources)* |
| **OpenAPI Documentation** | *(Placeholder: Swagger UI `/docs`)* |

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend Framework** | FastAPI | `0.139.0` | Asynchronous REST API server |
| **Programming Language** | Python | `3.12+` | Runtime environment |
| **Database** | PostgreSQL | `15.0+` | Primary relational database |
| **Vector Engine** | pgvector | `0.8.5` | Native vector similarity search extension |
| **ORM** | SQLAlchemy | `2.0.38` | Async SQL toolkit and ORM |
| **Database Migrations** | Alembic | `1.15.1` | Schema version control |
| **AI Gateway** | OpenRouter (OpenAI SDK) | `1.65.5` | Unified LLM & Embedding API access |
| **Embedding Models** | Nomic / Nemotron Embed | `v1.5` / `1b` | 768 / 2000-dimensional vector embeddings |
| **Primary LLM** | NVIDIA Nemotron 3 Ultra | `free` | Generative conversational model |
| **Caching & Broker** | Redis | `8.0` / `7.0+` | Cache-Aside storage and Celery message broker |
| **Task Queue** | Celery | `5.6.0` | Background document processing worker |
| **Authentication** | python-jose & passlib | `3.3.0` / `1.7.4` | JWT token handling and bcrypt password hashing |
| **Rate Limiting** | SlowAPI | `0.1.9` | Endpoint rate limiting |
| **Monitoring** | Prometheus Client | `0.21.1` | Metrics counter and histogram generation |
| **Frontend** | Vanilla JS / HTML5 / CSS3 | ES2022 | Responsive single-page application |

---

## 6. Project Architecture

### End-to-End System Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             FRONTEND (Single Page Application)                   │
│   static/index.html   ·   static/js/app.js   ·   static/css/main.css             │
│   Auth Forms  ·  Chat Canvas  ·  Collapsible Sidebar  ·  Knowledge Base Panel    │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ HTTP REST / Bearer JWT
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│                              FastAPI Gateway Server                              │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────────────┐  │
│  │ Auth Routes     │  │ Chat & RAG Routes│  │ Document & Session Routes       │  │
│  │ /auth/*         │  │ /chat, /rag/*    │  │ /documents, /sessions           │  │
│  └────────┬────────┘  └────────┬─────────┘  └────────────────┬────────────────┘  │
│           │                    │                             │                   │
│  ┌────────▼────────────────────▼─────────────────────────────▼────────────────┐  │
│  │                              SERVICE LAYER                                 │  │
│  │  AuthService  ·  ChatbotService  ·  RAGService  ·  RetrievalService        │  │
│  │  RerankingService  · ContextBuilderService  ·  GroundingService            │  │
│  │  DocumentService  ·  CacheService  ·  HealthService                       │  │
│  └────────┬────────────────────┬─────────────────────────────┬────────────────┘  │
│           │                    │                             │                   │
│  ┌────────▼────────┐  ┌────────▼─────────┐         ┌─────────▼────────────────┐  │
│  │ Data Repository │  │ OpenRouter AI   │         │ Redis & Celery           │  │
│  │ Layer (SQLAlchemy) │ API Gateway      │         │ Cache / Task Broker      │  │
│  └────────┬────────┘  └──────────────────┘         └──────────────────────────┘  │
│           │                                                                      │
│  ┌────────▼───────────────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database (pgvector HNSW Extension)                 │  │
│  │ users  ·  chat_sessions  ·  messages  ·  documents  ·  document_chunks  ·  │  │
│  │ chunk_metadata  ·  embeddings (Cosine Distance HNSW Index)                 │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Project Folder Structure

```
.
├── app/                          # Core application entry & wiring
│   ├── config.py                 # Application constants
│   ├── dependencies.py           # Dependency Injection Container
│   ├── main.py                   # FastAPI app factory & router registration
│   └── middleware.py             # Logging & Request ID tracking middleware
│
├── api/                          # HTTP Route Controllers
│   ├── auth_routes.py            # Signup, login, refresh, profile routes
│   ├── document_routes.py        # Document upload, list, and deletion routes
│   ├── rag_routes.py             # Phase 7 RAG debug and inspection endpoints
│   ├── routes.py                 # Chat, history, reset, health, metrics routes
│   └── session_routes.py         # Chat session CRUD and message endpoints
│
├── services/                     # Business Logic & Orchestration
│   ├── auth_service.py           # Authentication business logic
│   ├── cache_service.py          # Redis Caching service
│   ├── chatbot_service.py        # Core chat orchestration service
│   ├── chunking_service.py       # Text chunking logic
│   ├── context_builder_service.py# Token-budgeted context formatting
│   ├── document_service.py       # Document upload and state tracking
│   ├── embedding_service.py      # Embedding generation & dimension control
│   ├── grounding_service.py      # Query intent detection and grounding validation
│   ├── health_service.py         # Subsystem health verification
│   ├── jwt_service.py            # Token generation and verification
│   ├── loader_service.py         # Document loader routing
│   ├── metadata_service.py       # Chunk metadata extractor
│   ├── prompt_builder_service.py # Prompt template engineering
│   ├── rag_service.py            # End-to-end RAG pipeline orchestrator
│   ├── reranking_service.py      # Cross-encoder / score reranker
│   ├── retrieval_service.py      # Vector similarity search service
│   ├── session_service.py        # Session lifecycle management
│   ├── storage_service.py        # File storage abstraction
│   └── user_service.py           # User profile management
│
├── database/                     # Persistence Layer
│   ├── base.py                   # SQLAlchemy Base model
│   ├── session.py                # Database connection pool manager
│   ├── models/                   # ORM Models
│   │   ├── user.py               # User table
│   │   ├── session.py            # ChatSession table
│   │   ├── message.py            # Message table
│   │   ├── document.py           # Document table
│   │   ├── chunk.py              # DocumentChunk table
│   │   ├── chunk_metadata.py     # ChunkMetadata table
│   │   └── embedding.py          # Embedding vector table (pgvector)
│   └── repositories/             # Data Access Objects (DAOs)
│       ├── user_repository.py    # User queries
│       ├── session_repository.py # Session queries
│       ├── message_repository.py # Message queries
│       ├── document_repository.py# Document queries
│       ├── chunk_repository.py   # Chunk queries
│       └── embedding_repository.py# Cosine vector similarity search
│
├── loaders/                      # File Extractors
│   ├── base.py                   # Abstract Base Loader
│   ├── pdf.py                    # PDF Extractor with OCR fallback
│   ├── docx.py                   # Microsoft Word Extractor
│   ├── csv.py                    # CSV Table Extractor
│   ├── txt.py                    # Plain Text Extractor
│   └── markdown.py               # Markdown Extractor
│
├── storage/                      # File Storage Providers
│   ├── base.py                   # Storage interface
│   └── local.py                  # Local disk storage implementation
│
├── celery_app/                   # Background Task Queue
│   ├── celery.py                 # Celery app initialization
│   └── tasks.py                  # Background document processing tasks
│
├── schemas/                      # Pydantic Schemas
│   ├── auth.py                   # Auth requests & responses
│   ├── request.py                # Chat & search request payloads
│   ├── response.py               # Standardized API response wrappers
│   └── session.py                # Session payloads
│
├── core/                         # System Configuration
│   ├── settings.py               # Pydantic Settings reader (.env)
│   ├── security.py               # Password hashing helpers
│   └── limiter.py                # SlowAPI rate limiter
│
├── redis_client/                 # Redis Singleton
│   └── client.py                 # Async Redis connection wrapper
│
├── monitoring/                   # Observability
│   └── metrics.py                # Prometheus metric definitions
│
├── utils/                        # Utilities
│   └── helpers.py                # ANSI colorful logging system
│
├── static/                       # Frontend SPA Web Assets
│   ├── index.html                # HTML structure
│   ├── css/main.css              # Custom responsive CSS design system
│   └── js/                       # Modular ES JavaScript components
│       ├── api.js                # API Client with auto 401 refresh
│       ├── app.js                # Application bootstrapper
│       ├── chat.js               # Chat canvas & submit event handler
│       ├── ui.js                 # Toast notifications & theme manager
│       ├── retrieval_panel.js    # Context sources panel controller
│       └── retrieval_state.js    # Search state store
│
├── alembic/                      # Database Migration Scripts
├── .env                          # Local Environment Variables
├── alembic.ini                   # Alembic Config
├── requirements.txt              # Dependency file
└── README.md                     # Documentation
```

---

## 8. Installation Guide

### Step 1: Prerequisites
Ensure your machine has the following installed:
- **Python 3.12+**
- **PostgreSQL 15+** with `pgvector` extension
- **Redis 7+**

### Step 2: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend.git
cd AIChatbotFastAPIBackend

python -m venv vir_env
source vir_env/bin/activate  # Linux/macOS
# vir_env\Scripts\activate   # Windows
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Database Setup
Create the PostgreSQL database and activate the vector extension:
```sql
CREATE DATABASE chatbot_db;
\c chatbot_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 5: Configure Environment Variables
Copy `.env` and set your OpenRouter API Key and database credentials:
```bash
cp .env .env.example
```

### Step 6: Apply Database Migrations
```bash
alembic upgrade head
```

---

## 9. Environment Variables

| Variable | Type | Example Value | Description |
|----------|------|---------------|-------------|
| `OPENROUTER_API_KEY` | `string` | `sk-or-v1-xxxxxxxx...` | OpenRouter API Gateway Key |
| `MODEL_NAME` | `string` | `nvidia/nemotron-3-ultra-550b-a55b:free` | Chat Generation LLM |
| `EMBEDDING_MODEL` | `string` | `nomic-ai/nomic-embed-text-v1.5` | Vector Embedding Model |
| `BASE_URL` | `string` | `https://openrouter.ai/api/v1` | OpenRouter Base Endpoint |
| `DATABASE_HOST` | `string` | `localhost` | PostgreSQL Host |
| `DATABASE_PORT` | `integer` | `5432` | PostgreSQL Port |
| `DATABASE_NAME` | `string` | `chatbot_db` | Database Name |
| `DATABASE_USER` | `string` | `postgres` | Database Username |
| `DATABASE_PASSWORD` | `string` | `your_password` | Database Password |
| `JWT_SECRET_KEY` | `string` | `super-secret-key-32-chars` | Signing key for Access JWT |
| `JWT_REFRESH_SECRET_KEY` | `string` | `super-refresh-key-32-chars` | Signing key for Refresh JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `integer` | `30` | Access Token lifespan |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `integer` | `7` | Refresh Token lifespan |
| `REDIS_HOST` | `string` | `localhost` | Redis Server Host |
| `REDIS_PORT` | `integer` | `6379` | Redis Server Port |
| `REDIS_URL` | `string` | `redis://localhost:6379/0` | Cache Connection URL |
| `CELERY_BROKER_URL` | `string` | `redis://localhost:6379/1` | Celery Broker URL |
| `CELERY_RESULT_BACKEND` | `string` | `redis://localhost:6379/2` | Celery Results URL |
| `VECTOR_DIMENSION` | `integer` | `768` | Target pgvector Dimension |
| `TOP_K` | `integer` | `5` | Retrieved Document Chunks |
| `SIMILARITY_THRESHOLD` | `float` | `0.05` | Minimum Similarity Cutoff |

---

## 10. Database & Vector Indexing

The platform uses PostgreSQL with **pgvector**. The schema establishes clean 1:N relational chains with cascade deletions on document removal.

```
┌──────────────┐       1:N      ┌─────────────────┐       1:N      ┌──────────────┐
│    users     ├───────────────►│  chat_sessions  ├───────────────►│   messages   │
└──────┬───────┘                └─────────────────┘                └──────────────┘
       │
       │ 1:N                    ┌─────────────────┐       1:N      ┌──────────────┐
       └───────────────────────►│    documents    ├───────────────►│doc_chunks    │
                                └─────────────────┘                └──────┬───────┘
                                                                          │ 1:1
                                                                   ┌──────▼───────┐
                                                                   │  embeddings  │
                                                                   └──────────────┘
```

### pgvector Cosine Search SQL
```sql
SELECT c.id, c.content, 1 - (e.vector <=> :query_vector) AS similarity
FROM document_chunks c
JOIN embeddings e ON c.id = e.chunk_id
JOIN documents d ON c.document_id = d.id
WHERE d.user_id = :user_id AND d.status = 'COMPLETED'
ORDER BY e.vector <=> :query_vector ASC
LIMIT :top_k;
```

---

## 11. Authentication & Security

OAuth2 Bearer Token flow with dual JWTs:
1. **Access Token** (`POST /auth/login`): Standard Bearer token supplied in `Authorization: Bearer <token>` header for protected endpoints.
2. **Refresh Token** (`POST /auth/refresh`): Used seamlessly by `static/js/api.js` to renew access tokens without interrupting active chat sessions.

---

## 12. Chat System

- **Session Resolution**: `/chat` auto-creates or selects the user's active session if `session_id` is omitted.
- **Synchronous Persistence**: Both user prompt and generated AI reply are saved into PostgreSQL within transaction boundaries.
- **History Context**: Past turns are formatted and included in the LLM payload to enable seamless multi-turn conversations.

---

## 13. Document Processing Pipeline

```
[Upload File] ──► [Save to Local Storage] ──► [Trigger Celery Task]
                                                      │
 ┌────────────────────────────────────────────────────┘
 ▼
[Loader Service (PDF/Word/CSV)] ──► Text Extraction
 ▼
[Chunking Service] ──► Recursive Split (Size: 1000, Overlap: 200)
 ▼
[Embedding Service] ──► OpenRouter API (`nomic-embed-text-v1.5`)
 ▼
[Embedding Repository] ──► Store Vectors into PostgreSQL `embeddings`
```

---

## 14. Retrieval Pipeline

1. **Query Vectorization**: User message is converted to a 768-dim embedding vector via `EmbeddingService`.
2. **Similarity Search**: `EmbeddingRepository` runs pgvector Cosine distance search filtered by `user_id` and `status == 'COMPLETED'`.
3. **Re-Ranking**: `RerankingService` applies metadata weights and keyword matches to prioritize exact hits.
4. **Context Construction**: `ContextBuilderService` formats retrieved chunks into a token-budgeted prompt snippet.

---

## 15. AI & Prompt Pipeline

- **Grounding Validation**: `GroundingService` analyzes user message intent. If the prompt is conversational ("Hello", "Who are you?"), vector retrieval is bypassed to conserve API quota.
- **Prompt Assembly**: `PromptBuilderService` embeds retrieved document chunks, source citations, and session chat history into the system prompt.
- **Generative Reply**: `RAGService` calls OpenRouter LLM (`nvidia/nemotron-3-ultra-550b-a55b:free`) to synthesize a grounded response.

---

## 16. API Documentation

### Authentication Endpoints (`/auth`)
| Method | Endpoint | Auth | Request Body | Description |
|--------|----------|------|--------------|-------------|
| `POST` | `/auth/signup` | ❌ | `UserCreate` | Register a new user account |
| `POST` | `/auth/login` | ❌ | `OAuth2PasswordRequestForm` | Authenticate and get JWT tokens |
| `POST` | `/auth/refresh` | ❌ | `{ refresh_token }` | Get a new access token |
| `POST` | `/auth/logout` | ✅ | `None` | Invalidate current session |
| `GET` | `/auth/me` | ✅ | `None` | Get active user profile |

### Chat & RAG Endpoints (`/chat`, `/rag`)
| Method | Endpoint | Auth | Request Body | Description |
|--------|----------|------|--------------|-------------|
| `POST` | `/chat` | ✅ | `{ message, session_id }` | Send prompt & receive AI reply |
| `POST` | `/retrieve` | ✅ | `{ message }` | Run standalone vector retrieval |
| `GET` | `/rag/debug` | ✅ | `None` | RAG pipeline status check |
| `POST` | `/rag/context` | ✅ | `{ message }` | Inspect formatted RAG context |
| `POST` | `/rag/prompt` | ✅ | `{ message }` | Inspect compiled system prompt |

### Document Endpoints (`/documents`)
| Method | Endpoint | Auth | Request Body | Description |
|--------|----------|------|--------------|-------------|
| `POST` | `/documents/upload` | ✅ | `multipart/form-data` | Upload file for background indexing |
| `GET` | `/documents` | ✅ | `None` | List user documents and status |
| `DELETE` | `/documents/{id}` | ✅ | `None` | Delete document and embeddings |

---

## 17. Structured Logging

The application includes an ANSI colorful logging utility (`utils/helpers.py`) with `ContextVar` Request ID injection:
```
2026-07-19 00:01:25 | INFO | REQ-80f4e256 | GET /auth/me -> 200 OK (14.2ms)
2026-07-19 00:01:33 | INFO | REQ-3b83b5ed | POST /retrieve -> 200 OK (total_found: 3)
```

---

## 18. Monitoring & Observability

- **Metrics (`GET /metrics`)**: Exposes Prometheus counters and histograms for request duration, HTTP status codes, Redis cache hits/misses, and vector search latency.
- **Health Check (`GET /health`)**:
```json
{
  "status": "healthy",
  "components": {
    "database": { "status": "healthy" },
    "redis": { "status": "healthy" },
    "celery": { "status": "healthy" }
  }
}
```

---

## 19. Redis Integration

- **Cache DB 0**: Stores user profile and session metadata using the Cache-Aside pattern.
- **Celery Broker DB 1**: Queue broker for asynchronous background tasks.
- **Celery Results DB 2**: Task completion state store.
- **Rate Limiting**: Backs SlowAPI to track endpoint request frequencies.

---

## 20. Celery Task Queue

Background workers handle heavy document processing operations outside FastAPI's HTTP cycle.

### Starting Workers
```bash
celery -A celery_app.celery worker --loglevel=info --concurrency=2
```

---

## 21. Error Handling & Fallbacks

- **401 Unauthorized**: Handled automatically in `static/js/api.js` via refresh token exchange.
- **LLM Timeout / API Failure**: Catches `APITimeoutError` and returns HTTP 504 / 503 with user toasts.
- **Empty Retrieval**: Falls back gracefully to base LLM generation if no chunks pass the similarity threshold.

---

## 22. Security Mechanisms

- **Password Hashing**: Bcrypt algorithm with salt via `passlib`.
- **JWT Cryptographic Isolation**: Separate signing keys for Access (`JWT_SECRET_KEY`) and Refresh (`JWT_REFRESH_SECRET_KEY`) tokens.
- **Multi-Tenant Scoping**: All database queries enforce explicit `WHERE user_id = :user_id` filtering.

---

## 23. Configuration Management

Configuration is handled cleanly via Pydantic `BaseSettings` (`core/settings.py`), automatically validating types and reading values from `.env`.

---

## 24. Running the Project

### Development Execution Commands

1. **Start Redis Server**:
```bash
redis-server
```

2. **Start Celery Worker**:
```bash
celery -A celery_app.celery worker --loglevel=info --concurrency=2
```

3. **Start FastAPI Uvicorn Server**:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Access the application in your browser at `http://127.0.0.1:8000`.

---

## 25. Verification & Testing

### Test Script Execution
Run the integrated RAG pipeline verification script:
```bash
python -c "
import requests
r = requests.get('http://127.0.0.1:8000/health')
print('System Health Status:', r.status_code, r.json()['status'])
"
```

---

## 26. Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| `pgvector extension not found` | Extension missing in Postgres | Run `CREATE EXTENSION IF NOT EXISTS vector;` |
| `AttributeError: 'Settings' object has no attribute 'openrouter_model'` | Outdated variable access | Use `settings.model_name` and `settings.base_url` |
| `Page reloads on submit in Firefox` | Non-cancelable submit event | Ensure form uses `requestSubmit()` in `chat.js` |
| `Celery Connection Refused` | Redis server offline | Start Redis using `redis-server` |

---

## 27. Performance Optimizations

- **Vector HNSW Indexing**: Uses HNSW (`m=16, ef_construction=64`) for fast nearest neighbor searches.
- **CSS Containment**: Uses `contain: content` on `.messages-list` to minimize browser repaints during long streaming chats.
- **Connection Pooling**: SQLAlchemy async engine connection pooling with standard recycling timeouts.

---

## 28. Future Roadmap

- [x] **Phase 1-5**: Authentication, Sessions, Vector Storage, Celery Ingestion.
- [x] **Phase 6**: Vector Search & Retrieval Layer.
- [x] **Phase 7**: Production RAG Pipeline (Reranking, Grounding, Context Building).
- [ ] **Phase 8 (Planned)**: Sparse BM25 + Dense Hybrid Search.
- [ ] **Phase 9 (Planned)**: LangGraph Multi-Agent Workflows & Citation Highlighting.

---

## 29. Contributing

1. Fork the Repository.
2. Create your Feature Branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add NewFeature'`).
4. Push to the Branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

---

## 30. Author

**Vaibhav Sharma**  
- **GitHub**: [SharmaVaibhav976531](https://github.com/SharmaVaibhav976531)  
- **Project Repository**: [AIChatbotFastAPIBackend](https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend)  
- **Role**: Lead AI Backend & Systems Architect  

---

<p align="center">
  Crafted with ❤️ for scalable, enterprise-grade AI applications.
</p>