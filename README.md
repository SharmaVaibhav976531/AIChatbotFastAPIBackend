# Enterprise FastAPI AI Chatbot & Advanced RAG Engine

> **Version:** `1.0.0-phase9` | **Status:** `Production Ready & Advanced RAG Enabled`  
> A high-performance, modular, enterprise-grade AI Chatbot and Retrieval-Augmented Generation (RAG) platform built with FastAPI, PostgreSQL (`pgvector`), Celery, Redis, SQLAlchemy 2.0, OpenRouter LLM APIs, and a vanilla JavaScript frontend. Includes a real-time **Educational Live Live-Backend Logging System** that traces every request, dependency, repository call, and vector calculation like a live technical tutorial.

---

## 📌 1. Project Overview

### What is this project?
The **Enterprise FastAPI AI Chatbot** is a full-stack, production-grade conversational AI platform. It allows users to create multi-user accounts, manage persistent chat sessions, upload complex documents (PDF, DOCX, CSV, TXT, MD) with optical character recognition (OCR), and perform vector-similarity search across isolated document contexts using Retrieval-Augmented Generation (RAG).

### Why was it built?
1. **Context-Aware Conversational AI:** Standard LLMs lack knowledge of private or custom documents. This system bridges private documents with LLM inference while maintaining zero data leakages between users or chat sessions.
2. **Pedagogical Live Backend System:** Built with an **Educational Live-Backend Logging System** that turns terminal output into a step-by-step live technical tutorial for developers learning enterprise Python backend architecture.
3. **Asynchronous Scalability:** Heavy PDF parsing, OCR, text chunking, and vector embedding generation run as asynchronously dispatched tasks via Celery and Redis without blocking API response times.

### Target Users & Real-World Use Cases
- **Enterprise Staff & Researchers:** Query long internal policy manuals, contracts, financial reports, or technical whitepapers per project session.
- **Developers & Architecture Students:** Learn real-world FastAPI repository patterns, database session scoping, vector search algorithms (`pgvector`), and JWT token refresh mechanisms.

---

## 🌟 2. Feature Matrix

| Feature Category | Capability / Description | Status |
| :--- | :--- | :---: |
| **Authentication** | JWT Access & Refresh Tokens, bcrypt Hashing, Client-Side Logout | ✅ Completed |
| **User Profile** | Self-Profile Retrieval (`GET /auth/me`) & Updates (`PUT /auth/me`) with Redis Cache-Aside | ✅ Completed |
| **Chat Sessions** | Session Scoped Context, Multi-Session CRUD (`/sessions`), Title Renaming, History Retrieval | ✅ Completed |
| **Document Processing** | Asynchronous Uploads (`/documents/upload`), Celery Task Pipeline, Storage Abstraction | ✅ Completed |
| **OCR & Text Extraction** | Tesseract OCR (`pytesseract`), PDFium2, PDFPlumber, Docx, CSV, Text Loaders | ✅ Completed |
| **Chunking & Metadata** | Recursive Character Text Splitter (`ChunkingService`), Structured Metadata Extraction | ✅ Completed |
| **Vector Database** | PostgreSQL + `pgvector` HNSW Cosine Similarity Search (`EmbeddingRepository`) | ✅ Completed |
| **RAG Pipeline** | Context Assembly, Strict Grounding Prompts, Citation Attribution, OpenRouter Integration | ✅ Completed |
| **Advanced RAG** | Modular Flags: Query Expansion, HyDE, Multi-Query, Parent-Child Hierarchy, Context Compression | ✅ Completed |
| **Rate Limiting** | SlowAPI Rate Limiter backed by Redis (`20/min` Chat, `5/min` Login, `3/min` Signup) | ✅ Completed |
| **Monitoring** | Prometheus Custom Metrics (`/metrics` counting requests and latency histograms) | ✅ Completed |
| **Educational Logging** | Real-time Terminal Execution Trees, File Execution Banners, Function Intents, SQL Audits | ✅ Completed |
| **Admin Dashboard** | Superuser Authorization Dependencies (`get_admin_user`) | 🚧 Work In Progress |
| **Hybrid Search** | Combined BM25 Full-Text + Vector Dense Retrieval (`HYBRID_SEARCH_ENABLED=false`) | 🚧 Work In Progress |

