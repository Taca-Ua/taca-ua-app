"""
API routes for Tournaments Service.
"""

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from app.formats import FormatRegistry
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from taca_events.pydantic_schemas.tournaments import (
    RankingEntryData,
    TournamentCompetitorAddedData,
    TournamentCompetitorAddedV1,
    TournamentCompetitorDeletedData,
    TournamentCompetitorDeletedV1,
    TournamentCreatedData,
    TournamentCreatedV1,
    TournamentDeletedData,
    TournamentDeletedV1,
    TournamentFinishedData,
    TournamentFinishedV1,
    TournamentUpdatedData,
    TournamentUpdatedV1,
)

from .database import get_db, get_db_session
from .logger import logger
from .models import (
    CompetitorType,
    Tournament,
    TournamentCompetitor,
    TournamentRankingPosition,
)
from .outbox_publisher import outbox_publisher
from .schemas import (
    CompetitorInput,
    TournamentCreate,
    TournamentFinish,
    TournamentFormatMetaUpdate,
    TournamentResponse,
    TournamentSeasonSummary,
    TournamentSeasonSummaryRequest,
    TournamentStandingsResponse,
    TournamentUpdate,
)

router = APIRouter()


# ==================== Helpers ====================
def add_competitor(db: Session, tournament_id: UUID, competitor_input: CompetitorInput):
    """Add a competitor to a tournament.

    Args:
        db (Session): Database session
        tournament_id (UUID): ID of the tournament
        competitor_input (CompetitorInput): Competitor details

    Returns:
        None
    """

    competitor_type = (
        CompetitorType.TEAM
        if competitor_input.competitor_type == "team"
        else CompetitorType.ATHLETE
    )

    # Check if competitor is not already in tournament
    query = db.query(TournamentCompetitor).filter(
        TournamentCompetitor.tournament_id == tournament_id,
        TournamentCompetitor.competitor_type == competitor_type,
    )

    if competitor_type == CompetitorType.TEAM:
        query = query.filter(
            TournamentCompetitor.team_id == competitor_input.competitor_entity_id
        )
    else:
        query = query.filter(
            TournamentCompetitor.athlete_id == competitor_input.competitor_entity_id
        )

    existing = query.first()

    if existing:
        return  # Competitor already exists, skip adding

    tournament_competitor = TournamentCompetitor(
        tournament_id=tournament_id,
        competitor_type=competitor_type,
        team_id=(
            competitor_input.competitor_entity_id
            if competitor_type == CompetitorType.TEAM
            else None
        ),
        athlete_id=(
            competitor_input.competitor_entity_id
            if competitor_type == CompetitorType.ATHLETE
            else None
        ),
        competitor_course_id=competitor_input.competitor_course_id,
    )
    db.add(tournament_competitor)
    db.flush()

    # Update format-specific data if needed
    engine = FormatRegistry.get_engine(tournament_competitor.tournament.format)
    if not engine:
        logger.warn(
            f"No format engine found for format {tournament_competitor.tournament.format}, skipping format-specific competitor addition logic"
        )
    else:
        engine.on_competitor_added(db, tournament_competitor)
        db.flush()

    # Emit event for added competitor
    event = TournamentCompetitorAddedV1.create(
        aggregate_id=tournament_competitor.id,
        data=TournamentCompetitorAddedData(
            tournament_id=tournament_id,
            competitor_type=competitor_input.competitor_type,
            competitor_entity_id=competitor_input.competitor_entity_id,
            competitor_id=tournament_competitor.id,
            competitor_course_id=competitor_input.competitor_course_id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type=event.aggregate_type(),
        aggregate_id=str(tournament_competitor.id),
        data=event.to_data_dict(),
    )


# ==================== Tournament Endpoints ====================


@router.get("/tournaments", response_model=List[TournamentResponse])
async def list_tournaments(
    status_filter: str = None,
    modality_id: UUID = None,
    season_id: int = None,
    db: Session = Depends(get_db_session),
):
    """List all tournaments with optional filters"""
    query = db.query(Tournament)

    if status_filter:
        query = query.filter(Tournament.status == status_filter)
    if modality_id:
        query = query.filter(Tournament.modality_id == modality_id)
    if season_id:
        query = query.filter(Tournament.season_id == season_id)

    tournaments = query.all()
    return [TournamentResponse(**t.to_dict(include_ranking=False)) for t in tournaments]


@router.get("/tournaments/summary", response_model=TournamentSeasonSummary)
async def get_tournament_summary(
    season_id: int = None, db: Session = Depends(get_db_session)
):
    """Get summary information for all tournaments in a season"""

    tournaments = db.query(Tournament)
    if season_id:
        tournaments = tournaments.filter(Tournament.season_id == season_id)

    t_finished = tournaments.filter(Tournament.status == "finished").count()
    t_ongoing = tournaments.filter(Tournament.status == "active").count()
    t_scheduled = tournaments.filter(Tournament.status == "draft").count()

    return TournamentSeasonSummary(
        tournaments_finished=t_finished,
        tournaments_ongoing=t_ongoing,
        tournaments_scheduled=t_scheduled,
        tournaments_ids=[t.id for t in tournaments.all()],
    )


@router.post("/tournaments/summary", response_model=TournamentSeasonSummary)
async def get_tournament_summary_post(
    request: TournamentSeasonSummaryRequest, db: Session = Depends(get_db_session)
):
    """Get summary information for all tournaments in a season (POST version)"""
    season_id = request.season_id

    stmt_tournaments = db.query(Tournament)
    if season_id:
        stmt_tournaments = stmt_tournaments.filter(Tournament.season_id == season_id)

    # Start with base query for competitors
    stmt_tournaments_competitors = stmt_tournaments.join(
        TournamentCompetitor
    ).with_entities(
        TournamentCompetitor.id,
        TournamentCompetitor.tournament_id,
        TournamentCompetitor.competitor_type,
        TournamentCompetitor.athlete_id,
        TournamentCompetitor.team_id,
    )

    # Apply additional filters for teams and athletes if provided
    if request.teams_ids or request.athletes_ids:
        tournaments_teams = None
        tournaments_athletes = None

        if request.teams_ids:
            tournaments_teams = stmt_tournaments_competitors.filter(
                TournamentCompetitor.competitor_type == CompetitorType.TEAM,
                TournamentCompetitor.team_id.in_(request.teams_ids),
            )

        if request.athletes_ids:
            tournaments_athletes = stmt_tournaments_competitors.filter(
                TournamentCompetitor.competitor_type == CompetitorType.ATHLETE,
                TournamentCompetitor.athlete_id.in_(request.athletes_ids),
            )

        if request.teams_ids and request.athletes_ids:
            # If both filters are provided, we take the union of the two filtered sets
            assert tournaments_teams is not None and tournaments_athletes is not None
            stmt_tournaments_competitors = tournaments_teams.union(tournaments_athletes)
        elif request.teams_ids:
            # If only team filter is provided, use that
            assert tournaments_teams is not None
            stmt_tournaments_competitors = tournaments_teams
        elif request.athletes_ids:
            assert tournaments_athletes is not None
            # If only athlete filter is provided, use that
            stmt_tournaments_competitors = tournaments_athletes

        stmt_tournaments_competitors = stmt_tournaments_competitors.distinct()

        # Get distinct tournament IDs that match the criteria
        filtered_tournament_ids = {
            tc.tournament_id for tc in stmt_tournaments_competitors.all()
        }
    else:
        # No competitor filters provided, include all tournaments (even empty ones)
        filtered_tournament_ids = {t.id for t in stmt_tournaments.all()}

    # Count tournaments by status, considering only filtered tournaments
    stmt_tournaments = stmt_tournaments.filter(
        Tournament.id.in_(filtered_tournament_ids)
    )
    t_finished = stmt_tournaments.filter(Tournament.status == "finished").count()
    t_ongoing = stmt_tournaments.filter(Tournament.status == "active").count()
    t_scheduled = stmt_tournaments.filter(Tournament.status == "draft").count()

    # Build competitors distribution for each relevant tournament
    tournament_competitors_distribution: dict[UUID, set[UUID]] = {}
    for tc in stmt_tournaments_competitors.all():
        tournament_id = tc.tournament_id

        if tournament_id not in tournament_competitors_distribution:
            tournament_competitors_distribution[tournament_id] = set()

        tournament_competitors_distribution[tournament_id].add(tc.id)

    return TournamentSeasonSummary(
        tournaments_finished=t_finished,
        tournaments_ongoing=t_ongoing,
        tournaments_scheduled=t_scheduled,
        tournaments_ids=list(filtered_tournament_ids),
        competitors_distribution=(
            [
                TournamentSeasonSummary._TournamentSeasonSummaryCompetitors(
                    tournament_id=t_id,
                    competitors_ids=list(competitors_ids),
                )
                for t_id, competitors_ids in tournament_competitors_distribution.items()
            ]
            if tournament_competitors_distribution
            else None
        ),
    )


@router.get("/tournaments/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: UUID, db: Session = Depends(get_db_session)):
    """Get a tournament by ID"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    return TournamentResponse(**tournament.to_dict(include_ranking=False))


@router.post(
    "/tournaments",
    response_model=TournamentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tournament(data: TournamentCreate, db: Session = Depends(get_db)):
    """Create a new tournament"""
    competitor_type_map = {
        "team": CompetitorType.TEAM,
        "athlete": CompetitorType.ATHLETE,
    }

    if data.competitor_type not in competitor_type_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid competitor_type: {data.competitor_type!r}",
        )

    print(
        f"Creating tournament with format {data.format} and format_data {data.format_data}",
        flush=True,
    )
    engine = FormatRegistry.get_engine(data.format)
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {data.format!r}",
        )

    competitor_type = competitor_type_map[data.competitor_type]
    # Create tournament record using factory method (creates correct subclass based on format)
    tournament = Tournament.create(
        format=data.format,
        modality_id=data.modality_id,
        name=data.name,
        start_date=data.start_date,
        status="draft",
        scoring_format_id=data.scoring_format_id,
        competitor_type=competitor_type,
        created_by="00000000-0000-0000-0000-000000000000",  # Placeholder, should be replaced with actual user ID from auth context
        season_id=data.season_id,
    )

    try:
        tournament = engine.complete_tournament(
            tournament, format_data=data.format_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error completing tournament: {str(e)}",
        )

    db.add(tournament)
    db.flush()  # Get the ID before committing

    # Emit event for tournament creation
    event = TournamentCreatedV1.create(
        aggregate_id=tournament.id,
        data=TournamentCreatedData(
            tournament_id=tournament.id,
            modality_id=tournament.modality_id,
            name=tournament.name,
            start_date=tournament.start_date.isoformat(),
            status=tournament.status,
            scoring_format_id=tournament.scoring_format_id,
            season_id=tournament.season_id,
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="tournament",
        aggregate_id=str(tournament.id),
        data=event.to_data_dict(),
    )

    db.commit()
    db.refresh(tournament)

    logger.info(f"Created tournament {tournament.id}: {tournament.name}")
    return TournamentResponse(**tournament.to_dict(include_ranking=False))


@router.put("/tournaments/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: UUID, data: TournamentUpdate, db: Session = Depends(get_db_session)
):
    """Update a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    # Update fields
    changes_made = {}
    if data.name is not None:
        tournament.name = data.name
        changes_made["name"] = data.name
    if data.start_date is not None:
        tournament.start_date = data.start_date
        changes_made["start_date"] = data.start_date.isoformat()
    if data.status is not None:
        tournament.status = data.status
        changes_made["status"] = data.status
    if data.scoring_format_id is not None:
        tournament.scoring_format_id = data.scoring_format_id
        changes_made["scoring_format_id"] = str(data.scoring_format_id)

    tournament.updated_at = datetime.now(timezone.utc)

    # Create outbox event
    event = TournamentUpdatedV1.create(
        aggregate_id=tournament.id,
        data=TournamentUpdatedData(
            tournament_id=tournament.id,
            name=changes_made.get("name"),
            start_date=changes_made.get("start_date"),
            status=changes_made.get("status"),
            scoring_format_id=changes_made.get("scoring_format_id"),
        ),
    )
    outbox_publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type="tournament",
        aggregate_id=str(tournament.id),
        data=event.to_data_dict(),
    )

    try:
        db.commit()
        db.refresh(tournament)
        logger.info(f"Updated tournament {tournament.id}")
        return TournamentResponse(**tournament.to_dict(include_ranking=False))
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating tournament: {str(e)}",
        )


