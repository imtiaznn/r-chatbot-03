import time
import asyncio

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from db.events import insert_event

class EventTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000

        # Fire and forget
        asyncio.create_task(
            insert_event(
                # event_type="http",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
        )

        return response