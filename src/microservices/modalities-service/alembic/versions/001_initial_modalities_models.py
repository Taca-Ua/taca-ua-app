"""Initial modalities service models

Revision ID: 001
Revises:
Create Date: 2025-12-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create nucleo table
    op.create_table(
        "nucleo",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("abbreviation", sa.Text(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("abbreviation"),
        schema="modalities",
    )

    # Create course table
    op.create_table(
        "course",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("abbreviation", sa.Text(), nullable=False),
        sa.Column("nucleo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["nucleo_id"],
            ["modalities.nucleo.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("abbreviation"),
        schema="modalities",
    )
    op.create_index(
        op.f("ix_course_nucleo_id"),
        "course",
        ["nucleo_id"],
        unique=False,
        schema="modalities",
    )

    # Create modality_type table
    op.create_table(
        "modality_type",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("escaloes", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="modalities",
    )

    # Create modality table
    op.create_table(
        "modality",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("modality_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["modality_type_id"],
            ["modalities.modality_type.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        schema="modalities",
    )
    op.create_index(
        op.f("ix_modality_modality_type_id"),
        "modality",
        ["modality_type_id"],
        unique=False,
        schema="modalities",
    )

    # Create member table (base table for students and staff)
    op.create_table(
        "member",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("member_type", sa.String(length=50), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="modalities",
    )

    # Create student table
    op.create_table(
        "student",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_number", sa.Text(), nullable=False),
        sa.Column("is_member", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["modalities.course.id"],
        ),
        sa.ForeignKeyConstraint(
            ["id"],
            ["modalities.member.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_number"),
        schema="modalities",
    )
    op.create_index(
        op.f("ix_student_course_id"),
        "student",
        ["course_id"],
        unique=False,
        schema="modalities",
    )

    # Create staff table
    op.create_table(
        "staff",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("staff_number", sa.Text(), nullable=True),
        sa.Column("contact", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id"],
            ["modalities.member.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("staff_number"),
        sa.UniqueConstraint("contact"),
        schema="modalities",
    )

    # Create team table
    op.create_table(
        "team",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("modality_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["modalities.course.id"],
        ),
        sa.ForeignKeyConstraint(
            ["modality_id"],
            ["modalities.modality.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="modalities",
    )
    op.create_index(
        op.f("ix_team_course_id"),
        "team",
        ["course_id"],
        unique=False,
        schema="modalities",
    )
    op.create_index(
        op.f("ix_team_modality_id"),
        "team",
        ["modality_id"],
        unique=False,
        schema="modalities",
    )

    # Create team_players association table
    op.create_table(
        "team_players",
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["modalities.student.id"],
        ),
        sa.ForeignKeyConstraint(
            ["team_id"],
            ["modalities.team.id"],
        ),
        sa.PrimaryKeyConstraint("team_id", "student_id"),
        schema="modalities",
    )


def downgrade() -> None:
    op.drop_table("team_players", schema="modalities")
    op.drop_index(op.f("ix_team_modality_id"), table_name="team", schema="modalities")
    op.drop_index(op.f("ix_team_course_id"), table_name="team", schema="modalities")
    op.drop_table("team", schema="modalities")
    op.drop_table("staff", schema="modalities")
    op.drop_index(
        op.f("ix_student_course_id"), table_name="student", schema="modalities"
    )
    op.drop_table("student", schema="modalities")
    op.drop_table("member", schema="modalities")
    op.drop_index(
        op.f("ix_modality_modality_type_id"), table_name="modality", schema="modalities"
    )
    op.drop_table("modality", schema="modalities")
    op.drop_table("modality_type", schema="modalities")
    op.drop_index(op.f("ix_course_nucleo_id"), table_name="course", schema="modalities")
    op.drop_table("course", schema="modalities")
    op.drop_table("nucleo", schema="modalities")
