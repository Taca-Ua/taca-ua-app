"""
Database configuration for Public API.

This module provides database session management for read-only access
to the public_read schema containing materialized views.
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from taca_logging import get_logger

logger = get_logger("public-api.database")

# Database connection settings from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tacauser:tacapassword@postgres:5432/tacadb",
)

# For async operations (if needed in the future)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create synchronous engine for read-only access
engine = create_engine(
    DATABASE_URL,
    pool_size=30,
    max_overflow=50,
    pool_timeout=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/teams")
        def get_teams(db: Session = Depends(get_db)):
            return db.query(TeamDetailView).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("database_connection_check", status="success")
        return True
    except Exception as e:
        logger.error(
            "database_connection_check",
            status="failed",
            error=str(e),
        )
        return False


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.

    This is prepared for future async operations if needed.

    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )
    async_session_factory = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
