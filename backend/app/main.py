import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import settings
from app.db.db import engine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["Health"],
)
def root_health_check() -> dict[str, str]:
    """
    Root service status.

    Confirms that the API is running and that
    the PostgreSQL database is reachable.
    """

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return {
            "service": settings.APP_NAME,
            "version": "1.0.0",
            "status": "ok",
            "api": "healthy",
            "database": "connected",
            "docs": "/docs",
            "health": "/health",
            "database_health": "/health/db",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "service": settings.APP_NAME,
                "version": "1.0.0",
                "status": "degraded",
                "api": "healthy",
                "database": "unavailable",
            },
        )


# ---------------------------------------------------------
# Application Health
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["Health"],
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.APP_NAME,
    }


# ---------------------------------------------------------
# Database Health
# ---------------------------------------------------------

@app.get(
    "/health/db",
    tags=["Health"],
)
def database_health_check() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "ok",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
