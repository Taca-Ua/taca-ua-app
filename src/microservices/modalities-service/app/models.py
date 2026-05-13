"""
SQLAlchemy models for Modalities Service.
Schema: modalities
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, relationship
from taca_outbox.models import create_outbox_model
from taca_snapshots import modalities as snapshot_models

Base = declarative_base()

# OutboxEvent model — schema-bound via shared factory
OutboxEvent = create_outbox_model(Base, schema="modalities")


# Association tables for many-to-many relationships
team_players = Table(
    "team_players",
    Base.metadata,
    Column(
        "team_id",
        UUID(as_uuid=True),
        ForeignKey("modalities.team.id"),
        primary_key=True,
    ),
    Column(
        "student_id",
        UUID(as_uuid=True),
        ForeignKey("modalities.student.id"),
        primary_key=True,
    ),
    schema="modalities",
)

season_courses = Table(
    "season_course",
    Base.metadata,
    Column(
        "season_id",
        Integer,
        ForeignKey("modalities.season.id"),
        primary_key=True,
    ),
    Column(
        "course_id",
        UUID(as_uuid=True),
        ForeignKey("modalities.course.id"),
        primary_key=True,
    ),
    schema="modalities",
)


class SeasonModality(Base):  # need to be a full model to link modality_type
    """Association table linking Season, Modality, and ModalityType"""

    __tablename__ = "season_modality"
    __table_args__ = {"schema": "modalities"}

    season_id = Column(Integer, ForeignKey("modalities.season.id"), primary_key=True)
    modality_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.modality.id"), primary_key=True
    )
    modality_type_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.modality_type.id"), nullable=False
    )

    # Relationships
    season: Mapped["Season"] = relationship(
        "Season", back_populates="season_modalities"
    )
    modality: Mapped["Modality"] = relationship(
        "Modality", back_populates="season_modalities"
    )
    modality_type: Mapped["ModalityType"] = relationship(
        "ModalityType", back_populates="season_modalities"
    )


class Nucleo(Base):
    """Represents an academic nucleus"""

    __tablename__ = "nucleo"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    abbreviation = Column(Text, unique=True, nullable=False)
    logo_url = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )
    admins_ids = Column(ARRAY(Text), nullable=False, server_default="{}")

    # Relationships
    courses: Mapped[list["Course"]] = relationship("Course", back_populates="nucleo")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "abbreviation": self.abbreviation,
            "logo_url": self.logo_url,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "admins_ids": self.admins_ids,
            "courses": [
                course.to_dict(include_nucleo=False) for course in self.courses
            ],
        }

    def to_snapshot(self) -> snapshot_models.NucleoSnapshotItem:
        return snapshot_models.NucleoSnapshotItem(
            id=str(self.id),
            name=self.name,
            abbreviation=self.abbreviation,
            logo_url=self.logo_url,
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
            admins_ids=self.admins_ids,
        )


class Course(Base):
    """Represents an academic course"""

    __tablename__ = "course"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    abbreviation = Column(Text, unique=True, nullable=False)
    nucleo_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.nucleo.id"), nullable=False
    )
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    nucleo: Mapped["Nucleo"] = relationship("Nucleo", back_populates="courses")
    students = relationship("Student", back_populates="course")
    teams = relationship("Team", back_populates="course")
    seasons: Mapped[list["Season"]] = relationship(
        "Season", secondary=season_courses, back_populates="season_courses"
    )

    def to_dict(self, season_id: int = None, *, include_nucleo=True):
        return {
            "id": str(self.id),
            "name": self.name,
            "abbreviation": self.abbreviation,
            "nucleo": self.nucleo.to_dict() if self.nucleo and include_nucleo else None,
            "belongs_to_season": (
                any(season.id == season_id for season in self.seasons)
                if season_id is not None
                else False
            ),
            "relevant_season_ids": (
                [season.id for season in self.seasons] if self.seasons else []
            ),
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_snapshot(self) -> snapshot_models.CourseSnapshotItem:
        return snapshot_models.CourseSnapshotItem(
            id=str(self.id),
            name=self.name,
            abbreviation=self.abbreviation,
            nucleo_id=str(self.nucleo_id),
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Season(Base):
    """Represents a sports season"""

    __tablename__ = "season"
    __table_args__ = {"schema": "modalities"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    finished_by = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    season_modality_types: Mapped[list["ModalityType"]] = relationship(
        "ModalityType", back_populates="season"
    )
    season_modalities: Mapped[list["SeasonModality"]] = relationship(
        "SeasonModality", back_populates="season"
    )
    season_courses: Mapped[list["Course"]] = relationship(
        "Course", secondary=season_courses
    )
    season_teams: Mapped[list["Team"]] = relationship("Team", back_populates="season")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_by": str(self.created_by),
            "finished_by": str(self.finished_by) if self.finished_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }

    def to_snapshot(self) -> snapshot_models.SeasonSnapshotItem:
        return snapshot_models.SeasonSnapshotItem(
            id=self.id,
            name=self.name,
            created_by=str(self.created_by),
            finished_by=str(self.finished_by) if self.finished_by else None,
            created_at=self.created_at.isoformat() if self.created_at else None,
            finished_at=self.finished_at.isoformat() if self.finished_at else None,
        )


class ModalityType(Base):
    """Enumeration for modality types"""

    __tablename__ = "modality_type"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    escaloes = Column(JSON, nullable=True)  # Array of escaloes stored as JSON
    is_playoff = Column(
        Boolean, default=False
    )  # Indicates if this is the playoff modality type
    tournament_competitor_type = Column(
        Text, nullable=True
    )  # e.g. "individual", "team"
    season_id = Column(Integer, ForeignKey("modalities.season.id"), nullable=True)

    # bulshit fields
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    season_modalities: Mapped[list["SeasonModality"]] = relationship(
        "SeasonModality", back_populates="modality_type"
    )
    season: Mapped["Season"] = relationship(
        "Season", back_populates="season_modality_types"
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "escaloes": self.escaloes,
            "is_playoff": self.is_playoff,
            "tournament_competitor_type": self.tournament_competitor_type,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_snapshot(self) -> snapshot_models.ModalityTypeSnapshotItem:
        escaloes_list = []
        if self.escaloes:
            for escalo in self.escaloes:
                escaloes_list.append(
                    snapshot_models.ModalityTypeSnapshotItem.EscaloType(
                        name=escalo.get("escalao"),
                        min_participants=escalo.get("minParticipants"),
                        max_participants=escalo.get("maxParticipants"),
                        points=escalo.get("points"),
                    )
                )
        return snapshot_models.ModalityTypeSnapshotItem(
            id=str(self.id),
            name=self.name,
            description=self.description,
            escaloes=escaloes_list if escaloes_list else None,
            season_id=str(self.season_id) if self.season_id else None,
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Modality(Base):
    """Represents a sport modality"""

    __tablename__ = "modality"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, unique=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    teams = relationship("Team", back_populates="modality")
    season_modalities: Mapped[list["SeasonModality"]] = relationship(
        "SeasonModality", back_populates="modality"
    )

    def to_dict(self, season_id: int = None):
        # Get modality_type from the first available season_modality
        modality_type_data = None
        season_modality = None
        if self.season_modalities and season_id is not None:
            season_modality = next(
                (sm for sm in self.season_modalities if sm.season_id == season_id),
                None,
            )
            if season_modality and season_modality.modality_type:
                modality_type_data = season_modality.modality_type.to_dict()

        return {
            "id": str(self.id),
            "name": self.name,
            "modality_type": modality_type_data,
            "belongs_to_season": (
                season_modality.season_id is not None if season_modality else False
            ),
            "relevant_season_ids": (
                [sm.season_id for sm in self.season_modalities]
                if self.season_modalities
                else []
            ),
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_snapshot(self) -> snapshot_models.ModalitySnapshotItem:
        # Get modality_type_id from the first available season_modality
        modality_type_id = None
        if self.season_modalities and self.season_modalities[0].modality_type_id:
            modality_type_id = str(self.season_modalities[0].modality_type_id)

        return snapshot_models.ModalitySnapshotItem(
            id=str(self.id),
            name=self.name,
            modality_type_id=modality_type_id,
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Member(Base):
    """Base class for members (staff and students)"""

    __tablename__ = "member"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(Text, nullable=False)
    member_type = Column(String(50))  # Discriminator column
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )

    __mapper_args__ = {
        "polymorphic_identity": "member",
        "polymorphic_on": member_type,
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "full_name": self.full_name,
            "member_type": self.member_type,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Student(Member):
    """Represents a student"""

    __tablename__ = "student"
    __table_args__ = {"schema": "modalities"}

    id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.member.id"), primary_key=True
    )
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.course.id"), nullable=False
    )
    student_number = Column(Text, unique=True, nullable=False)
    is_member = Column(Boolean, default=False)

    # Relationships
    course = relationship("Course", back_populates="students")
    teams = relationship("Team", secondary=team_players, back_populates="players")

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "course": self.course.to_dict() if self.course else None,
                "student_number": self.student_number,
                "is_member": self.is_member,
            }
        )
        return base_dict

    def to_snapshot(self) -> snapshot_models.StudentSnapshotItem:
        return snapshot_models.StudentSnapshotItem(
            id=str(self.id),
            full_name=self.full_name,
            course_id=str(self.course_id),
            student_number=self.student_number,
            is_member=self.is_member,
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Staff(Member):
    """Represents a staff member"""

    __tablename__ = "staff"

    id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.member.id"), primary_key=True
    )
    staff_number = Column(Text, unique=True, nullable=True)
    contact = Column(Text, unique=True, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "staff",
    }

    __table_args__ = ({"schema": "modalities"},)

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "staff_number": self.staff_number,
                "contact": self.contact,
            }
        )
        return base_dict

    def to_snapshot(self) -> snapshot_models.StaffSnapshotItem:
        return snapshot_models.StaffSnapshotItem(
            id=str(self.id),
            full_name=self.full_name,
            staff_number=self.staff_number,
            contact=self.contact,
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Team(Base):
    """Represents a team for a modality and course"""

    __tablename__ = "team"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modality_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.modality.id"), nullable=False
    )
    course_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.course.id"), nullable=False
    )
    name = Column(Text, nullable=False)
    season_id = Column(Integer, ForeignKey("modalities.season.id"), nullable=True)
    derived_from_team_id = Column(
        UUID(as_uuid=True), ForeignKey("modalities.team.id"), nullable=True
    )  # For tracking team lineage across seasons

    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    modality: Mapped["Modality"] = relationship("Modality", back_populates="teams")
    course: Mapped["Course"] = relationship("Course", back_populates="teams")
    season: Mapped["Season"] = relationship("Season", back_populates="season_teams")
    players: Mapped[list["Student"]] = relationship(
        "Student", secondary=team_players, back_populates="teams"
    )

    def to_dict(self, include_players=False):
        result = {
            "id": str(self.id),
            "name": self.name,
            "modality": self.modality.to_dict() if self.modality else None,
            "course": self.course.to_dict() if self.course else None,
            "season": self.season.to_dict() if self.season else None,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_players:
            result["players"] = [player.to_dict() for player in self.players]
        return result

    def to_snapshot(self) -> snapshot_models.TeamSnapshotItem:
        return snapshot_models.TeamSnapshotItem(
            id=str(self.id),
            modality_id=str(self.modality_id),
            course_id=str(self.course_id),
            name=self.name,
            season_id=self.season_id,
            players=[str(player.id) for player in self.players],
            created_by=str(self.created_by),
            created_at=self.created_at.isoformat() if self.created_at else None,
            updated_at=self.updated_at.isoformat() if self.updated_at else None,
        )


class Regulation(Base):
    """Represents a sport regulation document in the microservice"""

    __tablename__ = "regulation"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(Text, nullable=False)
    season_id = Column(Integer, ForeignKey("modalities.season.id"), nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "file_url": self.file_url,
            "created_at": self.created_at.isoformat(),
        }

    def to_snapshot(self) -> snapshot_models.RegulationSnapshotItem:
        return snapshot_models.RegulationSnapshotItem(
            id=str(self.id),
            title=self.title,
            description=self.description,
            file_url=self.file_url,
            season_id=self.season_id,
            created_at=self.created_at.isoformat() if self.created_at else None,
        )
