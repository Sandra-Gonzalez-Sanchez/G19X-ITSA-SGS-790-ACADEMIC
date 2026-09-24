from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from database.database import Base


class Invitacion(Base):
    __tablename__ = "invitaciones"

    id = Column(Integer, primary_key=True, index=True)

    empleado_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=False
    )

    token = Column(
        String(255),
        unique=True,
        nullable=False
    )

    fecha_creacion = Column(
        DateTime(timezone=True),
        nullable=False
    )

    fecha_expiracion = Column(
        DateTime(timezone=True),
        nullable=False
    )

    utilizada = Column(
        Boolean,
        default=False,
        nullable=False
    )

    activa = Column(
        Boolean,
        default=True,
        nullable=False
    )