from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.empleado import Empleado
from schemas.empleado import EmpleadoCreate
from services.seguridad import verificar_rh, verificar_empleado


router = APIRouter(
    prefix="/empleados",
    tags=["Empleados"]
)


@router.get("/")
def obtener_empleados(
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    empleados = db.query(Empleado).all()
    return empleados


@router.post("/")
def crear_empleado(
    empleado: EmpleadoCreate,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):

    empleado_existente = db.query(Empleado).filter(
        Empleado.correo == empleado.correo
    ).first()

    if empleado_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un empleado registrado con este correo"
        )

    nuevo_empleado = Empleado(
        nombre=empleado.nombre,
        apellido_paterno=empleado.apellido_paterno,
        apellido_materno=empleado.apellido_materno,
        correo=empleado.correo,
        area=empleado.area,
        puesto=empleado.puesto,
        fecha_ingreso=empleado.fecha_ingreso
    )

    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)

    return {
        "mensaje": "Empleado registrado correctamente",
        "empleado": nuevo_empleado
    }

@router.get("/mi-perfil")
def obtener_mi_perfil(
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

    return empleado

@router.delete("/{empleado_id}")
def eliminar_empleado(
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

    db.delete(empleado)
    db.commit()

    return {
        "mensaje": "Empleado eliminado correctamente"
    }