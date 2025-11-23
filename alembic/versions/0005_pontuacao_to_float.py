"""Change pontuacao column to Float

Revision ID: 0005_pontuacao_float
Revises: 0004_created_at_progresso
Create Date: 2025-11-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0005_pontuacao_float'
down_revision = '0004_created_at_progresso'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'progresso' in inspector.get_table_names():
        cols = inspector.get_columns('progresso')
        col_names = [c['name'] for c in cols]
        if 'pontuacao' in col_names:
            # For Postgres, run an explicit ALTER TYPE with USING to cast integer->double precision
            dialect = conn.dialect.name
            if dialect == 'postgresql':
                try:
                    op.execute("ALTER TABLE progresso ALTER COLUMN pontuacao TYPE double precision USING pontuacao::double precision;")
                except Exception:
                    # Fall back to generic alter as a last resort
                    try:
                        op.alter_column('progresso', 'pontuacao', existing_type=sa.Integer(), type_=sa.Float(), nullable=False)
                    except Exception:
                        pass
            else:
                # Try a generic alter; some DBs (SQLite) may not support this and will require a manual migration
                try:
                    op.alter_column('progresso', 'pontuacao', existing_type=sa.Integer(), type_=sa.Float(), nullable=False)
                except Exception:
                    pass


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'progresso' in inspector.get_table_names():
        cols = inspector.get_columns('progresso')
        col_names = [c['name'] for c in cols]
        if 'pontuacao' in col_names:
            dialect = conn.dialect.name
            if dialect == 'postgresql':
                try:
                    # Round to nearest integer then cast
                    op.execute("ALTER TABLE progresso ALTER COLUMN pontuacao TYPE integer USING CAST(ROUND(pontuacao) AS integer);")
                except Exception:
                    try:
                        op.alter_column('progresso', 'pontuacao', existing_type=sa.Float(), type_=sa.Integer(), nullable=False)
                    except Exception:
                        pass
            else:
                try:
                    op.alter_column('progresso', 'pontuacao', existing_type=sa.Float(), type_=sa.Integer(), nullable=False)
                except Exception:
                    pass
