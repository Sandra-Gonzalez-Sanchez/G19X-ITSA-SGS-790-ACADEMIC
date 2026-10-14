from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
import secrets
from datetime import datetime, timedelta, timezone
from database.database import get_db
from models.usuario import Usuario
from schemas.usuario import (
    UsuarioCreate,
    LoginRequest,
    SolicitudRecuperacion,
    RestablecerPassword
)
from services.seguridad import validar_password, crear_token, verificar_rh
from services.correo import enviar_correo_recuperacion


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
    rh_existente = db.query(Usuario).filter(
        Usuario.rol == "RH"
    ).first()

    if rh_existente:
        raise HTTPException(
            status_code=403,
            detail="Ya existe un usuario de Recursos Humanos. Utiliza el endpoint protegido para crear nuevos usuarios RH."
        )

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
        "mensaje": "Usuario inicial de Recursos Humanos creado correctamente",
        "usuario_id": nuevo_usuario.id,
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }

@router.post("/rh/crear")
def crear_nuevo_usuario_rh(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db),
    datos_token: dict = Depends(verificar_rh)
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

@router.post("/recuperar-password")
def solicitar_recuperacion(
    datos: SolicitudRecuperacion,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.correo == datos.correo
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="No existe una cuenta registrada con este correo"
        )

    token = secrets.token_urlsafe(32)

    usuario.token_recuperacion = token
    usuario.token_recuperacion_expira = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    )

    enlace = (
        f"http://localhost:5173/restablecer-password/{token}"
    )

    try:
        enviar_correo_recuperacion(
            correo_destino=usuario.correo,
            enlace_recuperacion=enlace
        )

        db.commit()

    except Exception as error:
        db.rollback()

        print("ERROR AL ENVIAR CORREO DE RECUPERACIÓN:")
        print(error)

        raise HTTPException(
            status_code=500,
            detail="No fue posible enviar el correo de recuperación"
        )

    print("ENLACE DE RECUPERACIÓN:")
    print(enlace)

    return {
        "mensaje": "Se generó el enlace de recuperación correctamente",
        "enlace": enlace
    }

@router.post("/restablecer-password/{token}")
def restablecer_password(
    token: str,
    datos: RestablecerPassword,
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(
        Usuario.token_recuperacion == token
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="El enlace de recuperación no es válido"
        )

    if not usuario.token_recuperacion_expira:
        raise HTTPException(
            status_code=400,
            detail="El enlace de recuperación no es válido"
        )

    fecha_actual = datetime.now(timezone.utc)

    if fecha_actual > usuario.token_recuperacion_expira:
        raise HTTPException(
            status_code=400,
            detail="El enlace de recuperación ha expirado"
        )

    validar_password(datos.password)

    usuario.password_hash = password_hash.hash(
        datos.password
    )

    usuario.token_recuperacion = None
    usuario.token_recuperacion_expira = None

    db.commit()

    return {
        "mensaje": "Contraseña actualizada correctamente"
    }