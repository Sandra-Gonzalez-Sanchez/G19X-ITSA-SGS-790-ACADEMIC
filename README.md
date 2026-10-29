# Sistema Inteligente de Gestión Documental para Ingreso de Personal

Sistema web para la gestión de documentación requerida durante el proceso
de ingreso de personal. Permite registrar empleados, enviar invitaciones,
recibir documentos en formato PDF, procesarlos mediante OCR y realizar
validaciones mediante Inteligencia Artificial.


## Tecnologías utilizadas

- Python 3.14.2
- FastAPI 0.141.1
- React 19.2.8
- Vite 8.3.0
- PostgreSQL 18
- OCR
- Ollama 0.35.1
- Qwen3:4b-instruct
- Git

## Requisitos previos

Antes de ejecutar el sistema se requiere tener instalado:

- Python 3.14.2
- Node.js 22.21.0
- npm 10.9.4
- PostgreSQL 18
- Ollama 0.35.1

## Estructura del proyecto

El proyecto está organizado en diferentes módulos que separan las funciones
principales del sistema:

- `app/` — Configuración principal y punto de entrada de la aplicación.
- `database/` — Configuración y conexión con PostgreSQL.
- `frontend/` — Interfaz web desarrollada con React y Vite.
- `models/` — Modelos de datos utilizados por el sistema.
- `routers/` — Endpoints de la API para las diferentes funcionalidades.
- `schemas/` — Esquemas utilizados para validar y manejar los datos.
- `services/` — Lógica de servicios del sistema, incluyendo correo, OCR,
  Inteligencia Artificial, seguridad y validación documental.
- `ocr_pruebas/` — Archivos utilizados para realizar pruebas del procesamiento
  OCR.
- `.env.example` — Plantilla de las variables de entorno necesarias.
- `requirements.txt` — Dependencias de Python utilizadas por el backend.
- `requirements-ocr.txt` — Dependencias de Python utilizadas para el procesamiento OCR.

## Funcionalidades principales

### Recursos Humanos

- Inicio de sesión.
- Configuración inicial del acceso de Recursos Humanos.
- Registro de empleados.
- Asignación de área y puesto para empleado.
- Envío de invitaciones al empleado.
- Consulta de expedientes.
- Consulta de documentos cargados.

### Empleado

- Acceso mediante invitación.
- Creación de contraseña.
- Inicio de sesión.
- Consulta de sus datos.
- Carga de documentos en formato PDF.
- Consulta del estado de sus documentos.

### Procesamiento documental

- Validación del tipo de documento cargado.
- Procesamiento de documentos mediante OCR.
- Extracción de información relevante.
- Comparación de datos entre documentos.
- Validación documental mediante Inteligencia Artificial utilizando Ollama.
- Análisis de inconsistencias mediante el modelo de IA.

### Seguridad

- Contraseñas protegidas mediante hash.
- Autenticación mediante JWT.
- Invitaciones con vigencia limitada.
- Recuperación de contraseña mediante correo electrónico.
- Contraseñas con requisitos de seguridad.

## Documentos gestionados

El sistema está enfocado en el procesamiento y validación
de documentos oficiales de México.

El sistema contempla los siguientes documentos:

- Acta de nacimiento
- CURP
- INE
- RFC / Constancia de Situación Fiscal
- Comprobante de domicilio
- Documento bancario para nómina
- Documento de Seguridad Social (opcional).

Los documentos emitidos en otros países o que no correspondan con los formatos
contemplados por el sistema no deberán considerarse como documentos validados.

## Estados del documento

Los documentos pueden presentar los siguientes estados:

| Estado | Qué significa | Quién lo cambia |
|---|---|---|
| `PENDIENTE` | El documento aún no se ha cargado o está pendiente de procesamiento o validación. | El sistema |
| `VALIDADO` | El documento ha sido procesado y validado correctamente. | El sistema |
| `SOLICITA CORRECCION` | Se encontraron inconsistencias en el documento y es necesario cargar nuevamente el documento. | El sistema |
| `NO APLICA` | Se utiliza únicamente para el documento de Seguridad Social cuando el empleado no cuenta con este documento. | El empleado|

## Configuración

El proyecto utiliza variables de entorno para configurar la conexión
con la base de datos, la autenticación y el servicio de correo.

