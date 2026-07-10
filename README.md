# 🤖 AI Chatbot — Built with FastAPI & OpenRouter

A full-stack AI chatbot application with a **Python FastAPI backend** and a **vanilla HTML/CSS/JS frontend**. You type a message, it gets sent to an AI model (via [OpenRouter](https://openrouter.ai/)), and the AI's response appears in a chat-style interface — just like ChatGPT.

---

## 📸 What Does It Look Like?

When you run the app and open `http://127.0.0.1:8000` in your browser, you see:

- A **chat window** with a blue header saying "AI Assistant"
- A **text input** at the bottom where you type your message
- **User messages** appear as blue bubbles on the right
- **AI replies** appear as grey bubbles on the left
- A **🗑️ reset button** to clear the conversation
- **Bouncing dots** animation while the AI is thinking

---

## 🧠 How Does It Work? (The Big Picture)

Here is the complete flow of what happens when you send a message:

```
You type "Hello" and press Send
        │
        ▼
Frontend (script.js) sends a POST request to /chat
        │
        ▼
FastAPI backend (routes.py) receives the request
        │
        ▼
ChatbotService (chatbot_service.py) sends your message
to OpenRouter's API along with conversation history
        │
        ▼
OpenRouter forwards it to the AI model
(default: nvidia/nemotron-3-ultra-550b-a55b:free)
        │
        ▼
AI model generates a reply → comes back to your backend
        │
        ▼
Backend sends the reply as JSON → Frontend shows it as a chat bubble
```

The chatbot **remembers the conversation** — each new message is sent along with all previous messages so the AI understands context. The history is stored in memory (it resets when you restart the server).

---

## 📁 Project Structure — Every File Explained

```
.
├── app/                        # App setup and configuration
│   ├── __init__.py             # Makes this folder a Python package
│   ├── main.py                 # ⭐ Entry point — creates the FastAPI app
│   ├── config.py               # App name, version, description (constants)
│   └── dependencies.py         # Creates a single shared ChatbotService instance
│
├── api/                        # API layer — defines all URL endpoints
│   ├── __init__.py             # Makes this folder a Python package
│   └── routes.py               # ⭐ All API endpoints: /chat, /health, /history, /reset
│
├── services/                   # Business logic — talks to the AI
│   ├── __init__.py             # Makes this folder a Python package
│   └── chatbot_service.py      # ⭐ Core logic — sends messages to OpenRouter, stores history
│
├── schemas/                    # Data validation — what the API accepts and returns
│   ├── __init__.py             # Makes this folder a Python package
│   ├── request.py              # Validates incoming chat messages (1–4000 chars)
│   └── response.py             # Defines response shapes (ChatResponse, HealthResponse, etc.)
│
├── core/                       # Settings and configuration
│   ├── __init__.py             # Makes this folder a Python package
│   └── settings.py             # Loads environment variables from .env using Pydantic
│
├── utils/                      # Utility/helper functions
│   ├── __init__.py             # Makes this folder a Python package
│   └── helpers.py              # Sets up logging format and suppresses noisy libraries
│
├── static/                     # Frontend files (served by FastAPI)
│   ├── index.html              # ⭐ The chat UI webpage
│   ├── style.css               # All the styling (chat bubbles, animations, layout)
│   └── script.js               # ⭐ Frontend logic (send messages, show replies, load history)
│
├── .env                        # 🔑 Your API key and model settings (NEVER commit this!)
├── .gitignore                  # Files/folders Git should ignore
├── requirements.txt            # Python packages needed to run this project
└── README.md                   # This file
```

### What Does Each Key File Do?

| File | Purpose |
|------|---------|
| `app/main.py` | Creates the FastAPI app, sets up routes, serves static files, redirects `/` to the chat UI |
| `app/config.py` | Stores constants: app name (`"AI Chatbot API"`), version (`"1.0.0"`), description |
| `app/dependencies.py` | Creates **one shared instance** of `ChatbotService` so all requests share the same conversation |
| `api/routes.py` | Defines 4 endpoints: `GET /health`, `POST /chat`, `POST /reset`, `GET /history` — with full error handling |
| `services/chatbot_service.py` | The brain — uses OpenAI SDK to send messages to OpenRouter, keeps conversation history in a list |
| `schemas/request.py` | Validates that the user's message is between 1 and 4000 characters |
| `schemas/response.py` | Defines response models so the API always returns consistent JSON |
| `core/settings.py` | Loads your `.env` file and provides settings like API key, model name, temperature, etc. |
| `utils/helpers.py` | Configures logging (timestamps, log levels) and quiets noisy HTTP libraries |
| `static/index.html` | A simple chat interface with header, message area, and input form |
| `static/script.js` | Sends messages via `fetch()`, shows typing indicator, loads conversation history on page load |
| `static/style.css` | Styles for chat bubbles, animations (fade-in, bouncing dots), responsive layout |

---

## 🚀 Getting Started — Step by Step

### Prerequisites

Before you begin, make sure you have:

- **Python 3.10 or higher** installed ([Download Python](https://www.python.org/downloads/))
- **An OpenRouter API key** (free to create — [Get one here](https://openrouter.ai/keys))

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Chatbot_Using_FastAPI_and_OpenRouterAPIKey.git
cd Chatbot_Using_FastAPI_and_OpenRouterAPIKey
```

### Step 2 — Create a Virtual Environment

A virtual environment keeps this project's packages separate from your system Python.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows (Command Prompt)
venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

> **How do you know it's activated?** Your terminal prompt will change to show `(venv)` at the beginning.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, OpenAI SDK, Pydantic, and all other required packages.

### Step 4 — Set Up Your API Key

Create a file called `.env` in the project root directory:

```env
OPENROUTER_API_KEY=your_actual_api_key_here
MODEL_NAME=nvidia/nemotron-3-ultra-550b-a55b:free
BASE_URL=https://openrouter.ai/api/v1
TEMPERATURE=0.7
MAX_TOKENS=2048
TOP_P=0.9
FREQUENCY_PENALTY=0.2
```

> **⚠️ Important:** Replace `your_actual_api_key_here` with your real OpenRouter API key. The `.env` file is listed in `.gitignore`, so it will **never** be pushed to GitHub.

**What do these settings mean?**

| Variable | What It Does | Default Value |
|----------|-------------|---------------|
| `OPENROUTER_API_KEY` | Your secret key to access AI models via OpenRouter | *(required — no default)* |
| `MODEL_NAME` | Which AI model to use ([browse models](https://openrouter.ai/models)) | `nvidia/nemotron-3-ultra-550b-a55b:free` |
| `BASE_URL` | OpenRouter's API endpoint | `https://openrouter.ai/api/v1` |
| `TEMPERATURE` | Creativity level (0 = predictable, 1 = creative) | `0.7` |
| `MAX_TOKENS` | Maximum length of AI's response | `2048` |
| `TOP_P` | Controls diversity of word choices | `0.9` |
| `FREQUENCY_PENALTY` | Reduces repetition in responses | `0.2` |

### Step 5 — Start the Server

```bash
uvicorn app.main:app --reload
```

**What this command means:**
- `app.main` → Look in the `app/` folder, in the `main.py` file
- `:app` → Use the FastAPI instance named `app`
- `--reload` → Auto-restart when you edit code (for development only)

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Starting up AI Chatbot API v1.0.0...
```

### Step 6 — Open the Chatbot

Open your browser and go to:

```
http://127.0.0.1:8000
```

This automatically redirects you to the chat interface. Start typing and chatting with the AI! 🎉

---

## 📡 API Endpoints

The backend exposes 4 API endpoints. You can test them from the **Swagger UI** at `http://127.0.0.1:8000/docs` or use `cURL` / Postman.

### 1. Health Check

Check if the server is running.

```
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

---

### 2. Chat with the AI

Send a message and get a reply.

```
POST /chat
```

**Request Body:**
```json
{
  "message": "What is Python?"
}
```

**Response:**
```json
{
  "reply": "Python is a high-level, interpreted programming language known for its simplicity and readability...",
  "model": "nvidia/nemotron-3-ultra-550b-a55b:free"
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Explain FastAPI in one sentence."}'
```

**Possible Errors:**

| Status Code | Meaning |
|-------------|---------|
| `422` | Invalid request (empty message, too long, wrong format) |
| `500` | Invalid API key or unexpected server error |
| `502` | AI service returned an error |
| `503` | Cannot connect to AI service |
| `504` | AI service took too long to respond |

---

### 3. Get Conversation History

Retrieve all messages exchanged in the current session (user + AI messages, excludes the system prompt).

```
GET /history
```

**Response:**
```json
{
  "history": [
    { "role": "user", "content": "What is Python?" },
    { "role": "assistant", "content": "Python is a high-level programming language..." },
    { "role": "user", "content": "What about Java?" },
    { "role": "assistant", "content": "Java is a compiled, object-oriented language..." }
  ]
}
```

---

### 4. Reset Conversation

Clear all conversation history and start fresh.

```
POST /reset
```

**Response:**
```json
{
  "message": "Conversation history has been cleared."
}
```

---

## 🧪 Interactive API Docs (Swagger UI)

FastAPI auto-generates beautiful interactive docs. Once the server is running, open:

```
http://127.0.0.1:8000/docs
```

Here you can:
- See all available endpoints
- Try them out directly from the browser
- See request/response schemas
- Test without writing any code

---

## 🛠️ Tech Stack

| Technology | What It Does |
|-----------|--------------|
| [FastAPI](https://fastapi.tiangolo.com/) | Modern, fast Python web framework for building APIs |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server that runs the FastAPI app |
| [Pydantic](https://docs.pydantic.dev/) | Data validation — ensures API receives/returns correct data |
| [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Loads and validates environment variables from `.env` |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | Sends requests to the AI model (compatible with OpenRouter) |
| [OpenRouter](https://openrouter.ai/) | API gateway that gives access to 100+ AI models with one API key |
| HTML / CSS / JS | Frontend chat interface (no framework needed!) |

---

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
Your virtual environment is not activated. Run:
```bash
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows
```
Then try again.

### "Invalid AI service API key configuration"
Your `OPENROUTER_API_KEY` in the `.env` file is wrong or expired. Get a new key from [openrouter.ai/keys](https://openrouter.ai/keys).

### "Could not connect to the AI service"
Check your internet connection. OpenRouter requires an active internet connection.

### The server starts but the chat page is blank
Make sure the `static/` folder exists and contains `index.html`, `style.css`, and `script.js`.

### The AI gives a "No choices returned" response
The model might be temporarily unavailable. Try changing `MODEL_NAME` in your `.env` file to a different model from [openrouter.ai/models](https://openrouter.ai/models).

---

## 📝 Notes

- **Conversation memory is in-memory only** — restarting the server clears all chat history
- **The `.env` file is git-ignored** — your API key stays safe and private
- **The default model is free** — `nvidia/nemotron-3-ultra-550b-a55b:free` costs nothing on OpenRouter
- **The server runs on port 8000 by default** — you can change it with `--port`:
  ```bash
  uvicorn app.main:app --reload --port 3000
  ```

---

## 📄 License

This project is open source and available for learning and personal use.