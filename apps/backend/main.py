import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from core.app import VERSION, ApplicationCore
from core.config import Settings


def envelope(data=None, *, code=None, message=None):
    meta = {"request_id": f"req_{uuid.uuid4().hex}", "timestamp": datetime.now(UTC).isoformat()}
    if code:
        return {
            "ok": False,
            "error": {"code": code, "message": message, "details": {}},
            "meta": meta,
        }
    return {"ok": True, "data": data, "meta": meta}


def require_admin(request: Request):
    value = request.headers.get("authorization", "")
    if not value.startswith("Bearer ") or not request.app.state.core.credentials.permits_admin(
        value[7:]
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    core = ApplicationCore(settings)

    @asynccontextmanager
    async def lifespan(app):
        core.startup()
        try:
            yield
        finally:
            core.shutdown()

    app = FastAPI(
        title="LiveGame Studio",
        version=VERSION,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.core = core

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        messages = {
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not found",
            405: "Method not allowed",
        }
        return JSONResponse(
            envelope(
                code=f"HTTP_{exc.status_code}",
                message=messages.get(exc.status_code, "Request rejected"),
            ),
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request, exc):
        return JSONResponse(
            envelope(code="VALIDATION_ERROR", message="Invalid request"), status_code=422
        )

    @app.exception_handler(Exception)
    async def internal_error(request, exc):
        logging.getLogger("lgs").error("Unhandled request failure", exc_info=exc)
        return JSONResponse(
            envelope(code="INTERNAL_ERROR", message="Internal server error"), status_code=500
        )

    @app.middleware("http")
    async def restricted_origin(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin is not None and origin not in settings.allowed_origins:
            return JSONResponse(
                envelope(code="ORIGIN_DENIED", message="Forbidden origin"), status_code=403
            )
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["GET"],
        allow_headers=["Authorization"],
        allow_credentials=False,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @app.get("/api/v1/health")
    def health():
        return envelope(
            {
                "status": "running" if core.running else "starting",
                "version": VERSION,
                "db_smoke_ok": core.db_smoke_ok,
                "uptime_s": round(time.monotonic() - core.started_at, 3) if core.running else 0,
            }
        )

    # Development-only security smoke; not a production service or contract extension.
    if settings.environment == "development":

        @app.get("/dev/admin-ping", dependencies=[Depends(require_admin)])
        def admin_ping():
            return envelope({"status": "admin-boundary-ok"})

    return app
