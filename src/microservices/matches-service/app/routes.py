"""
API routes for Matches Service.
"""

import json
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
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
    MatchParticipantData,
    MatchResultEntryData,
    MatchResultUpdatedData,
    MatchResultUpdatedV1,
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
    MatchLineupStaff,
    MatchParticipant,
    MatchStatus,
)
from .outbox_publisher import outbox_publisher

router = APIRouter()


@router.get("/matches")
def list_matches(
    tournament_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db_session),
):
    """List matches with optional filters."""
    logger.info(
        "Listing matches",
        extra={
            "tournament_id": str(tournament_id) if tournament_id else None,
            "status": status,
        },
    )

    query = db.query(Match)

    if tournament_id:
        query = query.filter(Match.tournament_id == tournament_id)

    if status:
        try:
            status_enum = MatchStatus(status)
            query = query.filter(Match.status == status_enum)
        except ValueError:
            logger.warning("Invalid status", extra={"status": status})
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    total = query.count()
    matches = query.yield_per(100).all()  # Use yield_per for large datasets

    logger.info(
        "Matches listed successfully",
        extra={"total": total, "returned": len(matches)},
    )

    return {
        "matches": [m.to_dict(include_details=False) for m in matches],
        "total": total,
    }


@router.get("/matches/tournament-rounds/{tournament_id}")
def list_tournament_rounds(
    tournament_id: UUID,
    db: Session = Depends(get_db_session),
):
    """List rounds for a specific tournament."""
    logger.info(
        "Listing tournament rounds",
        extra={"tournament_id": str(tournament_id)},
    )

    query = (
        db.query(Match.journey).filter(Match.tournament_id == tournament_id).distinct()
    )
    rounds = [round[0] for round in query]

    logger.info(
        "Tournament rounds listed successfully",
        extra={"total": len(rounds), "rounds": rounds},
    )

    return {"rounds": rounds}


@router.get("/matches/stream")
def stream_matches(
    tournament_ids: Optional[List[UUID]] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: Optional[int] = Query(None),
    limit: Optional[int] = Query(None),
    db: Session = Depends(get_db_session),
):
    """Stream matches with optional filters."""
    logger.info(
        "Streaming matches",
        extra={
            "tournament_ids": (
                [str(t_id) for t_id in tournament_ids] if tournament_ids else None
            ),
            "status": status,
            "page": page,
            "limit": limit,
        },
    )

    query = db.query(Match)

    if tournament_ids is not None:
        query = query.filter(Match.tournament_id.in_(tournament_ids))

    if status:
        try:
            status_enum = MatchStatus(status)
            query = query.filter(Match.status == status_enum)
        except ValueError:
            logger.warning("Invalid status", extra={"status": status})
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if date_from:
        query = query.filter(Match.start_time >= date_from)

    if date_to:
        query = query.filter(Match.start_time <= date_to)

    # Apply pagination
    if page is not None and limit is not None:
        query = query.offset((page - 1) * limit).limit(limit)
    elif (page is not None) != (limit is not None):
        logger.warning(
            "Pagination parameters incomplete",
            extra={"page": page, "limit": limit},
        )
        raise HTTPException(
            status_code=400,
            detail="Both page and limit must be provided together for pagination.",
        )

    def match_generator():
        for match in query.yield_per(100):
            try:
                json_data = json.dumps(match.to_dict(include_details=False))
            except Exception as e:
                logger.error(
                    "Error serializing match",
                    extra={"match_id": str(match.id), "error": str(e)},
                )
                break
            yield f"data: {json_data}\n\n"

    return StreamingResponse(match_generator(), media_type="application/json")


@router.get("/matches/count")
def count_matches(
    tournament_ids: Optional[List[UUID]] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: Session = Depends(get_db_session),
):
    """Count matches with optional filters."""
    logger.info(
        "Counting matches",
        extra={
            "tournament_ids": (
                [str(t_id) for t_id in tournament_ids] if tournament_ids else None
            ),
            "status": status,
        },
    )

    query = db.query(Match)

    if tournament_ids is not None:
        query = query.filter(Match.tournament_id.in_(tournament_ids))

    if status:
        try:
            status_enum = MatchStatus(status)
            query = query.filter(Match.status == status_enum)
        except ValueError:
            logger.warning("Invalid status", extra={"status": status})
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    if date_from:
        query = query.filter(Match.start_time >= date_from)

    if date_to:
        query = query.filter(Match.start_time <= date_to)

    total = query.count()

    logger.info(
        "Matches counted successfully",
        extra={"total": total},
    )

    return {"count": total}


