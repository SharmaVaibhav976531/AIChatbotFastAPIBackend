from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from api.routes import router
from app.config import APP_NAME, APP_VERSION, DESCRIPTION
import logging
from utils.helpers import setup_logging

# Setup logging before anything else
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Event
    logger.info(f"Starting up {APP_NAME} v{APP_VERSION}...")
    yield
    # Shutdown Event
    logger.info("Shutting down application...")

app = FastAPI(
    title=APP_NAME,
    description=DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan
)

# Global Exception Handler for Pydantic Validation Errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )

# Register the API routes
app.include_router(router)