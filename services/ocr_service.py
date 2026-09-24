import os
import re

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

def extraer_rfc(textos):
    patron_rfc = r"\b[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}\b"

    for texto in textos:
        coincidencia = re.search(patron_rfc, texto.upper())

        if coincidencia:
            return coincidencia.group()

    return None

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
    datos = {
        "nombre": extraer_nombre(textos),
        "fecha_nacimiento": extraer_fecha_nacimiento(textos),
        "curp": extraer_curp(textos),
        "rfc": extraer_rfc(textos)
    }

    return datos

def procesar_documento(ruta_documento):
    textos = leer_documento(ruta_documento)
    datos = extraer_datos(textos)

    return datos