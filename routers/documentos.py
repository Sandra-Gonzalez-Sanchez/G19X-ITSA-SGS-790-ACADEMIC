import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import re


from database.database import get_db
from models.empleado import Empleado
from models.documento import Documento
from models.dato_extraido import DatoExtraido
from models.validacion import Validacion
from services.seguridad import (
    verificar_empleado,
    verificar_rh,
    verificar_acceso_documento
)
from services.ocr_bridge import ejecutar_ocr
from services.validacion_service import (
    comparar_nombres,
    comparar_fechas,
    comparar_curp,
    validar_tipo_documento
)
from services.ia_validacion import validar_documento_con_ia



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
    resultado,
    origen_validacion="REGLA",
    motivo=None
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
        validacion.origen_validacion = origen_validacion
        validacion.motivo = motivo

    else:
        validacion = Validacion(
            empleado_id=empleado_id,
            campo=campo,
            documento_origen=documento_origen,
            documento_comparado=documento_comparado,
            valor_origen=valor_origen,
            valor_comparado=valor_comparado,
            resultado=resultado,
            origen_validacion = origen_validacion,
            motivo = motivo
        )

        db.add(validacion)

    db.commit()

def validar_datos_esenciales(tipo_documento, datos):
    if not datos:
        return False

    if tipo_documento == "ACTA_NACIMIENTO":
        return bool(
            datos.nombre and
            datos.fecha_nacimiento
        )

    if tipo_documento == "CURP":
        return bool(
            datos.nombre and
            datos.fecha_nacimiento and
            datos.curp and
            len(datos.curp) == 18 and
            datos.estado_formato_curp not in (
                "REQUIERE REVISIÓN",
                "NO DETECTADO"
            )
        )

    if tipo_documento == "INE":
        return bool(
            datos.nombre and
            datos.fecha_nacimiento
        )

    if tipo_documento == "RFC":
        return bool(
            datos.nombre and
            datos.fecha_nacimiento and
            datos.rfc and
            len(datos.rfc) in (12, 13) and
            datos.estado_formato_rfc not in (
                "REQUIERE REVISIÓN",
                "NO DETECTADO"
            )
        )

    if tipo_documento == "COMPROBANTE_DOMICILIO":
        return bool(
            datos.domicilio
        )

    if tipo_documento == "DOCUMENTO_BANCARIO":
        return bool(
            datos.clabe and
            datos.clabe.isdigit() and
            len(datos.clabe) in (12, 18)
        )

    if tipo_documento == "SEGURIDAD_SOCIAL":
        return bool(
            datos.nombre and
            datos.nss and
            (
                    (
                            datos.nss.isdigit() and
                            len(datos.nss) == 11
                    )
                    or
                    re.fullmatch(
                        r"SS-[A-Z]{2}-\d{4}-\d{4}",
                        datos.nss.upper()
                    )
            )
        )

    return False

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
            detail="El archivo tiene que estar en formato PDF"
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
        documento.estado = "EN REVISION"

        nombres_documentos = {
            "ACTA_NACIMIENTO": "un Acta de nacimiento",
            "CURP": "una CURP",
            "INE": "una INE",
            "RFC": "una Constancia de Situación Fiscal",
            "COMPROBANTE_DOMICILIO": "un Comprobante de domicilio",
            "DOCUMENTO_BANCARIO": "un Documento bancario para nómina",
            "SEGURIDAD_SOCIAL": "un Documento de Seguridad Social"
        }

        nombre_esperado = nombres_documentos.get(
            tipo_documento,
            "el documento solicitado"
        )

        mensaje_tipo_documento = (
            f"El documento no corresponde al tipo de documento solicitado. "
            f"Se esperaba {nombre_esperado}."
        )
        guardar_validacion(
            db=db,
            empleado_id=empleado.id,
            campo="TIPO_DOCUMENTO",
            documento_origen=tipo_documento,
            documento_comparado=tipo_documento,
            valor_origen=archivo.filename,
            valor_comparado=nombre_esperado,
            resultado="NO COINCIDE",
            motivo=mensaje_tipo_documento
        )

        db.commit()
        db.refresh(documento)

        return {
            "mensaje": "El documento requiere corrección.",
            "empleado_id": empleado.id,
            "tipo_documento": tipo_documento,
            "estado": "EN REVISION",
            "archivo": archivo.filename,
            "motivo_revision": mensaje_tipo_documento,
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



    # VALIDACIÓN ACTA ↔ CURP

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
                resultado=resultado_fecha,
                motivo=(
                    "La fecha de nacimiento no coincide entre "
                    "ACTA_NACIMIENTO y CURP."
                ) if resultado_fecha == "NO COINCIDE" else None
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
                resultado=resultado_nombre,
                motivo=None
            )

            guardar_validacion(
                db=db,
                empleado_id=empleado.id,
                campo="FECHA_NACIMIENTO",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="INE",
                valor_origen=datos_acta.fecha_nacimiento,
                valor_comparado=datos_ine.fecha_nacimiento,
                resultado=resultado_fecha,
                motivo=(
                    "La fecha de nacimiento no coincide entre "
                    "ACTA_NACIMIENTO y INE."
                ) if resultado_fecha == "NO COINCIDE" else None
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
                resultado=resultado_curp,
                motivo=(
                    "La CURP no coincide entre "
                    "CURP y INE."
                ) if resultado_curp == "NO COINCIDE" else None
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
                resultado=resultado_fecha_rfc,
                motivo=None
            )

            print("VALIDACIÓN ACTA ↔ RFC:")
            print("NOMBRE:", resultado_nombre_rfc)
            print("FECHA DE NACIMIENTO:", resultado_fecha_rfc)

    datos_documento = db.query(DatoExtraido).filter(
        DatoExtraido.documento_id == documento.id
    ).first()

    nombre_empleado = " ".join(
        parte for parte in [
            empleado.nombre,
            empleado.apellido_paterno,
            empleado.apellido_materno
        ]
        if parte
    )

    if datos_documento and datos_documento.nombre:
        resultado_nombre_empleado = comparar_nombres(
            nombre_empleado,
            datos_documento.nombre
        )

        guardar_validacion(
            db=db,
            empleado_id=empleado.id,
            campo="NOMBRE_EMPLEADO",
            documento_origen="EMPLEADO",
            documento_comparado=tipo_documento,
            valor_origen=nombre_empleado,
            valor_comparado=datos_documento.nombre,
            resultado=resultado_nombre_empleado
        )

    datos_esenciales_correctos = validar_datos_esenciales(
        tipo_documento,
        datos_documento
    )

    requiere_revision = False

    if not datos_esenciales_correctos:
        requiere_revision = True


    db.query(Validacion).filter(
Validacion.empleado_id == empleado.id,
        Validacion.documento_origen == tipo_documento,
        Validacion.origen_validacion == "IA"
    ).delete(synchronize_session=False)

    db.commit()

    validaciones_documento = db.query(Validacion).filter(
        Validacion.empleado_id == empleado.id
    ).all()

    validaciones_para_ia = []

    for validacion in validaciones_documento:
        participa_documento = (
                validacion.documento_origen == tipo_documento or
                validacion.documento_comparado == tipo_documento
        )
        if not participa_documento:
            continue

        validaciones_para_ia.append({
            "campo": validacion.campo,
            "valor_origen": validacion.valor_origen,
            "valor_comparado": validacion.valor_comparado,
            "documento_origen": validacion.documento_origen,
            "documento_comparado": validacion.documento_comparado,
            "resultado_regla": validacion.resultado,
            "motivo_regla": validacion.motivo
        })

    datos_para_ia = {
        "nombre": datos_documento.nombre if datos_documento else None,
        "fecha_nacimiento": datos_documento.fecha_nacimiento if datos_documento else None,
        "curp": datos_documento.curp if datos_documento else None,
        "rfc": datos_documento.rfc if datos_documento else None,
        "domicilio": datos_documento.domicilio if datos_documento else None,
        "clabe": datos_documento.clabe if datos_documento else None,
        "nss": datos_documento.nss if datos_documento else None
    }

    resultado_ia = validar_documento_con_ia(
        tipo_documento=tipo_documento,
        datos_extraidos=datos_para_ia,
        nombre_empleado=nombre_empleado,
        validaciones=validaciones_para_ia
    )

    print("VALIDACIÓN DOCUMENTAL MEDIANTE IA:")
    print(resultado_ia)

    for inconsistencia in resultado_ia.get("inconsistencias", []):
        campo_ia = inconsistencia.get("campo", "DESCONOCIDO")
        valor_documento_ia = inconsistencia.get("valor_documento")
        valor_referencia_ia = inconsistencia.get("valor_referencia")

        motivo_ia = inconsistencia.get(
            "motivo",
            "La inteligencia artificial detectó una inconsistencia."
        )


        if (
                tipo_documento == "COMPROBANTE_DOMICILIO"
                and campo_ia in ("NOMBRE", "NOMBRE_EMPLEADO")
        ):
            motivo_ia = (
                "Comprobante de domicilio identificado correctamente. "
                "El nombre del titular del comprobante es diferente "
                "al nombre del empleado."
            )

        guardar_validacion(
            db=db,
            empleado_id=empleado.id,
            campo=campo_ia,
            documento_origen=tipo_documento,
            documento_comparado="REFERENCIA",
            valor_origen=valor_documento_ia,
            valor_comparado=valor_referencia_ia,
            resultado="INCONSISTENTE",
            origen_validacion="IA",
            motivo=motivo_ia
        )

    if resultado_ia["requiere_revision"]:
        requiere_revision = True

    if requiere_revision:
        documento.estado = "EN REVISION"
    else:
        documento.estado = "VALIDADO"

    db.commit()
    db.refresh(documento)

    mensaje_revision = None

    mensaje_revision = None
    motivos = []
    tipos_mensaje = set()

    for validacion in validaciones_documento:

        participa_documento = (
                validacion.documento_origen == tipo_documento or
                validacion.documento_comparado == tipo_documento
        )

        if participa_documento and validacion.resultado == "NO COINCIDE":

            if validacion.campo in ("NOMBRE", "NOMBRE_EMPLEADO"):

                if tipo_documento == "COMPROBANTE_DOMICILIO":
                    if "DOMICILIO" not in tipos_mensaje:
                        motivos.append(
                            "Comprobante de domicilio identificado correctamente. "
                            "El nombre del titular del comprobante es diferente "
                            "al nombre del empleado."
                        )
                        tipos_mensaje.add("DOMICILIO")

                else:
                    if "NOMBRE" not in tipos_mensaje:
                        motivos.append(
                            "El nombre del documento no coincide "
                            "con el nombre registrado para el empleado."
                        )
                        tipos_mensaje.add("NOMBRE")

            elif validacion.campo == "FECHA_NACIMIENTO":

                if "FECHA_NACIMIENTO" not in tipos_mensaje:
                    motivos.append(
                        "La fecha de nacimiento del documento no coincide "
                        "con la registrada en el Acta de nacimiento."
                    )
                    tipos_mensaje.add("FECHA_NACIMIENTO")

            elif validacion.campo == "CURP":

                if "CURP" not in tipos_mensaje:
                    motivos.append(
                        "La CURP del documento no coincide "
                        "con la registrada."
                    )
                    tipos_mensaje.add("CURP")

    # ==========================================================
    # VALIDACIONES DE IA
    # ==========================================================

    if resultado_ia.get("requiere_revision"):

        inconsistencias_ia = resultado_ia.get(
            "inconsistencias",
            []
        )

        for inconsistencia in inconsistencias_ia:

            if tipo_documento == "COMPROBANTE_DOMICILIO":

                if "DOMICILIO" not in tipos_mensaje:
                    motivos.append(
                        "Comprobante de domicilio identificado correctamente. "
                        "El nombre del titular del comprobante es diferente "
                        "al nombre del empleado."
                    )
                    tipos_mensaje.add("DOMICILIO")

            else:

                campo_ia = inconsistencia.get("campo")

                # Si la inconsistencia de IA corresponde a una fecha,
                # usamos el mismo mensaje general de fecha.
                if campo_ia == "FECHA_NACIMIENTO":

                    if "FECHA_NACIMIENTO" not in tipos_mensaje:
                        motivos.append(
                            "La fecha de nacimiento del documento no coincide "
                            "con la registrada en el Acta de nacimiento."
                        )
                        tipos_mensaje.add("FECHA_NACIMIENTO")

                # Si corresponde al nombre, mostramos un solo mensaje.
                elif campo_ia in ("NOMBRE", "NOMBRE_EMPLEADO"):

                    if "NOMBRE" not in tipos_mensaje:
                        motivos.append(
                            "El nombre del documento no coincide "
                            "con el nombre registrado para el empleado."
                        )
                        tipos_mensaje.add("NOMBRE")

                # Si corresponde a CURP, mostramos un solo mensaje.
                elif campo_ia == "CURP":

                    if "CURP" not in tipos_mensaje:
                        motivos.append(
                            "La CURP del documento no coincide "
                            "con la registrada."
                        )
                        tipos_mensaje.add("CURP")

                else:

                    motivo_ia = inconsistencia.get(
                        "motivo",
                        "La inteligencia artificial detectó una inconsistencia."
                    )

                    if motivo_ia not in motivos:
                        motivos.append(motivo_ia)

    motivos = list(dict.fromkeys(motivos))

    if motivos:
        mensaje_revision = " ".join(motivos)

    elif not resultado_ia["disponible"]:
        mensaje_revision = (
            "No fue posible completar la validación mediante "
            "inteligencia artificial."
        )

    return {
        "mensaje": (
            "Documento validado correctamente."
            if documento.estado == "VALIDADO"
            else "El documento requiere revisión."
        ),
        "empleado_id": empleado.id,
        "tipo_documento": tipo_documento,
        "archivo": archivo.filename,
        "estado": documento.estado,
        "motivo_revision": mensaje_revision
    }

