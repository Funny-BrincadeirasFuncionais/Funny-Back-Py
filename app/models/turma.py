from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    responsavel_id = Column(Integer, ForeignKey("responsaveis.id"))
    
    # Relacionamentos
    responsavel = relationship("Responsavel", back_populates="turmas")
    criancas = relationship("Crianca", back_populates="turma")