@router.delete("/tournaments/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(tournament_id: UUID, db: Session = Depends(get_db_session)):
    """Delete a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        # Emit event before deleting
        event = TournamentDeletedV1.create(
            aggregate_id=tournament.id,
            data=TournamentDeletedData(
                tournament_id=tournament.id,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            data=event.to_data_dict(),
        )

        db.delete(tournament)
        db.commit()

        logger.info(f"Deleted tournament {tournament_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting tournament: {str(e)}",
        )


@router.post("/tournaments/{tournament_id}/finish", response_model=TournamentResponse)
async def finish_tournament(
    tournament_id: UUID, data: TournamentFinish, db: Session = Depends(get_db_session)
):
    """Mark a tournament as finished and set final rankings"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    if tournament.status == "finished":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament is already finished",
        )

    try:
        # Delete existing ranking positions
        db.query(TournamentRankingPosition).filter(
            TournamentRankingPosition.tournament_id == tournament_id
        ).delete()

        # Create new ranking positions
        for entry in data.ranking_entries:
            ranking_position = TournamentRankingPosition(
                tournament_id=tournament_id,
                competitor_id=entry.competitor_id,
                position=entry.position,
            )
            db.add(ranking_position)

        # Update tournament status
        tournament.status = "finished"
        tournament.finished_at = datetime.now(timezone.utc)
        tournament.finished_by = data.finished_by
        tournament.updated_at = datetime.now(timezone.utc)

        # Create outbox event
        event = TournamentFinishedV1.create(
            aggregate_id=tournament.id,
            data=TournamentFinishedData(
                tournament_id=tournament.id,
                ranking_entries=[
                    RankingEntryData(
                        competitor_id=entry.competitor_id,
                        position=entry.position,
                    )
                    for entry in data.ranking_entries
                ],
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="tournament",
            aggregate_id=str(tournament.id),
            data=event.to_data_dict(),
        )

        db.commit()
        db.refresh(tournament)

        logger.info(f"Finished tournament {tournament.id}")
        return TournamentResponse(**tournament.to_dict(include_ranking=False))

    except Exception as e:
        db.rollback()
        logger.error(f"Error finishing tournament: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finishing tournament: {str(e)}",
        )


@router.put(
    "/tournaments/{tournament_id}/competitors/add", response_model=TournamentResponse
)
async def add_competitors_to_tournament(
    tournament_id: UUID,
    competitors: List[CompetitorInput],
    db: Session = Depends(get_db_session),
):
    """Add competitors to a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    try:
        for competitor_input in competitors:
            add_competitor(db, tournament_id, competitor_input)

        db.commit()
        logger.info(f"Added competitors to tournament {tournament_id}")

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding competitors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding competitors: {str(e)}",
        )

    return TournamentResponse(**tournament.to_dict(include_ranking=False))


@router.put(
    "/tournaments/{tournament_id}/competitors/remove", response_model=TournamentResponse
)
async def remove_competitors_from_tournament(
    tournament_id: UUID,
    competitor_ids: List[UUID],
    db: Session = Depends(get_db),
):
    """Remove competitors from a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    engine = FormatRegistry.get_engine(tournament.format)
    if not engine:
        logger.warning(
            f"No format engine found for format {tournament.format}, skipping format-specific competitor removal logic"
        )

    for competitor_id in competitor_ids:

        stmt_tc = db.query(TournamentCompetitor).filter(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.id == competitor_id,
        )
        tc = stmt_tc.first()
        if not tc:
            logger.warning(
                f"Competitor with ID {competitor_id} not found in tournament {tournament_id}, skipping"
            )
            continue

        if engine:
            engine.on_competitor_removed(db, tc)
            db.flush()

        # Now delete the competitor from the tournament
        stmt_tc.delete()
        db.flush()

        # Emit event for removed competitor
        event = TournamentCompetitorDeletedV1.create(
            aggregate_id=competitor_id,
            data=TournamentCompetitorDeletedData(
                competitor_id=competitor_id,
                tournament_id=tournament_id,
            ),
        )
        outbox_publisher.emit_event(
            db=db,
            event_type=event.event_type(),
            aggregate_type="tournament_competitor",
            aggregate_id=str(competitor_id),
            data=event.to_data_dict(),
        )

    db.commit()
    logger.info(f"Removed competitors from tournament {tournament_id}")

    return TournamentResponse(**tournament.to_dict(include_ranking=False))


@router.get(
    "/tournaments/{tournament_id}/standings", response_model=TournamentStandingsResponse
)
async def get_tournament_standings(tournament_id: UUID, db: Session = Depends(get_db)):
    """Get the current standings for a tournament in a format-agnostic way."""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    engine = FormatRegistry.get_engine(tournament.format)
    if not engine:
        logger.warning(
            f"No format engine found for format {tournament.format}, cannot provide standings"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No format engine found for format {tournament.format}, cannot provide standings",
        )

    # Build response
    try:
        standings = engine.get_standings(db, tournament_id)
        return TournamentStandingsResponse(
            standings=(
                [
                    TournamentStandingsResponse._TournamentStandingsEntry(
                        competitor_id=entry.competitor_id,
                        position=entry.position,
                        format_meta=entry.format_meta,
                    )
                    for entry in standings
                ]
                if standings is not None
                else None
            )
        )
    except Exception as e:
        logger.error(f"Error getting standings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting standings: {str(e)}",
        )


@router.put(
    "/tournaments/{tournament_id}/format-meta",
    response_model=TournamentResponse,
)
async def update_tournament_format_meta(
    tournament_id: UUID,
    data: TournamentFormatMetaUpdate,
    db: Session = Depends(get_db),
):
    """Update the format meta of a tournament"""
    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    engine = FormatRegistry.get_engine(tournament.format)
    if not engine:
        logger.warning(
            f"No format engine found for format {tournament.format}, cannot update format meta"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No format engine found for format {tournament.format}, cannot update format meta",
        )

    try:
        engine.update_tournament(tournament, data.format_meta)
        db.commit()
        db.refresh(tournament)

        logger.info(f"Updated format meta for tournament {tournament.id}")
        return TournamentResponse(**tournament.to_dict(include_ranking=False))

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating format meta: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating format meta: {str(e)}",
        )


# ==================== Health Check ====================


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tournaments-service"}
