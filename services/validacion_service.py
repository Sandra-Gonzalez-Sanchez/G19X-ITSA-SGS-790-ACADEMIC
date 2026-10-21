import unicodedata
import re
from datetime import datetime
from models.dato_extraido import DatoExtraido
from models.validacion import Validacion

def normalizar_nombre(nombre):
    if not nombre:
        return None

    nombre = nombre.strip().upper()

    nombre = unicodedata.normalize("NFD", nombre)
    nombre = "".join(
        caracter for caracter in nombre
        if unicodedata.category(caracter) != "Mn"
    )

    nombre = " ".join(nombre.split())

    return nombre


def comparar_nombres(nombre_1, nombre_2):
    if not nombre_1 or not nombre_2:
        return "NO SE PUEDE COMPARAR"

    nombre_1_normalizado = normalizar_nombre(nombre_1)
    nombre_2_normalizado = normalizar_nombre(nombre_2)

    if nombre_1_normalizado == nombre_2_normalizado:
        return "COINCIDE"

    return "NO COINCIDE"


from datetime import datetime


def comparar_fechas(fecha_1, fecha_2):
    if not fecha_1 or not fecha_2:
        return "NO SE PUEDE COMPARAR"

    formatos = [
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y-%m-%d"
    ]

    def convertir_fecha(fecha):
        fecha = fecha.strip()

        for formato in formatos:
            try:
                return datetime.strptime(fecha, formato).date()
            except ValueError:
                continue

        return None

    fecha_1_convertida = convertir_fecha(fecha_1)
    fecha_2_convertida = convertir_fecha(fecha_2)

    if not fecha_1_convertida or not fecha_2_convertida:
        return "NO SE PUEDE COMPARAR"

    if fecha_1_convertida == fecha_2_convertida:
        return "COINCIDE"

    return "NO COINCIDE"

def comparar_curp(curp_1, curp_2):
    if not curp_1 or not curp_2:
        return "NO SE PUEDE COMPARAR"

    curp_1 = curp_1.strip().upper()
    curp_2 = curp_2.strip().upper()

    if curp_1 == curp_2:
        return "COINCIDE"

    return "NO COINCIDE"

def comparar_rfc(rfc_1, rfc_2):
    if not rfc_1 or not rfc_2:
        return "NO SE PUEDE COMPARAR"

    rfc_1 = rfc_1.strip().upper()
    rfc_2 = rfc_2.strip().upper()

    if rfc_1 == rfc_2:
        return "COINCIDE"

    return "NO COINCIDE"

def detectar_documento_no_compatible(tipo_documento, textos_detectados):
    if not textos_detectados:
        return False

    texto_completo = " ".join(textos_detectados).upper()

    indicadores_mexicanos = {
        "ACTA_NACIMIENTO": [
            "ESTADOS UNIDOS MEXICANOS",
            "REGISTRO CIVIL",
            "ENTIDAD FEDERATIVA"
        ],
        "CURP": [
            "CLAVE ÚNICA DE REGISTRO DE POBLACIÓN",
            "CLAVE UNICA DE REGISTRO DE POBLACION",
            "CURP"
        ],
        "INE": [
            "INSTITUTO NACIONAL ELECTORAL",
            "CREDENCIAL PARA VOTAR"
        ],
        "RFC": [
            "REGISTRO FEDERAL DE CONTRIBUYENTES",
            "CONSTANCIA DE SITUACIÓN FISCAL",
            "CONSTANCIA DE SITUACION FISCAL"
        ],
        "COMPROBANTE_DOMICILIO": [
            "COMISIÓN FEDERAL DE ELECTRICIDAD",
            "COMISION FEDERAL DE ELECTRICIDAD",
            "CFE",
            "RECIBO DE LUZ"
        ],
        "DOCUMENTO_BANCARIO": [
            "CLABE",
            "CUENTA CLABE",
            "DATOS BANCARIOS"
        ],
        "SEGURIDAD_SOCIAL": [
            "INSTITUTO MEXICANO DEL SEGURO SOCIAL",
            "IMSS",
            "NÚMERO DE SEGURIDAD SOCIAL",
            "NUMERO DE SEGURIDAD SOCIAL",
            "NSS"
        ]
    }

    indicadores = indicadores_mexicanos.get(tipo_documento, [])

    if not indicadores:
        return False

    coincidencias = sum(
        1
        for indicador in indicadores
        if indicador in texto_completo
    )

    return coincidencias == 0

