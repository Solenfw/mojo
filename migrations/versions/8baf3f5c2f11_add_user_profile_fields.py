"""add user profile fields

Revision ID: 8baf3f5c2f11
Revises: 5a6d1d4f6b8f
Create Date: 2026-06-18 22:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8baf3f5c2f11'
down_revision: Union[str, Sequence[str], None] = '5a6d1d4f6b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.create_unique_constraint('users_phone_key', 'users', ['phone'])


def downgrade() -> None:
    op.drop_constraint('users_phone_key', 'users', type_='unique')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'full_name')
