from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Atividade(Base):
    __tablename__ = "atividades"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    nivel_dificuldade = Column(Integer, nullable=False)
    
    # Relacionamentos
    progressos = relationship("Progresso", back_populates="atividade")
