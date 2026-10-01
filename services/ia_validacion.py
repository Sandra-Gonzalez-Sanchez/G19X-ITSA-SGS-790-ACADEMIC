import json
import urllib.request
import urllib.error


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODELO_IA = "qwen3:4b-instruct"


def validar_documento_con_ia(
    tipo_documento,
    datos_extraidos,
    nombre_empleado,
    validaciones
):
    """
    Realiza validación documental mediante IA local.
    La IA analiza comparaciones explícitas entre campos equivalentes.
    """

    comparaciones = []

    # Comparación entre el nombre extraído y el registrado
    nombre_documento = datos_extraidos.get("nombre")

    if nombre_documento and nombre_empleado:
        comparaciones.append({
            "campo": "NOMBRE",
            "valor_documento": nombre_documento,
            "valor_referencia": nombre_empleado
        })

    # Agregamos las comparaciones que el sistema ya pudo construir
    # entre documentos para que la IA realice el análisis.
    for validacion in validaciones:
        campo = validacion.get("campo")
        valor_origen = validacion.get("valor_origen")
        valor_comparado = validacion.get("valor_comparado")

        if (
            campo
            and valor_origen is not None
            and valor_comparado is not None
        ):
            comparaciones.append({
                "campo": campo,
                "valor_documento": valor_origen,
                "valor_referencia": valor_comparado
            })

    informacion = {
        "tipo_documento": tipo_documento,
        "comparaciones_a_validar": comparaciones
    }

    prompt = f"""
Eres un sistema de validación documental mediante inteligencia artificial.

Debes validar EXCLUSIVAMENTE las comparaciones proporcionadas.

Cada comparación contiene:
- campo: indica qué dato estás validando;
- valor_documento: valor extraído de un documento mediante OCR;
- valor_referencia: valor equivalente utilizado para compararlo.

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

        # Protección ante respuestas contradictorias del modelo.
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

        print("ERROR EN VALIDACIÓN DOCUMENTAL CON IA:")
        print(error)

        return {
            "disponible": False,
            "resultado": "NO DISPONIBLE",
            "requiere_revision": True,
            "inconsistencias": [],
            "resumen": "No fue posible realizar la validación documental mediante IA."
        }