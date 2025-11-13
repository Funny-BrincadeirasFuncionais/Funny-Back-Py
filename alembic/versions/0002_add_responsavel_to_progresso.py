"""Add responsavel_id to progresso table

Revision ID: 0002_resp_progresso
Revises: 0001
Create Date: 2025-11-12 21:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_resp_progresso'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add responsavel_id column to progresso (nullable to avoid breaking existing rows)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'progresso' in tables:
        cols = [c['name'] for c in inspector.get_columns('progresso')]
        if 'responsavel_id' not in cols:
            op.add_column('progresso', sa.Column('responsavel_id', sa.Integer(), nullable=True))
            # create fk to responsaveis
            op.create_foreign_key('fk_progresso_responsavel_id_responsaveis', 'progresso', 'responsaveis', ['responsavel_id'], ['id'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'progresso' in inspector.get_table_names():
        cols = [c['name'] for c in inspector.get_columns('progresso')]
        if 'responsavel_id' in cols:
            try:
                op.drop_constraint('fk_progresso_responsavel_id_responsaveis', 'progresso', type_='foreignkey')
            except Exception:
                pass
            op.drop_column('progresso', 'responsavel_id')
