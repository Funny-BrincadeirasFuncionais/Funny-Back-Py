from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Progresso(Base):
    __tablename__ = "progressos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pontuacao = Column(Integer, nullable=False)
    observacoes = Column(Text, nullable=True)
    concluida = Column(Boolean, default=False)
    crianca_id = Column(Integer, ForeignKey("criancas.id"))
    atividade_id = Column(Integer, ForeignKey("atividades.id"))
    
    # Relacionamentos
    crianca = relationship("Crianca", back_populates="progressos")
    atividade = relationship("Atividade", back_populates="progressos")
