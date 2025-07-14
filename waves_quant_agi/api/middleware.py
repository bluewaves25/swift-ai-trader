### api/middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import logging

logger = logging.getLogger("prometheus")

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect metrics for Prometheus monitoring.
    Logs request duration, path, and status code.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"[METRIC] path={request.url.path} method={request.method} status_code={response.status_code} time_taken={process_time:.4f}s"
        )

        return response
