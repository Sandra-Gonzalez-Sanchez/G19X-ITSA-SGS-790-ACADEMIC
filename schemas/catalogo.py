from pydantic import BaseModel


class AreaCreate(BaseModel):
    nombre: str


class PuestoCreate(BaseModel):
    nombre: str

class CatalogoUpdate(BaseModel):
    nombre: str