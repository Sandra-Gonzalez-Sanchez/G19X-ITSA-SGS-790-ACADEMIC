import os
import subprocess
import json


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
        errors="replace"
    )

    for linea in resultado.stdout.splitlines():
        if linea.startswith("RESULTADO_OCR:"):
            json_texto = linea.replace("RESULTADO_OCR:", "", 1)
            return json.loads(json_texto)

    print("STDOUT DEL OCR:")
    print(resultado.stdout)

    print("STDERR DEL OCR:")
    print(resultado.stderr)

    print("CÓDIGO DE SALIDA DEL OCR:")
    print(resultado.returncode)

    raise RuntimeError(
        "No se encontró el resultado del OCR."
    )