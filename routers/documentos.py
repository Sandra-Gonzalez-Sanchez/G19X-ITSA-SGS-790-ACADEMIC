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
    comparar_curp,
    validar_tipo_documento
)



router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"]
)

def guardar_validacion(
    db,
    empleado_id,
    campo,
    documento_origen,
    documento_comparado,
    valor_origen,
    valor_comparado,
    resultado
):
    validacion = db.query(Validacion).filter(
        Validacion.empleado_id == empleado_id,
        Validacion.campo == campo,
        Validacion.documento_origen == documento_origen,
        Validacion.documento_comparado == documento_comparado
    ).first()

    if validacion:
        validacion.valor_origen = valor_origen
        validacion.valor_comparado = valor_comparado
        validacion.resultado = resultado

    else:
        validacion = Validacion(
            empleado_id=empleado_id,
            campo=campo,
            documento_origen=documento_origen,
            documento_comparado=documento_comparado,
            valor_origen=valor_origen,
            valor_comparado=valor_comparado,
            resultado=resultado
        )

        db.add(validacion)

    db.commit()

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
            domicilio=datos_ocr.get("domicilio"),
            clabe=datos_ocr.get("clabe"),
            nss=datos_ocr.get("nss"),
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
        dato_extraido_existente.domicilio = datos_ocr.get("domicilio")
        dato_extraido_existente.clabe = datos_ocr.get("clabe")
        dato_extraido_existente.nss = datos_ocr.get("nss")
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

    documento_ine = db.query(Documento).filter(
        Documento.empleado_id == empleado.id,
        Documento.tipo_documento == "INE"
    ).first()

    documento_rfc = db.query(Documento).filter(
        Documento.empleado_id == empleado.id,
        Documento.tipo_documento == "RFC"
    ).first()

    if documento_acta and documento_curp:
        datos_acta = db.query(DatoExtraido).filter(
            DatoExtraido.documento_id == documento_acta.id
        ).first()

        datos_curp = db.query(DatoExtraido).filter(
            DatoExtraido.documento_id == documento_curp.id
        ).first()

        if datos_acta and datos_curp:
            resultado_nombre = comparar_nombres(
                datos_acta.nombre,
                datos_curp.nombre
            )

            resultado_fecha = comparar_fechas(
                datos_acta.fecha_nacimiento,
                datos_curp.fecha_nacimiento
            )

            guardar_validacion(
                db=db,
                empleado_id=empleado.id,
                campo="NOMBRE",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="CURP",
                valor_origen=datos_acta.nombre,
                valor_comparado=datos_curp.nombre,
                resultado=resultado_nombre
            )

            guardar_validacion(
                db=db,
                empleado_id=empleado.id,
                campo="FECHA_NACIMIENTO",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="CURP",
                valor_origen=datos_acta.fecha_nacimiento,
                valor_comparado=datos_curp.fecha_nacimiento,
                resultado=resultado_fecha
            )

            print("VALIDACIÓN ACTA ↔ CURP:")
            print("NOMBRE:", resultado_nombre)
            print("FECHA DE NACIMIENTO:", resultado_fecha)

            if documento_acta and documento_ine:
                datos_acta = db.query(DatoExtraido).filter(
                    DatoExtraido.documento_id == documento_acta.id
                ).first()

                datos_ine = db.query(DatoExtraido).filter(
                    DatoExtraido.documento_id == documento_ine.id
                ).first()

                if datos_acta and datos_ine:
                    resultado_nombre = comparar_nombres(
                        datos_acta.nombre,
                        datos_ine.nombre
                    )

                    resultado_fecha = comparar_fechas(
                        datos_acta.fecha_nacimiento,
                        datos_ine.fecha_nacimiento
                    )

                    guardar_validacion(
                        db=db,
                        empleado_id=empleado.id,
                        campo="NOMBRE",
                        documento_origen="ACTA_NACIMIENTO",
                        documento_comparado="INE",
                        valor_origen=datos_acta.nombre,
                        valor_comparado=datos_ine.nombre,
                        resultado=resultado_nombre
                    )

                    guardar_validacion(
                        db=db,
                        empleado_id=empleado.id,
                        campo="FECHA_NACIMIENTO",
                        documento_origen="ACTA_NACIMIENTO",
                        documento_comparado="INE",
                        valor_origen=datos_acta.fecha_nacimiento,
                        valor_comparado=datos_ine.fecha_nacimiento,
                        resultado=resultado_fecha
                    )

                    print("VALIDACIÓN ACTA ↔ INE:")
                    print("NOMBRE:", resultado_nombre)
                    print("FECHA DE NACIMIENTO:", resultado_fecha)

                    if documento_curp and documento_ine:
                        datos_curp = db.query(DatoExtraido).filter(
                            DatoExtraido.documento_id == documento_curp.id
                        ).first()

                        datos_ine = db.query(DatoExtraido).filter(
                            DatoExtraido.documento_id == documento_ine.id
                        ).first()

                        if datos_curp and datos_ine:
                            resultado_curp = comparar_curp(
                                datos_curp.curp,
                                datos_ine.curp
                            )

                            guardar_validacion(
                                db=db,
                                empleado_id=empleado.id,
                                campo="CURP",
                                documento_origen="CURP",
                                documento_comparado="INE",
                                valor_origen=datos_curp.curp,
                                valor_comparado=datos_ine.curp,
                                resultado=resultado_curp
                            )

                            print("VALIDACIÓN CURP ↔ INE:")
                            print("CURP:", resultado_curp)

            if documento_acta and documento_rfc:
                datos_acta = db.query(DatoExtraido).filter(
                    DatoExtraido.documento_id == documento_acta.id
                ).first()

                datos_rfc = db.query(DatoExtraido).filter(
                    DatoExtraido.documento_id == documento_rfc.id
                ).first()

                if datos_acta and datos_rfc:
                    resultado_nombre_rfc = comparar_nombres(
                        datos_acta.nombre,
                        datos_rfc.nombre
                    )

                    resultado_fecha_rfc = comparar_fechas(
                        datos_acta.fecha_nacimiento,
                        datos_rfc.fecha_nacimiento
                    )

                    guardar_validacion(
                        db=db,
                        empleado_id=empleado.id,
                        campo="NOMBRE",
                        documento_origen="ACTA_NACIMIENTO",
                        documento_comparado="RFC",
                        valor_origen=datos_acta.nombre,
                        valor_comparado=datos_rfc.nombre,
                        resultado=resultado_nombre_rfc
                    )

                    guardar_validacion(
                        db=db,
                        empleado_id=empleado.id,
                        campo="FECHA_NACIMIENTO",
                        documento_origen="ACTA_NACIMIENTO",
                        documento_comparado="RFC",
                        valor_origen=datos_acta.fecha_nacimiento,
                        valor_comparado=datos_rfc.fecha_nacimiento,
                        resultado=resultado_fecha_rfc
                    )

                    print("VALIDACIÓN ACTA ↔ RFC:")
                    print("NOMBRE:", resultado_nombre_rfc)
                    print("FECHA DE NACIMIENTO:", resultado_fecha_rfc)

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

