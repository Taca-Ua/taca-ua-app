"""
Internal API endpoints for Matches Service.

This module provides internal-only endpoints for:
- Snapshot data for read model rebuilds
- Health checks
- Administrative operations

These endpoints should NOT be exposed via API Gateway.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from taca_snapshots.matches import (
    MatchCommentSnapshotItem,
    MatchesSnapshotResponse,
    MatchLineupSnapshotItem,
    MatchParticipantSnapshotItem,
    MatchResultSnapshotItem,
    MatchSnapshotItem,
)

from .database import get_db_session
from .logger import logger
from .models import Comment, Lineup, Match, MatchParticipant

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/snapshot", response_model=MatchesSnapshotResponse)
def get_snapshot(
    db: Session = Depends(get_db_session),
    limit: int = Query(
        default=10000,
        ge=1,
        le=50000,
        description="Maximum number of records to return per collection",
    ),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
):
    """
    Return complete snapshot of all matches data in read model format.

    This endpoint is used by the Read Model Updater to rebuild projections.
    Returns matches, participants (without results), results (separate),
    lineups, and comments as strongly typed DTOs.

    **IMPORTANT**: This endpoint should be internal-only and NOT exposed
    via API Gateway. Only accessible within Docker network.

    Query Parameters:
        limit: Maximum number of records returned per collection (default 10000).
        offset: Number of records to skip (default 0).

    Returns:
        MatchesSnapshotResponse with all matches domain data formatted for read model.
    """
    logger.info("snapshot_requested", service="matches", limit=limit, offset=offset)

    try:
        # Fetch domain data with pagination applied to the primary collection
        matches = db.query(Match).offset(offset).limit(limit).all()
        participants = db.query(MatchParticipant).offset(offset).limit(limit).all()
        lineups = db.query(Lineup).offset(offset).limit(limit).all()
        comments = db.query(Comment).offset(offset).limit(limit).all()

        # Build typed DTOs — transform domain model to read model format
        match_dtos = [
            MatchSnapshotItem(
                match_id=str(m.id),
                tournament_id=str(m.tournament_id) if m.tournament_id else None,
                location=m.location,
                status=m.status.value if m.status else None,
                start_time=m.start_time,
                created_at=m.created_at,
                updated_at=m.updated_at,
                deleted_at=None,  # Domain model doesn't track deletions
            )
            for m in matches
        ]

        # Participants in read model format (without result data)
        participant_dtos = [
            MatchParticipantSnapshotItem(
                participant_id=str(p.id),
                match_id=str(p.match_id),
                participant_type=(
                    p.participant_type.value if p.participant_type else None
                ),
                participant_entity_id=(
                    str(p.team_id)
                    if p.team_id
                    else str(p.athlete_id) if p.athlete_id else None
                ),
                added_at=None,  # Domain model doesn't track this
                removed_at=None,
            )
            for p in participants
        ]

        # Results as separate entities (extracted from participants)
        result_dtos = [
            MatchResultSnapshotItem(
                match_id=str(p.match_id),
                participant_id=str(p.id),
                score=p.score,
                position=p.position,
                results_metadata=p.result_metadata,
                updated_at=None,  # Domain model doesn't track result updates separately
            )
            for p in participants
            if p.score is not None or p.position is not None
        ]

        lineup_dtos = [
            MatchLineupSnapshotItem(
                match_id=str(lineup.match_id),
                team_id=str(lineup.team_id),
                player_id=str(lineup.player_id),
                jersey_number=lineup.jersey_number,
                is_starter=lineup.is_starter,
                assigned_at=lineup.created_at,
            )
            for lineup in lineups
        ]

        comment_dtos = [
            MatchCommentSnapshotItem(
                comment_id=str(c.id),
                match_id=str(c.match_id),
                message=c.message,
                created_at=c.created_at,
                deleted_at=None,
            )
            for c in comments
        ]

        snapshot = MatchesSnapshotResponse(
            matches=match_dtos,
            participants=participant_dtos,
            results=result_dtos,
            lineups=lineup_dtos,
            comments=comment_dtos,
        )

        logger.info(
            "snapshot_generated",
            service="matches",
            matches_count=len(match_dtos),
            participants_count=len(participant_dtos),
            results_count=len(result_dtos),
            lineups_count=len(lineup_dtos),
            comments_count=len(comment_dtos),
        )

        return snapshot

    except Exception as e:
        logger.error("snapshot_generation_failed", service="matches", error=str(e))
        raise


@router.get("/health")
def health_check():
    """Internal health check endpoint."""
    return {"status": "healthy", "service": "matches"}
