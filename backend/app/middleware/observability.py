"""
Observability and Telemetry Middleware.

Measures endpoint latency, attaches `X-Response-Time-Ms` header,
and logs slow queries/responses (>1500ms) for performance tracking.
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("Observability")
SLOW_REQUEST_THRESHOLD_MS = 1500.0


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        response: Response = await call_next(request)
        
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"
        
        # Log slow requests
        if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                f"Slow Request: {request.method} {request.url.path} "
                f"took {duration_ms:.2f}ms (status: {response.status_code})"
            )
            
        return response
