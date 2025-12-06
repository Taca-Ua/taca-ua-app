"""
API routes for Matches Service.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from . import schemas
from .database import get_db_session
from .events import (
    publish_match_cancelled,
    publish_match_created,
    publish_match_finished,
    publish_match_updated,
)
from .models import Comment, Lineup, Match, MatchStatus

router = APIRouter()


@router.post("/matches", response_model=schemas.MatchResponse, status_code=201)
def create_match(
    match_data: schemas.MatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Create a new match."""
    # TODO: Verify teams belong to tournament
    # TODO: Check for schedule conflicts

    match = Match(
        tournament_id=match_data.tournament_id,
        team_home_id=match_data.team_home_id,
        team_away_id=match_data.team_away_id,
        location=match_data.location,
        start_time=match_data.start_time,
        created_by=match_data.created_by,
        status=MatchStatus.SCHEDULED,
    )

    db.add(match)
    db.commit()
    db.refresh(match)

    background_tasks.add_task(publish_match_created, match)
    return match


@router.put("/matches/{match_id}", response_model=schemas.MatchResponse)
def update_match(
    match_id: UUID,
    match_data: schemas.MatchUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Update a match."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        raise HTTPException(
            status_code=409,
            detail="Cannot update a finished match",
        )

    if match_data.location is not None:
        match.location = match_data.location
    if match_data.start_time is not None:
        match.start_time = match_data.start_time
    if match_data.team_home_id is not None:
        match.team_home_id = match_data.team_home_id
    if match_data.team_away_id is not None:
        match.team_away_id = match_data.team_away_id

    match.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    background_tasks.add_task(publish_match_updated, match, "Match details updated")
    return match


@router.post("/matches/{match_id}/result")
def register_result(
    match_id: UUID,
    result_data: schemas.MatchResult,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Register result for a match."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        raise HTTPException(status_code=409, detail="Match already finished")

    match.home_score = result_data.home_score
    match.away_score = result_data.away_score
    match.additional_details = result_data.additional_details
    match.status = MatchStatus.FINISHED
    match.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    background_tasks.add_task(publish_match_finished, match)

    return match


@router.post("/matches/{match_id}/lineup")
def assign_lineup(
    match_id: UUID,
    lineup_data: schemas.MatchLineup,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Assign lineup for a team in a match."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        raise HTTPException(
            status_code=409, detail="Cannot modify lineup for finished match"
        )

    # Verify team is part of the match
    if lineup_data.team_id not in [match.team_home_id, match.team_away_id]:
        raise HTTPException(status_code=422, detail="Team is not part of this match")

    # Delete existing lineup for this team
    db.query(Lineup).filter(
        Lineup.match_id == match_id, Lineup.team_id == lineup_data.team_id
    ).delete()

    # Add new lineup
    for player_data in lineup_data.players:
        lineup = Lineup(
            match_id=match_id,
            team_id=lineup_data.team_id,
            player_id=player_data.player_id,
            jersey_number=player_data.jersey_number,
            is_starter=player_data.is_starter,
        )
        db.add(lineup)

    db.commit()

    background_tasks.add_task(publish_match_updated, match, "Lineup assigned")
    return {
        "message": "Lineup assigned successfully",
        "player_count": len(lineup_data.players),
    }


@router.post(
    "/matches/{match_id}/comments",
    response_model=schemas.CommentResponse,
    status_code=201,
)
def add_comment(
    match_id: UUID,
    comment_data: schemas.MatchComment,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Add a comment to a match."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    comment = Comment(
        match_id=match_id,
        message=comment_data.message,
        author_id=comment_data.author_id,
        created_at=comment_data.created_at or datetime.now(timezone.utc),
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    background_tasks.add_task(
        publish_match_updated, match, {"comment": comment_data.message}
    )
    return comment


@router.get("/matches/{match_id}", response_model=schemas.MatchResponse)
def get_match(
    match_id: UUID,
    db: Session = Depends(get_db_session),
):
    """Get a match by ID."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    return match


@router.get("/matches")
def list_matches(
    tournament_id: Optional[UUID] = Query(None),
    modality_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    course_id: Optional[UUID] = Query(None),
    date: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """List matches with optional filters."""
    query = db.query(Match)

    if tournament_id:
        query = query.filter(Match.tournament_id == tournament_id)
    if team_id:
        query = query.filter(
            (Match.team_home_id == team_id) | (Match.team_away_id == team_id)
        )
    if date:
        # Filter by specific date
        try:
            date_obj = datetime.fromisoformat(date)
            query = query.filter(Match.start_time >= date_obj)
            query = query.filter(
                Match.start_time < date_obj.replace(hour=23, minute=59, second=59)
            )
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid date format: {date}")
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(Match.start_time >= date_from_obj)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid date_from format: {date_from}"
            )
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(Match.start_time <= date_to_obj)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid date_to format: {date_to}"
            )
    if status:
        try:
            status_enum = MatchStatus(status)
            query = query.filter(Match.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    # TODO: Implement course_id and modality_id filtering (requires joins or caching)

    total = query.count()
    matches = query.offset(offset).limit(limit).all()

    return {
        "matches": matches,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/matches/{match_id}/sheet")
def generate_match_sheet(
    match_id: UUID,
    format: str = Query("pdf", pattern="^(pdf|json)$"),
    db: Session = Depends(get_db_session),
):
    """Generate match sheet (PDF or JSON)."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # Get lineups
    lineups = db.query(Lineup).filter(Lineup.match_id == match_id).all()

    # Get comments
    comments = db.query(Comment).filter(Comment.match_id == match_id).all()

    if format == "json":
        return {
            "match": {
                "id": str(match.id),
                "tournament_id": str(match.tournament_id),
                "team_home_id": str(match.team_home_id),
                "team_away_id": str(match.team_away_id),
                "location": match.location,
                "start_time": match.start_time.isoformat(),
                "status": match.status.value,
                "home_score": match.home_score,
                "away_score": match.away_score,
            },
            "lineups": [
                {
                    "team_id": str(li.team_id),
                    "player_id": str(li.player_id),
                    "jersey_number": li.jersey_number,
                    "is_starter": li.is_starter,
                }
                for li in lineups
            ],
            "comments": [
                {
                    "message": c.message,
                    "author_id": str(c.author_id),
                    "created_at": c.created_at.isoformat(),
                }
                for c in comments
            ],
        }
    else:
        # TODO: Generate PDF
        raise HTTPException(
            status_code=501, detail="PDF generation not implemented yet"
        )


@router.delete("/matches/{match_id}", status_code=204)
def delete_match(
    match_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Delete a match."""
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        raise HTTPException(status_code=409, detail="Cannot delete a finished match")

    db.delete(match)
    db.commit()

    background_tasks.add_task(publish_match_cancelled, str(match_id), "Deleted by user")
    return None
