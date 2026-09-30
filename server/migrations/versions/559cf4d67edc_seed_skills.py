"""seed skills

Revision ID: 559cf4d67edc
Revises: 097d3f021135
Create Date: 2026-09-29 00:45:04.289776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '559cf4d67edc'
down_revision: Union[str, Sequence[str], None] = '097d3f021135'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SKILLS = [
    {"code": "vocab", "name": "Vocabulary"},
    {"code": "reading", "name": "Reading"},
    {"code": "speaking", "name": "Speaking"},
    {"code": "writing", "name": "Writing"},
    {"code": "listening", "name": "Listening"},
]

skill = sa.table("skill", sa.column("code", sa.String), sa.column("name", sa.String))


def upgrade() -> None:
    """Reference data: activity_log rows point at these, and the code looks skills up by code."""
    op.bulk_insert(skill, SKILLS)


def downgrade() -> None:
    op.execute(skill.delete().where(skill.c.code.in_([row["code"] for row in SKILLS])))