@router.post("/matches", response_model=schemas.MatchResponse, status_code=201)
def create_match(
    match_data: schemas.MatchCreate,
    db: Session = Depends(get_db_session),
):
    """Create a new match with participants."""
    logger.info(
        "Creating match",
        extra={
            "tournament_id": str(match_data.tournament_id),
            "location": match_data.location,
            "start_time": match_data.start_time.isoformat(),
            "created_by": str(match_data.created_by),
            "participant_count": len(match_data.participants),
            "journey": match_data.journey,
            "new_journey": match_data.new_journey,
        },
    )

    if match_data.journey is None:
        # default to last journey for the tournament if not provided
        last_journey = (
            db.query(Match.journey)
            .filter(Match.tournament_id == match_data.tournament_id)
            .order_by(Match.journey.desc())
            .first()
        )
        match_data.journey = (
            last_journey[0] if last_journey and last_journey[0] is not None else 0
        )

    # Create match
    match = Match(
        tournament_id=match_data.tournament_id,
        location=match_data.location,
        start_time=match_data.start_time,
        created_by=match_data.created_by,
        status=MatchStatus.SCHEDULED,
        journey=(
            match_data.journey + 1 if match_data.new_journey else match_data.journey
        ),
    )
    db.add(match)
    db.flush()  # Get match.id before adding participants

    # Create participants
    for participant_data in match_data.participants:
        participant = MatchParticipant(
            match_id=match.id,
            participant=participant_data,
        )
        db.add(participant)
    db.flush()  # Get participant IDs if needed for events

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
                    participant_id=p.participant,
                    # participant_type=None,  # Not needed since we have the competitor ID
                    # participant_entity_id=None,  # Not needed since we have the competitor ID
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

    return match.to_dict(include_details=False)


@router.post("/matches/summary", response_model=schemas.MatchSummaryResponse)
def get_matches_summary(
    request_data: schemas.MatchesSummaryRequest,
    db: Session = Depends(get_db_session),
):
    """Get summary information about matches, optionally filtered by tournament."""
    tournament_ids = request_data.tournaments_ids if request_data else None
    tournaments_distribution = (
        request_data.tournaments_distribution if request_data else None
    )

    relevant_matches_query = db.query(Match)

    # If filtering by tournament IDs, apply filter
    if tournament_ids is not None:
        relevant_matches_query = relevant_matches_query.filter(
            Match.tournament_id.in_(tournament_ids)
        )

    # If filtering by tournaments distribution, we need to join with participants and apply complex filtering
    if tournaments_distribution is not None:
        relevant_matches_query = relevant_matches_query.join(
            MatchParticipant, Match.id == MatchParticipant.match_id
        )

        or_conditions = []
        for tournament_id, competitor_ids in tournaments_distribution.items():
            or_conditions.append(
                (Match.tournament_id == tournament_id)
                & (MatchParticipant.participant.in_(competitor_ids))
            )
        relevant_matches_query = relevant_matches_query.filter(
            or_(*or_conditions)
        ).distinct()

    # Count matches by status
    total_matches = relevant_matches_query.count()
    finished = relevant_matches_query.filter(
        Match.status == MatchStatus.FINISHED
    ).count()
    ongoing = relevant_matches_query.filter(
        Match.status == MatchStatus.IN_PROGRESS
    ).count()
    scheduled = relevant_matches_query.filter(
        Match.status == MatchStatus.SCHEDULED
    ).count()

    logger.info(
        "Matches summary fetched successfully",
        extra={
            "total_matches": total_matches,
            "finished": finished,
            "ongoing": ongoing,
            "scheduled": scheduled,
        },
    )

    return schemas.MatchSummaryResponse(
        total_matches=total_matches,
        finished=finished,
        ongoing=ongoing,
        scheduled=scheduled,
    )


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
    return match.to_dict(include_details=True)


