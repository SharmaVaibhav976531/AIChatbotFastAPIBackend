# Enterprise FastAPI AI Assistant & Advanced RAG Engine

> **Production-Grade Conversational AI Platform with Multi-Tier Memory, Semantic Agent Planning, Capability-Validated Tool Routing, and Asynchronous RAG Pipeline**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![pgvector](https://img.shields.io/badge/pgvector-0.5.0-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Redis](https://img.shields.io/badge/Redis-8.0.1-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.6.3-37B24D?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.51-D71F00?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-1.18.5-6B46C1?style=for-the-badge&logo=python&logoColor=white)](https://alembic.sqlalchemy.org/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM%20Gateway-742774?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai/)
[![JWT Auth](https://img.shields.io/badge/JWT-Protected-000000?style=for-the-badge&logo=json-web-tokens&logoColor=white)](https://jwt.io/)
[![Swagger](https://img.shields.io/badge/Swagger-OpenAPI%203.0-85EA2D?style=for-the-badge&logo=swagger&logoColor=white)](http://127.0.0.1:8000/docs)

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [System Architecture](#-system-architecture)
5. [Project Workflow](#-project-workflow)
6. [Folder Structure](#-folder-structure)
7. [Installation Guide](#-installation-guide)
8. [Environment Variables](#-environment-variables)
9. [Database & Migrations](#-database--migrations)
10. [Authentication & Security](#-authentication--security)
11. [AI & RAG Pipeline](#-ai--rag-pipeline)
12. [Agentic Workflow & Tool Routing](#-agentic-workflow--tool-routing)
13. [Logging & Diagnostic System](#-logging--diagnostic-system)
14. [Redis & Caching Infrastructure](#-redis--caching-infrastructure)
15. [Asynchronous Celery Tasks](#-asynchronous-celery-tasks)
16. [API Documentation](#-api-documentation)
17. [Example Requests & Responses](#-example-requests--responses)
18. [Running & Testing](#-running--testing)
19. [Screenshots & UI Placeholders](#-screenshots--ui-placeholders)
20. [Error Handling](#-error-handling)
21. [Performance Optimization](#-performance-optimization)
22. [Design Patterns](#-design-patterns)
23. [Future Improvements](#-future-improvements)
24. [Contributing](#-contributing)
25. [License](#-license)
26. [Author](#-author)

---

## 📌 Project Overview

### What is this project?
The **Enterprise FastAPI AI Assistant** is a full-stack, production-grade conversational AI platform built with Python, FastAPI, PostgreSQL (`pgvector`), Celery, Redis, and OpenRouter LLM gateways. It combines multi-user JWT authentication, session-isolated document knowledge retrieval (RAG), and an intelligent, capability-validated AI Agent system.

### Why does it exist?
Standard LLMs lack real-time context and access to private user documents. Furthermore, basic keyword-matching agent implementations often route general natural language queries to specialized tools (like math calculators), leading to application errors. This system solves these problems by providing:
1. **Strict Multi-Tenant Isolation:** Complete document, chat, and vector separation per user and session.
2. **Semantic Agent Intelligence:** LLM-driven intent classification and multi-step task decomposition with `supports()` capability checks to prevent tool execution errors.
3. **Advanced Retrieval Techniques:** Modular RAG enhancements including Query Expansion, HyDE (Hypothetical Document Embeddings), Multi-Query, Parent-Child Hierarchies, and Context Reranking.
4. **Educational Telemetry:** A live formatted logging system that outputs execution trees, SQL queries, and tool execution rationale in real time.

### Real-World Use Cases
- **Document Analysis & Comparison:** Compare private uploaded resumes or whitepapers against real-time market trends via combined RAG + Web Search.
- **Enterprise Knowledge Base:** Session-scoped search over internal PDFs, DOCX, CSVs, and markdown files.
- **Data & Formula Processing:** Safe mathematical evaluation and sandboxed Python execution for analytical tasks.

---

## 🌟 Key Features

### 🔐 Authentication & Session Isolation
- **JWT Authentication:** Access and Refresh Tokens with secure `bcrypt` password hashing.
- **Multi-Session Isolation:** Complete separation of user sessions, document embeddings, and chat history.
- **Cache-Aside Profile Management:** User profiles cached via Redis for fast authentication checks.

### 📄 Document Ingestion & Asynchronous RAG
- **Multi-Format Extraction:** Loaders for `.pdf`, `.docx`, `.csv`, `.txt`, and `.md` files.
- **OCR Support:** Tesseract OCR integration (`pytesseract`, `pdfplumber`, `pypdfium2`) for scanned documents.
- **Asynchronous Processing:** Celery task workers handle heavy chunking, metadata extraction, and vector embedding generation in the background.
- **Vector Database:** PostgreSQL storing 768-dimensional dense vectors with `pgvector` HNSW indexes for cosine similarity search.

### 🤖 Intelligent AI Agent System
- **Semantic Planner (`PlannerAgent`):** LLM-based intent detection covering 24+ categories (`MATH`, `DOCUMENT_COMPARISON`, `LIVE_SEARCH`, `PYTHON_EXECUTION`, `CODE_GENERATION`, `GENERAL_AI`, etc.).
- **Multi-Step Execution:** Automatic step-by-step task decomposition for complex multi-resource requests.
- **Tool Capability Validation (`supports()`):** Every tool dry-runs validation before execution. Natural language queries are skipped gracefully by math and python tools without raising syntax exceptions.
- **Sandboxed Python REPL:** Isolated execution environment with prohibited AST modules (OS, subprocess, socket) for secure code execution.
- **Web Search Integration:** Real-time web queries using DuckDuckGo / Tavily providers.

### 🚀 Performance & Observability
- **Redis Multi-Tier Caching:** Caching layer for search results, vector embeddings, and session state.
- **Rate Limiting:** IP and User-scoped rate limits powered by `SlowAPI` and Redis.
- **Prometheus Metrics:** Native `/metrics` endpoint measuring HTTP request throughput and duration histograms.
- **Educational Logging:** Terminal execution tree banners, SQL audit logs, and diagnostic error reports.

---

## 🛠️ Technology Stack

| Category | Technology | Purpose | Version |
| :--- | :--- | :--- | :--- |
| **Language** | Python | Primary programming language | `3.12` |
| **Web Framework** | FastAPI | Async high-performance REST API | `0.139.0` |
| **ASGI Server** | Uvicorn | High-speed web server runner | `0.51.0` |
| **Database** | PostgreSQL | Relational database engine | `14+ / 15+` |
| **Vector Engine** | pgvector | Dense vector storage & HNSW similarity search | `0.5.0` |
| **ORM & Migrations** | SQLAlchemy & Alembic | Database abstraction & schema migrations | `2.0.51` / `1.18.5` |
| **Task Queue** | Celery | Asynchronous background task processing | `5.6.3` |
| **Cache & Broker** | Redis | In-memory caching & Celery message broker | `8.0.1` |
| **LLM Gateway** | OpenRouter / OpenAI SDK | Unified interface for LLM completions | `2.45.0` |
| **Text Processing** | LangChain Text Splitters | Recursive character document chunking | `1.1.2` |
| **OCR & Document Extraction** | PyTesseract, PDFPlumber, Docx | Text extraction from images and documents | `0.3.13` / `0.11.10` |
| **Security & Auth** | Passlib (bcrypt), PyJWT | Password hashing & JWT token handling | `1.7.4` / `3.4.0` |
| **Rate Limiting** | SlowAPI | Request throttling middleware | `0.1.10` |
| **Metrics** | Prometheus Client | Application monitoring metrics | `0.25.0` |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    Client["Client / Web UI (Static JS)"] -->|HTTP REST Requests| FastAPI["FastAPI Application"]
    FastAPI -->|Token Check| Auth["JWT Auth Middleware & Security"]
    FastAPI -->|Enforce Limits| Limiter["SlowAPI Rate Limiter"]
    
    subgraph Agent Framework
        FastAPI --> Planner["PlannerAgent (Semantic Intent & Multi-Step)"]
        Planner --> Router["ToolRouter"]
        Router -->|Capability Check| CalcTool["CalculatorTool (AST Validation)"]
        Router -->|Capability Check| PyTool["PythonREPLTool (Sandbox)"]
        Router -->|Capability Check| SearchTool["SearchTool (Web Search)"]
        Router -->|Capability Check| RAGTool["RAGBridgeTool"]
        Executor["ExecutorAgent"] -->|Runs Steps| Router
    end

    subgraph Memory & Context Layer
        FastAPI --> Memory["MemoryService (Multi-Tier Chat Memory)"]
        RAGTool --> Retrieval["RetrievalService"]
        Retrieval --> VectorSearch["VectorSearchService"]
    end

    subgraph Data & Storage Layer
        VectorSearch --> VectorRepo["EmbeddingRepository / VectorRepository"]
        VectorRepo --> Postgres[("PostgreSQL DB + pgvector")]
        FastAPI --> Repos["User / Session / Message Repositories"]
        Repos --> Postgres
        FastAPI --> RedisCache[("Redis Cache & Broker")]
        Limiter --> RedisCache
    end

    subgraph Async Background Tasks
        FastAPI -->|Dispatch Ingestion| Celery["Celery Worker"]
        Celery --> RedisCache
        Celery --> Loader["Loader & Chunking Service"]
        Loader --> EmbedSvc["EmbeddingService"]
        EmbedSvc -->|Save Chunks & Vectors| Postgres
    end

    subgraph External LLM API
        Executor --> OpenRouter["OpenRouter API Gateway"]
        FastAPI --> OpenRouter
    end
```

---

## 🔄 Project Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Client / User
    participant App as FastAPI App
    participant Auth as JWT Dependency
    participant Plan as Planner Agent
    participant Route as Tool Router
    participant Tool as Capability Tool (RAG/Search/Calc)
    participant LLM as OpenRouter LLM API
    participant DB as PostgreSQL / Redis

    User->>App: POST /chat (Prompt + Session ID)
    App->>Auth: Validate Bearer Access Token
    Auth-->>App: Authenticated User Context
    App->>DB: Persist User Message to DB
    App->>Plan: Analyze Query & Generate ExecutionPlan
    Plan-->>App: ExecutionPlan (Intent, Steps)
    
    loop For Each Step in Plan
        App->>Route: route_and_execute(step.tool_name, tool_input, intent)
        Route->>Tool: supports(tool_input, intent)
        alt Tool Supported
            Tool-->>Route: Execution Success Output
        else Tool Unsupported
            Tool-->>Route: Status: "skipped" (Graceful Skip)
        end
        Route-->>App: ToolExecutionResult
    end

    App->>DB: Retrieve Session Memory & RAG Context
    App->>LLM: Send System Prompt + History + Tool Outputs + Query
    LLM-->>App: Final AI Answer
    App->>DB: Persist Assistant Response to DB
    App-->>User: ChatResponse (Reply text + Model metadata)
```

---

## 📁 Folder Structure

```
Chatbot_Using_FastAPI_and_OpenRouterAPIKey/
├── agents/                       # Intelligent Agentic AI System
│   ├── executor.py               # Executes multi-step plans sequentially
│   ├── planner.py                # Semantic intent classifier & task decomposer
│   ├── tool_router.py            # Validates tool supports() & routes execution
│   ├── state/
│   │   └── agent_state.py        # LangGraph State Schema for agent nodes
│   └── tools/
│       ├── calculator_tool.py    # Math & financial AST evaluator with supports()
│       ├── python_repl_tool.py   # Sandboxed Python REPL execution environment
│       ├── search_tool.py        # Real-time DuckDuckGo web search adapter
│       └── rag_bridge_tool.py    # RAG document retrieval tool bridge
├── api/                          # FastAPI Endpoint Routers
│   ├── auth_routes.py            # User registration, login, refresh, logout
│   ├── document_routes.py        # Document upload, listing, and deletion
│   ├── rag_routes.py             # RAG debug, prompt, and reranking endpoints
│   ├── routes.py                 # Core /chat, /history, /reset, /health endpoints
│   ├── search_routes.py          # Vector search, chunk inspection, and retrieval
│   └── session_routes.py         # Chat session CRUD endpoints
├── app/                          # Application Configuration & Dependencies
│   ├── config.py                 # Application metadata constants
│   ├── dependencies.py           # Centralized FastAPI Dependency Injection (DI)
│   ├── main.py                   # FastAPI app instance, middleware & lifespan
│   └── middleware.py             # Custom request telemetry & execution tree logger
├── celery_app/                   # Asynchronous Background Processing
│   ├── celery.py                 # Celery worker initialization & Redis broker config
│   └── tasks.py                  # Ingestion pipeline tasks (Load -> Chunk -> Embed)
├── core/                         # Core Utilities & Settings
│   ├── limiter.py                # SlowAPI rate limiter configuration
│   ├── security.py               # Password hashing & JWT token utilities
│   └── settings.py               # Pydantic v2 BaseSettings configuration
├── database/                     # Database Access Layer
│   ├── base.py                   # SQLAlchemy Base declarative class
│   ├── session.py                # Engine initialization & SessionLocal factory
│   ├── models/                   # SQLAlchemy Database Models
│   │   ├── user.py               # User authentication model
│   │   ├── session.py            # Chat session model
│   │   ├── message.py            # Chat message history model
│   │   ├── document.py           # Uploaded document metadata model
│   │   ├── chunk.py              # Extracted text chunk model
│   │   ├── chunk_metadata.py     # Structural chunk metadata model
│   │   └── embedding.py          # pgvector embedding model (dim=768)
│   └── repositories/             # Repository Pattern Classes
│       ├── user_repository.py    # User DB operations
│       ├── session_repository.py # Chat session DB operations
│       ├── message_repository.py # Chat message DB operations
│       ├── document_repository.py# Document DB operations
│       ├── chunk_repository.py   # Chunk DB operations
│       ├── metadata_repository.py# Chunk metadata DB operations
│       ├── embedding_repository.py# Dense vector storage DB operations
│       └── vector_repository.py   # pgvector HNSW search queries
├── loaders/                      # Document Text Loaders
│   ├── base.py                   # Base document loader interface
│   ├── csv.py                    # CSV file parser loader
│   ├── docx.py                   # Word document loader
│   ├── markdown.py               # Markdown file loader
│   ├── pdf.py                    # PDF loader with PyPDFium2 & Tesseract OCR fallback
│   └── txt.py                    # Plain text loader
├── monitoring/                   # Observability & Metrics
│   └── metrics.py                # Prometheus HTTP counter & histogram metrics
├── redis_client/                 # Redis Infrastructure
│   └── client.py                 # Async/Sync Redis connection pool manager
├── schemas/                      # Pydantic Data Models (DTOs)
│   ├── agent.py                  # Agent plan, step, and tool result schemas
│   ├── auth.py                   # Auth requests and token response schemas
│   ├── request.py                # Chat and search payload request schemas
│   └── response.py               # Chat, history, and system response schemas
├── services/                     # Business Logic Services Layer
│   ├── auth_service.py           # Authentication business logic
│   ├── cache_service.py          # Redis cache helper service
│   ├── chatbot_service.py        # Main chat lifecycle orchestrator
│   ├── chunking_service.py       # Recursive text splitting logic
│   ├── citation_service.py       # Source attribution builder
│   ├── document_service.py       # Document management logic
│   ├── embedding_service.py      # Embedding generation service
│   ├── memory_service.py         # Multi-tiered chat session memory
│   ├── prompt_builder_service.py # Prompt assembly service
│   ├── rag_service.py            # Advanced RAG orchestrator service
│   ├── retrieval_service.py      # RAG context retrieval service
│   └── vector_search_service.py  # Cosine similarity vector search service
├── static/                       # Frontend Web UI Assets
│   ├── index.html                # Modern dark-mode Chat interface
│   ├── script.js                 # Vanilla JavaScript API client logic
│   └── style.css                 # Custom CSS design system & styling
├── storage/                      # File Storage Providers
│   ├── base.py                   # Abstract storage interface
│   └── local.py                  # Local disk storage implementation
├── utils/                        # Utilities & Logging
│   ├── educational_logger.py     # Terminal educational logging system
│   └── helpers.py                # Request ID ContextVar & terminal color helpers
├── alembic.ini                   # Alembic database migration config
├── migrations/                   # Database migration scripts
└── requirements.txt              # Production Python dependencies
```

---

## 📥 Installation Guide

### Prerequisites
- **Python:** `3.10` or higher (Tested on Python `3.12`)
- **PostgreSQL:** `14+` or `15+` with `pgvector` extension installed
- **Redis:** `6.x` or higher running locally or remotely
- **Tesseract OCR (Optional for PDF OCR):** `sudo apt install tesseract-ocr`

### Step 1: Clone Repository
```bash
git clone https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend.git
cd AIChatbotFastAPIBackend
```

### Step 2: Set Up Virtual Environment
```bash
python3 -m venv vir_env
source vir_env/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create Environment File
Copy the sample environment configuration file:
```bash
cp .env.example .env
```

### Step 5: Initialize PostgreSQL & Enable pgvector
Create a PostgreSQL database and enable the `vector` extension:
```sql
CREATE DATABASE chatbot_db;
\c chatbot_db;
CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 6: Run Database Migrations
Apply Alembic migrations to create tables and vector indexes:
```bash
alembic upgrade head
```

---

## ⚙️ Environment Variables

The application relies on `pydantic-settings` to parse configuration variables from `.env`:

| Variable | Description | Required | Default |
| :--- | :--- | :---: | :--- |
| `DATABASE_URL` | PostgreSQL connection string with `psycopg` driver | Yes | `postgresql+psycopg://postgres:postgres@localhost:5432/chatbot_db` |
| `REDIS_URL` | Redis connection URL | Yes | `redis://localhost:6379/0` |
| `OPENROUTER_API_KEY` | OpenRouter API Key for LLM completion calls | Yes | `sk-or-v1-...` |
| `SECRET_KEY` | Cryptographic secret key for signing JWT tokens | Yes | `super-secret-key-change-in-production` |
| `ALGORITHM` | JWT signing algorithm | No | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan in minutes | No | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan in days | No | `7` |
| `EMBEDDING_MODEL` | HuggingFace / OpenRouter embedding model | No | `thenlper/gte-base` |
| `EMBEDDING_DIMENSION` | Dimension of embedding vectors | No | `768` |
| `MODEL_NAME` | Primary LLM model for completion | No | `mistralai/mistral-7b-instruct:free` |
| `UPLOAD_DIRECTORY` | Disk folder for uploaded files | No | `./uploaded_files` |
| `ENABLE_PLANNER` | Enable AI Agent Planner & Tool Router | No | `true` |
| `ENABLE_MEMORY` | Enable Multi-Tier Chat Memory Service | No | `true` |
| `ENABLE_HYDE` | Enable Hypothetical Document Embeddings in RAG | No | `false` |
| `ENABLE_RERANKING` | Enable RAG Context Reranking | No | `false` |

---

## 💾 Database & Migrations

### Database Schema Architecture
The database layer uses SQLAlchemy 2.0 with PostgreSQL `pgvector`:
- **`users`**: Manages user accounts, email credentials, and hashed passwords (`bcrypt`).
- **`chat_sessions`**: Session records associated with a specific user ID.
- **`messages`**: Chat history entries (`user` / `assistant` role, model name, tokens).
- **`documents`**: Metadata for uploaded files (filename, hash, MIME type, upload status).
- **`chunks`**: Split text passages linked to parent documents.
- **`chunk_metadata`**: Page numbers, section headings, and extracted keywords per chunk.
- **`embeddings`**: 768-dimensional dense vector representations stored using `pgvector` with HNSW cosine index (`vector_cosine_ops`).

### Migration Workflow (Alembic)
Generate a new migration script:
```bash
alembic revision --autogenerate -m "Add new column"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback last migration:
```bash
alembic downgrade -1
```

---

## 🔒 Authentication & Security

1. **Password Encryption:** Uses `Passlib` with `bcrypt` salt hashing before saving to PostgreSQL.
2. **Dual-Token JWT Architecture:**
   - **Access Token:** Short-lived (30 min) bearer token used for endpoint authorization.
   - **Refresh Token:** Long-lived (7 days) token used to mint new access tokens without requiring re-login.
3. **Protected Route Access:** Endpoints require `Depends(get_current_active_user)` dependency injection to retrieve the authenticated user.
4. **Sandboxed Code Execution:** The `PythonREPLTool` blocks AST nodes referencing `os`, `sys`, `subprocess`, `socket`, `builtins`, or `eval` to prevent remote code execution vulnerabilities.

---

## 🧠 AI & RAG Pipeline

```
User Prompt ──► Request Sanitization ──► Multi-Tier Memory Retrieval
                                              │
                                              ▼
Context Synthesis ◄── Reranking ◄── Vector Search ◄── Embedding Generation
        │
        ▼
Advanced Prompt Construction ──► OpenRouter LLM ──► Persist Response ──► Client Output
```

1. **Document Upload & OCR:** Documents uploaded to `/documents/upload` undergo text extraction using format-specific loaders or Tesseract OCR.
2. **Chunking & Storage:** `ChunkingService` splits raw text into overlapping passages (e.g., 500 characters, 50-character overlap).
3. **Vector Generation:** `EmbeddingService` converts text chunks into 768-dimensional floating point vectors via HuggingFace or OpenRouter embedding endpoints.
4. **Similarity Search:** Cosine similarity vector search is executed via `EmbeddingRepository.search_similar_chunks()` querying the HNSW index.
5. **Context Reranking & Grounding:** Retrieved chunks are reranked, formatted into a strict grounding system prompt, and submitted to OpenRouter.

---

## 🤖 AI Agent Workflow & Tool Routing

The application incorporates a multi-step Agentic execution loop:

```
                          ┌────────────────────────┐
                          │    User Prompt Input   │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │      PlannerAgent      │
                          │ (Semantic Classifier)  │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │     ExecutionPlan      │
                          │ (Intent, Steps, Tools) │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │     ExecutorAgent      │
                          └───────────┬────────────┘
                                      │
                  ┌───────────────────┼───────────────────┐
                  ▼                   ▼                   ▼
          ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
          │CalculatorTool │   │  SearchTool   │   │ RAGBridgeTool │
          │(supports Check)   │(supports Check)   │(supports Check)
          └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
                  │                   │                   │
                  └───────────────────┼───────────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │ Tool Execution Results │
                          │ (Status: success/skip) │
                          └───────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │ OpenRouter LLM Answer  │
                          └────────────────────────┘
```

### Supported Agent Tools
1. **`CalculatorTool`**: Performs mathematical formula evaluations. Features AST parsing dry-runs via `supports()` to safely skip natural language queries without throwing exceptions.
2. **`PythonREPLTool`**: Executes raw Python snippets in an isolated scope. Validates syntax using `ast.parse()`.
3. **`SearchTool`**: Fetches real-time web news and facts using DuckDuckGo search adapters.
4. **`RAGBridgeTool`**: Queries internal user documents and vector store contexts.

---

## 📊 Logging & Diagnostic System

The project features a built-in **Educational Live-Backend Logging System** (`utils/educational_logger.py`). Terminal output displays formatted telemetry:

- **Architectural Banners:** Highlights file entry points and component responsibilities.
- **Function Entry/Exit Telemetry:** Logs parameters, latency in milliseconds, and exit status.
- **SQL Audit Logs:** Details repository database operations, executed SQL statements, row counts, and latency.
- **Execution Tree:** Renders an end-of-request visual execution tree showing only the components invoked during request processing.

---

## ⚡ Redis & Caching Infrastructure

Redis is utilized for caching and rate-limiting operations:
- **Search Result Cache:** Caches DuckDuckGo web search responses to minimize external API calls.
- **Embedding Cache:** Avoids re-computing vector embeddings for duplicate text passages.
- **Session & User Profile Cache:** Speeds up user authentication checks in `get_current_active_user`.
- **Celery Task Broker:** Serves as the message transport queue for background document processing workers.

---

## ⚙️ Asynchronous Celery Tasks

Heavy tasks are offloaded to background Celery workers:
- **`process_document_task`**: Orchestrates text extraction, cleaning, chunking, metadata extraction, embedding generation, and vector insertion.
- **`cleanup_expired_sessions_task`**: Scheduled maintenance task for purging expired session data.
- **`simulate_heavy_rag_processing_task`**: Routed to `heavy_queue` for isolated background processing.

Run Celery worker:
```bash
celery -A celery_app.celery worker --loglevel=info
```

---

## 📡 API Documentation

FastAPI automatically exposes interactive OpenAPI documentation:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### Core Endpoints Summary

| Category | Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- | :---: |
| **System** | `GET` | `/health` | Application health check & service status | No |
| **System** | `GET` | `/metrics` | Prometheus metrics endpoint | No |
| **Auth** | `POST` | `/auth/signup` | Register new user account | No |
| **Auth** | `POST` | `/auth/login` | Authenticate & receive OAuth2 tokens | No |
| **Auth** | `POST` | `/auth/refresh` | Mint new access token using refresh token | No |
| **Auth** | `POST` | `/auth/logout` | Revoke user authentication session | Yes |
| **Auth** | `GET` | `/auth/me` | Retrieve authenticated user profile | Yes |
| **Sessions** | `GET` | `/sessions` | List user chat sessions | Yes |
| **Sessions** | `POST` | `/sessions` | Create new chat session | Yes |
| **Sessions** | `GET` | `/sessions/{id}` | Retrieve specific session details | Yes |
| **Sessions** | `DELETE`| `/sessions/{id}` | Delete chat session & message history | Yes |
| **Chat** | `POST` | `/chat` | Submit message to AI Agent & receive reply | Yes |
| **Chat** | `GET` | `/history` | Retrieve conversation history | Yes |
| **Chat** | `POST` | `/reset` | Clear active session history | Yes |
| **Documents**| `POST` | `/documents/upload` | Upload document for async ingestion | Yes |
| **Documents**| `GET` | `/documents` | List uploaded user documents | Yes |
| **Documents**| `DELETE`| `/documents/{id}` | Delete document and associated chunks | Yes |
| **Search** | `POST` | `/search` | Trigger web search query | Yes |
| **Search** | `POST` | `/vector-search`| Execute direct pgvector similarity search | Yes |
| **Search** | `POST` | `/retrieve` | Retrieve grounded RAG context passages | Yes |
| **RAG Debug**| `POST` | `/rag/debug` | Inspect full RAG pipeline telemetry | Yes |

---

## 🧪 Example Requests & Responses

### 1. User Signup (`POST /auth/signup`)
```bash
curl -X POST "http://127.0.0.1:8000/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
       "username": "johndoe",
       "password": "SecurePassword123!"
     }'
```
**Response (201 Created):**
```json
{
  "id": "9f18b666-df89-47ae-bec2-c8699758af3a",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2026-07-20T02:00:00Z"
}
```

### 2. User Login (`POST /auth/login`)
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=johndoe&password=SecurePassword123!"
```
**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "d3b07384d113edec49eaa6238ad5ff00...",
  "token_type": "bearer"
}
```

### 3. Send AI Agent Chat Message (`POST /chat`)
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Calculate compound interest on $1000 at 5% for 2 years",
       "session_id": "c8699758-df89-47ae-bec2-c8699758af3a"
     }'
```
**Response (200 OK):**
```json
{
  "reply": "The compound interest on $1,000 at an annual interest rate of 5% compounded annually for 2 years is $102.50, bringing the total amount to $1,102.50.",
  "model": "mistralai/mistral-7b-instruct:free"
}
```

---

## 🏃 Running & Testing

### Running the FastAPI Development Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Access the static Web Interface at: `http://127.0.0.1:8000`

### Running the Celery Background Task Worker
```bash
celery -A celery_app.celery worker --loglevel=info
```

### Running Automated Test Suite
Examine agent planner and router capabilities:
```bash
python -c "
from agents.planner import PlannerAgent
from agents.tool_router import ToolRouter
from agents.executor import ExecutorAgent
import uuid

planner = PlannerAgent()
router = ToolRouter()
executor = ExecutorAgent(router)

plan = planner.create_plan('245*876')
results = executor.execute_plan(plan, user_id=uuid.uuid4())
print(results)
"
```

---

## 🖼️ Screenshots & UI Placeholders

| Authentication Interface | Interactive Chat Interface |
| :---: | :---: |
| ![Auth Interface](static/icons/login_mockup.png) <br> *JWT-secured login and user registration modal.* | ![Chat Interface](static/icons/chat_mockup.png) <br> *Session-scoped chat window with real-time response rendering.* |

| Document Ingestion | RAG Inspection Telemetry |
| :---: | :---: |
| ![Upload Workspace](static/icons/upload_mockup.png) <br> *Drag-and-drop document upload with ingestion status.* | ![RAG Telemetry](static/icons/rag_debug_mockup.png) <br> *Detailed vector similarity score & document citation viewer.* |

---

## ⚠️ Error Handling

The application uses standard HTTP status codes and structured Pydantic error responses:

- **`400 Bad Request`**: Validation failures or malformed query payloads.
- **`401 Unauthorized`**: Missing, expired, or invalid JWT bearer tokens.
- **`422 Unprocessable Entity`**: Pydantic schema validation failures.
- **`429 Too Many Requests`**: Rate limit exceeded (managed via `SlowAPI`).
- **`503 Service Unavailable`**: External service timeouts or database connection failures.

---

## 🔐 Security Best Practices

- **Zero Hardcoded Secrets:** All credentials loaded dynamically via `.env` and Pydantic Settings.
- **No Unsafe Code Evaluation:** Math expressions evaluated using constrained AST whitelists; Python REPL executes within an isolated, stripped global namespace.
- **Scoped User Access:** DB repositories filter all document and session queries by `user_id`.

---

## ⚡ Performance Optimization

- **HNSW Vector Indexing:** Employs `pgvector` Hierarchical Navigable Small World (`hnsw`) indexing for sub-millisecond similarity lookups over dense embeddings.
- **Connection Pooling:** SQLAlchemy `QueuePool` and Redis connection pools prevent connection creation overhead.
- **Async Execution:** Asynchronous request handling via `asyncio` and Uvicorn ASGI workers.

---

## 🧩 Design Patterns Applied

- **Repository Pattern:** Separates database access code (`database/repositories/`) from FastAPI route handlers.
- **Service Layer Pattern:** Encapsulates core domain business logic (`services/`) into reusable service classes.
- **Dependency Injection (DI):** Uses FastAPI `Depends()` for injecting services, database sessions, and authenticated user contexts.
- **Adapter Pattern:** Implemented in `RAGBridgeTool`, `CalculatorTool`, and `SearchTool` to standardize tool execution interfaces for `ToolRouter`.

---

## 🚀 Future Improvements Checklist

- [ ] Add Hybrid Search (combining BM25 keyword matching with dense `pgvector` embeddings).
- [ ] Implement Server-Sent Events (SSE) / WebSockets for streaming LLM responses.
- [ ] Add support for Multi-Agent Collaboration using LangGraph state machines.
- [ ] Implement automated RAG evaluation metrics using Ragas / TruLens framework.

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the Repository:** Create a personal fork of the project.
2. **Create a Feature Branch:** `git checkout -b feature/amazing-feature`
3. **Commit Changes:** `git commit -m "Add amazing feature"`
4. **Push to Branch:** `git push origin feature/amazing-feature`
5. **Open a Pull Request:** Submit a PR against the `main` branch with detailed explanations.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

**Vaibhav Sharma**
- **GitHub:** [@SharmaVaibhav976531](https://github.com/SharmaVaibhav976531)
- **Project Repository:** [AIChatbotFastAPIBackend](https://github.com/SharmaVaibhav976531/AIChatbotFastAPIBackend)
