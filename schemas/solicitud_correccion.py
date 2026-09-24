from pydantic import BaseModel
from typing import Optional


class SolicitudCorreccionCreate(BaseModel):
    nombre_solicitado: Optional[str] = None
    apellido_paterno_solicitado: Optional[str] = None
    apellido_materno_solicitado: Optional[str] = None
    motivo: str

class SolicitudCorreccionResolver(BaseModel):
    decision: str