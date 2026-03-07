"""
API routes for Matches Service.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.matches import (
    LineupPlayerData,
    MatchCommentAddedData,
    MatchCommentAddedV1,
    MatchCommentDeletedData,
    MatchCommentDeletedV1,
    MatchCreatedData,
    MatchCreatedV1,
    MatchDeletedData,
    MatchDeletedV1,
    MatchLineupAssignedData,
    MatchLineupAssignedV1,
    MatchParticipantAddedData,
    MatchParticipantAddedV1,
    MatchParticipantData,
    MatchParticipantRemovedData,
    MatchParticipantRemovedV1,
    MatchResultEntryData,
    MatchResultUpdatedData,
    MatchUpdatedData,
    MatchUpdatedV1,
)

from . import schemas
from .database import get_db_session
from .logger import logger
from .models import (
    Comment,
    Lineup,
    Match,
    MatchParticipant,
    MatchStatus,
    ParticipantType,
)
from .outbox_publisher import outbox_publisher

router = APIRouter()


@router.get("/matches")
def list_matches(
    tournament_id: Optional[UUID] = Query(None),
    team_id: Optional[UUID] = Query(None),
    athlete_id: Optional[UUID] = Query(None),
    date: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db_session),
):
    """List matches with optional filters."""
    logger.info(
        "Listing matches",
        extra={
            "tournament_id": str(tournament_id) if tournament_id else None,
            "team_id": str(team_id) if team_id else None,
            "athlete_id": str(athlete_id) if athlete_id else None,
            "status": status,
            "limit": limit,
            "offset": offset,
        },
    )

    query = db.query(Match)

    if tournament_id:
        query = query.filter(Match.tournament_id == tournament_id)

    if team_id or athlete_id:
        # Join with participants to filter by team or athlete
        query = query.join(MatchParticipant)
        if team_id:
            query = query.filter(MatchParticipant.team_id == team_id)
        if athlete_id:
            query = query.filter(MatchParticipant.athlete_id == athlete_id)

    if date:
        try:
            date_obj = datetime.fromisoformat(date)
            query = query.filter(Match.start_time >= date_obj)
            query = query.filter(
                Match.start_time < date_obj.replace(hour=23, minute=59, second=59)
            )
        except ValueError:
            logger.warning("Invalid date format", extra={"date": date})
            raise HTTPException(status_code=400, detail=f"Invalid date format: {date}")

    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
            query = query.filter(Match.start_time >= date_from_obj)
        except ValueError:
            logger.warning("Invalid date_from format", extra={"date_from": date_from})
            raise HTTPException(
                status_code=400, detail=f"Invalid date_from format: {date_from}"
            )

    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
            query = query.filter(Match.start_time <= date_to_obj)
        except ValueError:
            logger.warning("Invalid date_to format", extra={"date_to": date_to})
            raise HTTPException(
                status_code=400, detail=f"Invalid date_to format: {date_to}"
            )

    if status:
        try:
            status_enum = MatchStatus(status)
            query = query.filter(Match.status == status_enum)
        except ValueError:
            logger.warning("Invalid status", extra={"status": status})
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    total = query.count()
    matches = query.offset(offset).limit(limit).all()

    logger.info(
        "Matches listed successfully",
        extra={"total": total, "returned": len(matches)},
    )

    return {
        "matches": [schemas.MatchResponse.from_orm(m) for m in matches],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/matches", response_model=schemas.MatchResponse, status_code=201)
def create_match(
    match_data: schemas.MatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Create a new match with participants."""
    logger.info(
        "Creating match",
        extra={
            "tournament_id": (
                str(match_data.tournament_id) if match_data.tournament_id else None
            ),
            "location": match_data.location,
            "start_time": match_data.start_time.isoformat(),
            "created_by": str(match_data.created_by),
            "participant_count": len(match_data.participants),
        },
    )

    # Create match
    match = Match(
        tournament_id=match_data.tournament_id,
        location=match_data.location,
        start_time=match_data.start_time,
        created_by=match_data.created_by,
        status=MatchStatus.SCHEDULED,
    )
    db.add(match)
    db.flush()  # Get match.id before adding participants

    # Create participants
    for participant_data in match_data.participants:
        try:
            participant_type = ParticipantType(participant_data.participant_type)
        except ValueError:
            logger.error(
                "Invalid participant type",
                extra={"participant_type": participant_data.participant_type},
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid participant type: {participant_data.participant_type}",
            )

        # Validate participant has appropriate ID
        if participant_type == ParticipantType.TEAM and not participant_data.team_id:
            raise HTTPException(
                status_code=400, detail="Team participant must have team_id"
            )
        if (
            participant_type == ParticipantType.ATHLETE
            and not participant_data.athlete_id
        ):
            raise HTTPException(
                status_code=400, detail="Athlete participant must have athlete_id"
            )

        participant = MatchParticipant(
            match_id=match.id,
            participant_type=participant_type,
            team_id=participant_data.team_id,
            athlete_id=participant_data.athlete_id,
        )
        db.add(participant)

    # Emit event
    event = MatchCreatedV1.create(
        aggregate_id=match.id,
        data=MatchCreatedData(
            match_id=match.id,
            tournament_id=match.tournament_id,
            location=match.location,
            status=match.status.value,
            start_time=match.start_time.isoformat(),
            participants=[
                MatchParticipantData(
                    participant_id=p.id,
                    participant_type=p.participant_type.value,
                    participant_entity_id=p.team_id or p.athlete_id,
                )
                for p in match.participants
            ],
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match.id,
        data=event.to_data_dict(),
    )

    db.commit()
    db.refresh(match)

    logger.info(
        "Match created successfully",
        extra={"match_id": str(match.id), "status": match.status.value},
    )

    return match


@router.get("/matches/{match_id}", response_model=schemas.MatchResponse)
def get_match(
    match_id: UUID,
    db: Session = Depends(get_db_session),
):
    """Get a match by ID."""
    logger.info("Fetching match", extra={"match_id": str(match_id)})

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning("Match not found", extra={"match_id": str(match_id)})
        raise HTTPException(status_code=404, detail="Match not found")

    logger.info("Match fetched successfully", extra={"match_id": str(match_id)})
    return match


@router.put("/matches/{match_id}", response_model=schemas.MatchResponse)
def update_match(
    match_id: UUID,
    match_data: schemas.MatchUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Update a match."""
    logger.info(
        "Updating match",
        extra={
            "match_id": str(match_id),
            "location": match_data.location,
            "start_time": (
                match_data.start_time.isoformat() if match_data.start_time else None
            ),
            "status": match_data.status,
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning("Match not found for update", extra={"match_id": str(match_id)})
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to update finished match", extra={"match_id": str(match_id)}
        )
        raise HTTPException(
            status_code=409,
            detail="Cannot update a finished match",
        )

    changes_made = {}
    if match_data.location is not None:
        match.location = match_data.location
        changes_made["location"] = match_data.location

    if match_data.start_time is not None:
        match.start_time = match_data.start_time
        changes_made["start_time"] = match_data.start_time.isoformat()

    if match_data.status is not None:
        try:
            status_enum = MatchStatus(match_data.status)
            match.status = status_enum
            changes_made["status"] = match_data.status
        except ValueError:
            logger.error("Invalid status value", extra={"status": match_data.status})
            raise HTTPException(
                status_code=400, detail=f"Invalid status: {match_data.status}"
            )

    match.updated_at = datetime.now(timezone.utc)

    # Emit event for match update
    event = MatchUpdatedV1.create(
        aggregate_id=match_id,
        data=MatchUpdatedData(
            match_id=match_id,
            location=changes_made.get("location"),
            start_time=changes_made.get("start_time"),
            status=changes_made.get("status"),
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    db.commit()
    db.refresh(match)

    logger.info(
        "Match updated successfully",
        extra={"match_id": str(match_id), "changes": changes_made},
    )

    return match


@router.delete("/matches/{match_id}", status_code=204)
def delete_match(
    match_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Delete a match."""
    logger.info("Deleting match", extra={"match_id": str(match_id)})

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning(
            "Match not found for deletion", extra={"match_id": str(match_id)}
        )
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to delete finished match", extra={"match_id": str(match_id)}
        )
        raise HTTPException(status_code=409, detail="Cannot delete a finished match")

    # Emit event before deletion
    event = MatchDeletedV1.create(
        aggregate_id=match_id,
        data=MatchDeletedData(
            match_id=match_id,
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    db.delete(match)
    db.commit()

    logger.info("Match deleted successfully", extra={"match_id": str(match_id)})

    return None


# Participant routes
@router.post(
    "/matches/{match_id}/participants",
    response_model=schemas.MatchParticipantResponse,
    status_code=201,
)
def add_participant(
    match_id: UUID,
    participant_data: schemas.MatchParticipantCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Add a participant to a match."""
    logger.info(
        "Adding participant to match",
        extra={
            "match_id": str(match_id),
            "participant_type": participant_data.participant_type,
            "team_id": (
                str(participant_data.team_id) if participant_data.team_id else None
            ),
            "athlete_id": (
                str(participant_data.athlete_id)
                if participant_data.athlete_id
                else None
            ),
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning(
            "Match not found for adding participant", extra={"match_id": str(match_id)}
        )
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to add participant to finished match",
            extra={"match_id": str(match_id)},
        )
        raise HTTPException(
            status_code=409, detail="Cannot modify participants for finished match"
        )

    try:
        participant_type = ParticipantType(participant_data.participant_type)
    except ValueError:
        logger.error(
            "Invalid participant type",
            extra={"participant_type": participant_data.participant_type},
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid participant type: {participant_data.participant_type}",
        )

    # Validate participant has appropriate ID
    if participant_type == ParticipantType.TEAM and not participant_data.team_id:
        raise HTTPException(
            status_code=400, detail="Team participant must have team_id"
        )
    if participant_type == ParticipantType.ATHLETE and not participant_data.athlete_id:
        raise HTTPException(
            status_code=400, detail="Athlete participant must have athlete_id"
        )

    participant = MatchParticipant(
        match_id=match_id,
        participant_type=participant_type,
        team_id=participant_data.team_id,
        athlete_id=participant_data.athlete_id,
    )
    db.add(participant)
    db.flush()  # Get participant.id

    # Emit event
    event = MatchParticipantAddedV1.create(
        aggregate_id=match_id,
        data=MatchParticipantAddedData(
            match_id=match_id,
            participant_id=participant.id,
            participant_type=participant_type.value,
            participant_entity_id=participant_data.team_id
            or participant_data.athlete_id,
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    db.commit()
    db.refresh(participant)

    logger.info(
        "Participant added successfully",
        extra={"match_id": str(match_id), "participant_id": str(participant.id)},
    )

    return participant


@router.delete("/matches/{match_id}/participants/{participant_id}", status_code=204)
def remove_participant(
    match_id: UUID,
    participant_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Remove a participant from a match."""
    logger.info(
        "Removing participant from match",
        extra={"match_id": str(match_id), "participant_id": str(participant_id)},
    )

    participant = (
        db.query(MatchParticipant)
        .filter(
            MatchParticipant.id == participant_id,
            MatchParticipant.match_id == match_id,
        )
        .first()
    )

    if not participant:
        logger.warning(
            "Participant not found for removal",
            extra={"match_id": str(match_id), "participant_id": str(participant_id)},
        )
        raise HTTPException(status_code=404, detail="Participant not found")

    match = db.query(Match).filter(Match.id == match_id).first()
    if match and match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to remove participant from finished match",
            extra={"match_id": str(match_id)},
        )
        raise HTTPException(
            status_code=409, detail="Cannot modify participants for finished match"
        )

    # Emit event before deletion
    event = MatchParticipantRemovedV1.create(
        aggregate_id=match_id,
        data=MatchParticipantRemovedData(
            match_id=match_id, participant_id=participant_id
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    db.delete(participant)

    db.commit()

    logger.info(
        "Participant removed successfully",
        extra={"match_id": str(match_id), "participant_id": str(participant_id)},
    )
    return None


# Lineup routes
@router.post("/matches/{match_id}/lineup", status_code=201)
def assign_lineup(
    match_id: UUID,
    lineup_data: schemas.LineupBatchCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Assign lineup for a team in a match."""
    logger.info(
        "Assigning lineup",
        extra={
            "match_id": str(match_id),
            "team_id": str(lineup_data.team_id),
            "player_count": len(lineup_data.players),
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning("Match not found for lineup", extra={"match_id": str(match_id)})
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to assign lineup to finished match",
            extra={"match_id": str(match_id)},
        )
        raise HTTPException(
            status_code=409, detail="Cannot modify lineup for finished match"
        )

    # Verify team is a participant in the match
    team_participant = (
        db.query(MatchParticipant)
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.team_id == lineup_data.team_id,
            MatchParticipant.participant_type == ParticipantType.TEAM,
        )
        .first()
    )

    if not team_participant:
        logger.warning(
            "Team is not a participant in match",
            extra={"match_id": str(match_id), "team_id": str(lineup_data.team_id)},
        )
        raise HTTPException(status_code=422, detail="Team is not part of this match")

    # Delete existing lineup for this team
    db.query(Lineup).filter(
        Lineup.match_id == match_id, Lineup.team_id == lineup_data.team_id
    ).delete()

    # Add new lineup
    created_lineups = []
    for player_data in lineup_data.players:
        lineup = Lineup(
            match_id=match_id,
            team_id=lineup_data.team_id,
            player_id=UUID(player_data["player_id"]),
            jersey_number=player_data["jersey_number"],
            is_starter=player_data.get("is_starter", True),
        )
        db.add(lineup)
        created_lineups.append(lineup)

    # Emit event for lineup assignment
    event = MatchLineupAssignedV1.create(
        aggregate_id=match_id,
        data=MatchLineupAssignedData(
            match_id=match_id,
            team_id=lineup_data.team_id,
            lineup=[
                LineupPlayerData(
                    player_id=player_data["player_id"],
                    jersey_number=player_data["jersey_number"],
                    is_starter=player_data.get("is_starter", True),
                )
                for player_data in lineup_data.players
            ],
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    db.commit()

    logger.info(
        "Lineup assigned successfully",
        extra={
            "match_id": str(match_id),
            "team_id": str(lineup_data.team_id),
            "player_count": len(created_lineups),
        },
    )

    return {
        "message": "Lineup assigned successfully",
        "player_count": len(created_lineups),
    }


@router.get("/matches/{match_id}/lineup", response_model=list[schemas.LineupResponse])
def get_lineup(
    match_id: UUID,
    team_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db_session),
):
    """Get lineup for a match, optionally filtered by team."""
    logger.info(
        "Fetching lineup",
        extra={
            "match_id": str(match_id),
            "team_id": str(team_id) if team_id else None,
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning("Match not found for lineup", extra={"match_id": str(match_id)})
        raise HTTPException(status_code=404, detail="Match not found")

    query = db.query(Lineup).filter(Lineup.match_id == match_id)

    if team_id:
        query = query.filter(Lineup.team_id == team_id)

    lineups = query.all()

    logger.info(
        "Lineup fetched successfully",
        extra={"match_id": str(match_id), "lineup_count": len(lineups)},
    )

    return lineups


# Comment routes
@router.post(
    "/matches/{match_id}/comments",
    response_model=schemas.CommentResponse,
    status_code=201,
)
def add_comment(
    match_id: UUID,
    comment_data: schemas.CommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Add a comment to a match."""
    logger.info(
        "Adding comment to match",
        extra={
            "match_id": str(match_id),
            "created_by": str(comment_data.created_by),
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning("Match not found for comment", extra={"match_id": str(match_id)})
        raise HTTPException(status_code=404, detail="Match not found")

    comment = Comment(
        match_id=match_id,
        message=comment_data.message,
        created_by=comment_data.created_by,
    )
    db.add(comment)
    db.flush()  # Get comment.id

    # Emit event for comment addition
    event = MatchCommentAddedV1.create(
        aggregate_id=match_id,
        data=MatchCommentAddedData(
            comment_id=comment.id,
            match_id=match_id,
            message=comment.message,
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )
    db.commit()
    db.refresh(comment)

    logger.info(
        "Comment added successfully",
        extra={"match_id": str(match_id), "comment_id": str(comment.id)},
    )

    return comment


@router.get(
    "/matches/{match_id}/comments", response_model=list[schemas.CommentResponse]
)
def get_comments(
    match_id: UUID,
    db: Session = Depends(get_db_session),
):
    """Get all comments for a match."""
    logger.info("Fetching comments", extra={"match_id": str(match_id)})

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning(
            "Match not found for comments", extra={"match_id": str(match_id)}
        )
        raise HTTPException(status_code=404, detail="Match not found")

    comments = (
        db.query(Comment)
        .filter(Comment.match_id == match_id)
        .order_by(Comment.created_at.desc())
        .all()
    )

    logger.info(
        "Comments fetched successfully",
        extra={"match_id": str(match_id), "comment_count": len(comments)},
    )

    return comments


@router.delete("/matches/{match_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    match_id: UUID,
    comment_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Delete a comment."""
    logger.info(
        "Deleting comment",
        extra={"match_id": str(match_id), "comment_id": str(comment_id)},
    )

    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.match_id == match_id)
        .first()
    )

    if not comment:
        logger.warning(
            "Comment not found",
            extra={"match_id": str(match_id), "comment_id": str(comment_id)},
        )
        raise HTTPException(status_code=404, detail="Comment not found")

    # Emit event before deletion
    event = MatchCommentDeletedV1.create(
        aggregate_id=match_id,
        data=MatchCommentDeletedData(
            comment_id=comment_id,
            match_id=match_id,
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    db.delete(comment)
    db.commit()

    logger.info(
        "Comment deleted successfully",
        extra={"match_id": str(match_id), "comment_id": str(comment_id)},
    )

    return None


# Batch result update
@router.put("/matches/{match_id}/results", response_model=schemas.MatchResponse)
def update_match_results(
    match_id: UUID,
    result_data: schemas.MatchResultUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
):
    """Update results for multiple participants and optionally finish the match."""
    logger.info(
        "Updating match results",
        extra={
            "match_id": str(match_id),
            "participant_count": len(result_data.participant_results),
            "new_status": result_data.status,
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning("Match not found for results", extra={"match_id": str(match_id)})
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to update results for finished match",
            extra={"match_id": str(match_id)},
        )
        raise HTTPException(status_code=409, detail="Match already finished")

    # Update each participant's result
    updated_participants = []
    for participant_result in result_data.participant_results:
        participant = (
            db.query(MatchParticipant)
            .filter(
                MatchParticipant.id == participant_result.participant_id,
                MatchParticipant.match_id == match_id,
            )
            .first()
        )

        if not participant:
            logger.warning(
                "Participant not found in result update",
                extra={
                    "match_id": str(match_id),
                    "participant_id": str(participant_result.participant_id),
                },
            )
            raise HTTPException(
                status_code=404,
                detail=f"Participant {participant_result.participant_id} not found",
            )

        if participant_result.score is not None:
            participant.score = participant_result.score

        if participant_result.position is not None:
            participant.position = participant_result.position

        if participant_result.result_metadata is not None:
            participant.result_metadata = participant_result.result_metadata

        updated_participants.append(
            {
                "participant_id": str(participant.id),
                "score": participant.score,
                "position": participant.position,
                "results_metadata": participant.result_metadata,
            }
        )

    # Emit event for result updates
    event = MatchUpdatedV1.create(
        aggregate_id=match_id,
        data=MatchResultUpdatedData(
            match_id=match_id,
            results=[
                MatchResultEntryData(
                    participant_id=r["participant_id"],
                    score=r.get("score"),
                    position=r.get("position"),
                    results_metadata=r.get("results_metadata"),
                )
                for r in updated_participants
            ],
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    # Update match status if provided
    if result_data.status:
        try:
            status_enum = MatchStatus(result_data.status)
            match.status = status_enum
        except ValueError:
            logger.error("Invalid status value", extra={"status": result_data.status})
            raise HTTPException(
                status_code=400, detail=f"Invalid status: {result_data.status}"
            )

    # Emit match updated event for status change
    event = MatchUpdatedV1.create(
        aggregate_id=match_id,
        data=MatchUpdatedData(
            match_id=match_id,
            status=match.status.value,
        ),
    )
    outbox_publisher.emit_event(
        db,
        event_type=event.event_type(),
        aggregate_type="match",
        aggregate_id=match_id,
        data=event.to_data_dict(),
    )

    match.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(match)

    logger.info(
        "Match results updated successfully",
        extra={
            "match_id": str(match_id),
            "updated_count": len(updated_participants),
            "new_status": match.status.value,
        },
    )

    return match
