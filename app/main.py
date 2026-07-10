from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from api.routes import router
from app.config import APP_NAME, APP_VERSION, DESCRIPTION
from utils.helpers import (
    setup_logging, request_id_var, generate_request_id,
    build_request_banner, build_response_banner,
    CYAN, GREEN, YELLOW, RED, MAGENTA, BOLD, DIM, RESET, WHITE
)
import logging
import time
from datetime import datetime

# Setup logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# APPLICATION LIFESPAN — Startup and shutdown events
# ══════════════════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{CYAN}{'═' * 60}{RESET}")
    logger.info(f"{GREEN}{BOLD}  [STARTUP] {APP_NAME} v{APP_VERSION}{RESET}")
    logger.info(f"{DIM}  {DESCRIPTION}{RESET}")
    logger.info(f"  {WHITE}Swagger UI{RESET} : {CYAN}http://127.0.0.1:8000/docs{RESET}")
    logger.info(f"  {WHITE}Chat UI{RESET}    : {CYAN}http://127.0.0.1:8000{RESET}")
    logger.info(f"{CYAN}{'═' * 60}{RESET}")
    yield
    logger.info(f"{YELLOW}{'═' * 60}{RESET}")
    logger.info(f"{YELLOW}{BOLD}  [SHUTDOWN] Application shutting down...{RESET}")
    logger.info(f"{YELLOW}{BOLD}  [SHUTDOWN] Cleanup complete. Goodbye!{RESET}")
    logger.info(f"{YELLOW}{'═' * 60}{RESET}")


app = FastAPI(
    title=APP_NAME,
    description=DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)


# ══════════════════════════════════════════════════════════════════
# HTTP MIDDLEWARE — Logs every request/response lifecycle
# ══════════════════════════════════════════════════════════════════
@app.middleware("http")
async def request_response_logging_middleware(request: Request, call_next):
    """
    Captures and logs the full request/response lifecycle:
    1. Generates a unique Request ID for tracing
    2. Logs FRONTEND → BACKEND banner (with request body)
    3. Processes the request through the application
    4. Captures the response body
    5. Logs BACKEND → FRONTEND banner (with response body)
    """
    # Generate unique request ID and set it in context for all downstream loggers
    req_id = generate_request_id()
    request_id_var.set(req_id)

    method = request.method
    path = request.url.path
    client_ip = request.client.host if request.client else "unknown"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()

    # Skip detailed logging for static file requests (CSS, JS, HTML, images)
    is_static = path.startswith("/static")

    if is_static:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        logger.debug(f"[STATIC] {method} {path} → {response.status_code} ({duration:.1f}ms)")
        return response

    # ── Read the request body for API endpoints ──
    body_text = ""
    if method in ("POST", "PUT", "PATCH"):
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8", errors="replace")

    # ── Log FRONTEND → BACKEND banner ──
    banner = build_request_banner(req_id, method, path, client_ip, body_text, timestamp)
    logger.info(banner)

    # ── Process the request ──
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    # ── Capture response body ──
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    response_text = response_body.decode("utf-8", errors="replace")

    # ── Log BACKEND → FRONTEND banner ──
    resp_banner = build_response_banner(req_id, response.status_code, duration_ms, response_text)
    if response.status_code >= 500:
        logger.error(resp_banner)
    elif response.status_code >= 400:
        logger.warning(resp_banner)
    else:
        logger.info(resp_banner)

    # ── Reconstruct and return the response ──
    # (We consumed the body_iterator above, so we must create a new Response)
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers={k: v for k, v in response.headers.items()
                 if k.lower() != "content-length"},
        media_type=response.media_type,
    )


# ══════════════════════════════════════════════════════════════════
# GLOBAL EXCEPTION HANDLER — Pydantic validation errors
# ══════════════════════════════════════════════════════════════════
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"{YELLOW}[VALIDATION ERROR] {request.method} {request.url.path}{RESET}")
    for err in exc.errors():
        field = err.get("loc", "?")
        msg = err.get("msg", "?")
        err_type = err.get("type", "?")
        logger.warning(f"  → Field: {field} | Type: {err_type} | {msg}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )


# ══════════════════════════════════════════════════════════════════
# ROUTE REGISTRATION & STATIC FILES
# ══════════════════════════════════════════════════════════════════
logger.info(f"[SETUP] Registering API routes from api.routes...")
app.include_router(router)
logger.info(f"[SETUP] ✅ Routes registered: /health, /chat, /reset, /history")

logger.info(f"[SETUP] Mounting static files at /static...")
app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info(f"[SETUP] ✅ Static files mounted (index.html, style.css, script.js)")


@app.get("/", include_in_schema=False)
async def root_redirect():
    logger.debug("[REDIRECT] / → /static/index.html")
    return RedirectResponse(url="/static/index.html")