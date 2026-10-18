
import hashlib
import os
from contextvars import ContextVar

import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from mcp.server.fastmcp import FastMCP, Context

EMAIL = "24f1001236@ds.study.iitm.ac.in"
challenge_header = ContextVar("exam_challenge", default=None)

mcp = FastMCP(
    "Exam Challenge",
    stateless_http=True,
)

class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = challenge_header.set(
            request.headers.get("x-exam-challenge")
        )
        try:
            return await call_next(request)
        finally:
            challenge_header.reset(token)

@mcp.tool()
async def solve_challenge(ctx: Context) -> str:
    """Solve the current exam challenge using the HTTP request header."""
    challenge = challenge_header.get()

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    return hashlib.sha256(
        f"{challenge}:{EMAIL}".encode("utf-8")
    ).hexdigest()[:16]

app = mcp.streamable_http_app()
app.add_middleware(HeaderMiddleware)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )
