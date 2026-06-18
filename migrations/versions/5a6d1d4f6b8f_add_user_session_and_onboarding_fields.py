"""add user session and onboarding fields

Revision ID: 5a6d1d4f6b8f
Revises: 8278f5a306ee
Create Date: 2026-06-18 22:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a6d1d4f6b8f'
down_revision: Union[str, Sequence[str], None] = '8278f5a306ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('session_token', sa.String(length=512), nullable=True))
    op.add_column('users', sa.Column('is_logged_in', sa.Boolean(), server_default=sa.text('false'), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_onboarded', sa.Boolean(), server_default=sa.text('false'), nullable=True))
    op.add_column('users', sa.Column('onboarded_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'onboarded_at')
    op.drop_column('users', 'is_onboarded')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'is_logged_in')
    op.drop_column('users', 'session_token')
