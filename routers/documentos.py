import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session


from database.database import get_db
from models.empleado import Empleado
from models.documento import Documento
from models.dato_extraido import DatoExtraido
from services.seguridad import verificar_empleado
from services.ocr_bridge import ejecutar_ocr


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

        documento = documento_existente

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
        documento = nuevo_documento

    datos_ocr = ejecutar_ocr(ruta_archivo)
    dato_extraido_existente = db.query(DatoExtraido).filter(
        DatoExtraido.documento_id == documento.id
    ).first()

    if not dato_extraido_existente:
        nuevo_dato_extraido = DatoExtraido(
            documento_id=documento.id,
            nombre=datos_ocr.get("nombre"),
            fecha_nacimiento=datos_ocr.get("fecha_nacimiento"),
            curp=datos_ocr.get("curp"),
            curp_candidata=datos_ocr.get("curp_candidata"),
            estado_formato_curp=datos_ocr.get("estado_formato_curp"),
            rfc=datos_ocr.get("rfc"),
            estado_formato_rfc=datos_ocr.get("estado_formato_rfc"),
            comparacion_fecha_curp=datos_ocr.get("comparacion_fecha_curp"),
            comparacion_fecha_rfc=datos_ocr.get("comparacion_fecha_rfc")
        )

        db.add(nuevo_dato_extraido)
        db.commit()
        db.refresh(nuevo_dato_extraido)

    else:
        dato_extraido_existente.nombre = datos_ocr.get("nombre")
        dato_extraido_existente.fecha_nacimiento = datos_ocr.get("fecha_nacimiento")
        dato_extraido_existente.curp = datos_ocr.get("curp")
        dato_extraido_existente.curp_candidata = datos_ocr.get("curp_candidata")
        dato_extraido_existente.estado_formato_curp = datos_ocr.get("estado_formato_curp")
        dato_extraido_existente.rfc = datos_ocr.get("rfc")
        dato_extraido_existente.estado_formato_rfc = datos_ocr.get("estado_formato_rfc")
        dato_extraido_existente.comparacion_fecha_curp = datos_ocr.get("comparacion_fecha_curp")
        dato_extraido_existente.comparacion_fecha_rfc = datos_ocr.get("comparacion_fecha_rfc")

        db.commit()
        db.refresh(dato_extraido_existente)


    print("RESULTADO OCR DESDE FASTAPI:")
    print(datos_ocr)
    print("DOCUMENTO ID:", documento.id)

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

