"""Add tempo_segundos to progresso table

Revision ID: 0003_tempo_progresso
Revises: 0002_resp_progresso
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_tempo_progresso'
down_revision = '0002_resp_progresso'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tempo_segundos column to progresso (nullable to avoid breaking existing rows)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'progresso' in tables:
        cols = [c['name'] for c in inspector.get_columns('progresso')]
        if 'tempo_segundos' not in cols:
            op.add_column('progresso', sa.Column('tempo_segundos', sa.Integer(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'progresso' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('progresso')]
        if 'tempo_segundos' in cols:
            op.drop_column('progresso', 'tempo_segundos')

