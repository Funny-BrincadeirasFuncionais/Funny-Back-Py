"""Add created_at to progresso table

Revision ID: 0004_created_at_progresso
Revises: 0003_tempo_progresso
Create Date: 2025-01-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '0004_created_at_progresso'
down_revision = '0003_tempo_progresso'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at column to progresso (nullable initially for existing rows, then set default)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'progresso' in tables:
        cols = [c['name'] for c in inspector.get_columns('progresso')]
        if 'created_at' not in cols:
            # Add column as nullable first
            op.add_column('progresso', sa.Column('created_at', sa.DateTime(), nullable=True))
            
            # Update existing rows with current timestamp
            # Usar CURRENT_TIMESTAMP que é compatível com SQLite e PostgreSQL
            try:
                op.execute(text("UPDATE progresso SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))
            except Exception:
                # Fallback: usar datetime Python se CURRENT_TIMESTAMP não funcionar
                current_time = datetime.utcnow()
                op.execute(text("UPDATE progresso SET created_at = :current_time WHERE created_at IS NULL"),
                          {"current_time": current_time})
            
            # Now make it non-nullable
            op.alter_column('progresso', 'created_at', nullable=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'progresso' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('progresso')]
        if 'created_at' in cols:
            op.drop_column('progresso', 'created_at')

