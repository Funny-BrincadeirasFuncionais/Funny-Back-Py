from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Crianca(Base):
    __tablename__ = "criancas"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    idade = Column(Integer, nullable=False)
    responsavel_id = Column(Integer, ForeignKey("responsaveis.id"))
    diagnostico_id = Column(Integer, ForeignKey("diagnosticos.id"))
    
    # Relacionamentos
    responsavel = relationship("Responsavel", back_populates="criancas")
    diagnostico = relationship("Diagnostico", back_populates="criancas")
    progressos = relationship("Progresso", back_populates="crianca")
