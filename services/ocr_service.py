import os
import re
from services.comparacion_service import (
    comparar_nombres,
    comparar_fechas,
    comparar_curp,
    comparar_rfc,
)

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
    patron_identificador_usa = r"\bUS-TEST-[A-Z]+-\d{8}\b"

    for texto in textos:
        texto_mayusculas = texto.upper()

        coincidencia_curp = re.search(
            patron_curp,
            texto_mayusculas
        )

        if coincidencia_curp:
            return coincidencia_curp.group()

        coincidencia_usa = re.search(
            patron_identificador_usa,
            texto_mayusculas
        )

        if coincidencia_usa:
            return coincidencia_usa.group()

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
    patron_nit = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d\b"

    for texto in textos:
        texto_mayusculas = texto.upper()

        coincidencia_rfc = re.search(
            patron_rfc,
            texto_mayusculas
        )

        if coincidencia_rfc:
            return coincidencia_rfc.group()

        if (
            "NIT" in texto_mayusculas
            or "IDENTIFICACIÓN TRIBUTARIA" in texto_mayusculas
            or "IDENTIFICACION TRIBUTARIA" in texto_mayusculas
        ):
            coincidencia_nit = re.search(
                patron_nit,
                texto_mayusculas
            )

            if coincidencia_nit:
                return coincidencia_nit.group()

    return None

def extraer_clabe(textos):
    patron_clabe = r"(?<!\d)(?:\d\s*){18}(?!\d)"

    for i, texto in enumerate(textos):
        texto_mayusculas = texto.strip().upper()

        if "CLABE" in texto_mayusculas:
            coincidencia = re.search(
                patron_clabe,
                texto_mayusculas
            )

            if coincidencia:
                return re.sub(
                    r"\s+",
                    "",
                    coincidencia.group()
                )

            for siguiente_texto in textos[i + 1:i + 3]:
                siguiente_mayusculas = siguiente_texto.strip().upper()

                coincidencia = re.search(
                    patron_clabe,
                    siguiente_mayusculas
                )

                if coincidencia:
                    return re.sub(
                        r"\s+",
                        "",
                        coincidencia.group()
                    )

    return None

