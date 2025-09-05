from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Diagnostico(Base):
    __tablename__ = "diagnosticos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipo = Column(String, nullable=False)
    
    # Relacionamentos
    criancas = relationship("Crianca", back_populates="diagnostico")