@router.delete("/{documento_id}")
def eliminar_documento(
    documento_id: int,
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
            detail="No se encontró información del empleado."
        )
    documento = db.query(Documento).filter(
        Documento.id == documento_id
    ).first()

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado."
        )


    if documento.empleado_id != empleado.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para eliminar este documento."
        )

    tipo_documento = documento.tipo_documento
    empleado_id = documento.empleado_id

    # Eliminar datos extraídos del documento
    db.query(DatoExtraido).filter(
        DatoExtraido.documento_id == documento.id
    ).delete(synchronize_session=False)

    # Eliminar validaciones relacionadas con este tipo de documento
    db.query(Validacion).filter(
        Validacion.empleado_id == empleado_id,
        Validacion.documento_origen == tipo_documento
    ).delete(synchronize_session=False)

    db.query(Validacion).filter(
        Validacion.empleado_id == empleado_id,
        Validacion.documento_comparado == tipo_documento
    ).delete(synchronize_session=False)

    # Eliminar el archivo físico
    if documento.ruta_archivo and os.path.exists(documento.ruta_archivo):
        os.remove(documento.ruta_archivo)

    # Eliminar el registro del documento
    db.delete(documento)
    db.commit()

    return {
        "mensaje": "Documento eliminado correctamente.",
        "tipo_documento": tipo_documento
    }