Estas variables deben configurarse en un archivo `.env`.

El archivo `.env` no debe incluirse en el repositorio ni compartirse
públicamente. Tomar como referencia el archivo `.env.example` incluido
en el proyecto.

## Base de datos

El sistema utiliza PostgreSQL 18.

La base de datos utilizada es `ingreso_personal`.

Para crear la base de datos:

```sql
CREATE DATABASE ingreso_personal;
```

## Uso de IA

### IA utilizada en el sistema

El sistema utiliza Ollama con el modelo Qwen3:4b-instruct para realizar la validación de los documentos cargados, analizar la información obtenida
mediante OCR e identificar posibles inconsistencias entre los datos documentales y la información registrada del empleado.

### IA utilizada durante el desarrollo

Durante el desarrollo se utilizó ChatGPT como herramienta de apoyo para resolver dudas técnicas, revisar código, analizar errores y orientar
algunos ajustes del sistema.

Las sugerencias se revisaron y ajustaron de acuerdo con los requerimientos y las pruebas realizadas en el sistema.


## Instalación

### 1. Configurar el entorno de Python

El backend utiliza Python 3.14.2.

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activar el entorno virtual:

```bash
.venv\Scripts\activate
```

### 2. Instalar las dependencias del backend

Con el entorno virtual activado, instalar las dependencias:

```bash
pip install -r requirements.txt
```
### 3. Configurar el entorno OCR

El sistema utiliza PaddleOCR para procesar los documentos PDF y extraer información mediante reconocimiento óptico de caracteres (OCR).

El procesamiento OCR se ejecuta en un entorno virtual independiente llamado `.venv_ocr`.

Crear el entorno OCR desde la carpeta principal del proyecto:

```powershell
python -m venv .venv_ocr
```

Activar el entorno OCR:

```powershell
.\.venv_ocr\Scripts\Activate.ps1
```

Instalar las dependencias del OCR:

```powershell
pip install -r requirements-ocr.txt
```

Las principales dependencias utilizadas son:

- PaddleOCR 3.7.0
- PaddlePaddle 3.3.1

La ruta del intérprete de Python utilizado para ejecutar el OCR se configura mediante la variable de entorno `OCR_PYTHON`.

Ejemplo:

```text
OCR_PYTHON=.venv_ocr/Scripts/python.exe
```

### 4. Configurar PostgreSQL

Crear la base de datos utilizada por el sistema:

```text
ingreso_personal
```

La conexión con PostgreSQL se configura mediante las variables de entorno del archivo `.env`.

### 5. Configurar Ollama

Verificar que Ollama esté instalado:

```bash
ollama --version
```

Descargar el modelo utilizado para la validación mediante Inteligencia Artificial:

```bash
ollama pull qwen3:4b-instruct
```

Comprobar que el modelo esté disponible:

```bash
ollama list
```

### 6. Configurar el archivo `.env`

Crear un archivo `.env` en la carpeta principal del proyecto y configurar las variables necesarias para:

- Conexión con PostgreSQL.
- Autenticación.
- Servicio de correo.
- Configuración de Inteligencia Artificial.

El archivo `.env` debe mantenerse privado y no debe subirse al repositorio.

## Ejecución del sistema

El sistema está compuesto por un backend desarrollado con FastAPI y un frontend desarrollado con React y Vite.

### 1. Ejecutar el backend

Desde la carpeta principal del proyecto, con el entorno virtual activado:

```bash
uvicorn app.main:app --reload --port 8001
```

El backend estará disponible en:

```text
http://127.0.0.1:8001
```

La documentación de la API puede consultarse en:

```text
http://127.0.0.1:8001/docs
```

### 2. Ejecutar el frontend

Abrir una segunda terminal y entrar a la carpeta del frontend:

```bash
cd frontend
```

Instalar las dependencias:

```bash
npm install
```

Ejecutar el servidor de desarrollo:

```bash
npm run dev
```

El frontend estará disponible en:

```text
http://localhost:5173
```

## Ejecución de Ollama

Para utilizar la validación mediante Inteligencia Artificial, Ollama debe estar disponible en el equipo y contar con el modelo:

```text
qwen3:4b-instruct
```
## Documentos del proyecto

- [PRD](docs/PRD.md)
- [MVP](docs/MVP.md)


