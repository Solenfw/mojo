"""widen learner_profile.target_level for 'beginner'

Revision ID: c3a1f0e2d4b5
Revises: 559cf4d67edc
Create Date: 2026-11-02 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a1f0e2d4b5'
down_revision: Union[str, Sequence[str], None] = '559cf4d67edc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('learner_profile', 'target_level', type_=sa.String(length=20), existing_type=sa.String(length=2))


def downgrade() -> None:
    op.execute("UPDATE learner_profile SET target_level = NULL WHERE length(target_level) > 2")
    op.alter_column('learner_profile', 'target_level', type_=sa.String(length=2), existing_type=sa.String(length=20))
