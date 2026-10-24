import os
import subprocess
import json
import logging

logger = logging.getLogger(__name__)

def ejecutar_ocr(ruta_documento):
    ruta_proyecto = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    python_ocr = os.getenv(
        "OCR_PYTHON",
        os.path.join(
            ruta_proyecto,
            ".venv_ocr",
            "Scripts",
            "python.exe"
        )
    )

    script_ocr = os.path.join(
        ruta_proyecto,
        "ocr_pruebas",
        "procesar_archivo.py"
    )

    resultado = subprocess.run(
        [
            python_ocr,
            script_ocr,
            ruta_documento
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120
    )

    for linea in resultado.stdout.splitlines():
        if linea.startswith("RESULTADO_OCR:"):
            json_texto = linea.replace("RESULTADO_OCR:", "", 1)
            return json.loads(json_texto)

    logger.info("STDOUT DEL OCR:\n%s", resultado.stdout)
    logger.error("STDERR DEL OCR:\n%s", resultado.stderr)
    logger.error("CÓDIGO DE SALIDA DEL OCR: %s", resultado.returncode)

    raise RuntimeError(
        "No se encontró el resultado del OCR."
    )