def extraer_nss(textos):
    patrones = [
        r"\b\d{11}\b",
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b\d{9}\b",
        r"\bSS-[A-Z]{2}-\d{4}-\d{4}\b"
    ]

    etiquetas = [
        "NÚMERO DE SEGURIDAD SOCIAL",
        "NUMERO DE SEGURIDAD SOCIAL",
        "NSS:",
        "NSS",
        "SOCIAL SECURITY NUMBER",
        "SSN:",
        "SSN",
        "NÚMERO DE AFILIACIÓN",
        "NUMERO DE AFILIACION",
        "AFILIACIÓN",
        "AFILIACION"
    ]

    for i, texto in enumerate(textos):
        texto_mayusculas = texto.strip().upper()

        if any(etiqueta in texto_mayusculas for etiqueta in etiquetas):
            for patron in patrones:
                coincidencia = re.search(
                    patron,
                    texto_mayusculas
                )

                if coincidencia:
                    return coincidencia.group()

            for siguiente_texto in textos[i + 1:i + 3]:
                for patron in patrones:
                    coincidencia = re.search(
                        patron,
                        siguiente_texto.upper()
                    )

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
    etiquetas_nombre = [
        "NOMBRE",
        "NOMBRE COMPLETO",
        "FULL NAME",
        "NAME",
        "NOMBRE / RAZÓN",
        "NOMBRE/RAZÓN",
        "NOMBRE(S)",
        "NOMBRE(S):",
        "TITULAR",
        "AFILIADO"
    ]

    textos_ignorar = [
        "NOMBRE DE LA PERSONA",
        "NOMBRE DEL TITULAR",
        "NOMBRE / RAZÓN",
        "NOMBRE/RAZÓN",
        "SEXO M",
        "SEXO F"
    ]

    texto_completo = " ".join(textos).upper()


    if (
        "COMISIÓN FEDERAL DE ELECTRICIDAD" in texto_completo
        or "COMISION FEDERAL DE ELECTRICIDAD" in texto_completo
    ):
        for i, texto in enumerate(textos):
            candidato = texto.strip()

            if not candidato:
                continue

            if (
                len(candidato.split()) >= 3
                and candidato.replace(" ", "").isalpha()
                and i + 1 < len(textos)
                and textos[i + 1].strip().upper() == "TOTAL A PAGAR:"
            ):
                return candidato

        for i, texto in enumerate(textos):
            texto_mayusculas = texto.strip().upper()

            if texto_mayusculas == "NOMBRE, DENOMINACIÓN O RAZÓN":
                for texto_anterior in reversed(textos[max(0, i - 3):i]):
                    candidato = texto_anterior.strip()

                    if (
                        candidato
                        and candidato.upper() != "SOCIAL"
                        and candidato.replace(" ", "").isalpha()
                        and len(candidato.split()) >= 2
                    ):
                        return candidato

    for i, texto in enumerate(textos):
        texto_mayusculas = texto.strip().upper()

        if (
                "NOMBRE(S)" in texto_mayusculas
                and "PRIMER APELLIDO" in texto_mayusculas
                and "SEGUNDO APELLIDO" in texto_mayusculas
        ):
            for siguiente_texto in textos[i + 1:i + 4]:
                candidato = siguiente_texto.strip()

                if (
                        candidato
                        and len(candidato.split()) >= 3
                        and candidato.replace(" ", "").isalpha()
                ):
                    return candidato

    for i, texto in enumerate(textos):
        texto_limpio = texto.strip()
        texto_mayusculas = texto_limpio.upper().rstrip(":")

        if texto_mayusculas == "NOMBRE":
            siguientes = [
                t.strip()
                for t in textos[i + 1:i + 7]
                if t.strip()
            ]

            if (
                siguientes
                and siguientes[0].upper().startswith("SEXO")
            ):
                candidatos = []

                for candidato in siguientes[1:]:
                    candidato_mayusculas = candidato.upper().rstrip(":")

                    if candidato_mayusculas in [
                        "DOMICILIO",
                        "CURP",
                        "AÑO DE REGISTRO",
                        "SECCIÓN",
                        "VIGENCIA",
                        "FECHA DE NACIMIENTO",
                        "PRIMER APELLIDO",
                        "SEGUNDO APELLIDO"
                    ]:
                        break

                    if (
                        candidato
                        and candidato.replace(" ", "").isalpha()
                    ):
                        candidatos.append(candidato)

                if len(candidatos) >= 3:
                    return " ".join([
                        candidatos[2],
                        candidatos[0],
                        candidatos[1]
                    ])

        if texto_mayusculas in ["NOMBRE(S)", "NOMBRE(S):"]:
            if i >= 3:
                nombre = textos[i - 3].strip()
                apellido_paterno = textos[i - 2].strip()
                apellido_materno = textos[i - 1].strip()

                valores = [
                    nombre,
                    apellido_paterno,
                    apellido_materno
                ]

                if all(
                    valor
                    and valor.replace(" ", "").isalpha()
                    for valor in valores
                ):
                    return " ".join(valores)

        if texto_mayusculas in etiquetas_nombre:
            for siguiente_texto in textos[i + 1:i + 5]:
                candidato = siguiente_texto.strip()
                candidato_mayusculas = candidato.upper().rstrip(":")

                if candidato_mayusculas in textos_ignorar:
                    continue

                if candidato_mayusculas.startswith("SEXO"):
                    continue

                if candidato_mayusculas in [
                    "DOMICILIO",
                    "CURP",
                    "FECHA DE NACIMIENTO",
                    "AÑO DE REGISTRO",
                    "SECCIÓN",
                    "VIGENCIA",
                    "PRIMER APELLIDO",
                    "SEGUNDO APELLIDO"
                ]:
                    continue

                if candidato:
                    return candidato

        for etiqueta in etiquetas_nombre:
            if texto_mayusculas.startswith(etiqueta + ":"):
                nombre = texto_limpio[len(etiqueta) + 1:].strip()

                if nombre and nombre.upper() not in textos_ignorar:
                    return nombre

    return None


