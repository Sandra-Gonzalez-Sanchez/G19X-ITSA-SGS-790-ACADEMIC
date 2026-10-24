import unicodedata
from datetime import datetime


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