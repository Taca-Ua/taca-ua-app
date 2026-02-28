"""
Internal API endpoints for Matches Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db_session
from .logger import logger
from .models import Comment, Lineup, Match, MatchParticipant

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot")
def get_snapshot(db: Session = Depends(get_db_session)):
    """
    Return complete snapshot of all matches data in read model format.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns matches, participants (without results), results (separate),
    lineups, and comments.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Returns:
        JSON object with all matches domain data formatted for read model:
        - matches: List of all matches
        - participants: List of match participants (without result data)
        - results: List of match results (score, position)
        - lineups: List of all match lineups
        - comments: List of all match comments
    """
    logger.info("snapshot_requested", service="matches")

    try:
        # Fetch all domain data
        matches = db.query(Match).all()
        participants = db.query(MatchParticipant).all()
        lineups = db.query(Lineup).all()
        comments = db.query(Comment).all()

        # Convert to dictionaries - transform domain model to read model format
        snapshot = {
            "matches": [
                {
                    "match_id": str(m.id),  # Read model uses match_id as PK
                    "tournament_id": str(m.tournament_id) if m.tournament_id else None,
                    "location": m.location,
                    "status": m.status.value if m.status else None,
                    "start_time": m.start_time.isoformat() if m.start_time else None,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "updated_at": m.updated_at.isoformat() if m.updated_at else None,
                    "deleted_at": None,  # Domain model doesn't track deletions
                }
                for m in matches
            ],
            # Participants in read model format (without result data)
            "participants": [
                {
                    "participant_id": str(p.id),  # Domain id becomes participant_id
                    "match_id": str(p.match_id),
                    "participant_type": (
                        p.participant_type.value if p.participant_type else None
                    ),
                    "participant_entity_id": (
                        str(p.team_id)
                        if p.team_id
                        else str(p.athlete_id) if p.athlete_id else None
                    ),
                    "added_at": None,  # Domain model doesn't track this
                    "removed_at": None,
                }
                for p in participants
            ],
            # Results as separate entities (extracted from participants)
            "results": [
                {
                    # id is auto-increment in read model, don't include it
                    "match_id": str(p.match_id),
                    "participant_id": str(p.id),  # Link to participant
                    "score": p.score,
                    "position": p.position,
                    "results_metadata": p.result_metadata,
                    "updated_at": None,  # Domain model doesn't track result updates separately
                }
                for p in participants
                if p.score is not None
                or p.position is not None  # Only create results if there's result data
            ],
            "lineups": [
                {
                    # id is auto-increment in read model, don't include it
                    "match_id": str(lineup.match_id),
                    "team_id": str(lineup.team_id),
                    "player_id": str(
                        lineup.player_id
                    ),  # Read model also uses player_id
                    "jersey_number": lineup.jersey_number,
                    "is_starter": lineup.is_starter,
                    "assigned_at": (
                        lineup.created_at.isoformat() if lineup.created_at else None
                    ),
                }
                for lineup in lineups
            ],
            "comments": [
                {
                    "comment_id": str(c.id),  # Read model uses comment_id as PK
                    "match_id": str(c.match_id),
                    "message": c.message,  # Read model also uses message
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "deleted_at": None,
                }
                for c in comments
            ],
        }

        logger.info(
            "snapshot_generated",
            service="matches",
            matches_count=len(matches),
            participants_count=len(participants),
            results_count=len(snapshot["results"]),
            lineups_count=len(lineups),
            comments_count=len(comments),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="matches", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "matches"}