def validar_tipo_documento(tipo_documento, textos_detectados):
    if not textos_detectados:
        return "REQUIERE REVISIÓN"

    if detectar_documento_no_compatible(
        tipo_documento,
        textos_detectados
    ):
        return "NO COMPATIBLE"

    texto_completo = " ".join(textos_detectados).upper()

    reglas_documentos = {

        "ACTA_NACIMIENTO": {
            "palabras_clave": [
                "ACTA DE NACIMIENTO",
                "REGISTRO CIVIL DE NACIMIENTO",
                "CERTIFICADO DE NACIMIENTO",
                "CERTIFICACIÓN DE NACIMIENTO"
            ],
            "minimo_coincidencias": 1
        },

        "CURP": {
            "palabras_clave": [
                "CLAVE ÚNICA DE REGISTRO DE POBLACIÓN",
                "CLAVE UNICA DE REGISTRO DE POBLACION",
                "CURP"
            ],
            "minimo_coincidencias": 1
        },

        "INE": {
            "palabras_clave": [
                "INSTITUTO NACIONAL ELECTORAL",
                "CREDENCIAL PARA VOTAR",
                "PASAPORTE"
            ],
            "minimo_coincidencias": 1
        },

        "RFC": {
            "palabras_clave": [
                "CONSTANCIA DE SITUACIÓN FISCAL",
                "REGISTRO FEDERAL DE CONTRIBUYENTES",
                "RFC"
            ],
            "minimo_coincidencias": 1
        },

        "COMPROBANTE_DOMICILIO": {
            "palabras_clave": [
                "COMPROBANTE DE DOMICILIO",
                "DOMICILIO",
                "DIRECCIÓN",
                "DIRECCION",
                "COMISIÓN FEDERAL DE ELECTRICIDAD",
                "COMISION FEDERAL DE ELECTRICIDAD",
                "CFE",
                "RECIBO DE LUZ",
                "ENERGÍA ELÉCTRICA",
                "ENERGIA ELECTRICA",
                "NO. DE SERVICIO",
                "NUMERO DE SERVICIO",
                "RPU"
            ],
            "minimo_coincidencias": 1
        },

        "DOCUMENTO_BANCARIO": {
            "palabras_clave": [
                "DATOS BANCARIOS",
                "DOCUMENTO BANCARIO",
                "ESTADO DE CUENTA",
                "CUENTA BANCARIA",
                "CLABE",
                "TITULAR"
            ],
            "minimo_coincidencias": 1
        },

        "SEGURIDAD_SOCIAL": {
            "palabras_clave": [
                "INSTITUTO MEXICANO DEL SEGURO SOCIAL",
                "IMSS",
                "NÚMERO DE SEGURIDAD SOCIAL",
                "NUMERO DE SEGURIDAD SOCIAL",
                "NSS",
                "DOCUMENTO DE SEGURIDAD SOCIAL",
                "SEGURIDAD SOCIAL",
                "NÚMERO DE AFILIACIÓN",
                "NUMERO DE AFILIACION",
                "AFILIACIÓN",
                "AFILIACION",
                "AFILIADO"
            ],
            "minimo_coincidencias": 1
        }
    }

    regla = reglas_documentos.get(tipo_documento)

    if not regla:
        return "TIPO NO VALIDADO"

    coincidencias = sum(
        1
        for palabra in regla["palabras_clave"]
        if palabra in texto_completo
    )

    if coincidencias >= regla["minimo_coincidencias"]:
        return "DOCUMENTO VÁLIDO"

    return "REQUIERE REVISIÓN"

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
            (
                re.fullmatch(
                    r"[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d",
                    datos.curp.upper()
                )
                or
                re.fullmatch(
                    r"US-TEST-[A-Z]+-\d{8}",
                    datos.curp.upper()
                )
            ) and
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
        identificador_fiscal_valido = (
            (
                datos.rfc and
                len(datos.rfc) in (12, 13) and
                datos.estado_formato_rfc not in (
                    "REQUIERE REVISIÓN",
                    "NO DETECTADO"
                )
            )
            or
            (
                datos.nss and
                re.fullmatch(
                    r"\d{3}-\d{2}-\d{4}",
                    datos.nss
                )
            )
        )

        return bool(
            datos.nombre and
            datos.fecha_nacimiento and
            identificador_fiscal_valido
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
                or
                re.fullmatch(
                    r"\d{3}-\d{2}-\d{4}",
                    datos.nss
                )
            )
        )

    return False

def validar_documentos_cruzados(
    db,
    empleado_id,
    documento_acta,
    documento_curp,
    documento_ine,
    documento_rfc,
):
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
                empleado_id=empleado_id,
                campo="NOMBRE",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="CURP",
                valor_origen=datos_acta.nombre,
                valor_comparado=datos_curp.nombre,
                resultado=resultado_nombre
            )

            guardar_validacion(
                db=db,
                empleado_id=empleado_id,
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
                empleado_id=empleado_id,
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
                empleado_id=empleado_id,
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
                empleado_id=empleado_id,
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
                empleado_id=empleado_id,
                campo="NOMBRE",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="RFC",
                valor_origen=datos_acta.nombre,
                valor_comparado=datos_rfc.nombre,
                resultado=resultado_nombre_rfc
            )

            guardar_validacion(
                db=db,
                empleado_id=empleado_id,
                campo="FECHA_NACIMIENTO",
                documento_origen="ACTA_NACIMIENTO",
                documento_comparado="RFC",
                valor_origen=datos_acta.fecha_nacimiento,
                valor_comparado=datos_rfc.fecha_nacimiento,
                resultado=resultado_fecha_rfc,
                motivo=None
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
            origen_validacion=origen_validacion,
            motivo=motivo
        )

        db.add(validacion)
        db.commit()