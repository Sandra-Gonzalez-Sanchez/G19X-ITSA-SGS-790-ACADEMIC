import os
import json
import urllib.request
import urllib.error
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/chat"
)
MODELO_IA = "qwen3:4b-instruct"


def validar_documento_con_ia(
    tipo_documento,
    datos_extraidos,
    nombre_empleado,
    validaciones
):


    comparaciones = []

    nombre_documento = datos_extraidos.get("nombre")

    if (
            tipo_documento != "COMPROBANTE_DOMICILIO"
            and nombre_documento
            and nombre_empleado
    ):
        comparaciones.append({
            "campo": "NOMBRE",
            "valor_documento": nombre_documento,
            "valor_referencia": nombre_empleado
        })

    for validacion in validaciones:
        campo = validacion.get("campo")
        valor_origen = validacion.get("valor_origen")
        valor_comparado = validacion.get("valor_comparado")

        documento_origen = validacion.get("documento_origen")
        documento_comparado = validacion.get("documento_comparado")

        if not (
                campo
                and valor_origen is not None
                and valor_comparado is not None
        ):
            continue

        if documento_origen == tipo_documento:
            valor_documento = valor_origen
            valor_referencia = valor_comparado
            documento_referencia = documento_comparado

        elif documento_comparado == tipo_documento:
            valor_documento = valor_comparado
            valor_referencia = valor_origen
            documento_referencia = documento_origen

        else:
            continue

        if documento_referencia == "COMPROBANTE_DOMICILIO":
            continue

        if campo == "FECHA_NACIMIENTO":
            if documento_referencia not in (
                    "CURP",
                    "INE",
                    "RFC"
            ):
                continue

        if campo == "CURP":
            if documento_referencia != "INE":
                continue

        comparaciones.append({
            "campo": campo,
            "valor_documento": valor_documento,
            "valor_referencia": valor_referencia,
            "documento_documento": tipo_documento,
            "documento_referencia": documento_referencia,
            "resultado_regla": validacion.get("resultado_regla"),
            "motivo_regla": validacion.get("motivo_regla")
        })

    informacion = {
        "tipo_documento": tipo_documento,
        "comparaciones_a_validar": comparaciones
    }

    prompt = f"""
Eres un sistema de validación documental mediante inteligencia artificial.

Debes validar EXCLUSIVAMENTE las comparaciones proporcionadas.

IMPORTANTE:
- El nombre del empleado proporcionado por el sistema es la única referencia válida para identificar al empleado.
- Nunca debes obtener el nombre del empleado directamente del texto OCR.
- El documento puede contener nombres de padres, madres, tutores, testigos, representantes u otras personas.
- Esos nombres NO deben utilizarse como referencia del empleado.
- Para el campo NOMBRE, utiliza exclusivamente el valor de "valor_referencia" proporcionado en la comparación.
- Nunca sustituyas "valor_referencia" por otro nombre encontrado en el documento.

Cada comparación contiene:
- campo: indica qué dato estás validando;
- valor_documento: valor extraído de un documento mediante OCR;
- valor_referencia: valor equivalente utilizado para compararlo;
- resultado_regla: resultado obtenido previamente por las reglas de comparación;
- motivo_regla: motivo de la comparación cuando existe.

El resultado_regla es una evidencia importante de la validación.
La IA debe analizar esta evidencia y confirmar si la comparación es consistente.

REGLAS OBLIGATORIAS:
- Analiza cada comparación de manera independiente.
- Compara únicamente valor_documento contra valor_referencia
  dentro de la misma comparación.
- Nunca compares una comparación con otra.
- Nunca relaciones campos diferentes.
- No inventes datos.
- No cambies el significado de los valores.
- Para campos de identidad como NOMBRE, CURP, RFC o FECHA_NACIMIENTO,
  la comparación debe ser estricta.
- En el campo NOMBRE, todos los nombres y apellidos deben coincidir.
- Si cambia, falta o se agrega un nombre o apellido, la comparación es INCONSISTENTE.
- Ejemplo: "JUAN PEREZ GARCIA" y "JUAN PEREZ LOPEZ" son INCONSISTENTES,
  porque GARCIA y LOPEZ son apellidos diferentes.
- Ejemplo: "JUAN PEREZ LOPEZ" y "JUAN PEREZ LOPEZ" son CONSISTENTES.
- En CURP y RFC, cualquier carácter diferente representa una inconsistencia.
- En fechas, ambas fechas deben representar exactamente la misma fecha.
- Puedes ignorar únicamente diferencias de mayúsculas, minúsculas,
  acentos y espacios adicionales.
- No consideres dos valores consistentes solamente porque son parecidos.
- Ante una diferencia real entre valor_documento y valor_referencia,
  debes incluirla obligatoriamente en "inconsistencias" y establecer
  "requiere_revision": true.
- No determines autenticidad, falsificación ni validez legal del documento.
- Si resultado_regla es "NO COINCIDE", debes considerar esa comparación como INCONSISTENTE.
- Si resultado_regla es "INCONSISTENTE", debes considerar esa comparación como INCONSISTENTE.
- Si una comparación tiene resultado_regla "NO COINCIDE" o "INCONSISTENTE",
  debes establecer "requiere_revision": true.
- Nunca puedes devolver "VALIDADO" si alguna comparación tiene
  resultado_regla "NO COINCIDE" o "INCONSISTENTE".
- El motivo_regla debe utilizarse como apoyo para explicar la inconsistencia.
- Nunca muestres al usuario nombres de campos internos del sistema.
- Nunca menciones "resultado_regla", "motivo_regla",
  "NOMBRE_EMPLEADO", "documento_origen" ni "documento_comparado".
- Nunca expliques cómo funciona internamente la validación.
- Los mensajes deben estar redactados en lenguaje claro para el empleado.
- Si la comparación corresponde al campo NOMBRE y la referencia es el
  nombre del empleado, el motivo debe ser EXACTAMENTE:
  "El nombre del documento no coincide con el nombre registrado para el empleado."
- No agregues nombres de otros documentos al motivo.
- No menciones "RFC", "Acta de nacimiento", "CURP", "INE" u otros
  documentos dentro de este motivo.
- No expliques con qué otros documentos se relaciona la comparación.

- Si la comparación corresponde al campo FECHA_NACIMIENTO y existe otro
  documento como referencia, indica que la fecha de nacimiento del
  documento no coincide con la fecha de nacimiento del documento de
  referencia.

- Si la comparación corresponde a CURP o RFC y existe otro documento
  como referencia, indica que el valor del documento no coincide con
  el valor del documento de referencia.

- Nunca digas que una fecha de nacimiento está "registrada" por RH,
  porque RH no registra la fecha de nacimiento del empleado.

- Nunca inventes que RH registró una CURP, RFC o fecha de nacimiento.

- Cuando exista una comparación entre dos documentos, utiliza los nombres
  de los documentos para explicar la diferencia de forma clara.

- No muestres nombres técnicos como ACTA_NACIMIENTO. Utiliza nombres
  comprensibles como "Acta de nacimiento", "CURP", "INE",
  "RFC" o "comprobante de domicilio".

- Si no existe un documento de referencia para un campo, no inventes
  una comparación.
- No muestres resultados técnicos de las reglas de comparación.

INFORMACIÓN:
{json.dumps(informacion, ensure_ascii=False, default=str)}

Devuelve EXCLUSIVAMENTE JSON válido con esta estructura:

{{
    "resultado": "VALIDADO",
    "requiere_revision": false,
    "inconsistencias": [],
    "resumen": "No se detectaron inconsistencias."
}}

Si detectas una inconsistencia:

{{
    "resultado": "INCONSISTENTE",
    "requiere_revision": true,
    "inconsistencias": [
        {{
            "campo": "NOMBRE",
            "valor_documento": "valor recibido",
            "valor_referencia": "valor recibido",
            "motivo": "Descripción breve de la diferencia"
        }}
    ],
    "resumen": "Se detectaron inconsistencias en la validación documental."
}}
"""

    payload = {
        "model": MODELO_IA,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {
            "temperature": 0
        }
    }

    solicitud = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            solicitud,
            timeout=180
        ) as respuesta:
            resultado_ollama = json.loads(
                respuesta.read().decode("utf-8")
            )

        contenido = resultado_ollama["message"]["content"]
        analisis = json.loads(contenido)

        resultado_ia = str(
            analisis.get("resultado", "INCONSISTENTE")
        ).upper()

        requiere_revision = bool(
            analisis.get("requiere_revision", True)
        )

        inconsistencias = analisis.get(
            "inconsistencias",
            []
        )

        if not isinstance(inconsistencias, list):
            inconsistencias = []

        if inconsistencias:
            requiere_revision = True
            resultado_ia = "INCONSISTENTE"

        if requiere_revision:
            resultado_ia = "INCONSISTENTE"
        else:
            resultado_ia = "VALIDADO"

        return {
            "disponible": True,
            "resultado": resultado_ia,
            "requiere_revision": requiere_revision,
            "inconsistencias": inconsistencias,
            "resumen": analisis.get(
                "resumen",
                "Validación documental realizada mediante IA."
            )
        }

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        KeyError
    ) as error:

        logger.error("ERROR EN VALIDACIÓN DOCUMENTAL CON IA: %s", error)

        return {
            "disponible": False,
            "resultado": "NO DISPONIBLE",
            "requiere_revision": True,
            "inconsistencias": [],
            "resumen": "No fue posible realizar la validación documental mediante IA."
        }