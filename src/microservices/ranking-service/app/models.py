"""
SQLAlchemy models for Ranking Service.
Schema: ranking
"""

from sqlalchemy.ext.declarative import declarative_base
from taca_outbox.models import create_outbox_model

Base = declarative_base()


# OutboxEvent model — schema-bound via shared factory
OutboxEvent = create_outbox_model(Base, schema="ranking")
