from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Atividade(Base):
    __tablename__ = "atividades"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String, nullable=False)  # Obrigatório - front-end sempre envia
    descricao = Column(Text, nullable=False)  # Obrigatório - front-end sempre envia
    categoria = Column(String, nullable=False)  # Matemáticas, Português, Lógica ou Cotidiano
    nivel_dificuldade = Column(Integer, nullable=False, default=1)  # Front-end sempre envia (padrão: 1)
    
    # Relacionamentos
    progressos = relationship("Progresso", back_populates="atividade")
    
    # Nota: Validação de categoria feita no schema Pydantic para compatibilidade com SQLite
    # Front-end busca por titulo (case-insensitive) antes de criar nova atividade
