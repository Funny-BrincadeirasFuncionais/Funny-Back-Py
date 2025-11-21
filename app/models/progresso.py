from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Progresso(Base):
    # Use the singular table name 'progresso' to match the Alembic initial migration
    # (the migrations create 'progresso' not 'progressos'). Keeping this aligned
    # avoids ProgrammingError: relation "progressos" does not exist.
    __tablename__ = "progresso"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pontuacao = Column(Integer, nullable=False)  # Pontuação (pode ser qualquer valor >= 0)
    observacoes = Column(Text, nullable=True)
    concluida = Column(Boolean, default=True)  # Front-end sempre envia como true
    crianca_id = Column(Integer, ForeignKey("criancas.id"), nullable=False)  # Aluno
    atividade_id = Column(Integer, ForeignKey("atividades.id"), nullable=False)  # Atividade (mini-jogo)
    # Note: previously this referenced a `usuario_id`. The data model should
    # relate progresso to a responsavel (guardian/parent) instead. We keep the
    # column nullable initially to avoid breaking existing data during migration.
    responsavel_id = Column(Integer, ForeignKey("responsaveis.id"), nullable=True)
    tempo_segundos = Column(Integer, nullable=True)  # Tempo em segundos para completar a atividade (opcional para compatibilidade retroativa)

    # Relacionamentos
    crianca = relationship("Crianca", back_populates="progressos")
    atividade = relationship("Atividade", back_populates="progressos")