import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Cargar las variables almacenadas en el archivo .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


# Dirección de nuestra base de datos PostgreSQL
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Crear la conexión con PostgreSQL
engine = create_engine(DATABASE_URL)


# Crear sesiones para trabajar con la base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base que utilizaremos para crear nuestros modelos/tablas
Base = declarative_base()


# Proporciona una conexión a la base de datos
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    try:
        with engine.connect():
            print("Conexion exitosa con PostgreSQL")
    except Exception as error:
        print("Error al conectar con PostgreSQL:")
        print(error)