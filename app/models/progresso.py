from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Progresso(Base):
    __tablename__ = "progressos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pontuacao = Column(Integer, nullable=False)  # Pontuação (pode ser qualquer valor >= 0)
    observacoes = Column(Text, nullable=True)
    concluida = Column(Boolean, default=True)  # Front-end sempre envia como true
    crianca_id = Column(Integer, ForeignKey("criancas.id"), nullable=False)  # Aluno
    atividade_id = Column(Integer, ForeignKey("atividades.id"), nullable=False)  # Atividade (mini-jogo)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  # Professor que aplicou (preenchido automaticamente do token)
    
    # Relacionamentos
    crianca = relationship("Crianca", back_populates="progressos")
    atividade = relationship("Atividade", back_populates="progressos")
    usuario = relationship("Usuario")
