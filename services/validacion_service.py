import unicodedata


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

    curp_1 = curp_1.strip().upper()
    curp_2 = curp_2.strip().upper()

    if curp_1 == curp_2:
        return "COINCIDE"

    return "NO COINCIDE"

def validar_tipo_documento(tipo_documento, textos_detectados):
    if not textos_detectados:
        return "REQUIERE REVISIÓN"

    texto_completo = " ".join(textos_detectados).upper()

    reglas_documentos = {
        "ACTA_NACIMIENTO": {
            "palabras_clave": [
                "ACTA DE NACIMIENTO",
                "FECHA DE NACIMIENTO"
            ],
            "minimo_coincidencias": 2
        },

        "CURP": {
            "palabras_clave": [
                "CLAVE ÚNICA DE REGISTRO DE POBLACIÓN",
                "CURP"
            ],
            "minimo_coincidencias": 1
        },

        "INE": {
            "palabras_clave": [
                "INSTITUTO NACIONAL ELECTORAL",
                "CREDENCIAL PARA VOTAR"
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