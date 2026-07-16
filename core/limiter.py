# core/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.settings import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address, # Default to IP-based limiting
    storage_uri=settings.redis_url,
    storage_options={"socket_connect_timeout": 2, "socket_timeout": 2}
)
