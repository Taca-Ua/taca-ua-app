"""
Pydantic schemas for Public API responses.

These schemas validate and serialize data from the materialized views
in the public_read schema.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ==================== TeamDetailView Schemas ====================


class TeamDetail(BaseModel):
    """Schema for team detail view response."""

    model_config = ConfigDict(from_attributes=True)

    team_id: UUID = Field(..., description="Unique identifier for the team")
    team_name: str = Field(..., description="Name of the team")

    # Course info
    course_id: UUID = Field(..., description="Course identifier")
    course_name: str = Field(..., description="Full name of the course")
    course_abbreviation: str = Field(..., description="Course abbreviation")

    # Nucleo info
    nucleo_id: UUID = Field(..., description="Nucleo identifier")
    nucleo_name: str = Field(..., description="Full name of the nucleo")
    nucleo_abbreviation: str = Field(..., description="Nucleo abbreviation")
    nucleo_logo_url: Optional[str] = Field(None, description="Nucleo logo URL")

    # Modality info
    modality_id: UUID = Field(..., description="Modality identifier")
    modality_name: Optional[str] = Field(None, description="Modality name")
    modality_type_id: UUID = Field(..., description="Modality type identifier")
    modality_type_name: str = Field(..., description="Type of modality")

    # Statistics
    player_count: int = Field(..., ge=0, description="Number of players in the team")
    players: Optional[list[dict[str, Any]]] = Field(
        None, description="List of players with their details"
    )


class TeamDetailList(BaseModel):
    """Schema for paginated list of team details."""

    items: list[TeamDetail] = Field(..., description="List of team details")
    total: int = Field(..., ge=0, description="Total number of teams")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# ==================== StudentDetailView Schemas ====================


class StudentDetail(BaseModel):
    """Schema for student detail view response."""

    model_config = ConfigDict(from_attributes=True)

    student_id: UUID = Field(..., description="Unique identifier for the student")
    student_number: str = Field(..., description="Student number")
    full_name: str = Field(..., description="Full name of the student")
    is_member: bool = Field(..., description="Whether the student is a member")

    # Course info
    course_id: UUID = Field(..., description="Course identifier")
    course_name: str = Field(..., description="Full name of the course")
    course_abbreviation: str = Field(..., description="Course abbreviation")

    # Nucleo info
    nucleo_id: UUID = Field(..., description="Nucleo identifier")
    nucleo_name: str = Field(..., description="Full name of the nucleo")
    nucleo_abbreviation: str = Field(..., description="Nucleo abbreviation")

    # Statistics
    team_count: int = Field(..., ge=0, description="Number of teams the student is in")


class StudentDetailList(BaseModel):
    """Schema for paginated list of student details."""

    items: list[StudentDetail] = Field(..., description="List of student details")
    total: int = Field(..., ge=0, description="Total number of students")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# ==================== TournamentDetailView Schemas ====================


class TournamentDetail(BaseModel):
    """Schema for tournament detail view response."""

    model_config = ConfigDict(from_attributes=True)

    tournament_id: UUID = Field(..., description="Unique identifier for the tournament")
    tournament_name: str = Field(..., description="Name of the tournament")
    start_date: date = Field(..., description="Tournament start date")
    status: str = Field(..., description="Tournament status")

    # Modality info
    modality_id: UUID = Field(..., description="Modality identifier")
    modality_name: Optional[str] = Field(None, description="Modality name")
    modality_type_id: UUID = Field(..., description="Modality type identifier")
    modality_type_name: str = Field(..., description="Type of modality")

    # Statistics
    competitor_count: int = Field(
        ..., ge=0, description="Number of competitors in the tournament"
    )
    match_count: int = Field(
        ..., ge=0, description="Number of matches in the tournament"
    )


class TournamentDetailList(BaseModel):
    """Schema for paginated list of tournament details."""

    items: list[TournamentDetail] = Field(..., description="List of tournament details")
    total: int = Field(..., ge=0, description="Total number of tournaments")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# ==================== MatchDetailView Schemas ====================


class MatchDetail(BaseModel):
    """Schema for match detail view response."""

    model_config = ConfigDict(from_attributes=True)

    match_id: UUID = Field(..., description="Unique identifier for the match")
    location: str = Field(..., description="Match location")
    status: str = Field(..., description="Match status")
    start_time: datetime = Field(..., description="Match start time")

    # Tournament info
    tournament_id: UUID = Field(..., description="Tournament identifier")
    tournament_name: str = Field(..., description="Tournament name")

    # Modality info
    modality_id: UUID = Field(..., description="Modality identifier")
    modality_name: Optional[str] = Field(None, description="Modality name")

    # Participants and results
    participants: list[dict[str, Any]] = Field(
        ..., description="List of participants with their details"
    )
    results: Optional[list[dict[str, Any]]] = Field(
        None, description="List of results with scores/positions"
    )

    # Statistics
    participant_count: int = Field(
        ..., ge=0, description="Number of participants in the match"
    )
    comment_count: int = Field(..., ge=0, description="Number of comments on the match")


class MatchDetailList(BaseModel):
    """Schema for paginated list of match details."""

    items: list[MatchDetail] = Field(..., description="List of match details")
    total: int = Field(..., ge=0, description="Total number of matches")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# ==================== TournamentStandingsView Schemas ====================


class TournamentStanding(BaseModel):
    """Schema for tournament standings response."""

    model_config = ConfigDict(from_attributes=True)

    tournament_id: UUID = Field(..., description="Tournament identifier")
    competitor_type: str = Field(..., description="Type of competitor (team/athlete)")
    competitor_entity_id: UUID = Field(..., description="Competitor entity ID")
    competitor_name: str = Field(..., description="Name of the competitor")
    position: Optional[int] = Field(None, ge=1, description="Position in the standings")

    # Additional metadata
    statistics_metadata: Optional[dict[str, Any]] = Field(
        None, description="Additional statistics metadata"
    )


class TournamentStandingsList(BaseModel):
    """Schema for list of tournament standings."""

    items: list[TournamentStanding] = Field(
        ..., description="List of tournament standings"
    )
    total: int = Field(..., ge=0, description="Total number of standings")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# ==================== Common Schemas ====================


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Current timestamp")


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


# ==================== GeneralRankingView Schemas ====================


class GeneralRanking(BaseModel):
    """Schema for general ranking view response."""

    model_config = ConfigDict(from_attributes=True)

    # Course info
    course_id: UUID = Field(..., description="Course identifier")
    course_name: str = Field(..., description="Full name of the course")
    course_abbreviation: str = Field(..., description="Course abbreviation")

    # Nucleo info
    nucleo_id: UUID = Field(..., description="Nucleo identifier")
    nucleo_name: str = Field(..., description="Full name of the nucleo")
    nucleo_abbreviation: str = Field(..., description="Nucleo abbreviation")

    # Ranking data
    points: int = Field(..., ge=0, description="Total points earned by the course")
    rank: Optional[int] = Field(None, ge=1, description="Position in the ranking")
    tournaments_participated: int = Field(
        ..., ge=0, description="Number of tournaments participated"
    )


class GeneralRankingList(BaseModel):
    """Schema for list of general rankings."""

    items: list[GeneralRanking] = Field(..., description="List of course rankings")
    total: int = Field(..., ge=0, description="Total number of courses ranked")


# ==================== Regulation Schemas ====================


class RegulationPublic(BaseModel):
    """Schema for a public regulation document."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique identifier")
    title: str = Field(..., description="Regulation title")
    description: Optional[str] = Field(None, description="Optional description")
    file_url: str = Field(..., description="URL to the PDF file")