---

## 🎨 3. User Interface Screenshots

Below are visual placeholders representing the user interface workflow:

| Login & Authentication | Workspace Chat & Sidebar |
| :---: | :---: |
| ![Login Mockup](static/icons/login_mockup.png) <br> *Sleek dark-mode login & registration with JWT auth.* | ![Chat Mockup](static/icons/chat_mockup.png) <br> *Session-scoped chat with expandable document retrieval drawer.* |

| Knowledge Base & Uploads | Advanced RAG Context Debugger |
| :---: | :---: |
| ![Upload Mockup](static/icons/upload_mockup.png) <br> *Asynchronous file drag-and-drop & OCR status indicators.* | ![RAG Debug Mockup](static/icons/rag_debug_mockup.png) <br> *Live telemetry for vector search score and citation inspection.* |

---

## 🛠️ 4. Technology Stack & Versions

### Backend & Core Frameworks
- **Python**: `3.10+`
- **FastAPI**: `0.139.0` (High-performance web API framework)
- **Uvicorn**: `0.51.0` (ASGI web server)
- **Starlette**: `1.3.1` (Core ASGI engine)
- **Pydantic / Pydantic Settings**: `2.13.4` / `2.14.2` (Schema validation & settings management)

### Database, ORM & Vectors
- **PostgreSQL**: `14+` / `15+` with `pgvector` extension `0.5.0`
- **SQLAlchemy**: `2.0.51` (Modern async/sync Python ORM)
- **Alembic**: `1.18.5` (Database schema migrations)
- **psycopg (v3)**: `3.3.4` (PostgreSQL driver)

### Asynchronous Queue & Caching
- **Redis**: `8.0.1` (In-memory cache & task broker)
- **Celery**: `5.6.3` (Asynchronous task queue worker)
- **SlowAPI**: `0.1.10` (Rate limiting middleware)

### AI, Machine Learning & Document Extraction
- **OpenAI Python SDK**: `2.45.0` (Connected via OpenRouter unified LLM API gateway)
- **LangChain Core & Text Splitters**: `1.4.9` / `1.1.2` (Recursive character text splitting)
- **PyTesseract / Pillow**: `0.3.13` / `12.3.0` (Optical Character Recognition)
- **PDFPlumber / PyPDFium2 / PDF2Image**: `0.11.10` / `5.12.1` / `1.17.0` (PDF processing)
- **Python-Docx**: `1.2.0` (Microsoft Word processing)

---

## 🏗️ 5. Architectural Diagram & Layers

```text
               ┌────────────────────────────────────────────────────────┐
               │              Browser / User Interface                  │
               │         (Vanilla JS + Async Fetch API)                 │
               └──────────────────────────┬─────────────────────────────┘
                                          │ HTTP REST Requests
                                          ▼
               ┌────────────────────────────────────────────────────────┐
               │                 FastAPI Application                    │
               │   • Request ID & Response Banners (utils/helpers.py)   │
               │   • EducationalLive Logger (utils/educational_logger)  │
               │   • SlowAPI Rate Limiting (core/limiter.py)            │
               └──────────────────────────┬─────────────────────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   ▼                                             ▼
     ┌──────────────────────────┐                  ┌──────────────────────────┐
     │   Authentication Guard   │                  │  Prometheus Metrics Middleware│
     │   (app/dependencies.py)  │                  │   (monitoring/metrics.py)│
     └─────────────┬────────────┘                  └──────────────────────────┘
                   │
                   ▼
     ┌────────────────────────────────────────────────────────────────────────┐
     │                          API Router Layer                              │
     │   /auth       → auth_routes.py    │   /documents → document_routes.py│
     │   /sessions   → session_routes.py │   /search    → search_routes.py  │
     │   /chat       → routes.py         │   /rag       → rag_routes.py     │
     └────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
     ┌────────────────────────────────────────────────────────────────────────┐
     │                         Service Layer                                  │
     │   • ChatbotService   • RAGService       • RetrievalService             │
     │   • AuthService      • DocumentService  • VectorSearchService          │
     └──────┬──────────────────────┬──────────────────────┬───────────────────┘
            │                      │                      │
            ▼                      ▼                      ▼
┌──────────────────────┐ ┌────────────────────┐ ┌─────────────────────────────┐
│  Repository Layer    │ │   Celery Broker    │ │    OpenRouter API Gateway   │
│ • UserRepository     │ │   (Redis Queue)    │ │ • Model Inference           │
│ • SessionRepository  │ └─────────┬──────────┘ │ • Text Vector Embeddings    │
│ • MessageRepository  │           │            └─────────────────────────────┘
│ • DocumentRepo       │           ▼
│ • EmbeddingRepo      │ ┌────────────────────┐
└───────────┬──────────┘ │ Celery Workers     │
            │            │ • Document OCR     │
            ▼            │ • Text Chunking    │
┌──────────────────────┐ │ • Vector Embeddings│
│ PostgreSQL + pgvector│ └────────────────────┘
│ (Isolated User &     │
│  Session Vectors)    │
└──────────────────────┘
```

