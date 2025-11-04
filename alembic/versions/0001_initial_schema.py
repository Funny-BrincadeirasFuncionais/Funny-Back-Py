"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-11-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela usuarios
    op.create_table('usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('senha_hash', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)

    # Criar tabela responsaveis
    op.create_table('responsaveis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('telefone', sa.String(), nullable=True),
        sa.Column('turmas', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_responsaveis_email'), 'responsaveis', ['email'], unique=True)
    op.create_index(op.f('ix_responsaveis_id'), 'responsaveis', ['id'], unique=False)

    # Criar tabela diagnosticos
    op.create_table('diagnosticos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diagnosticos_id'), 'diagnosticos', ['id'], unique=False)

    # Criar tabela turmas
    op.create_table('turmas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('responsavel_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['responsavel_id'], ['responsaveis.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_turmas_id'), 'turmas', ['id'], unique=False)

    # Criar tabela criancas
    op.create_table('criancas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('idade', sa.Integer(), nullable=False),
        sa.Column('diagnostico_id', sa.Integer(), nullable=True),
        sa.Column('turma_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['diagnostico_id'], ['diagnosticos.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_criancas_id'), 'criancas', ['id'], unique=False)

    # Criar tabela atividades
    op.create_table('atividades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('categoria', sa.String(), nullable=False),
        sa.Column('nivel_dificuldade', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_atividades_id'), 'atividades', ['id'], unique=False)

    # Criar tabela progresso
    op.create_table('progresso',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('crianca_id', sa.Integer(), nullable=False),
        sa.Column('atividade_id', sa.Integer(), nullable=False),
        sa.Column('pontuacao', sa.Float(), nullable=True),
        sa.Column('data_realizacao', sa.DateTime(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('concluida', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['atividade_id'], ['atividades.id'], ),
        sa.ForeignKeyConstraint(['crianca_id'], ['criancas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_progresso_id'), 'progresso', ['id'], unique=False)


def downgrade() -> None:
    # Reverter criação das tabelas
    op.drop_index(op.f('ix_progresso_id'), table_name='progresso')
    op.drop_table('progresso')
    
    op.drop_index(op.f('ix_atividades_id'), table_name='atividades')
    op.drop_table('atividades')
    
    op.drop_index(op.f('ix_criancas_id'), table_name='criancas')
    op.drop_table('criancas')
    
    op.drop_index(op.f('ix_turmas_id'), table_name='turmas')
    op.drop_table('turmas')
    
    op.drop_index(op.f('ix_diagnosticos_id'), table_name='diagnosticos')
    op.drop_table('diagnosticos')
    
    op.drop_index(op.f('ix_responsaveis_id'), table_name='responsaveis')
    op.drop_index(op.f('ix_responsaveis_email'), table_name='responsaveis')
    op.drop_table('responsaveis')
    
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
