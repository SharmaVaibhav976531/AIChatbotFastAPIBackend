# app/config.py

import logging

logger = logging.getLogger(__name__)

APP_NAME = "AI Chatbot API"
APP_VERSION = "1.0.0"
DESCRIPTION = "A production-style FastAPI backend for an AI chatbot using OpenRouter."

logger.debug(f"[CONFIG] Constants loaded → name='{APP_NAME}', version='{APP_VERSION}'")