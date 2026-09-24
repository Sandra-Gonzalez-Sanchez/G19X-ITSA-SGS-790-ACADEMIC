from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pwdlib import PasswordHash

from database.database import get_db
from models.empleado import Empleado
from models.invitacion import Invitacion
from services.seguridad import validar_password, verificar_rh
from services.correo import enviar_correo_invitacion
from schemas.invitacion import CrearPassword
from models.usuario import Usuario



password_hash = PasswordHash.recommended()

router = APIRouter(
    tags=["Invitaciones"]
)


@router.post("/empleados/{empleado_id}/invitacion")
def generar_invitacion(
    empleado_id: int,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )
    invitaciones_anteriores = db.query(Invitacion).filter(
        Invitacion.empleado_id == empleado.id,
        Invitacion.activa == True
    ).all()

    for invitacion_anterior in invitaciones_anteriores:
        invitacion_anterior.activa = False

    token = secrets.token_urlsafe(32)

    fecha_creacion = datetime.now(timezone.utc)
    fecha_expiracion = fecha_creacion + timedelta(hours=72)

    nueva_invitacion = Invitacion(
        empleado_id=empleado.id,
        token=token,
        fecha_creacion=fecha_creacion,
        fecha_expiracion=fecha_expiracion,
        utilizada=False,
        activa=True
    )

    db.add(nueva_invitacion)
    db.commit()
    db.refresh(nueva_invitacion)

    enlace_invitacion = (
        f"http://localhost:5173/invitacion/{nueva_invitacion.token}"
    )

    enviar_correo_invitacion(
        correo_destino=empleado.correo,
        nombre_empleado=empleado.nombre,
        enlace_invitacion=enlace_invitacion
    )

    return {
        "mensaje": "Invitación generada correctamente",
        "invitacion_id": nueva_invitacion.id,
        "empleado_id": empleado.id,
        "token": nueva_invitacion.token,
        "fecha_expiracion": nueva_invitacion.fecha_expiracion
    }
@router.get("/invitaciones/{token}/validar")
def validar_invitacion(
    token: str,
    db: Session = Depends(get_db)
):
    invitacion = db.query(Invitacion).filter(
        Invitacion.token == token
    ).first()

    if not invitacion:
        raise HTTPException(
            status_code=404,
            detail="Invitación no encontrada"
        )

    if not invitacion.activa:
        raise HTTPException(
            status_code=400,
            detail="La invitación ya no está activa"
        )

    if invitacion.utilizada:
        raise HTTPException(
            status_code=400,
            detail="La invitación ya fue utilizada"
        )

    fecha_actual = datetime.now(timezone.utc)

    if fecha_actual > invitacion.fecha_expiracion:
        raise HTTPException(
            status_code=400,
            detail="La invitación ha expirado"
        )

    return {
        "mensaje": "Invitación válida",
        "empleado_id": invitacion.empleado_id,
        "fecha_expiracion": invitacion.fecha_expiracion
    }

@router.post("/invitaciones/{token}/crear-password")
def crear_password_empleado(
    token: str,
    datos: CrearPassword,
    db: Session = Depends(get_db)
):
    invitacion = db.query(Invitacion).filter(
        Invitacion.token == token
    ).first()

    if not invitacion:
        raise HTTPException(
            status_code=404,
            detail="Invitación no encontrada"
        )

    if not invitacion.activa:
        raise HTTPException(
            status_code=400,
            detail="La invitación ya no está activa"
        )

    if invitacion.utilizada:
        raise HTTPException(
            status_code=400,
            detail="La invitación ya fue utilizada"
        )

    fecha_actual = datetime.now(timezone.utc)

    if fecha_actual > invitacion.fecha_expiracion:
        raise HTTPException(
            status_code=400,
            detail="La invitación ha expirado"
        )

    validar_password(datos.password)

    empleado = db.query(Empleado).filter(
        Empleado.id == invitacion.empleado_id
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    if empleado.usuario_id is not None:
        raise HTTPException(
            status_code=400,
            detail="El empleado ya tiene una cuenta de usuario"
        )

    usuario_existente = db.query(Usuario).filter(
        Usuario.correo == empleado.correo
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una cuenta registrada con este correo"
        )

    hash_generado = password_hash.hash(datos.password)

    nuevo_usuario = Usuario(
        correo=empleado.correo,
        password_hash=hash_generado,
        rol="EMPLEADO",
        activo=True
    )

    db.add(nuevo_usuario)
    db.flush()

    empleado.usuario_id = nuevo_usuario.id

    invitacion.utilizada = True
    invitacion.activa = False

    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Cuenta de empleado creada correctamente",
        "usuario_id": nuevo_usuario.id,
        "empleado_id": empleado.id,
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }