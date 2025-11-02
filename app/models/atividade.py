from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Atividade(Base):
    __tablename__ = "atividades"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    categoria = Column(String, nullable=False)  # Matemáticas, Português, Lógica ou Cotidiano
    # Titulo e descricao são opcionais (podem ser gerados no front)
    titulo = Column(String, nullable=True)  # Opcional - pode ser gerado no front
    descricao = Column(Text, nullable=True)  # Opcional - pode ser gerado no front
    
    # Relacionamentos
    progressos = relationship("Progresso", back_populates="atividade")
    
    # Nota: Validação de categoria feita no schema Pydantic para compatibilidade com SQLite
    # Cada atividade tem ID único, permitindo que o mesmo aluno/professor faça múltiplas atividades da mesma categoria
