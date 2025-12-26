"""
Database connection and session management for Tournaments Service.
"""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/taca_db",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    """
    Database session context manager.

    Usage:
        with get_db() as db:
            # use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session():
    """
    Get database session for FastAPI dependency injection.

    Usage:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db_session)):
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
