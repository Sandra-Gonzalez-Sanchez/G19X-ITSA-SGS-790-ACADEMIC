import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session


from database.database import get_db
from models.empleado import Empleado
from models.documento import Documento
from models.dato_extraido import DatoExtraido
from models.validacion import Validacion
from services.seguridad import verificar_empleado
from services.ocr_bridge import ejecutar_ocr
from services.validacion_service import (
    comparar_nombres,
    comparar_fechas,
    validar_tipo_documento
)



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
    resultado_tipo_documento = validar_tipo_documento(
        tipo_documento,
        datos_ocr.get("textos_detectados", [])
    )

    print("VALIDACIÓN DEL TIPO DE DOCUMENTO:")
    print(tipo_documento, "->", resultado_tipo_documento)

    if resultado_tipo_documento == "REQUIERE REVISIÓN":
        documento.estado = "PENDIENTE"
        db.commit()
        db.refresh(documento)

        return {
            "mensaje": "El archivo no parece corresponder al tipo de documento seleccionado. Verifica el archivo y vuelve a cargarlo.",
            "empleado_id": empleado.id,
            "tipo_documento": tipo_documento,
            "estado": "PENDIENTE",
            "archivo": archivo.filename,
            "documento_aceptado": False
        }

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

    documento_acta = db.query(Documento).filter(
        Documento.empleado_id == empleado.id,
        Documento.tipo_documento == "ACTA_NACIMIENTO"
    ).first()

    documento_curp = db.query(Documento).filter(
        Documento.empleado_id == empleado.id,
        Documento.tipo_documento == "CURP"
    ).first()

    if documento_acta and documento_curp:
        datos_acta = db.query(DatoExtraido).filter(
            DatoExtraido.documento_id == documento_acta.id
        ).first()

        datos_curp = db.query(DatoExtraido).filter(
            DatoExtraido.documento_id == documento_curp.id
        ).first()

        print("DATOS PARA VALIDACIÓN CRUZADA:")
        print("ACTA:", datos_acta.nombre, datos_acta.fecha_nacimiento)
        print("CURP:", datos_curp.nombre, datos_curp.fecha_nacimiento)

        resultado_nombre = comparar_nombres(
            datos_acta.nombre,
            datos_curp.nombre
        )

        resultado_fecha = comparar_fechas(
            datos_acta.fecha_nacimiento,
            datos_curp.fecha_nacimiento
        )

        print("RESULTADO COMPARACIÓN:")
        print("NOMBRE:", resultado_nombre)
        print("FECHA DE NACIMIENTO:", resultado_fecha)

        validacion_nombre = db.query(Validacion).filter(
            Validacion.empleado_id == empleado.id,
            Validacion.campo == "NOMBRE",
            Validacion.documento_origen == "ACTA_NACIMIENTO",
            Validacion.documento_comparado == "CURP"
        ).first()

        if validacion_nombre:
            validacion_nombre.valor_origen = datos_acta.nombre
            validacion_nombre.valor_comparado = datos_curp.nombre
            validacion_nombre.resultado = resultado_nombre

        else:
            validacion_nombre = Validacion(
                empleado_id=empleado.id,
                campo="NOMBRE",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="CURP",
                valor_origen=datos_acta.nombre,
                valor_comparado=datos_curp.nombre,
                resultado=resultado_nombre
            )

            db.add(validacion_nombre)

        db.commit()

        print("VALIDACIÓN DE NOMBRE GUARDADA O ACTUALIZADA")

        validacion_fecha = db.query(Validacion).filter(
            Validacion.empleado_id == empleado.id,
            Validacion.campo == "FECHA_NACIMIENTO",
            Validacion.documento_origen == "ACTA_NACIMIENTO",
            Validacion.documento_comparado == "CURP"
        ).first()

        if validacion_fecha:
            validacion_fecha.valor_origen = datos_acta.fecha_nacimiento
            validacion_fecha.valor_comparado = datos_curp.fecha_nacimiento
            validacion_fecha.resultado = resultado_fecha

        else:
            validacion_fecha = Validacion(
                empleado_id=empleado.id,
                campo="FECHA_NACIMIENTO",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="CURP",
                valor_origen=datos_acta.fecha_nacimiento,
                valor_comparado=datos_curp.fecha_nacimiento,
                resultado=resultado_fecha
            )

            db.add(validacion_fecha)

        db.commit()

        print("VALIDACIÓN DE FECHA GUARDADA O ACTUALIZADA")

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

