# services/health_service.py
import logging
from sqlalchemy import text
from database.session import engine
from redis_client.client import redis_manager
from celery_app.celery import celery_app

logger = logging.getLogger(__name__)

class HealthService:
    """
    Orchestrates health checks for all critical infrastructure components.
    Implements timeouts to prevent the /health endpoint from hanging.
    """
    
    def check_database(self) -> dict:
        """Check PostgreSQL connectivity."""
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            logger.error(f"[HEALTH] Database check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    def check_redis(self) -> dict:
        """Check Redis connectivity."""
        try:
            client = redis_manager.client
            if client and client.ping():
                return {"status": "healthy", "message": "Redis connection successful"}
            return {"status": "degraded", "message": "Redis client unavailable (Graceful Degradation Active)"}
        except Exception as e:
            logger.error(f"[HEALTH] Redis check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    def check_celery(self) -> dict:
        """Check if Celery workers are alive and responding."""
        try:
            # inspect().ping() sends a ping to all active workers and waits for a response
            inspect = celery_app.control.inspect(timeout=2.0)
            stats = inspect.ping()
            
            if stats:
                worker_count = len(stats)
                return {
                    "status": "healthy", 
                    "message": f"{worker_count} Celery worker(s) active",
                    "workers": list(stats.keys())
                }
            return {"status": "degraded", "message": "No Celery workers responding to ping"}
        except Exception as e:
            logger.error(f"[HEALTH] Celery check failed: {e}")
            return {"status": "unhealthy", "message": str(e)}

    def get_overall_health(self) -> dict:
        """
        Aggregates all health checks.
        Overall status is 'unhealthy' if any critical component (DB) is down.
        """
        db_health = self.check_database()
        redis_health = self.check_redis()
        celery_health = self.check_celery()

        # Determine overall status
        if db_health["status"] == "unhealthy":
            overall_status = "unhealthy"
        elif redis_health["status"] == "unhealthy" or celery_health["status"] == "unhealthy":
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "environment": "development", # Can be pulled from settings
            "components": {
                "database": db_health,
                "redis": redis_health,
                "celery": celery_health
            }
        }

health_service = HealthService()