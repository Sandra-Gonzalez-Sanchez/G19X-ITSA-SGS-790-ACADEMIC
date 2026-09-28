from PIL import Image

imagen = Image.open("ocr_pruebas/curp_prueba.webp")

if imagen.mode != "RGB":
    imagen = imagen.convert("RGB")

imagen.save("ocr_pruebas/curp_prueba.pdf", "PDF")

print("PDF creado correctamente.")