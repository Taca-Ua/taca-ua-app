"""
SQLAlchemy models for Modalities Service.
Schema: modalities
"""

import uuid

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Modality(Base):
    """
    Represents a sport modality.
    """

    __tablename__ = "modality"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)

    def __repr__(self):
        return f"<Modality {self.id} - {self.name}>"


class Rule(Base):
    """
    Represents scoring rules for a modality.
    Allows custom scoring formulas per modality.
    """

    __tablename__ = "rule"
    __table_args__ = {"schema": "modalities"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    modality_id = Column(
        UUID(as_uuid=True),
        ForeignKey("modalities.modality.id"),
        nullable=False,
        index=True,
    )
    points_for_win = Column(Integer, nullable=False, default=3)
    points_for_draw = Column(Integer, nullable=False, default=1)
    points_for_loss = Column(Integer, nullable=False, default=0)
    scoring_formula = Column(JSONB, nullable=True)  # Custom scoring logic as JSON

    def __repr__(self):
        return f"<Rule {self.id} - Modality {self.modality_id}>"
