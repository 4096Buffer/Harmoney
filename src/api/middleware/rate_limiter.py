# src/api/middleware/rate_limiter.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from time import time
from collections import defaultdict

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit=30):
        super().__init__(app)
        self.max_requests = requests_limit
        self.requests = defaultdict(list)

    async def dispatch(self, request, call_next):
        ip = request.client.host

        now = time()

        self.requests[ip] = [
            t for t in self.requests[ip] if now - t < 60
        ]

        if len(self.requests[ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"message": "Zbyt wiele zapytań. Spróbuj ponownie za chwilę.", "code": 0},
            )

        self.requests[ip].append(now)
        response = await call_next(request)
        
        return response