---

## 📂 6. Repository Folder Structure & Responsibilities

```text
Chatbot_Using_FastAPI_and_OpenRouterAPIKey/
├── .env                              # Environment configuration & secret keys
├── .gitignore                        # Git exclusion rules
├── README.md                         # Project documentation
├── alembic.ini                       # Alembic migration configuration
├── requirements.txt                  # Python dependencies with exact versions
│
├── alembic/                          # Alembic Database Migration Scripts
│   ├── env.py                        # Migration environment & model target metadata
│   └── versions/                     # Migration version scripts (Tables, pgvector, etc.)
│
├── api/                              # HTTP API Endpoint Handlers (Routers)
│   ├── auth_routes.py                # Signup, Login, Refresh Token, User Profile
│   ├── document_routes.py            # Document Upload, Listing, and Deletion
│   ├── rag_routes.py                 # RAG Debug, Context Inspection, Prompt Builder
│   ├── routes.py                     # Primary Chat (/chat), Reset, and Health routes
│   ├── search_routes.py              # Vector similarity search & chunk inspection
│   └── session_routes.py             # Chat Session management & Message history
│
├── app/                              # Core Application Initialization
│   ├── config.py                     # Application metadata (Name, Version, Description)
│   ├── dependencies.py               # Dependency Injection Providers & Auth Guards
│   ├── main.py                       # FastAPI Instance, Lifespan, Middleware, Static Files
│   └── middleware.py                 # Custom Request/Response Logging Middleware
│
├── celery_app/                       # Background Asynchronous Task Processing
│   ├── celery.py                     # Celery Client Instance & Redis Broker Setup
│   └── tasks.py                      # Background Document Processing & Embedding Tasks
│
├── core/                             # System Core Utilities & Security
│   ├── limiter.py                    # SlowAPI Rate Limiter instance setup
│   ├── security.py                   # Password hashing (bcrypt) & verify functions
│   └── settings.py                   # Pydantic BaseSettings loading .env configuration
│
├── database/                         # Database Access Layer
│   ├── base.py                       # Declarative Base for SQLAlchemy Models
│   ├── session.py                    # SQLAlchemy Engine & SessionLocal Factory
│   ├── models/                       # SQLAlchemy Database Models
│   │   ├── user.py                   # User account schema & credentials
│   │   ├── session.py                # Chat session entity schema
│   │   ├── message.py                # Scoped chat message history entity
│   │   ├── document.py               # Uploaded document metadata entity
│   │   ├── chunk.py                  # Extracted text chunk entity (Parent-Child)
│   │   ├── chunk_metadata.py         # Key-value chunk metadata entity
│   │   └── embedding.py              # pgvector vector storage entity
│   └── repositories/                 # Data Access Object (DAO) Repository Classes
│       ├── user_repository.py        # Database queries for Users
│       ├── session_repository.py     # Database queries for Sessions
│       ├── message_repository.py     # Database queries for Messages
│       ├── document_repository.py    # Database queries for Documents
│       ├── embedding_repository.py   # pgvector cosine similarity search queries
│       ├── vector_repository.py      # Scoped Vector Data Access
│       └── search_repository.py      # Document chunk search queries
│
├── loaders/                          # Document Readers & Text Extractor Adapters
│   ├── base.py                       # BaseDocumentLoader abstract interface
│   ├── pdf.py                        # PDF Loader (PDFPlumber + Tesseract OCR fallback)
│   ├── docx.py                       # Microsoft Word (.docx) document loader
│   ├── csv.py                        # Structured CSV spreadsheet loader
│   ├── txt.py                        # Plain text loader
│   └── markdown.py                   # Markdown (.md) document loader
│
├── monitoring/                       # System Metrics & Observability
│   └── metrics.py                    # Prometheus Request Count & Latency Histograms
│
├── redis_client/                     # Caching & Rate Limiting Storage
│   └── client.py                     # Redis Connection Manager & Helper Functions
│
├── schemas/                          # Pydantic Schemas for DTO Validation
│   ├── auth.py                       # Auth Request/Response validation schemas
│   ├── document.py                   # Document DTO schemas
│   ├── rag.py                        # RAG Context, Citations & Telemetry schemas
│   ├── request.py                    # Chat Request schemas
│   ├── response.py                   # Chat Response schemas
│   ├── search.py                     # Vector Search schemas
│   └── session.py                    # Session DTO schemas
│
├── services/                         # Core Business Logic Layer
│   ├── auth_service.py               # User authentication & token creation logic
│   ├── chatbot_service.py            # Primary Chat orchestration & OpenRouter LLM call
│   ├── chunking_service.py           # Text splitting & chunking logic
│   ├── context_builder_service.py    # RAG context formatting service
│   ├── document_service.py           # Document saving & deletion business logic
│   ├── embedding_service.py          # Vector embedding generation via OpenRouter
│   ├── grounding_service.py          # Grounded prompt enforcement service
│   ├── health_service.py             # System component health checking
│   ├── jwt_service.py                # Access & Refresh JWT signing/verification
│   ├── loader_service.py             # File loader dispatcher service
│   ├── metadata_service.py           # Metadata extraction service
│   ├── prompt_builder_service.py     # System prompt formatting service
│   ├── rag_service.py                # Phase 7 & 8 Advanced RAG orchestration
│   ├── reranking_service.py          # Search result reranking service
│   ├── retrieval_service.py          # Document chunk retrieval bridge service
│   ├── session_service.py            # Chat session CRUD business logic
│   ├── storage_service.py            # Disk storage provider wrapper
│   ├── user_service.py               # User profile management & caching
│   └── vector_search_service.py      # High-level vector search orchestration
│
├── static/                           # Single-Page Web Frontend Interface
│   ├── index.html                    # Main HTML web application interface
│   ├── css/                          # Application styles (main.css)
│   └── js/                           # Modular Frontend Scripts (app.js, api.js, chat.js, documents.js)
│
├── storage/                          # Storage Backend System Providers
│   ├── base.py                       # BaseStorageProvider abstract class
│   └── local.py                      # Local filesystem storage provider implementation
│
├── uploaded_files/                   # Local file storage directory for uploads
└── utils/                            # Shared Helper Utilities & Logging
    ├── educational_logger.py         # Educational live-backend logging utility
    └── helpers.py                    # Request ID propagation & ANSI log formatting
```