def extraer_domicilio(textos):
    etiquetas_domicilio = [
        "DOMICILIO",
        "DIRECCIÓN",
        "DIRECCION",
        "SERVICE ADDRESS",
        "ADDRESS"
    ]

    for i, texto in enumerate(textos):
        texto_mayusculas = texto.strip().upper()

        if texto_mayusculas in etiquetas_domicilio:
            lineas_domicilio = []

            for siguiente_texto in textos[i + 1:i + 4]:
                linea = siguiente_texto.strip()

                if linea:
                    lineas_domicilio.append(linea)

            if lineas_domicilio:
                return " ".join(lineas_domicilio)

    texto_completo = " ".join(textos).upper()

    if "CFE" in texto_completo and "NO. DE SERVICIO" in texto_completo:
        indice_servicio = None

        for i, texto in enumerate(textos):
            if "NO. DE SERVICIO" in texto.upper():
                indice_servicio = i
                break

        if indice_servicio is not None:
            candidatos = []

            for texto in textos[max(0, indice_servicio - 6):indice_servicio]:
                linea = texto.strip()

                if not linea:
                    continue

                linea_mayusculas = linea.upper()

                if "TOTAL A PAGAR" in linea_mayusculas:
                    continue

                if linea.startswith("$"):
                    continue

                candidatos.append(linea)

            if candidatos:
                return " ".join(candidatos[-4:])

    return None

def extraer_fecha_nacimiento(textos):
    patrones_fecha = [
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        r"\b\d{1,2}-\d{1,2}-\d{4}\b",
        r"\b\d{1,2}\.\d{1,2}\.\d{4}\b"
    ]

    etiquetas_fecha = [
        "FECHA DE NACIMIENTO",
        "DATE OF BIRTH",
        "BIRTH DATE",
        "DOB"
    ]

    for i, texto in enumerate(textos):
        texto_mayusculas = texto.upper()

        if any(
            etiqueta in texto_mayusculas
            for etiqueta in etiquetas_fecha
        ):
            # Buscar primero en los textos cercanos posteriores.
            for siguiente_texto in textos[i + 1:i + 6]:
                siguiente_mayusculas = siguiente_texto.upper()

                for patron in patrones_fecha:
                    coincidencia = re.search(
                        patron,
                        siguiente_mayusculas
                    )

                    if coincidencia:
                        return coincidencia.group()

            for texto_anterior in textos[max(0, i - 6):i]:
                anterior_mayusculas = texto_anterior.upper()

                for patron in patrones_fecha:
                    coincidencia = re.search(
                        patron,
                        anterior_mayusculas
                    )

                    if coincidencia:
                        return coincidencia.group()

            break

    return None


def extraer_datos(textos):
    analisis_curp = analizar_curp(textos)
    analisis_rfc = analizar_rfc(textos)
    fecha_nacimiento = extraer_fecha_nacimiento(textos)
    domicilio = extraer_domicilio(textos)
    clabe = extraer_clabe(textos)
    nss = extraer_nss(textos)

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
        "domicilio": domicilio,
        "clabe": clabe,
        "nss": nss,
        "curp": analisis_curp["curp"],
        "curp_candidata": analisis_curp["curp_candidata"],
        "estado_formato_curp": analisis_curp["estado_formato_curp"],
        "rfc": analisis_rfc["rfc"],
        "estado_formato_rfc": analisis_rfc["estado_formato_rfc"],
        "comparacion_fecha_curp": comparacion_fecha_curp,
        "comparacion_fecha_rfc": comparacion_fecha_rfc
    }

    return datos

def procesar_documento_ocr(ruta_documento):
    textos = leer_documento(ruta_documento)
    datos = extraer_datos(textos)

    datos["textos_detectados"] = textos

    return datos


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

def obtener_resultado_general(comparaciones):
    if "NO COINCIDE" in comparaciones.values():
        return "REQUIERE REVISIÓN"

    if "NO SE PUEDE COMPARAR" in comparaciones.values():
        return "REQUIERE REVISIÓN"

    return "SIN INCONSISTENCIAS"

def validar_documentos(datos_documento_1, datos_documento_2):
    comparaciones = comparar_documentos(
        datos_documento_1,
        datos_documento_2
    )

    resultado_general = obtener_resultado_general(comparaciones)

    return {
        "comparaciones": comparaciones,
        "resultado_general": resultado_general
    }