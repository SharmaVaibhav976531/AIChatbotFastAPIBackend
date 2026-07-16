# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)

# 1. HTTP Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total number of HTTP requests", 
    ["method", "endpoint", "http_status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds", 
    "HTTP request duration in seconds", 
    ["method", "endpoint"]
)

# 2. Cache Metrics
CACHE_HIT_TOTAL = Counter("cache_hits_total", "Total number of cache hits")
CACHE_MISS_TOTAL = Counter("cache_misses_total", "Total number of cache misses")

# 3. AI/LLM Metrics
LLM_CALLS_TOTAL = Counter("llm_calls_total", "Total number of LLM API calls", ["model", "status"])
LLM_RESPONSE_TIME = Histogram("llm_response_time_seconds", "LLM API response time in seconds", ["model"])

# 4. System/Celery Metrics
CELERY_WORKERS_ACTIVE = Gauge("celery_workers_active", "Number of active Celery workers")
CELERY_TASKS_TOTAL = Counter("celery_tasks_total", "Total number of Celery tasks executed", ["task_name", "status"])

def get_metrics():
    """Returns the latest Prometheus metrics in the correct format."""
    return generate_latest()

def get_metrics_content_type():
    """Returns the correct Content-Type for Prometheus scraping."""
    return CONTENT_TYPE_LATEST