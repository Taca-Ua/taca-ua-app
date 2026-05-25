from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import Season


def get_active_season(db: Session) -> Season:
    """Helper function to get the active season"""
    active_season = (
        db.query(Season).filter(Season.finished_at == None).first()  # noqa: E711
    )  # noqa: E711
    if not active_season:
        raise HTTPException(status_code=404, detail="No active season found")
    return active_season