# ==================== ModalityRankingView Schemas ====================


class ModalityRanking(BaseModel):
    """Schema for modality-specific ranking view response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier for the ranking entry")

    # Modality info
    modality_id: UUID = Field(..., description="Modality identifier")
    modality_name: Optional[str] = Field(None, description="Modality name")

    # Course info
    course_id: UUID = Field(..., description="Course identifier")
    course_name: str = Field(..., description="Full name of the course")
    course_abbreviation: str = Field(..., description="Course abbreviation")

    # Nucleo info
    nucleo_id: UUID = Field(..., description="Nucleo identifier")
    nucleo_name: str = Field(..., description="Full name of the nucleo")
    nucleo_abbreviation: str = Field(..., description="Nucleo abbreviation")

    # Ranking data
    points: int = Field(
        ..., ge=0, description="Total points earned by the course in the modality"
    )
    rank: Optional[int] = Field(
        None, ge=1, description="Position in the ranking within the modality"
    )


class ModalityRankingList(BaseModel):
    """Schema for list of modality rankings."""

    items: list[ModalityRanking] = Field(..., description="List of course rankings")
    total: int = Field(
        ..., ge=0, description="Total number of course rankings in the result"
    )


# ==================== Nucleo Schemas ====================


class NucleoPublic(BaseModel):
    """Schema for a nucleo (organisational unit)."""

    model_config = ConfigDict(from_attributes=True)

    nucleo_id: UUID = Field(..., description="Unique identifier for the nucleo")
    name: str = Field(..., description="Full name of the nucleo")
    abbreviation: str = Field(..., description="Short abbreviation")
    logo_url: Optional[str] = Field(None, description="Logo image URL")


class NucleoList(BaseModel):
    """Schema for paginated list of nucleos."""

    items: list[NucleoPublic] = Field(..., description="List of nucleos")
    total: int = Field(..., ge=0, description="Total number of nucleos")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")


# ==================== Season Schemas ====================


class SeasonDetail(BaseModel):
    """Schema for season detail view response."""

    model_config = ConfigDict(from_attributes=True)

    season_id: int = Field(..., description="Unique identifier for the season")
    name: str = Field(..., description="Season name")
    is_active: bool = Field(
        ..., description="Whether this is the current active season"
    )


class SeasonDetailList(BaseModel):
    """Schema for paginated list of seasons."""

    items: list[SeasonDetail] = Field(..., description="List of season details")
    total: int = Field(..., ge=0, description="Total number of seasons")


# ==================== HomePageConfig Schemas ====================


class HomePageSponsor(BaseModel):
    """Schema for a sponsor on the home page."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(..., description="Name of the sponsor")
    logo_url: Optional[str] = Field(None, description="URL to the sponsor's logo")
    website_url: Optional[str] = Field(None, description="URL to the sponsor's website")


class HomePageConfig(BaseModel):
    """Schema for home page configuration."""

    model_config = ConfigDict(from_attributes=True)

    title: str = Field(..., description="Title of the home page")
    subtitle: str = Field(..., description="Subtitle of the home page")
    welcome_message: str = Field(..., description="Welcome message for visitors")
    about_us: str = Field(..., description="About us section content")
    hero_image_url: Optional[str] = Field(
        None, description="URL to the hero image on the home page"
    )
    sponsors: list[HomePageSponsor] = Field(
        ..., description="List of sponsors to display on the home page"
    )
