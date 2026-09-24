from pydantic import BaseModel


class CrearPassword(BaseModel):
    password: str