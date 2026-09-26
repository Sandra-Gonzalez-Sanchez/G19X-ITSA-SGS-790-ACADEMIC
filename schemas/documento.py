from datetime import datetime
from pydantic import BaseModel


class DocumentoResponse(BaseModel):
    id: int
    empleado_id: int
    tipo_documento: str
    ruta_archivo: str
    estado: str
    fecha_carga: datetime

    model_config = {
        "from_attributes": True
    }