import os
import re
import unicodedata

os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    lang="es",
    enable_mkldnn=False
)

def leer_documento(ruta_documento):
    resultado = ocr.predict(
        input=ruta_documento
    )

    textos = []

    for pagina in resultado:
        textos.extend(pagina["rec_texts"])

    return textos

def extraer_curp(textos):
    patron_curp = r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b"

    for texto in textos:
        coincidencia = re.search(patron_curp, texto.upper())

        if coincidencia:
            return coincidencia.group()

    return None

def extraer_curp_candidata(textos):
    patron_candidato = r"\b[A-Z]{4}\d{6}[A-Z0-9]{8,9}\b"

    for texto in textos:
        coincidencia = re.search(patron_candidato, texto.upper())

        if coincidencia:
            return coincidencia.group()

    return None

def analizar_curp(textos):
    curp = extraer_curp(textos)

    if curp:
        return {
            "curp": curp,
            "curp_candidata": None,
            "estado_formato_curp": "FORMATO VÁLIDO"
        }

    curp_candidata = extraer_curp_candidata(textos)

    if curp_candidata:
        return {
            "curp": None,
            "curp_candidata": curp_candidata,
            "estado_formato_curp": "REQUIERE REVISIÓN"
        }

    return {
        "curp": None,
        "curp_candidata": None,
        "estado_formato_curp": "NO DETECTADA"
    }

def extraer_fecha_desde_curp(curp):
    if not curp or len(curp) != 18:
        return None

    anio_corto = curp[4:6]
    mes = curp[6:8]
    dia = curp[8:10]
    caracter_siglo = curp[16]

    if caracter_siglo.isdigit():
        anio = "19" + anio_corto
    elif caracter_siglo.isalpha():
        anio = "20" + anio_corto
    else:
        return None

    return f"{dia}/{mes}/{anio}"

def comparar_fecha_con_curp(fecha_nacimiento, curp):
    if not fecha_nacimiento or not curp:
        return "NO SE PUEDE COMPARAR"

    fecha_curp = extraer_fecha_desde_curp(curp)

    if not fecha_curp:
        return "NO SE PUEDE COMPARAR"

    if fecha_nacimiento == fecha_curp:
        return "COINCIDE"

    return "NO COINCIDE"

def extraer_rfc(textos):
    patron_rfc = r"\b[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}\b"

    for texto in textos:
        coincidencia = re.search(patron_rfc, texto.upper())

        if coincidencia:
            return coincidencia.group()

    return None

def analizar_rfc(textos):
    rfc = extraer_rfc(textos)

    if rfc:
        return {
            "rfc": rfc,
            "estado_formato_rfc": "FORMATO VÁLIDO"
        }

    return {
        "rfc": None,
        "estado_formato_rfc": "NO DETECTADO"
    }

def extraer_fecha_desde_rfc(rfc):
    if not rfc or len(rfc) != 13:
        return None

    anio = rfc[4:6]
    mes = rfc[6:8]
    dia = rfc[8:10]

    return {
        "anio": anio,
        "mes": mes,
        "dia": dia
    }

def comparar_fecha_con_rfc(fecha_nacimiento, rfc):
    if not fecha_nacimiento or not rfc:
        return "NO SE PUEDE COMPARAR"

    fecha_rfc = extraer_fecha_desde_rfc(rfc)

    if not fecha_rfc:
        return "NO SE PUEDE COMPARAR"

    partes_fecha = fecha_nacimiento.split("/")

    if len(partes_fecha) != 3:
        return "NO SE PUEDE COMPARAR"

    dia, mes, anio = partes_fecha

    if (
        dia == fecha_rfc["dia"]
        and mes == fecha_rfc["mes"]
        and anio[-2:] == fecha_rfc["anio"]
    ):
        return "COINCIDE"

    return "NO COINCIDE"

def extraer_nombre(textos):
    etiquetas_nombre = ["NOMBRE:", "NOMBRE COMPLETO:"]

    for i, texto in enumerate(textos):
        if texto.strip().upper() in etiquetas_nombre:
            if i + 1 < len(textos):
                return textos[i + 1].strip()

    return None

def extraer_fecha_nacimiento(textos):
    patron_fecha = r"\b\d{2}/\d{2}/\d{4}\b"

    for i, texto in enumerate(textos):
        if "FECHA DE NACIMIENTO" in texto.upper():

            for siguiente_texto in textos[i + 1:i + 6]:
                coincidencia = re.search(patron_fecha, siguiente_texto)

                if coincidencia:
                    return coincidencia.group()

            break

    return None

def extraer_datos(textos):
    analisis_curp = analizar_curp(textos)
    analisis_rfc = analizar_rfc(textos)
    fecha_nacimiento = extraer_fecha_nacimiento(textos)

    comparacion_fecha_curp = comparar_fecha_con_curp(
        fecha_nacimiento,
        analisis_curp["curp"]
    )

    comparacion_fecha_rfc = comparar_fecha_con_rfc(
        fecha_nacimiento,
        analisis_rfc["rfc"]
    )

    datos = {
        "nombre": extraer_nombre(textos),
        "fecha_nacimiento": fecha_nacimiento,
        "curp": analisis_curp["curp"],
        "curp_candidata": analisis_curp["curp_candidata"],
        "estado_formato_curp": analisis_curp["estado_formato_curp"],
        "rfc": analisis_rfc["rfc"],
        "estado_formato_rfc": analisis_rfc["estado_formato_rfc"],
        "comparacion_fecha_curp": comparacion_fecha_curp,
        "comparacion_fecha_rfc": comparacion_fecha_rfc
    }

    return datos

def procesar_documento(ruta_documento):
    textos = leer_documento(ruta_documento)
    datos = extraer_datos(textos)

    return datos

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

def comparar_fechas(fecha_1, fecha_2):
    if not fecha_1 or not fecha_2:
        return "NO SE PUEDE COMPARAR"

    if fecha_1 == fecha_2:
        return "COINCIDE"

    return "NO COINCIDE"

def comparar_curp(curp_1, curp_2):
    if not curp_1 or not curp_2:
        return "NO SE PUEDE COMPARAR"

    if curp_1.strip().upper() == curp_2.strip().upper():
        return "COINCIDE"

    return "NO COINCIDE"

def comparar_rfc(rfc_1, rfc_2):
    if not rfc_1 or not rfc_2:
        return "NO SE PUEDE COMPARAR"

    if rfc_1.strip().upper() == rfc_2.strip().upper():
        return "COINCIDE"

    return "NO COINCIDE"

def comparar_documentos(datos_documento_1, datos_documento_2):
    resultado = {
        "nombre": comparar_nombres(
            datos_documento_1.get("nombre"),
            datos_documento_2.get("nombre")
        ),
        "fecha_nacimiento": comparar_fechas(
            datos_documento_1.get("fecha_nacimiento"),
            datos_documento_2.get("fecha_nacimiento")
        ),
        "curp": comparar_curp(
            datos_documento_1.get("curp"),
            datos_documento_2.get("curp")
        ),
        "rfc": comparar_rfc(
            datos_documento_1.get("rfc"),
            datos_documento_2.get("rfc")
        )
    }

    return resultado