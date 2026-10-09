from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from database.database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        unique=True,
        nullable=True
    )

    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(100), nullable=False)
    apellido_materno = Column(String(100), nullable=True)
    correo = Column(String(150), unique=True, nullable=False)
    area = Column(String(100), nullable=False)
    puesto = Column(String(100), nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

