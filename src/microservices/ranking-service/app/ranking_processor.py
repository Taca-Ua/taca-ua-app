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
from uuid import UUID

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


def compute_all_rankings(db: Session) -> None:
    """
    Recompute all derived ranking tables from the current core-table state.

    Steps:
    1. Clear GeneralRanking, CourseRanking, ModalityRanking.
    2. Iterate over every modality; for each tournament in that modality that
       has results, compute per-course points using the matching escalao.
    3. Persist ModalityRanking rows.
    4. Aggregate to CourseRanking and GeneralRanking rows.

    The caller is responsible for committing or rolling back the session.
    """
    logger.info("ranking_computation_started")

    # --- 1. Clear derived tables -------------------------------------------
    db.query(GeneralRanking).delete()
    db.query(CourseRanking).delete()
    db.query(ModalityRanking).delete()
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
            .filter(Tournament.modality_id == modality.modality_id)
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

            participant_count: int = (
                db.query(TournamentCompetitor)
                .filter(TournamentCompetitor.tournament_id == tid)
                .count()
            )

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

            for result in results:
                pts = _points_for_position(escalao, result.position)
                if pts:
                    modality_course_points[modality.modality_id][
                        result.competitor_id
                    ] += pts

    # --- 4. Persist ModalityRanking -----------------------------------------
    for modality_id, course_points in modality_course_points.items():
        for course_id, pts in course_points.items():
            db.add(
                ModalityRanking(
                    modality_id=modality_id,
                    course_id=course_id,
                    points=pts,
                )
            )
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
                course_id=course_id, points=total, modality_breakdown=breakdown
            )
        )
        db.add(GeneralRanking(course_id=course_id, points=total))

    db.flush()

    logger.info(
        "ranking_computation_completed",
        modalities=len(modality_course_points),
        courses=len(all_course_ids),
    )