---

## ⚡ 7. Environment Configuration Guide

Create a `.env` file in the root directory and configure the following parameters:

| Parameter | Purpose & Description | Example Value | Default |
| :--- | :--- | :--- | :--- |
| `OPENROUTER_API_KEY` | Secret API key for OpenRouter LLM Gateway | `sk-or-v1-xxxxxxxx...` | *Required* |
| `MODEL_NAME` | Primary LLM model for chat inference | `nvidia/nemotron-3-ultra-550b-a55b:free` | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| `BASE_URL` | OpenRouter API base URL | `https://openrouter.ai/api/v1` | `https://openrouter.ai/api/v1` |
| `DATABASE_HOST` | PostgreSQL Database hostname | `localhost` | `localhost` |
| `DATABASE_PORT` | PostgreSQL Database port | `5432` | `5432` |
| `DATABASE_NAME` | PostgreSQL Database name | `chatbot_db` | `chatbot_db` |
| `DATABASE_USER` | PostgreSQL Database username | `postgres` | `postgres` |
| `DATABASE_PASSWORD` | PostgreSQL Database password | `your_secure_password` | *Required* |
| `JWT_SECRET_KEY` | HMAC key for signing Access Tokens | `64-char-hex-string` | *Required* |
| `JWT_REFRESH_SECRET_KEY`| Separate HMAC key for Refresh Tokens | `64-char-hex-string` | *Required* |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan in minutes | `30` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan in days | `7` | `7` |
| `REDIS_HOST` | Redis Server hostname | `localhost` | `localhost` |
| `REDIS_PORT` | Redis Server port | `6379` | `6379` |
| `CELERY_BROKER_URL` | Redis URL for Celery Task Queue | `redis://localhost:6379/1` | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery Task Results | `redis://localhost:6379/2` | `redis://localhost:6379/2` |
| `UPLOAD_DIRECTORY` | Disk directory for uploaded files | `./uploaded_files` | `./uploaded_files` |
| `OCR_ENABLED` | Enable Tesseract OCR fallback | `true` | `true` |
| `CHUNK_SIZE` | Max characters per text chunk | `1000` | `1000` |
| `CHUNK_OVERLAP` | Character overlap between chunks | `200` | `200` |
| `EMBEDDING_MODEL` | Embedding model identifier | `nvidia/nemotron-3-embed-1b:free` | `nvidia/nemotron-3-embed-1b:free` |
| `VECTOR_DIMENSION` | Vector embedding dimension | `2000` | `2000` |
| `ENABLE_QUERY_EXPANSION` | Phase 8 Advanced RAG Flag | `true` | `true` |
| `ENABLE_HYDE` | Phase 8 Advanced RAG Flag | `true` | `true` |
| `ENABLE_MULTI_QUERY` | Phase 8 Advanced RAG Flag | `true` | `true` |
| `ENABLE_PARENT_CHILD` | Phase 8 Advanced RAG Flag | `true` | `true` |

