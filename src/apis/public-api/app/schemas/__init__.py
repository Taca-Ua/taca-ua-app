"""
Pydantic schemas package for public API
"""

from .calendar import MatchPublicDetail, MatchPublicList
from .courses import CoursePublic
from .history import HistoricalMatch, HistoricalRanking
from .modalities import ModalityPublic
from .rankings import CourseRanking, GeneralRanking, ModalityRanking, RankingEntry
from .regulations import RegulationPublic
from .results import ResultPublic
from .seasons import SeasonPublic
from .teams import TeamPublic
from .tournaments import (
    TournamentPublicDetail,
    TournamentPublicList,
    TournamentRankingEntry,
    TournamentRankings,
)

__all__ = [
    # Calendar
    "MatchPublicList",
    "MatchPublicDetail",
    # Results
    "ResultPublic",
    # Rankings
    "RankingEntry",
    "ModalityRanking",
    "CourseRanking",
    "GeneralRanking",
    # Tournaments
    "TournamentPublicList",
    "TournamentPublicDetail",
    "TournamentRankings",
    "TournamentRankingEntry",
    # Modalities
    "ModalityPublic",
    # Courses
    "CoursePublic",
    # Regulations
    "RegulationPublic",
    # History
    "HistoricalMatch",
    "HistoricalRanking",
    # Seasons
    "SeasonPublic",
    # Teams
    "TeamPublic",
]
