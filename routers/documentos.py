import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid


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
from services.validacion_service import (
    procesar_documento
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

    extension = os.path.splitext(archivo.filename)[1].lower()
    nombre_archivo = f"{tipo_documento}_{uuid.uuid4().hex}{extension}"

    ruta_archivo = os.path.join(
        carpeta_empleado,
        nombre_archivo
    )

    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(
            archivo.file,
            buffer
        )

    if documento_existente:

        db.query(DatoExtraido).filter(
            DatoExtraido.documento_id == documento_existente.id
        ).delete(synchronize_session=False)

        db.query(Validacion).filter(
            Validacion.empleado_id == empleado.id,
            Validacion.documento_origen == tipo_documento
        ).delete(synchronize_session=False)

        db.query(Validacion).filter(
            Validacion.empleado_id == empleado.id,
            Validacion.documento_comparado == tipo_documento
        ).delete(synchronize_session=False)

        if (
                documento_existente.ruta_archivo
                and os.path.exists(documento_existente.ruta_archivo)
        ):
            os.remove(documento_existente.ruta_archivo)

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

    return procesar_documento(
    db=db,
    empleado=empleado,
    documento=documento,
    tipo_documento=tipo_documento,
    nombre_archivo=nombre_archivo,
    ruta_archivo=ruta_archivo
    )


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

    db.query(DatoExtraido).filter(
        DatoExtraido.documento_id == documento.id
    ).delete(synchronize_session=False)

    db.query(Validacion).filter(
        Validacion.empleado_id == empleado_id,
        Validacion.documento_origen == tipo_documento
    ).delete(synchronize_session=False)

    db.query(Validacion).filter(
        Validacion.empleado_id == empleado_id,
        Validacion.documento_comparado == tipo_documento
    ).delete(synchronize_session=False)


    if documento.ruta_archivo and os.path.exists(documento.ruta_archivo):
        os.remove(documento.ruta_archivo)


    db.delete(documento)
    db.commit()

    return {
        "mensaje": "Documento eliminado correctamente.",
        "tipo_documento": tipo_documento
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

                elif campo in ("NOMBRE", "NOMBRE_EMPLEADO"):

                    if documento.tipo_documento == "COMPROBANTE_DOMICILIO":

                        if "DOMICILIO" not in tipos_mensaje:
                            motivos_revision.append({
                                "campo": "DOMICILIO",
                                "motivo": (
                                    "Comprobante de domicilio identificado correctamente. "
                                    "El nombre del titular del comprobante es diferente "
                                    "al nombre del empleado."
                                ),
                                "valor_documento": validacion.valor_origen,
                                "valor_referencia": validacion.valor_comparado,
                                "origen_validacion": validacion.origen_validacion
                            })

                            tipos_mensaje.add("DOMICILIO")

                    else:

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

                elif campo == "CURP":

                    if "CURP" not in tipos_mensaje:
                        motivos_revision.append({
                            "campo": "CURP",
                            "motivo": (
                                "La CURP del documento no coincide "
                                "con la que se muestra en la INE."
                            ),
                            "valor_documento": validacion.valor_origen,
                            "valor_referencia": validacion.valor_comparado,
                            "origen_validacion": validacion.origen_validacion
                        })

                        tipos_mensaje.add("CURP")

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

        motivos_unicos = []
        nombres_mostrados = False

        for motivo in motivos_revision:
            campo = motivo.get("campo", "")
            texto = motivo.get("motivo", "")

            if campo in ("NOMBRE", "NOMBRE_EMPLEADO") or \
                    "NOMBRE_EMPLEADO" in texto or \
                    "NOMBRE: NO COINCIDE" in texto:

                if not nombres_mostrados:
                    motivos_unicos.append({
                        "campo": "NOMBRE",
                        "motivo": (
                            "El nombre del documento no coincide "
                            "con el nombre registrado para el empleado."
                        )
                    })
                    nombres_mostrados = True

            else:
                motivos_unicos.append(motivo)

        motivos_revision = motivos_unicos

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

    ruta_archivo = os.path.abspath(documento.ruta_archivo)

    if not os.path.isfile(ruta_archivo):
        raise HTTPException(
            status_code=404,
            detail="El archivo PDF no fue encontrado."
        )

    return FileResponse(
        path=ruta_archivo,
        media_type="application/pdf",
        filename=os.path.basename(ruta_archivo),
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

                elif campo in ("NOMBRE", "NOMBRE_EMPLEADO"):

                    if documento.tipo_documento == "COMPROBANTE_DOMICILIO":

                        if "DOMICILIO" not in tipos_mensaje:
                            motivos_revision.append({
                                "campo": "DOMICILIO",
                                "motivo": (
                                    "Comprobante de domicilio identificado correctamente. "
                                    "El nombre del titular del comprobante es diferente "
                                    "al nombre del empleado."
                                ),
                                "valor_documento": validacion.valor_origen,
                                "valor_referencia": validacion.valor_comparado,
                                "origen_validacion": validacion.origen_validacion
                            })

                            tipos_mensaje.add("DOMICILIO")

                    else:

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


                elif campo == "CURP":

                    if "CURP" not in tipos_mensaje:
                        motivos_revision.append({
                            "campo": "CURP",
                            "motivo": (
                                "La CURP del documento no coincide "
                                "con la que se muestra en la INE."
                            ),
                            "valor_documento": validacion.valor_origen,
                            "valor_referencia": validacion.valor_comparado,
                            "origen_validacion": validacion.origen_validacion
                        })

                        tipos_mensaje.add("CURP")

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

@router.delete("/empleado/seguridad-social/no-aplica")
def quitar_seguridad_social_no_aplica(
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

    if not documento:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el documento de Seguridad Social"
        )

    if documento.estado != "NO APLICA":
        raise HTTPException(
            status_code=400,
            detail="El documento de Seguridad Social no está marcado como NO APLICA"
        )

    db.delete(documento)
    db.commit()

    return {
        "mensaje": "Seguridad Social nuevamente disponible para cargar",
        "estado": "PENDIENTE"
    }

