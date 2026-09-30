from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.database import get_db
from models.area import Area
from models.puesto import Puesto
from schemas.catalogo import AreaCreate, PuestoCreate
from services.seguridad import verificar_rh


router = APIRouter(
    prefix="/catalogos",
    tags=["Catálogos"]
)


# =========================
# ÁREAS
# =========================

@router.get("/areas")
def obtener_areas(
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    return db.query(Area).order_by(Area.nombre).all()


@router.post("/areas")
def crear_area(
    datos: AreaCreate,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    nombre = datos.nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del área es obligatorio"
        )

    existente = db.query(Area).filter(
        func.lower(Area.nombre) == nombre.lower()
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El área ya existe"
        )

    nueva_area = Area(
        nombre=nombre,
        activo=True
    )

    db.add(nueva_area)
    db.commit()
    db.refresh(nueva_area)

    return {
        "mensaje": "Área registrada correctamente",
        "area": nueva_area
    }


@router.patch("/areas/{area_id}/estado")
def cambiar_estado_area(
    area_id: int,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    area = db.query(Area).filter(
        Area.id == area_id
    ).first()

    if not area:
        raise HTTPException(
            status_code=404,
            detail="Área no encontrada"
        )

    area.activo = not area.activo

    db.commit()
    db.refresh(area)

    return {
        "mensaje": "Estado del área actualizado correctamente",
        "area": area
    }


# =========================
# PUESTOS
# =========================

@router.get("/puestos")
def obtener_puestos(
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    return db.query(Puesto).order_by(Puesto.nombre).all()


@router.post("/puestos")
def crear_puesto(
    datos: PuestoCreate,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    nombre = datos.nombre.strip()

    if not nombre:
        raise HTTPException(
            status_code=400,
            detail="El nombre del puesto es obligatorio"
        )

    existente = db.query(Puesto).filter(
        func.lower(Puesto.nombre) == nombre.lower()
    ).first()

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El puesto ya existe"
        )

    nuevo_puesto = Puesto(
        nombre=nombre,
        activo=True
    )

    db.add(nuevo_puesto)
    db.commit()
    db.refresh(nuevo_puesto)

    return {
        "mensaje": "Puesto registrado correctamente",
        "puesto": nuevo_puesto
    }


@router.patch("/puestos/{puesto_id}/estado")
def cambiar_estado_puesto(
    puesto_id: int,
    db: Session = Depends(get_db),
    usuario_rh: dict = Depends(verificar_rh)
):
    puesto = db.query(Puesto).filter(
        Puesto.id == puesto_id
    ).first()

    if not puesto:
        raise HTTPException(
            status_code=404,
            detail="Puesto no encontrado"
        )

    puesto.activo = not puesto.activo

    db.commit()
    db.refresh(puesto)

    return {
        "mensaje": "Estado del puesto actualizado correctamente",
        "puesto": puesto
    }