@router.put("/{documento_id}/aprobar")
def aprobar_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    datos_rh: dict = Depends(verificar_rh)
):
    documento = db.query(Documento).filter(
        Documento.id == documento_id
    ).first()

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado"
        )

    if documento.estado != "EN REVISION":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden aprobar documentos que estén EN REVISION"
        )

    documento.estado = "VALIDADO"

    db.commit()
    db.refresh(documento)

    return {
        "mensaje": "Documento aprobado correctamente",
        "documento_id": documento.id,
        "tipo_documento": documento.tipo_documento,
        "estado": documento.estado
    }

@router.put("/{documento_id}/solicitar-correccion")
def solicitar_correccion_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    datos_rh: dict = Depends(verificar_rh)
):
    documento = db.query(Documento).filter(
        Documento.id == documento_id
    ).first()

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado"
        )

    if documento.estado != "EN REVISION":
        raise HTTPException(
            status_code=400,
            detail="Solo se puede solicitar corrección de documentos que estén EN REVISION"
        )

    documento.estado = "PENDIENTE"

    db.commit()
    db.refresh(documento)

    return {
        "mensaje": "Corrección solicitada correctamente",
        "documento_id": documento.id,
        "tipo_documento": documento.tipo_documento,
        "estado": documento.estado
    }

