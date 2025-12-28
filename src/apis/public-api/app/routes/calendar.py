"""
Calendar/Matches routes
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Query

from ..schemas import MatchPublicDetail, MatchPublicList

router = APIRouter(prefix="/api/public", tags=["Calendar"])


@router.get(
    "/matches",
    response_model=List[MatchPublicList],
    summary="List matches with filters",
    description="Get a list of matches filtered by date, modality, course, team, or status",
)
async def list_matches(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    modality_id: Optional[int] = Query(None, description="Filter by modality ID"),
    course_id: Optional[int] = Query(None, description="Filter by course ID"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    status: Optional[str] = Query(
        None, description="Filter by status (scheduled, finished)"
    ),
    limit: Optional[int] = Query(50, description="Number of results to return"),
    offset: Optional[int] = Query(0, description="Number of results to skip"),
):
    """List matches with optional filters"""
    # Mock database with matches across December 2025 and January 2026
    # Map modality IDs to names
    modality_names = {
        1: "Futebol",
        2: "Futsal",
        3: "Andebol",
        4: "Voleibol",
    }

    # Map course IDs to abbreviations
    course_abbr = {
        1: "NEI",
        2: "NEC",
        3: "NET",
        4: "NEMat",
        5: "NEGeo",
    }

    # Map tournament IDs to names
    tournament_names = {
        1: "Campeonato de Futebol 25/26",
        2: "Campeonato de Futsal 25/26",
        3: "Torneio de Andebol 25/26",
        4: "Liga de Voleibol 25/26",
    }

    dummy_matches = [
        # November 28, 2025 (Past - Finished)
        {
            "id": 14,
            "tournament_id": 1,
            "tournament_name": tournament_names[1],
            "modality": {
                "id": 1,
                "name": modality_names[1],
            },
            "team_home": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "team_away": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "location": "Campo Exterior UA",
            "start_time": datetime(2025, 11, 28, 15, 0),
            "status": "finished",
            "home_score": 3,
            "away_score": 2,
        },
        {
            "id": 15,
            "tournament_id": 2,
            "tournament_name": tournament_names[2],
            "modality": {
                "id": 2,
                "name": modality_names[2],
            },
            "team_home": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "team_away": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 11, 28, 17, 0),
            "status": "finished",
            "home_score": 4,
            "away_score": 4,
        },
        # November 30, 2025 (Past - Finished)
        {
            "id": 16,
            "tournament_id": 3,
            "tournament_name": tournament_names[3],
            "modality": {
                "id": 3,
                "name": modality_names[3],
            },
            "team_home": {
                "id": 5,
                "name": "NEGeo",
                "course_abbreviation": course_abbr[5],
            },
            "team_away": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 11, 30, 14, 0),
            "status": "finished",
            "home_score": 25,
            "away_score": 28,
        },
        {
            "id": 1,
            "tournament_id": 1,
            "tournament_name": tournament_names[1],
            "modality": {
                "id": 1,
                "name": modality_names[1],
            },
            "team_home": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "team_away": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 3, 14, 0),
            "status": "finished",
            "home_score": 2,
            "away_score": 1,
        },
        {
            "id": 2,
            "tournament_id": 2,
            "tournament_name": tournament_names[2],
            "modality": {
                "id": 2,
                "name": modality_names[2],
            },
            "team_home": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "team_away": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 3, 16, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        # December 7, 2025
        {
            "id": 3,
            "tournament_id": 2,
            "tournament_name": tournament_names[2],
            "modality": {
                "id": 2,
                "name": modality_names[2],
            },
            "team_home": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "team_away": {
                "id": 5,
                "name": "NEGeo",
                "course_abbreviation": course_abbr[5],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 7, 14, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 4,
            "tournament_id": 3,
            "tournament_name": tournament_names[3],
            "modality": {
                "id": 3,
                "name": modality_names[3],
            },
            "team_home": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "team_away": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 7, 16, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 5,
            "tournament_id": 3,
            "tournament_name": tournament_names[3],
            "modality": {
                "id": 3,
                "name": modality_names[3],
            },
            "team_home": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "team_away": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 7, 18, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        # December 10, 2025
        {
            "id": 6,
            "tournament_id": 1,
            "tournament_name": tournament_names[1],
            "modality": {
                "id": 1,
                "name": modality_names[1],
            },
            "team_home": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "team_away": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "location": "Campo Exterior UA",
            "start_time": datetime(2025, 12, 10, 15, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        # December 14, 2025
        {
            "id": 7,
            "tournament_id": 4,
            "tournament_name": tournament_names[4],
            "modality": {
                "id": 4,
                "name": modality_names[4],
            },
            "team_home": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "team_away": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 14, 14, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 8,
            "tournament_id": 4,
            "tournament_name": tournament_names[4],
            "modality": {
                "id": 4,
                "name": modality_names[4],
            },
            "team_home": {
                "id": 5,
                "name": "NEGeo",
                "course_abbreviation": course_abbr[5],
            },
            "team_away": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 14, 16, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        # December 17, 2025
        {
            "id": 9,
            "tournament_id": 2,
            "tournament_name": tournament_names[2],
            "modality": {
                "id": 2,
                "name": modality_names[2],
            },
            "team_home": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "team_away": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 17, 15, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        # December 21, 2025
        {
            "id": 10,
            "tournament_id": 1,
            "tournament_name": tournament_names[1],
            "modality": {
                "id": 1,
                "name": modality_names[1],
            },
            "team_home": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "team_away": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "location": "Campo Exterior UA",
            "start_time": datetime(2025, 12, 21, 14, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 11,
            "tournament_id": 3,
            "tournament_name": tournament_names[3],
            "modality": {
                "id": 3,
                "name": modality_names[3],
            },
            "team_home": {
                "id": 5,
                "name": "NEGeo",
                "course_abbreviation": course_abbr[5],
            },
            "team_away": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 21, 16, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        # January 2026
        {
            "id": 12,
            "tournament_id": 2,
            "tournament_name": tournament_names[2],
            "modality": {
                "id": 2,
                "name": modality_names[2],
            },
            "team_home": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "team_away": {
                "id": 5,
                "name": "NEGeo",
                "course_abbreviation": course_abbr[5],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2026, 1, 7, 15, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
        {
            "id": 13,
            "tournament_id": 4,
            "tournament_name": tournament_names[4],
            "modality": {
                "id": 4,
                "name": modality_names[4],
            },
            "team_home": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "team_away": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2026, 1, 11, 14, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        },
    ]

    # Apply filters
    filtered_matches = dummy_matches

    if date:
        # Filter by exact date
        filter_date = datetime.strptime(date, "%Y-%m-%d").date()
        filtered_matches = [
            m for m in filtered_matches if m["start_time"].date() == filter_date
        ]

    if modality_id:
        filtered_matches = [
            m for m in filtered_matches if m["modality"]["id"] == modality_id
        ]

    if course_id:
        # Need to check both home and away teams
        filtered_matches = [
            m
            for m in filtered_matches
            if (m["team_home"]["id"] == course_id or m["team_away"]["id"] == course_id)
        ]

    if team_id:
        filtered_matches = [
            m
            for m in filtered_matches
            if (m["team_home"]["id"] == team_id or m["team_away"]["id"] == team_id)
        ]

    if status:
        filtered_matches = [m for m in filtered_matches if m["status"] == status]

    return filtered_matches[offset : offset + limit]


@router.get(
    "/matches/today",
    response_model=List[MatchPublicList],
    summary="Get today's matches",
    description="Get all matches scheduled for today",
)
async def list_today_matches():
    """Get today's matches"""
    return [
        {
            "id": 5,
            "tournament_id": 1,
            "modality_id": 1,
            "team_home_id": 2,
            "team_away_id": 3,
            "team_home_name": "LEI A",
            "team_away_name": "MIEET A",
            "course_home_id": 2,
            "course_away_id": 3,
            "location": "Campo Principal",
            "start_time": datetime(2025, 12, 1, 18, 0),
            "status": "scheduled",
            "home_score": None,
            "away_score": None,
        }
    ]


