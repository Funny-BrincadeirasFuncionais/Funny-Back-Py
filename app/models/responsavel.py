from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Responsavel(Base):
    __tablename__ = "responsaveis"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    
    # Relacionamentos
    turmas = relationship("Turma", back_populates="responsavel")
