"""init_schemas

Revision ID: c683b45f4978
Revises: b5612f002db3
Create Date: 2026-04-29 17:34:06.944962

"""
import os
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c683b45f4978'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_file_path = os.path.join(os.path.dirname(__file__), 'init_schemas.sql')
    with open(sql_file_path, 'r') as sql_file:
        sql_commands = sql_file.read()
    op.execute(sql_commands)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP SCHEMA IF EXISTS public CASCADE;')
    op.execute('CREATE SCHEMA public;')