---

## 🔐 8. Authentication & Multi-Tenant Isolation Flow

The application enforces security at both the network transport level and database query level:

```text
[Client Request] ──(Bearer Access JWT)──> [OAuth2 Security Scheme]
                                                    │
                                                    ▼
                                      [JWTService.verify_access_token()]
                                                    │
                                           Valid    │   Invalid
                                      ┌─────────────┴────────────┐
                                      ▼                          ▼
                          [UserRepository.get_by_id()]    [HTTP 401 Unauthorized]
                                      │
                                      ▼
                      [Set request.state.user = User]
                                      │
                                      ▼
                 [Database Operations Filtered By User ID & Session ID]
```

1. **Dual Token Security**: Short-lived access tokens (30 mins) prevent long exposure, while long-lived refresh tokens (7 days) allow seamless session renewals.
2. **Context Isolation**: Every document chunk and vector embedding in PostgreSQL is strictly bound to `user_id` and `session_id`. RAG vector queries apply mandatory relational filters:
   ```sql
   WHERE documents.user_id = :current_user_id 
     AND documents.session_id = :current_session_id 
     AND documents.status = 'COMPLETED'
   ```

---

## 📄 9. Async Document Processing & Vector Pipeline Flow

```text
Upload API ──> Disk Storage ──> DB Record ('PENDING') ──> Dispatch Celery Task
                                                                │
  ┌─────────────────────────────────────────────────────────────┘
  ▼
[Celery Background Worker]
  ├── 1. Loader Service (Extract text via PDFPlumber / Tesseract OCR)
  ├── 2. Chunking Service (Split text into 1000-char chunks with overlap)
  ├── 3. Metadata Service (Extract word count, headers, chunk index)
  ├── 4. Embedding Service (Generate 2000-dim vectors via OpenRouter)
  ├── 5. Database Save (Commit Chunks & Embeddings in Transaction)
  └── 6. Status Update (Set Document Status to 'COMPLETED')
```