@router.get(
    "/matches/{match_id}",
    response_model=MatchPublicDetail,
    summary="Get match details",
    description="Get detailed information about a specific match",
)
async def get_match_detail(match_id: int):
    """Get match details by ID"""
    # Create the same mock database structure used in list_matches
    modality_names = {
        1: "Futebol",
        2: "Futsal",
        3: "Andebol",
        4: "Voleibol",
    }

    course_abbr = {
        1: "NEI",
        2: "NEC",
        3: "NET",
        4: "NEMat",
        5: "NEGeo",
    }

    tournament_names = {
        1: "Campeonato de Futebol 25/26",
        2: "Campeonato de Futsal 25/26",
        3: "Torneio de Andebol 25/26",
        4: "Liga de Voleibol 25/26",
    }

    # Mock database with key matches (can expand this as needed)
    mock_matches = {
        1: {
            "id": 1,
            "tournament_id": 1,
            "tournament_name": tournament_names[1],
            "modality": {"id": 1, "name": modality_names[1]},
            "team_home": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "team_away": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 12, 3, 14, 0),
            "status": "finished",
            "home_score": 2,
            "away_score": 1,
        },
        14: {
            "id": 14,
            "tournament_id": 1,
            "tournament_name": tournament_names[1],
            "modality": {"id": 1, "name": modality_names[1]},
            "team_home": {
                "id": 1,
                "name": "NEI",
                "course_abbreviation": course_abbr[1],
            },
            "team_away": {
                "id": 4,
                "name": "NEMat",
                "course_abbreviation": course_abbr[4],
            },
            "location": "Campo Exterior UA",
            "start_time": datetime(2025, 11, 28, 15, 0),
            "status": "finished",
            "home_score": 3,
            "away_score": 2,
        },
        15: {
            "id": 15,
            "tournament_id": 2,
            "tournament_name": tournament_names[2],
            "modality": {"id": 2, "name": modality_names[2]},
            "team_home": {
                "id": 2,
                "name": "NEC",
                "course_abbreviation": course_abbr[2],
            },
            "team_away": {
                "id": 3,
                "name": "NET",
                "course_abbreviation": course_abbr[3],
            },
            "location": "Pavilhão Gimnodesportivo da UA",
            "start_time": datetime(2025, 11, 28, 17, 0),
            "status": "finished",
            "home_score": 4,
            "away_score": 4,
        },
    }

    # Return the match if it exists, otherwise return a default
    if match_id in mock_matches:
        return mock_matches[match_id]

    # Default response for matches not in the detailed database
    return {
        "id": match_id,
        "tournament_id": 1,
        "tournament_name": "Campeonato de Futebol 25/26",
        "modality": {
            "id": 1,
            "name": "Futebol",
        },
        "team_home": {
            "id": 1,
            "name": "NEI",
            "course_abbreviation": "NEI",
        },
        "team_away": {
            "id": 2,
            "name": "NEC",
            "course_abbreviation": "NEC",
        },
        "location": "Pavilhão Gimnodesportivo da UA",
        "start_time": datetime(2025, 12, 3, 14, 0),
        "status": "scheduled",
        "home_score": None,
        "away_score": None,
    }
