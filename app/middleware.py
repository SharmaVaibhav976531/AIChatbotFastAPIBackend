# app/middleware.py
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from utils.helpers import (
    generate_request_id, 
    request_id_var, 
    build_request_banner, 
    build_response_banner
)

logger = logging.getLogger(__name__)

class RequestLifecycleMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track the entire lifecycle of an HTTP request.
    Generates a Request ID, logs beautiful banners, and measures duration.
    """
    async def dispatch(self, request: Request, call_next):
        # 1. Generate and set Request ID in the ContextVar
        req_id = generate_request_id()
        token = request_id_var.set(req_id)
        
        try:
            # 2. Read Request Body (Streams can only be read once, so we must capture it here)
            body_bytes = await request.body()
            body_text = body_bytes.decode("utf-8") if body_bytes else ""
            
            # 3. Log the Request Banner
            client_ip = request.client.host if request.client else "unknown"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            banner_req = build_request_banner(
                req_id=req_id, method=request.method, path=request.url.path,
                client_ip=client_ip, body_text=body_text, timestamp=timestamp
            )
            logger.info(banner_req)
            
            # 4. CRITICAL: Re-attach the body to the request so FastAPI routes can read it
            async def receive():
                return {"type": "http.request", "body": body_bytes, "more_body": False}
            request._receive = receive
            
            # 5. Process the request and measure execution time
            start_time = time.time()
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # 6. Read the Response Body (Again, consuming the stream to log it)
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
                
            body_text_resp = response_body.decode("utf-8") if response_body else ""
            
            # 7. Log the Response Banner
            banner_resp = build_response_banner(
                req_id=req_id, status_code=response.status_code,
                duration_ms=duration_ms, body_text=body_text_resp
            )
            logger.info(banner_resp)
            
            # 8. Rebuild the response (Since we consumed the iterator, we must recreate it)
            new_response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            # Inject the Request ID into the HTTP headers (Great for frontend debugging!)
            new_response.headers["X-Request-ID"] = req_id
            
            return new_response
            
        finally:
            # 9. Clean up the ContextVar to prevent state leaking to concurrent requests
            request_id_var.reset(token)