@router.put("/matches/{match_id}", response_model=schemas.MatchResponse)
def update_match(
    match_id: UUID,
    match_data: schemas.MatchUpdate,
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

    # Prevent updates to finished or cancelled matches that would revert them back to scheduled or in_progress
    if match.status == MatchStatus.FINISHED or match.status == MatchStatus.CANCELLED:
        if (
            match_data.status == MatchStatus.SCHEDULED.value
            or match_data.status == MatchStatus.IN_PROGRESS.value
        ):
            logger.warning(
                "Attempted to update match to invalid status",
                extra={
                    "match_id": str(match_id),
                    "current_status": match.status.value,
                    "attempted_status": match_data.status,
                },
            )
            raise HTTPException(
                status_code=409,
                detail=f"Cannot change status from {match.status.value} to {match_data.status}",
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

    return match.to_dict(include_details=True)


@router.delete("/matches/{match_id}", status_code=204)
def delete_match(
    match_id: UUID,
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
            tournament_id=match.tournament_id,
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


# Lineup routes
@router.post(
    "/matches/{match_id}/lineup", status_code=201, response_model=schemas.MatchResponse
)
def assign_lineup(
    match_id: UUID,
    lineup_data: schemas.LineupBatchCreate,
    db: Session = Depends(get_db_session),
):
    """Assign lineup for a team in a match."""
    logger.info(
        "Assigning lineup",
        extra={
            "match_id": str(match_id),
            "participant_id": str(lineup_data.participant),
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
        )
        .first()
    )

    if not team_participant:
        logger.warning(
            "Team is not a participant in match",
            extra={
                "match_id": str(match_id),
                "participant_id": str(lineup_data.participant),
            },
        )
        raise HTTPException(status_code=422, detail="Team is not part of this match")

    # Delete existing lineup for this team
    db.query(Lineup).filter(
        Lineup.match_id == match_id, Lineup.participant == lineup_data.participant
    ).delete()

    # Add new lineup
    created_lineups = []
    for player_data in lineup_data.players:
        lineup = Lineup(
            match_id=match_id,
            participant=lineup_data.participant,
            player_id=player_data,
        )
        db.add(lineup)
        created_lineups.append(lineup)

    # Emit event for lineup assignment
    event = MatchLineupAssignedV1.create(
        aggregate_id=match_id,
        data=MatchLineupAssignedData(
            match_id=match_id,
            team_id=lineup_data.participant,
            lineup=[
                LineupPlayerData(
                    player_id=player_data,
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
            "participant_id": str(lineup_data.participant),
            "player_count": len(created_lineups),
        },
    )

    return match.to_dict(include_details=True)


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


@router.put("/matches/{match_id}/lineup", response_model=schemas.MatchResponse)
def update_lineup(
    match_id: UUID,
    lineup_data: schemas.LineupBatchUpdate,
    db: Session = Depends(get_db_session),
):
    """Update lineup for a team in a match."""
    logger.info(
        "Updating lineup",
        extra={
            "match_id": str(match_id),
            "participant_id": str(lineup_data.participant),
            "player_count": len(lineup_data.players),
        },
    )

    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning(
            "Match not found for lineup update", extra={"match_id": str(match_id)}
        )
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to update lineup for finished match",
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
        )
        .first()
    )

    if not team_participant:
        logger.warning(
            "Team is not a participant in match for lineup update",
            extra={
                "match_id": str(match_id),
                "participant_id": str(lineup_data.participant),
            },
        )
        raise HTTPException(status_code=422, detail="Team is not part of this match")

    # Update lineup entries
    updated_lineups = []
    for player_update in lineup_data.players:
        lineup_entry = (
            db.query(Lineup)
            .filter(
                Lineup.match_id == match_id,
                Lineup.participant == lineup_data.participant,
                Lineup.player_id == player_update.player_id,
            )
            .first()
        )

        if not lineup_entry:
            logger.warning(
                "Lineup entry not found for update",
                extra={
                    "match_id": str(match_id),
                    "participant_id": str(lineup_data.participant),
                    "player_id": str(player_update.player_id),
                },
            )
            raise HTTPException(
                status_code=404,
                detail=f"Lineup entry for player {player_update.player_id} not found",
            )

        if player_update.is_starter is not None:
            lineup_entry.is_starter = player_update.is_starter
        lineup_entry.jersey_number = player_update.jersey_number
        updated_lineups.append(lineup_entry)

    # Emit event for lineup update
    event = MatchLineupAssignedV1.create(
        aggregate_id=match_id,
        data=MatchLineupAssignedData(
            match_id=match_id,
            team_id=lineup_data.participant,
            lineup=[
                LineupPlayerData(
                    player_id=player_update.player_id,
                )
                for player_update in lineup_data.players
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
    db.refresh(match)

    logger.info(
        "Lineup updated successfully",
        extra={
            "match_id": str(match_id),
            "participant_id": str(lineup_data.participant),
            "updated_count": len(updated_lineups),
        },
    )
    return match.to_dict(include_details=True)


@router.post(
    "/matches/{match_id}/participants/{participant_id}/staff",
    response_model=schemas.MatchResponse,
)
def assign_staff_to_lineup(
    match_id: UUID,
    participant_id: UUID,
    staff_data: schemas.LineupAssignStaff,
    db: Session = Depends(get_db_session),
):
    """Assign staff to a match participant."""
    logger.info(
        "Assigning staff to lineup",
        extra={
            "match_id": str(match_id),
            "participant_id": str(participant_id),
            "staff_count": len(staff_data.staff_ids),
        },
    )
    match = db.query(Match).filter(Match.id == match_id).first()

    if not match:
        logger.warning(
            "Match not found for staff assignment",
            extra={"match_id": str(match_id)},
        )
        raise HTTPException(status_code=404, detail="Match not found")

    if match.status == MatchStatus.FINISHED:
        logger.warning(
            "Attempted to assign staff to finished match",
            extra={"match_id": str(match_id)},
        )
        raise HTTPException(
            status_code=409, detail="Cannot modify lineup for finished match"
        )

    # Verify participant is part of the match
    participant = (
        db.query(MatchParticipant)
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.participant == participant_id,
        )
        .first()
    )
    if not participant:
        logger.warning(
            "Participant not found in match for staff assignment",
            extra={
                "match_id": str(match_id),
                "participant_id": str(participant_id),
            },
        )
        raise HTTPException(
            status_code=422, detail="Participant is not part of this match"
        )

    # Delete existing staff assignments for this participant
    db.query(MatchLineupStaff).filter(
        MatchLineupStaff.match_id == match_id,
        MatchLineupStaff.participant_id == participant_id,
    ).delete()

    # Add new staff assignments
    for staff_id in staff_data.staff_ids:
        staff_assignment = MatchLineupStaff(
            match_id=match_id,
            participant_id=participant_id,
            staff_id=staff_id,
        )
        db.add(staff_assignment)

    db.commit()
    db.refresh(match)

    return match.to_dict(include_details=True)


# Comment routes
@router.post(
    "/matches/{match_id}/comments",
    response_model=schemas.MatchResponse,
    status_code=201,
)
def add_comment(
    match_id: UUID,
    comment_data: schemas.CommentCreate,
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

    return comment.match.to_dict(include_details=True)


@router.delete(
    "/matches/{match_id}/comments/{comment_id}",
    status_code=200,
    response_model=schemas.MatchResponse,
)
def delete_comment(
    match_id: UUID,
    comment_id: UUID,
    admin_id_check: Optional[UUID] = Query(
        None, description="Admin ID for permission check"
    ),
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

    # Access the match before deletion for event data
    match = comment.match

    if admin_id_check and comment.created_by != admin_id_check:
        logger.warning(
            "Unauthorized attempt to delete comment",
            extra={
                "match_id": str(match_id),
                "comment_id": str(comment_id),
                "attempted_by": str(admin_id_check),
                "comment_author": str(comment.created_by),
            },
        )
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this comment"
        )

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

    return match.to_dict(include_details=True)


# Batch result update
@router.put("/matches/{match_id}/results", response_model=schemas.MatchResponse)
def update_match_results(
    match_id: UUID,
    result_data: schemas.MatchResultUpdate,
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
                MatchParticipant.participant == participant_result.participant_id,
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

        updated_participants.append(
            {
                "participant_id": str(participant.participant),
                "score": participant.score,
                "position": participant.position,
            }
        )

    # Emit event for result updates
    event = MatchResultUpdatedV1.create(
        aggregate_id=match_id,
        data=MatchResultUpdatedData(
            match_id=match_id,
            tournament_id=match.tournament_id,
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

    return match.to_dict(include_details=True)
