from fastapi import FastAPI

from database.database import Base, engine
from models.empleado import Empleado
from models.invitacion import Invitacion
from models.usuario import Usuario
from models.solicitud_correccion import SolicitudCorreccion
from models.documento import Documento
from models.dato_extraido import DatoExtraido
from models.validacion import Validacion
from routers.empleados import router as empleados_router
from routers.invitaciones import router as invitaciones_router
from routers.usuarios import router as usuarios_router
from routers.solicitudes_correccion import router as solicitudes_correccion_router
from routers.documentos import router as documentos_router
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Sistema Inteligente de Gestión Documental",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(empleados_router)
app.include_router(invitaciones_router)
app.include_router(usuarios_router)
app.include_router(solicitudes_correccion_router)
app.include_router(documentos_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "Bienvenido al Sistema de Ingreso de Personal",
        "empresa": "PluriOne"
    }