from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from database.database import get_db
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate, LoginRequest
from services.seguridad import validar_password, crear_token


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

password_hash = PasswordHash.recommended()

@router.post("/rh")
def crear_usuario_rh(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):
    usuario_existente = db.query(Usuario).filter(
        Usuario.correo == usuario.correo
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario registrado con este correo"
        )

    validar_password(usuario.password)

    hash_generado = password_hash.hash(usuario.password)

    nuevo_usuario = Usuario(
        correo=usuario.correo,
        password_hash=hash_generado,
        rol="RH",
        activo=True
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario de Recursos Humanos creado correctamente",
        "usuario_id": nuevo_usuario.id,
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }

@router.post("/login")
def iniciar_sesion(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == datos.correo
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    password_correcto = password_hash.verify(
        datos.password,
        usuario.password_hash
    )

    if not password_correcto:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=403,
            detail="La cuenta se encuentra desactivada"
        )

    token = crear_token(
        usuario_id=usuario.id,
        correo=usuario.correo,
        rol=usuario.rol
    )

    return {
        "mensaje": "Inicio de sesión correcto",
        "access_token": token,
        "token_type": "bearer",
        "usuario_id": usuario.id,
        "correo": usuario.correo,
        "rol": usuario.rol
    }