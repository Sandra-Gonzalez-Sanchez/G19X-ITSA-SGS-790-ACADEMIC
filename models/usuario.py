from sqlalchemy import Column, Integer, String, Boolean, DateTime
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

    token_recuperacion = Column(
        String(255),
        nullable=True
    )

    token_recuperacion_expira = Column(
        DateTime(timezone=True),
        nullable=True
    )