# celery_app/celery.py
from celery import Celery
from core.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def make_celery() -> Celery:
    """
    Creates and configures the Celery application.
    Uses Redis as both the message broker and the result backend.
    """
    celery_app = Celery(
        "chatbot_worker",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["celery_app.tasks"] # We will create this in Phase 4.3
    )

    # Production-ready Celery configuration
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        
        # Retry strategy for transient failures
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=1,
        
        # Task routing (preparation for Phase 5 RAG heavy tasks)
        task_routes={
            "celery_app.tasks.heavy_processing.*": {"queue": "heavy_queue"},
            "celery_app.tasks.light_processing.*": {"queue": "light_queue"},
        },
        
        # Logging
        worker_hijack_root_logger=False,
        worker_log_format="%(asctime)s | %(levelname)s | %(processName)s | %(message)s",
        worker_task_log_format="%(asctime)s | %(levelname)s | %(processName)s | Task %(task_name)s[%(task_id)s]: %(message)s"
    )

    logger.info("[CELERY] ✅ Celery application configured successfully.")
    return celery_app

celery_app = make_celery()