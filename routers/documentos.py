import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session


from database.database import get_db
from models.empleado import Empleado
from models.documento import Documento
from services.seguridad import verificar_empleado


router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"]
)

@router.post("/subir")
def subir_documento(
    tipo_documento: str = Form(...),
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    datos_empleado: dict = Depends(verificar_empleado)
):
    tipos_permitidos = [
        "ACTA_NACIMIENTO",
        "CURP",
        "INE",
        "RFC",
        "COMPROBANTE_DOMICILIO",
        "DOCUMENTO_BANCARIO",
        "SEGURIDAD_SOCIAL"
    ]

    if tipo_documento not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Tipo de documento no válido"
        )

    if archivo.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF"
        )




    usuario_id = int(datos_empleado.get("sub"))

    empleado = db.query(Empleado).filter(
        Empleado.usuario_id == usuario_id
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="No se encontró información del empleado"
        )

    documento_existente = db.query(Documento).filter(
        Documento.empleado_id == empleado.id,
        Documento.tipo_documento == tipo_documento
    ).first()


    carpeta_empleado = os.path.join(
        "uploads",
        "empleados",
        str(empleado.id)
    )

    os.makedirs(
        carpeta_empleado,
        exist_ok=True
    )

    ruta_archivo = os.path.join(
        carpeta_empleado,
        archivo.filename
    )

    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(
            archivo.file,
            buffer
        )

    if documento_existente:
        documento_existente.ruta_archivo = ruta_archivo
        documento_existente.estado = "PENDIENTE"

        db.commit()
        db.refresh(documento_existente)

    else:
        nuevo_documento = Documento(
            empleado_id=empleado.id,
            tipo_documento=tipo_documento,
            ruta_archivo=ruta_archivo,
            estado="PENDIENTE"
        )

        db.add(nuevo_documento)
        db.commit()
        db.refresh(nuevo_documento)

    return {
        "mensaje": "Documento guardado correctamente",
        "empleado_id": empleado.id,
        "tipo_documento": tipo_documento,
        "archivo": archivo.filename
    }

@router.get("/mis-documentos")
def obtener_mis_documentos(
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



    documentos = db.query(Documento).filter(
        Documento.empleado_id == empleado.id
    ).all()

    return documentos