---

## 🧠 10. RAG & Advanced RAG Architecture

When a user asks a question in a chat session, the system executes the multi-stage **Advanced RAG Pipeline**:

```text
           ┌──────────────────────────────────────────────┐
           │          User Prompt / Question              │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │           1. Query Expansion                 │
           │  (Generates query variations for broad capture)│
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        2. HyDE (Hypothetical Embeddings)     │
           │  (Generates hypothetical answer for search)  │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        3. Vector Search (pgvector)           │
           │ (Cosine similarity: 1 - distance <= threshold)│
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        4. Parent-Child Context Retrieval     │
           │  (Swaps small child chunk for full parent)   │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │       5. Grounded Prompt Assembly            │
           │  (Injects retrieved excerpts with sources)   │
           └──────────────────────┬───────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │        6. OpenRouter LLM Inference           │
           │      (Generates accurate grounded answer)    │
           └──────────────────────────────────────────────┘
```

---

## 📡 11. Core REST API Endpoints Reference

### 🔐 Authentication (`/auth`)
- `POST /auth/signup`: Register user (`SignupRequest` -> `SignupResponse`)
- `POST /auth/login`: Authenticate user (`LoginRequest` -> `TokenResponse`)
- `POST /auth/refresh`: Refresh access token (`RefreshTokenRequest` -> `TokenResponse`)
- `POST /auth/logout`: Invalidate client session (`MessageResponse`)
- `GET /auth/me`: Fetch authenticated user profile (Cache-Aside enabled)
- `PUT /auth/me`: Update profile details (`UpdateProfileRequest`)

### 💬 Chat & Sessions (`/chat`, `/sessions`)
- `POST /chat`: Submit prompt & receive AI response (`ChatRequest` -> `ChatResponse`)
- `POST /reset`: Reset active session history
- `GET /history`: Fetch message history for active session
- `GET /sessions`: List all user chat sessions (`SessionListResponse`)
- `POST /sessions`: Create a new session (`CreateSessionRequest` -> `SessionResponse`)
- `GET /sessions/{id}`: Retrieve specific session details
- `PUT /sessions/{id}`: Rename session title
- `DELETE /sessions/{id}`: Delete session & associated messages
- `GET /sessions/{id}/messages`: List all chronological messages in session

### 📄 Document & Search (`/documents`, `/search`, `/rag`)
- `POST /documents/upload`: Upload document with optional `session_id` form field
- `GET /documents`: List user documents (filtered by `session_id`)
- `DELETE /documents/{id}`: Delete document & underlying vector embeddings
- `POST /search`: Execute vector similarity search on document chunks
- `POST /rag/debug`: Inspect RAG execution pipeline, retrieved chunks & prompt

---

## ⚙️ 12. Complete Command Reference

This section outlines **every terminal command** used to set up, operate, and maintain the project.

### Environment & Dependency Setup

```bash
# 1. Create Python Virtual Environment
# Purpose: Isolates project dependencies from system Python packages.
python3 -m venv vir_env

# 2. Activate Virtual Environment
# Linux / macOS:
source vir_env/bin/activate
# Windows PowerShell:
# .\vir_env\Scripts\Activate.ps1

# 3. Upgrade Pip Package Manager
pip install --upgrade pip

# 4. Install Project Dependencies
pip install -r requirements.txt
```

### PostgreSQL Database & Vector Extensions

```bash
# 1. Access PostgreSQL CLI
psql -U postgres

# 2. Create Application Database (inside psql)
CREATE DATABASE chatbot_db;

# 3. Enable pgvector Extension (inside psql target DB)
\c chatbot_db
CREATE EXTENSION IF NOT EXISTS vector;
```

### Database Schema Migrations (Alembic)

