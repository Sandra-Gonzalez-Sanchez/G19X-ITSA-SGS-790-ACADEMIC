from pydantic import BaseModel
from datetime import date

class EmpleadoCreate(BaseModel):
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo: str
    area: str
    puesto: str
    fecha_ingreso: date
