from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.api.v1.ws import router as ws_router
from app.core.config import settings
from app.core.database import engine
from app.core.logging import logger, setup_logging
from app.models.base import Base
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting DevLens FastAPI Service", version=settings.VERSION)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.warning(f"Database table auto-creation notice: {e}")
    yield
    logger.info("Shutting down DevLens FastAPI Service")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handler - RFC 7807 Problem Details
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled Exception", path=request.url.path, error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://devlens.dev/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": request.url.path,
        },
    )

# Register Routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)