```bash
# 1. Generate Automatic Migration Script
# Purpose: Compares SQLAlchemy models against current DB schema and generates a revision script.
alembic revision --autogenerate -m "add_parent_id_to_document_chunks"

# 2. Apply Migrations to Target Database
# Purpose: Upgrades database schema to the latest revision.
alembic upgrade head

# 3. Rollback Previous Migration
# Purpose: Reverts database schema by one revision step.
alembic downgrade -1
```

### Infrastructure Services (Redis, Celery, FastAPI)

```bash
# 1. Start Redis Server
redis-server

# 2. Verify Redis Health
redis-cli ping
# Expected Output: PONG

# 3. Start Celery Asynchronous Worker
# Purpose: Processes document text extraction, OCR, and vector embedding generation in background.
celery -A celery_app.celery worker --loglevel=info

# 4. Start FastAPI Application Server
# Purpose: Runs Uvicorn ASGI server with live reload for development.
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🚀 13. Step-by-Step Local Setup Walkthrough

Follow these steps to get the platform running locally:

```bash
# Step 1: Clone Repository
git clone https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend.git
cd AIChatbotFastAPIBackend

# Step 2: Initialize Virtual Environment & Dependencies
python3 -m venv vir_env
source vir_env/bin/activate
pip install -r requirements.txt

# Step 3: Configure Environment Variables
cp .env.example .env
# Open .env and fill in OPENROUTER_API_KEY and DATABASE_PASSWORD

# Step 4: Run Database Migrations
alembic upgrade head

# Step 5: Start Redis & Celery (In separate terminal windows)
redis-server
celery -A celery_app.celery worker --loglevel=info

# Step 6: Launch FastAPI Server
uvicorn app.main:app --reload

# Step 7: Access Web Applications
# • User Web UI   : http://127.0.0.1:8000
# • Interactive API Docs (Swagger): http://127.0.0.1:8000/docs
```

---

## 🔧 14. Troubleshooting & Common Issues

| Issue / Error | Cause | Recommended Solution |
| :--- | :--- | :--- |
| `NameError: name 'Vector' is not defined` | Missing import in Alembic script | Ensure `from pgvector.sqlalchemy import Vector` is present in migration files. |
| `400 Bad Request` during embedding generation | Dimension mismatch between model and DB | Confirm `EMBEDDING_MODEL` returns vector dimensions matching `VECTOR_DIMENSION` (e.g., 2000). |
| `RedisConnectionError: Error 111 connecting to localhost:6379` | Redis server not started | Run `redis-server` in terminal or check service status using `redis-cli ping`. |
| `413 Payload Too Large` on file upload | Upload size exceeds configured threshold | Increase `MAX_FILE_SIZE_MB` in `.env`. |
| `Celery Task Pending Indefinitely` | Celery worker not running | Ensure `celery -A celery_app.celery worker --loglevel=info` is active in background. |

---

## 🗺️ 15. Development Roadmap

- [x] **Phase 1-3**: Authentication, JWT tokens, Multi-Session Chat, PostgreSQL Repositories.
- [x] **Phase 4**: Redis Caching, SlowAPI Rate Limiting, Celery Async Worker Setup.
- [x] **Phase 5**: Document Processing Pipeline, Loaders (PDF, DOCX, CSV, TXT, MD), Tesseract OCR.
- [x] **Phase 6**: Vector Embeddings & `pgvector` Cosine Distance Similarity Search.
- [x] **Phase 7-8**: Advanced RAG (Query Expansion, HyDE, Multi-Query, Parent-Child, Citations).
- [x] **Phase 9**: Live Educational Live-Backend Logging Utility (`EducationalLogger`).
- [ ] **Phase 10**: Full-Text BM25 Hybrid Vector Search Integration.
- [ ] **Phase 11**: Administrative Telemetry Dashboard & Superuser Management UI.

---

## 📜 16. License & Author

### License
This project is licensed under the **MIT License** — feel free to use, modify, and distribute for educational or commercial purposes.

### Author
- **Name**: Vaibhav Sharma
- **GitHub**: [@SharmaVaibhav976531](https://github.com/SharmaVaibhav976531)
- **Repository**: [AIChatbotFastAPIBackend](https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend)
