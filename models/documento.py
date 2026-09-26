from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from database.database import Base


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)

    empleado_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=False
    )

    tipo_documento = Column(String(50), nullable=False)
    ruta_archivo = Column(String(500), nullable=False)
    estado = Column(String(30), nullable=False, default="PENDIENTE")
    fecha_carga = Column(DateTime, nullable=False, default=datetime.now)