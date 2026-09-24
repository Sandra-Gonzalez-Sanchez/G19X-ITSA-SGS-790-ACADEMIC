from sqlalchemy import Column, Integer, String, Boolean
from database.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)

    correo = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    rol = Column(
        String(20),
        nullable=False
    )

    activo = Column(
        Boolean,
        default=True,
        nullable=False
    )