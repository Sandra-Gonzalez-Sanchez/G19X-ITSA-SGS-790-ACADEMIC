import os
import subprocess
import json


def ejecutar_ocr(ruta_documento):
    ruta_proyecto = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    python_ocr = os.path.join(
        ruta_proyecto,
        ".venv_ocr",
        "Scripts",
        "python.exe"
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
        encoding="cp1252",
        errors="replace"
    )

    for linea in resultado.stdout.splitlines():
        if linea.startswith("RESULTADO_OCR:"):
            json_texto = linea.replace("RESULTADO_OCR:", "", 1)
            return json.loads(json_texto)

    raise RuntimeError(
        "No se encontró el resultado del OCR."
    )