"""add reading resources

Revision ID: 9c4a6d2e1f30
Revises: 2bf0683f3fbc
Create Date: 2026-06-24 10:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c4a6d2e1f30'
down_revision: Union[str, Sequence[str], None] = '2bf0683f3fbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'reading_passages',
        sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, increment=1), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('source_passage_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('vietnamese_title', sa.String(length=255), nullable=True),
        sa.Column('content_japanese', sa.Text(), nullable=False),
        sa.Column('content_vietnamese', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], name='reading_passages_lesson_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='reading_passages_pkey'),
        sa.UniqueConstraint('lesson_id', 'source_passage_id', name='reading_passages_lesson_source_key'),
    )
    op.create_index('idx_reading_passages_lesson_id', 'reading_passages', ['lesson_id'], unique=False)

    op.create_table(
        'reading_vocabulary_items',
        sa.Column('id', sa.Integer(), sa.Identity(always=False, start=1, increment=1), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('word', sa.String(length=255), nullable=False),
        sa.Column('kana', sa.String(length=255), nullable=True),
        sa.Column('kanji', sa.String(length=255), nullable=True),
        sa.Column('romaji', sa.String(length=255), nullable=True),
        sa.Column('word_type', sa.String(length=50), nullable=True),
        sa.Column('meaning', sa.Text(), nullable=False),
        sa.Column('level', sa.String(length=50), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], name='reading_vocabulary_items_lesson_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='reading_vocabulary_items_pkey'),
        sa.UniqueConstraint('lesson_id', 'word', name='reading_vocabulary_items_lesson_word_key'),
    )
    op.create_index('idx_reading_vocabulary_items_lesson_id', 'reading_vocabulary_items', ['lesson_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_reading_vocabulary_items_lesson_id', table_name='reading_vocabulary_items')
    op.drop_table('reading_vocabulary_items')
    op.drop_index('idx_reading_passages_lesson_id', table_name='reading_passages')
    op.drop_table('reading_passages')
