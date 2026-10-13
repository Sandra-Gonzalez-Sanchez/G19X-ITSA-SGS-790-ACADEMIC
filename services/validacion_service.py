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

def validar_tipo_documento(tipo_documento, textos_detectados):
    if not textos_detectados:
        return "REQUIERE REVISIÓN"

    texto_completo = " ".join(textos_detectados).upper()

    reglas_documentos = {

        "ACTA_NACIMIENTO": {
            "palabras_clave": [
                "ACTA DE NACIMIENTO",
                "REGISTRO CIVIL DE NACIMIENTO",
                "CERTIFICADO DE NACIMIENTO",
                "CERTIFICACIÓN DE NACIMIENTO",
                "BIRTH CERTIFICATE",
                "CERTIFICATE OF BIRTH"
            ],
            "minimo_coincidencias": 1
        },

        "CURP": {
            "palabras_clave": [
                "CLAVE ÚNICA DE REGISTRO DE POBLACIÓN",
                "CLAVE UNICA DE REGISTRO DE POBLACION",
                "CURP",
                "NATIONAL IDENTIFICATION NUMBER",
                "PERSONAL IDENTIFICATION NUMBER",
                "NATIONAL ID NUMBER",
                "IDENTIFICATION NUMBER"
            ],
            "minimo_coincidencias": 1
        },

        "INE": {
            "palabras_clave": [
                "INSTITUTO NACIONAL ELECTORAL",
                "CREDENCIAL PARA VOTAR",
                "IDENTIFICATION CARD",
                "ID CARD",
                "DRIVER LICENSE",
                "DRIVER'S LICENSE",
                "STATE ID",
                "STATE IDENTIFICATION",
                "CÉDULA DE CIUDADANÍA",
                "CEDULA DE CIUDADANIA",
                "PASSPORT",
                "PASAPORTE"
            ],
            "minimo_coincidencias": 1
        },

        "RFC": {
            "palabras_clave": [
                "CONSTANCIA DE SITUACIÓN FISCAL",
                "REGISTRO FEDERAL DE CONTRIBUYENTES",
                "RFC",
                "DOCUMENTO TRIBUTARIO",
                "IDENTIFICACIÓN TRIBUTARIA",
                "IDENTIFICACION TRIBUTARIA",
                "NIT",
                "RUT",
                "REGISTRO ÚNICO TRIBUTARIO",
                "REGISTRO UNICO TRIBUTARIO",
                "DIAN"
            ],
            "minimo_coincidencias": 1
        },

        "COMPROBANTE_DOMICILIO": {
    "palabras_clave": [
        "COMPROBANTE DE DOMICILIO",
        "PROOF OF ADDRESS",
        "ADDRESS VERIFICATION",
        "UTILITY BILL",
        "ELECTRICITY BILL",
        "WATER BILL",
        "GAS BILL",
        "TELEPHONE BILL",
        "PHONE BILL",
        "RESIDENTIAL ADDRESS",
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
                "BANK STATEMENT",
                "BANK ACCOUNT",
                "BANK ACCOUNT NUMBER",
                "ACCOUNT NUMBER",
                "BANK DETAILS",
                "BANK INFORMATION",
                "CLABE",
                "TITULAR",
                "ACCOUNT HOLDER"
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
        "AFILIADO",
        "COLOMBIA",
        "SOCIAL SECURITY",
        "SOCIAL SECURITY RECORD",
        "SOCIAL SECURITY NUMBER",
        "SSN",
        "UNITED STATES"
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