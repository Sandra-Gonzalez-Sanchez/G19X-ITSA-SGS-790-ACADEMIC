from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone

from database.database import Base


class SolicitudCorreccion(Base):
    __tablename__ = "solicitudes_correccion"

    id = Column(Integer, primary_key=True, index=True)

    empleado_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=False
    )

    nombre_solicitado = Column(String(100), nullable=True)
    apellido_paterno_solicitado = Column(String(100), nullable=True)
    apellido_materno_solicitado = Column(String(100), nullable=True)

    motivo = Column(String(500), nullable=False)

    estado = Column(
        String(20),
        default="PENDIENTE",
        nullable=False
    )

    fecha_solicitud = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )