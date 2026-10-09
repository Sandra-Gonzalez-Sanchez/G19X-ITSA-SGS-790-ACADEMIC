from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv


load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

security = HTTPBearer()

def crear_token(usuario_id: int, correo: str, rol: str):
    fecha_expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRE_MINUTES
    )

    datos_token = {
        "sub": str(usuario_id),
        "correo": correo,
        "rol": rol,
        "exp": fecha_expiracion
    }

    token = jwt.encode(
        datos_token,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token

def verificar_token(
    credenciales: HTTPAuthorizationCredentials = Depends(security)
):
    token = credenciales.credentials

    try:
        datos = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        return datos

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="El token ha expirado"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

def verificar_rh(
    datos_token: dict = Depends(verificar_token)
):
    if datos_token.get("rol") != "RH":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para realizar esta acción"
        )
    return datos_token

def verificar_rh_o_primero(
    datos_token: dict = Depends(verificar_token)
):
    if datos_token.get("rol") != "RH":
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para realizar esta acción"
        )

    return datos_token

def verificar_acceso_documento(
    datos_token: dict = Depends(verificar_token)
):
    rol = datos_token.get("rol")
    print("ROL QUE LLEGA AL DOCUMENTO:", rol)

    if rol not in ["EMPLEADO", "RH"]:
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para visualizar documentos."
        )

    return datos_token

def verificar_empleado(
    datos_token: dict = Depends(verificar_token)
):
    if datos_token.get("rol") != "EMPLEADO":
        raise HTTPException(
            status_code=403,
            detail="Esta acción es exclusiva para empleados"
        )

    return datos_token

def validar_password(password: str):
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 8 caracteres"
        )

    if " " in password:
        raise HTTPException(
            status_code=400,
            detail="La contraseña no debe contener espacios"
        )

    if not any(caracter.isupper() for caracter in password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos una letra mayúscula"
        )

    if not any(caracter.islower() for caracter in password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos una letra minúscula"
        )

    if not any(caracter.isdigit() for caracter in password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos un número"
        )

    caracteres_especiales = "@#$%&!"

    if not any(caracter in caracteres_especiales for caracter in password):
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe contener al menos un carácter especial (@#$%&!)"
        )