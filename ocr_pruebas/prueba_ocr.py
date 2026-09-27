import os
import re

os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR

print("Iniciando PaddleOCR...")

ocr = PaddleOCR(
    lang="es",
    enable_mkldnn=False
)

print("Analizando documento...")

resultado = ocr.predict(
    input="ocr_pruebas/acta_prueba.pdf"
)

print("\n=== TEXTO RECONOCIDO ===")

for pagina in resultado:
    textos = pagina["rec_texts"]

    for texto in textos:
        print(texto)

print("\n=== CURP EXTRAÍDA ===")

patron_curp = r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b"

curp = None

for texto in textos:
    coincidencia = re.search(patron_curp, texto.upper())

    if coincidencia:
        curp = coincidencia.group()
        break

print("CURP:", curp)

curp_candidata = None

if curp is None:
    patron_candidato = r"\b[A-Z]{4}\d{6}[A-Z0-9]{8,9}\b"

    for texto in textos:
        coincidencia = re.search(patron_candidato, texto.upper())

        if coincidencia:
            curp_candidata = coincidencia.group()
            break

print("CURP candidata:", curp_candidata)
if curp:
    estado_curp = "VALIDADO"
elif curp_candidata:
    estado_curp = "EN REVISIÓN"
else:
    estado_curp = "PENDIENTE"

print("Estado CURP:", estado_curp)


print("\n=== RFC EXTRAÍDO ===")

patron_rfc = r"\b[A-ZÑ&]{4}\d{6}[A-Z0-9]{3}\b"

rfc = None

for texto in textos:
    coincidencia = re.search(patron_rfc, texto.upper())

    if coincidencia:
        rfc = coincidencia.group()
        break

print("RFC:", rfc)

print("\n=== NOMBRE EXTRAÍDO ===")

nombre = None

for i, texto in enumerate(textos):
    if texto.strip().upper() in ["NOMBRE:", "NOMBRE COMPLETO:"]:
        if i + 1 < len(textos):
            nombre = textos[i + 1]
            break

print("Nombre:", nombre)

print("\n=== FECHA DE NACIMIENTO EXTRAÍDA ===")

fecha_nacimiento = None

patron_fecha = r"\b\d{2}/\d{2}/\d{4}\b"

for i, texto in enumerate(textos):
    if "FECHA DE NACIMIENTO" in texto.upper():

        for siguiente_texto in textos[i + 1:i + 6]:
            coincidencia = re.search(patron_fecha, siguiente_texto)

            if coincidencia:
                fecha_nacimiento = coincidencia.group()
                break

        break

print("Fecha de nacimiento:", fecha_nacimiento)

datos_extraidos = {
    "nombre": nombre,
    "fecha_nacimiento": fecha_nacimiento,
    "curp": curp,
    "curp_candidata": curp_candidata,
    "estado_curp": estado_curp,
    "rfc": rfc
}

print("\n=== DATOS EXTRAÍDOS DEL DOCUMENTO ===")

for campo, valor in datos_extraidos.items():
    print(f"{campo}: {valor}")