# AI Chatbot FastAPI Backend

A production-style, scalable REST API backend for an AI chatbot, built with FastAPI and powered by OpenRouter. This project demonstrates clean architecture, dependency injection, and robust error handling.

## 📁 Project Structure
```text
├── app/                 # Application entry point and core setup
├── api/                 # HTTP routes and endpoints
├── services/            # Business logic (OpenRouter integration)
├── schemas/             # Pydantic models for request/response validation
├── core/                # Environment variables and settings
├── utils/               # Helper functions (logging, etc.)
├── .env                 # Environment variables (Not committed to Git)
└── requirements.txt     # Python dependencies
```

## 🚀 Installation & Setup

### 1. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add your OpenRouter API key:
```env
OPENROUTER_API_KEY=your_actual_api_key_here
MODEL_NAME=nvidia/nemotron-3-ultra-550b-a55b:free
BASE_URL=https://openrouter.ai/api/v1
TEMPERATURE=0.7
MAX_TOKENS=2048
TOP_P=0.9
FREQUENCY_PENALTY=0.2
```

## 🏃 Running the Server

Start the Uvicorn ASGI server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## 📡 API Endpoints

### 1. Health Check
- **GET** `/health`
- **Response**: `{"status": "healthy"}`

### 2. Chat with AI
- **POST** `/chat`
- **Body**: `{"message": "Hello!"}`
- **Response**: `{"reply": "Hello! How can I help?", "model": "..."}`

### 3. Get Conversation History
- **GET** `/history`
- **Response**: `{"history": [{"role": "user", "content": "..."}, ...]}`

### 4. Reset Conversation
- **POST** `/reset`
- **Response**: `{"message": "Conversation history has been cleared."}`

## 🧪 Testing

### Interactive Documentation (Swagger UI)
Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test the APIs directly in your browser.

### Using cURL
```bash
curl -X POST http://127.0.0.1:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Explain FastAPI in one sentence."}'
```

## 🛠️ Tech Stack
- **FastAPI**: Modern web framework
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation and settings management
- **OpenAI SDK**: Interfacing with OpenRouter