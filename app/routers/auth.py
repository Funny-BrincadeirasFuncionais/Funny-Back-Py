from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioLogin, Token
from app.auth import hash_password, verify_password, create_access_token
import httpx
from app.models.responsavel import Responsavel
from datetime import timedelta
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UsuarioCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    
    try:
        # Verificar se email já existe
        existing_user = db.query(Usuario).filter(Usuario.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Criar novo usuário
        hashed_password = hash_password(user_data.senha)
        new_user = Usuario(
            nome=user_data.nome,
            email=user_data.email,
            senha_hash=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user

    except IntegrityError:
        # Violação de unicidade (email duplicado) ou outra integridade relacional
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(user_credentials: UsuarioLogin, db: Session = Depends(get_db)):
    """Login do usuário"""
    
    # If recaptcha_secret is configured, require recaptcha_token and verify it
    if settings.recaptcha_secret:
        token = user_credentials.recaptcha_token
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reCAPTCHA token missing")
        try:
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            resp = httpx.post(verify_url, data={"secret": settings.recaptcha_secret, "response": token}, timeout=10.0)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"reCAPTCHA verification error: {str(e)}")

        try:
            result = resp.json()
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid response from reCAPTCHA verification service")

        if not result.get("success"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reCAPTCHA verification failed")

    # Buscar usuário
    user = db.query(Usuario).filter(Usuario.email == user_credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Verificar senha
    if not verify_password(user_credentials.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Criar token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"id": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    # Tentar achar um responsável com o mesmo e-mail do usuário
    responsavel = db.query(Responsavel).filter(Responsavel.email == user.email).first()
    responsavel_id = responsavel.id if responsavel else None

    return {"access_token": access_token, "token_type": "bearer", "responsavel_id": responsavel_id}
