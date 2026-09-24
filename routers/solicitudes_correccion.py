from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.empleado import Empleado
from models.solicitud_correccion import SolicitudCorreccion
from schemas.solicitud_correccion import (
    SolicitudCorreccionCreate,
    SolicitudCorreccionResolver
)
from services.seguridad import verificar_empleado, verificar_rh


router = APIRouter(
    prefix="/solicitudes-correccion",
    tags=["Solicitudes de corrección"]
)


@router.post("/")
def crear_solicitud_correccion(
    datos: SolicitudCorreccionCreate,
    db: Session = Depends(get_db),
    datos_empleado: dict = Depends(verificar_empleado)
):
    usuario_id = int(datos_empleado.get("sub"))

    empleado = db.query(Empleado).filter(
        Empleado.usuario_id == usuario_id
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="No se encontró información del empleado"
        )

    nueva_solicitud = SolicitudCorreccion(
        empleado_id=empleado.id,
        nombre_solicitado=datos.nombre_solicitado,
        apellido_paterno_solicitado=datos.apellido_paterno_solicitado,
        apellido_materno_solicitado=datos.apellido_materno_solicitado,
        motivo=datos.motivo,
        estado="PENDIENTE"
    )

    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)

    return {
        "mensaje": "Solicitud de corrección enviada correctamente",
        "solicitud_id": nueva_solicitud.id,
        "estado": nueva_solicitud.estado
    }

@router.get("/")
def obtener_solicitudes_correccion(
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    solicitudes = db.query(SolicitudCorreccion).order_by(
        SolicitudCorreccion.id.desc()
    ).all()

    return solicitudes

@router.put("/{solicitud_id}/resolver")
def resolver_solicitud_correccion(
    solicitud_id: int,
    datos: SolicitudCorreccionResolver,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    solicitud = db.query(SolicitudCorreccion).filter(
        SolicitudCorreccion.id == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(
            status_code=404,
            detail="Solicitud de corrección no encontrada"
        )

    if solicitud.estado != "PENDIENTE":
        raise HTTPException(
            status_code=400,
            detail="La solicitud ya fue resuelta"
        )

    decision = datos.decision.upper()

    if decision not in ["APROBAR", "RECHAZAR"]:
        raise HTTPException(
            status_code=400,
            detail="La decisión debe ser APROBAR o RECHAZAR"
        )

    empleado = db.query(Empleado).filter(
        Empleado.id == solicitud.empleado_id
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    if decision == "APROBAR":
        if solicitud.nombre_solicitado is not None:
            empleado.nombre = solicitud.nombre_solicitado

        if solicitud.apellido_paterno_solicitado is not None:
            empleado.apellido_paterno = solicitud.apellido_paterno_solicitado

        if solicitud.apellido_materno_solicitado is not None:
            empleado.apellido_materno = solicitud.apellido_materno_solicitado

        solicitud.estado = "APROBADA"

    else:
        solicitud.estado = "RECHAZADA"

    db.commit()
    db.refresh(solicitud)

    return {
        "mensaje": "Solicitud resuelta correctamente",
        "solicitud_id": solicitud.id,
        "estado": solicitud.estado
    }