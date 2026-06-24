"""sync user gamification and onboarding metadata

Revision ID: b7f9c3a1d2e4
Revises: 9c4a6d2e1f30
Create Date: 2026-06-24 14:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f9c3a1d2e4'
down_revision: Union[str, Sequence[str], None] = '9c4a6d2e1f30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('xp', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('users', sa.Column('streak', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('users', sa.Column('gems', sa.Integer(), server_default=sa.text('0'), nullable=False))
    op.add_column('users', sa.Column('hearts', sa.Integer(), server_default=sa.text('5'), nullable=False))
    op.add_column('users', sa.Column('hearts_last_updated', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('last_activity_date', sa.Date(), nullable=True))

    op.add_column('learner_profiles', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True))
    op.add_column('learner_profiles', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True))

    op.add_column('onboarding_answers', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True))
    op.create_index('idx_onboarding_answers_session_id', 'onboarding_answers', ['session_id'], unique=False)
    op.create_unique_constraint(
        'onboarding_answers_session_question_key',
        'onboarding_answers',
        ['session_id', 'question_code'],
    )


def downgrade() -> None:
    op.drop_constraint('onboarding_answers_session_question_key', 'onboarding_answers', type_='unique')
    op.drop_index('idx_onboarding_answers_session_id', table_name='onboarding_answers')
    op.drop_column('onboarding_answers', 'updated_at')

    op.drop_column('learner_profiles', 'updated_at')
    op.drop_column('learner_profiles', 'created_at')

    op.drop_column('users', 'last_activity_date')
    op.drop_column('users', 'hearts_last_updated')
    op.drop_column('users', 'hearts')
    op.drop_column('users', 'gems')
    op.drop_column('users', 'streak')
    op.drop_column('users', 'xp')