@router.put("/{documento_id}/no-aplica")
def marcar_documento_no_aplica(
    documento_id: int,
    db: Session = Depends(get_db),
    datos_rh: dict = Depends(verificar_rh)
):
    documento = db.query(Documento).filter(
        Documento.id == documento_id
    ).first()

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado"
        )

    if documento.tipo_documento != "SEGURIDAD_SOCIAL":
        raise HTTPException(
            status_code=400,
            detail="Solo el documento de Seguridad Social puede marcarse como NO APLICA"
        )

    documento.estado = "NO APLICA"

    db.commit()
    db.refresh(documento)

    return {
        "mensaje": "Documento marcado como NO APLICA",
        "documento_id": documento.id,
        "tipo_documento": documento.tipo_documento,
        "estado": documento.estado
    }

@router.get("/empleado/{empleado_id}")
def obtener_expediente_empleado(
    empleado_id: int,
    db: Session = Depends(get_db),
    datos_rh: dict = Depends(verificar_rh)
):
    empleado = db.query(Empleado).filter(
        Empleado.id == empleado_id
    ).first()

    if not empleado:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado"
        )

    documentos = db.query(Documento).filter(
        Documento.empleado_id == empleado_id
    ).all()

    documentos_expediente = []

    for documento in documentos:
        datos_extraidos = db.query(DatoExtraido).filter(
            DatoExtraido.documento_id == documento.id
        ).first()


        validaciones_documento = db.query(Validacion).filter(
            Validacion.empleado_id == empleado_id
        ).all()

        motivos_revision = []

        for validacion in validaciones_documento:
            participa_documento = (
                validacion.documento_origen == documento.tipo_documento or
                validacion.documento_comparado == documento.tipo_documento
            )

            if participa_documento and validacion.resultado in (
                    "NO COINCIDE",
                    "INCONSISTENTE"
            ):
                motivos_revision.append({
                    "campo": validacion.campo,
                    "documento_origen": validacion.documento_origen,
                    "documento_comparado": validacion.documento_comparado,
                    "valor_origen": validacion.valor_origen,
                    "valor_comparado": validacion.valor_comparado,
                    "resultado": validacion.resultado,
                    "motivo": validacion.motivo,
                    "origen_validacion": validacion.origen_validacion
                })

        documentos_expediente.append({
            "id": documento.id,
            "tipo_documento": documento.tipo_documento,
            "estado": documento.estado,
            "fecha_carga": documento.fecha_carga,
            "motivos_revision": motivos_revision,
            "datos_extraidos": {
                "nombre": datos_extraidos.nombre,
                "fecha_nacimiento": datos_extraidos.fecha_nacimiento,
                "domicilio": datos_extraidos.domicilio,
                "curp": datos_extraidos.curp,
                "rfc": datos_extraidos.rfc,
                "clabe": datos_extraidos.clabe,
                "nss": datos_extraidos.nss
            } if datos_extraidos else None
        })

    return {
        "empleado": {
            "id": empleado.id,
            "nombre": empleado.nombre,
            "apellido_paterno": empleado.apellido_paterno,
            "apellido_materno": empleado.apellido_materno,
            "correo": empleado.correo,
            "area": empleado.area,
            "puesto": empleado.puesto,
            "fecha_ingreso": empleado.fecha_ingreso
        },
        "documentos": documentos_expediente
    }
