from sqlalchemy import Column, Integer, String, ForeignKey
from database.database import Base


class Validacion(Base):
    __tablename__ = "validaciones"

    id = Column(Integer, primary_key=True, index=True)

    empleado_id = Column(
        Integer,
        ForeignKey("empleados.id"),
        nullable=False
    )

    campo = Column(String(50), nullable=False)

    documento_origen = Column(String(50), nullable=False)
    documento_comparado = Column(String(50), nullable=False)

    valor_origen = Column(String(255), nullable=True)
    valor_comparado = Column(String(255), nullable=True)

    resultado = Column(String(50), nullable=False)