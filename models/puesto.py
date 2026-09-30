from sqlalchemy import Column, Integer, String, Boolean
from database.database import Base


class Puesto(Base):
    __tablename__ = "puestos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)