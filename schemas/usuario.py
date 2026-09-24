from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    correo: str
    password: str

class LoginRequest(BaseModel):
    correo: str
    password: str