from types import SimpleNamespace

from services.validacion_service import (
    validar_tipo_documento,
    validar_datos_esenciales,
)

def test_ine_se_reconoce():
    textos = [
        "INSTITUTO NACIONAL ELECTORAL",
        "CREDENCIAL PARA VOTAR"
    ]

    assert validar_tipo_documento("INE", textos) == "DOCUMENTO VÁLIDO"


def test_acta_subida_como_ine_no_es_compatible():
    textos = [
        "ACTA DE NACIMIENTO",
        "REGISTRO CIVIL"
    ]

    assert validar_tipo_documento("INE", textos) == "NO COMPATIBLE"


def test_documento_sin_texto_no_es_compatible():
    textos = []

    assert validar_tipo_documento("INE", textos) == "NO COMPATIBLE"


# Pruebas para validar_datos_esenciales

def test_curp_valida():
    datos = SimpleNamespace(
        nombre="ANA LOPEZ",
        curp="LOPA900101MDFPRN01",
        estado_formato_curp="FORMATO VÁLIDO",
    )

    assert validar_datos_esenciales("CURP", datos) is True


def test_curp_de_prueba_se_rechaza():
    datos = SimpleNamespace(
        nombre="ANA LOPEZ",
        curp="US-TEST-1234",
        estado_formato_curp="FORMATO VÁLIDO",
    )

    assert validar_datos_esenciales("CURP", datos) is False


def test_curp_con_formato_incorrecto_se_rechaza():
    datos = SimpleNamespace(
        nombre="ANA LOPEZ",
        curp="CURP-INCORRECTA",
        estado_formato_curp="FORMATO VÁLIDO",
    )

    assert validar_datos_esenciales("CURP", datos) is False


def test_documento_bancario_con_clabe_valida():
    datos = SimpleNamespace(
        clabe="012345678901234567"
    )

    assert validar_datos_esenciales("DOCUMENTO_BANCARIO", datos) is True


def test_documento_bancario_sin_clabe_se_rechaza():
    datos = SimpleNamespace(
        clabe=None
    )

    assert validar_datos_esenciales("DOCUMENTO_BANCARIO", datos) is False


def test_nss_de_nueve_digitos_se_rechaza():
    datos = SimpleNamespace(
        nombre="ANA LOPEZ",
        nss="123456789"
    )

    assert validar_datos_esenciales("SEGURIDAD_SOCIAL", datos) is False