from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            token = request.headers.get("x-csrf-token")
            if token != settings.csrf_token:
                return Response("Invalid CSRF token", status_code=403)
        return await call_next(request)