@router.get("/archivo/{documento_id}")
def ver_mi_documento(
    documento_id: int,
    db: Session = Depends(get_db),
    datos_usuario: dict = Depends(verificar_acceso_documento)
):
    usuario_id = int(datos_usuario.get("sub"))
    rol = datos_usuario.get("rol")


    if rol == "RH":

        documento = db.query(Documento).filter(
            Documento.id == documento_id
        ).first()

        if not documento:
            raise HTTPException(
                status_code=404,
                detail="Documento no encontrado"
            )


    else:

        empleado = db.query(Empleado).filter(
            Empleado.usuario_id == usuario_id
        ).first()

        if not empleado:
            raise HTTPException(
                status_code=404,
                detail="No se encontró información del empleado"
            )

        documento = db.query(Documento).filter(
            Documento.id == documento_id,
            Documento.empleado_id == empleado.id
        ).first()

        if not documento:
            raise HTTPException(
                status_code=404,
                detail="Documento no encontrado"
            )


    if documento.estado == "NO APLICA" or documento.ruta_archivo == "NO_APLICA":
        raise HTTPException(
            status_code=400,
            detail="Este documento no cuenta con un archivo PDF."
        )

    if not os.path.isfile(documento.ruta_archivo):
        raise HTTPException(
            status_code=404,
            detail="El archivo PDF no fue encontrado."
        )

    return FileResponse(
        path=documento.ruta_archivo,
        media_type="application/pdf",
        filename=os.path.basename(documento.ruta_archivo),
        content_disposition_type="inline"
    )

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

    documentos_respuesta = []

    for documento in documentos:
        validaciones_documento = db.query(Validacion).filter(
            Validacion.empleado_id == empleado.id
        ).all()

        motivos_revision = []
        tipos_mensaje = set()

        for validacion in validaciones_documento:

            participa_documento = (
                    validacion.documento_origen == documento.tipo_documento or
                    validacion.documento_comparado == documento.tipo_documento
            )

            if participa_documento and validacion.resultado in (
                    "NO COINCIDE",
                    "INCONSISTENTE"
            ):

                campo = validacion.campo

                # FECHA DE NACIMIENTO
                if campo == "FECHA_NACIMIENTO":

                    if "FECHA_NACIMIENTO" not in tipos_mensaje:
                        motivos_revision.append({
                            "campo": "FECHA_NACIMIENTO",
                            "motivo": (
                                "La fecha de nacimiento del documento "
                                "no coincide con la registrada "
                                "en los documentos del expediente."
                            ),
                            "valor_documento": validacion.valor_origen,
                            "valor_referencia": validacion.valor_comparado,
                            "origen_validacion": validacion.origen_validacion
                        })

                        tipos_mensaje.add("FECHA_NACIMIENTO")

                # NOMBRE
                elif campo in ("NOMBRE", "NOMBRE_EMPLEADO"):

                    if "NOMBRE" not in tipos_mensaje:
                        motivos_revision.append({
                            "campo": "NOMBRE",
                            "motivo": (
                                "El nombre del documento no coincide "
                                "con el nombre registrado para el empleado."
                            ),
                            "valor_documento": validacion.valor_origen,
                            "valor_referencia": validacion.valor_comparado,
                            "origen_validacion": validacion.origen_validacion
                        })

                        tipos_mensaje.add("NOMBRE")

                # CURP
                elif campo == "CURP":

                    if "CURP" not in tipos_mensaje:
                        motivos_revision.append({
                            "campo": "CURP",
                            "motivo": (
                                "La CURP del documento no coincide "
                                "con la registrada."
                            ),
                            "valor_documento": validacion.valor_origen,
                            "valor_referencia": validacion.valor_comparado,
                            "origen_validacion": validacion.origen_validacion
                        })

                        tipos_mensaje.add("CURP")

                # OTROS
                elif validacion.motivo:

                    if validacion.motivo not in [
                        motivo["motivo"]
                        for motivo in motivos_revision
                    ]:
                        motivos_revision.append({
                            "campo": campo,
                            "motivo": validacion.motivo,
                            "valor_documento": validacion.valor_origen,
                            "valor_referencia": validacion.valor_comparado,
                            "origen_validacion": validacion.origen_validacion
                        })

        documentos_respuesta.append({
            "id": documento.id,
            "tipo_documento": documento.tipo_documento,
            "estado": documento.estado,
            "fecha_carga": documento.fecha_carga,
            "motivo_revision": " ".join(
                motivo["motivo"]
                for motivo in motivos_revision
                if motivo.get("motivo")
            )
        })

    return documentos_respuesta



@router.put("/empleado/seguridad-social/no-aplica")
def marcar_seguridad_social_no_aplica(
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

    documento = db.query(Documento).filter(
        Documento.empleado_id == empleado.id,
        Documento.tipo_documento == "SEGURIDAD_SOCIAL"
    ).first()

    if documento:
        documento.estado = "NO APLICA"
    else:
        documento = Documento(
            empleado_id=empleado.id,
            tipo_documento="SEGURIDAD_SOCIAL",
            ruta_archivo="NO_APLICA",
            estado="NO APLICA"
        )

        db.add(documento)

    db.commit()
    db.refresh(documento)

    return {
        "mensaje": "Seguridad Social marcada como NO APLICA",
        "estado": documento.estado
    }

