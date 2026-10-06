from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base


class DatoExtraido(Base):
    __tablename__ = "datos_extraidos"

    id = Column(Integer, primary_key=True, index=True)

    documento_id = Column(
        Integer,
        ForeignKey("documentos.id"),
        nullable=False,
        unique=True
    )

    nombre = Column(String(200), nullable=True)
    fecha_nacimiento = Column(String(20), nullable=True)
    domicilio = Column(String(500), nullable=True)
    clabe = Column(String(18), nullable=True)
    nss = Column(String(30), nullable=True)

    curp = Column(String(18), nullable=True)
    curp_candidata = Column(String(50), nullable=True)
    estado_formato_curp = Column(String(50), nullable=True)

    rfc = Column(String(13), nullable=True)
    estado_formato_rfc = Column(String(50), nullable=True)

    comparacion_fecha_curp = Column(String(50), nullable=True)
    comparacion_fecha_rfc = Column(String(50), nullable=True)