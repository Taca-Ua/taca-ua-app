"""
Ranking computation logic.

Derives the three ranking tables (ModalityRanking, CourseRanking,
GeneralRanking) from the core tables populated by event handlers.

Computation rules
-----------------
For every finished tournament:
1. Count participants (TournamentCompetitor rows) to pick the right escalao.
2. Look up the ModalityTypeEscalao whose [min_participants, max_participants]
   range covers the participant count.
3. Award escalao.points[position - 1] to each result position; positions
   beyond the points array receive 0 points.
4. Accumulate per (modality, course) → ModalityRanking.
5. Roll up ModalityRanking per course → CourseRanking (with per-modality
   breakdown) and GeneralRanking (total only).

This module is intentionally free of I/O side-effects: all it does is
read from the DB session passed in, clear the derived tables, and write
the recomputed rows back.  Commit/rollback is left to the caller.
"""

from collections import defaultdict
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from .logger import logger
from .models import (
    CourseRanking,
    GeneralRanking,
    Modality,
    ModalityRanking,
    ModalityTypeEscalao,
    Tournament,
    TournamentCompetitor,
    TournamentResult,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_escalao(
    escaloes: List[ModalityTypeEscalao], participant_count: int
) -> Optional[ModalityTypeEscalao]:
    """Return the escalao whose participant range covers *participant_count*."""
    for escalao in escaloes:
        if (
            escalao.min_participants is not None
            and participant_count < escalao.min_participants
        ):
            continue
        if (
            escalao.max_participants is not None
            and participant_count > escalao.max_participants
        ):
            continue
        return escalao
    return None


def _points_for_position(escalao: ModalityTypeEscalao, position: int) -> int:
    """Return the points awarded for *position* (1-indexed) from the escalao."""
    idx = position - 1
    if idx < 0 or idx >= len(escalao.points):
        return 0
    return escalao.points[idx]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


<<<<<<< HEAD
def compute_all_rankings(db: Session) -> int:
=======
def compute_all_rankings(db: Session, season_id=None) -> None:
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd
    """
    Recompute derived ranking tables for a given season (or all unscoped
    data when season_id is None).

    Steps:
    1. Clear GeneralRanking, CourseRanking, ModalityRanking rows for this season.
    2. Iterate over every modality; for each tournament in that modality that
       has results, compute per-course points using the matching escalao.
    3. Persist ModalityRanking rows.
    4. Aggregate to CourseRanking and GeneralRanking rows.

    The caller is responsible for committing or rolling back the session.
    """
<<<<<<< HEAD
    logger.info("ranking_computation_started")
    count = 0
=======
    logger.info("ranking_computation_started", season_id=str(season_id) if season_id else None)
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd

    # --- 1. Clear derived tables for this season --------------------------
    db.query(GeneralRanking).filter(GeneralRanking.season_id == season_id).delete()
    db.query(CourseRanking).filter(CourseRanking.season_id == season_id).delete()
    db.query(ModalityRanking).filter(ModalityRanking.season_id == season_id).delete()
    db.flush()

    # --- 2. Load modalities and their escaloes in bulk ----------------------
    modalities: List[Modality] = db.query(Modality).all()
    if not modalities:
        logger.info("ranking_computation_skipped", reason="no modalities")
        return

    # Stable ordering for the modality_breakdown array in CourseRanking
    ordered_modality_ids: List[UUID] = sorted(
        (m.modality_id for m in modalities), key=str
    )

    # escaloes keyed by scoring_format_id (modality_type_id)
    all_escaloes: List[ModalityTypeEscalao] = db.query(ModalityTypeEscalao).all()
    escaloes_by_type: Dict[UUID, List[ModalityTypeEscalao]] = defaultdict(list)
    for e in all_escaloes:
        escaloes_by_type[e.modality_type_id].append(e)

    # --- 3. Accumulate points per (modality_id, course_id) ------------------
    # modality_id -> {course_id -> points}
    modality_course_points: Dict[UUID, Dict[UUID, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for modality in modalities:
        tournaments: List[Tournament] = (
            db.query(Tournament)
            .filter(
                Tournament.modality_id == modality.modality_id,
                Tournament.season_id == season_id,
            )
            .all()
        )

        for tournament in tournaments:
            tid = tournament.tournament_id

            # Only process tournaments that actually have results
            results: List[TournamentResult] = (
                db.query(TournamentResult)
                .filter(TournamentResult.tournament_id == tid)
                .all()
            )
            if not results:
                continue

            tournament_competitors: List[TournamentCompetitor] = (
                db.query(TournamentCompetitor)
                .filter(TournamentCompetitor.tournament_id == tid)
                .all()
            )
            participant_count: int = len(tournament_competitors)
            course_by_competitor: Dict[UUID, UUID] = {
                tc.competitor_id: tc.competitor_course_id
                for tc in tournament_competitors
            }

            if tournament.scoring_format_id is None:
                logger.warning(
                    "tournament_without_scoring_format",
                    tournament_id=str(tid),
                    modality_id=str(modality.modality_id),
                )
                continue

            escaloes = escaloes_by_type.get(tournament.scoring_format_id, [])

            escalao = _find_escalao(escaloes, participant_count)
            if escalao is None:
                logger.warning(
                    "no_escalao_for_tournament",
                    tournament_id=str(tid),
                    participant_count=participant_count,
                    scoring_format_id=str(tournament.scoring_format_id),
                )
                continue

            print(
                f"Tournament {tid} has {participant_count} participants, using escalao with points {escalao.points}"
            )
            print(f"Processing {len(results)} results for tournament {tid}")

            # Group results by position to handle ties
            results_by_position: Dict[int, List[TournamentResult]] = defaultdict(list)
            for result in results:
                results_by_position[result.position].append(result)

            for position, tied_results in results_by_position.items():
                n = len(tied_results)
                # Average the points over the range of positions the tied competitors occupy
                total_pts = sum(
                    _points_for_position(escalao, position + i) for i in range(n)
                )
                pts = round(total_pts / n)
                if pts:
                    for result in tied_results:
                        course_id = course_by_competitor.get(result.competitor_id)
                        if course_id is None:
                            logger.warning(
                                "result_competitor_not_found_in_tournament_competitors",
                                tournament_id=str(tid),
                                competitor_id=str(result.competitor_id),
                            )
                            continue
                        modality_course_points[modality.modality_id][course_id] += pts

    # --- 4. Persist ModalityRanking -----------------------------------------
    for modality_id, course_points in modality_course_points.items():
        for course_id, pts in course_points.items():
            db.add(
                ModalityRanking(
                    modality_id=modality_id,
                    course_id=course_id,
                    season_id=season_id,
                    points=pts,
                )
            )
            count += 1
    db.flush()

    # --- 5. Aggregate → CourseRanking + GeneralRanking ----------------------
    # Collect every course that has at least one point
    all_course_ids: set = set()
    for course_points in modality_course_points.values():
        all_course_ids.update(course_points.keys())

    for course_id in all_course_ids:
        breakdown: List[int] = [
            modality_course_points.get(mid, {}).get(course_id, 0)
            for mid in ordered_modality_ids
        ]
        total: int = sum(breakdown)

        db.add(
            CourseRanking(
                course_id=course_id, season_id=season_id, points=total, modality_breakdown=breakdown
            )
        )
<<<<<<< HEAD
        db.add(GeneralRanking(course_id=course_id, points=total))
        count += 2  # one CourseRanking + one GeneralRanking per course
        print(
            f"Course {course_id} has total {total} points with breakdown {breakdown}",
            flush=True,
        )
=======
        db.add(GeneralRanking(course_id=course_id, season_id=season_id, points=total))
>>>>>>> 02edffb2045a79c2f37d752e668240a5161cf0dd

    db.flush()

    logger.info(
        "ranking_computation_completed",
        modalities=len(modality_course_points),
        courses=len(all_course_ids),
    )

    return count


def emit_ranking_computed_event(db: Session, publisher, season_id=None) -> None:
    """
    Build and persist a RankingComputedV1 outbox event from the current
    state of the derived ranking tables for the given season.

    Must be called **after** :func:`compute_all_rankings` and **before**
    the session is committed so that the outbox row is written in the same
    transaction as the ranking data.

    Parameters
    ----------
    db:
        Active SQLAlchemy ``Session`` (must have the freshly flushed
        ranking rows visible).
    publisher:
        An :class:`~taca_outbox.OutboxPublisher` instance used to persist
        the event to the outbox table.
    season_id:
        The season UUID to scope this event to (or None for unscoped).
    """
    from taca_events.pydantic_schemas.ranking import (
        GeneralRankingEntryData,
        ModalityRankingEntryData,
        RankingComputedData,
        RankingComputedV1,
    )

    general_rows: List[GeneralRanking] = (
        db.query(GeneralRanking).filter(GeneralRanking.season_id == season_id).all()
    )
    modality_rows: List[ModalityRanking] = (
        db.query(ModalityRanking).filter(ModalityRanking.season_id == season_id).all()
    )

    # Count distinct tournaments each course has at least one result in
    from .models import TournamentCompetitor as TC
    from .models import TournamentResult as TR

    tournaments_by_course: Dict[UUID, int] = {}
    for row in general_rows:
        count = (
            db.query(func.count(func.distinct(TC.tournament_id)))
            .join(
                TR,
                and_(
                    TR.tournament_id == TC.tournament_id,
                    TR.competitor_id == TC.competitor_id,
                ),
            )
            .filter(TC.competitor_course_id == row.course_id)
            .scalar()
            or 0
        )
        tournaments_by_course[row.course_id] = count

    general_data = [
        GeneralRankingEntryData(
            course_id=r.course_id,
            points=r.points,
            tournaments_participated=tournaments_by_course.get(r.course_id, 0),
        )
        for r in general_rows
    ]
    modality_data = [
        ModalityRankingEntryData(
            modality_id=r.modality_id,
            course_id=r.course_id,
            points=r.points,
        )
        for r in modality_rows
    ]

    aggregate_id = uuid4()
    event = RankingComputedV1.create(
        aggregate_id=aggregate_id,
        data=RankingComputedData(
            general_ranking=general_data,
            modality_rankings=modality_data,
            season_id=season_id,
        ),
    )
    publisher.emit_event(
        db=db,
        event_type=event.event_type(),
        aggregate_type=event.aggregate_type(),
        aggregate_id=str(aggregate_id),
        data=event.to_data_dict(),
    )

    logger.info(
        "ranking_computed_event_queued",
        general_entries=len(general_data),
        modality_entries=len(modality_data),
    )
