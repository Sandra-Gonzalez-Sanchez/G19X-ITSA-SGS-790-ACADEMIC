import sys
import json
import os

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ruta_proyecto = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(ruta_proyecto)

from services.ocr_service import procesar_documento_ocr


if len(sys.argv) < 2:
    print(json.dumps({
        "error": "No se proporcionó la ruta del documento"
    }))
    sys.exit(1)

ruta_documento = sys.argv[1]

datos = procesar_documento_ocr(ruta_documento)

print(
    "RESULTADO_OCR:" + json.dumps(
        datos,
        ensure_ascii=False
    )
)