# PRD / MVP — Sistema Inteligente de Gestión Documental para Ingreso de Personal

## 1. Alcance

El sistema está enfocado en la gestión documental del ingreso de personal después de su contratación.

El flujo comienza cuando Recursos Humanos registra al empleado y genera una invitación. El empleado utiliza la invitación, crea su contraseña y carga los documentos requeridos en formato PDF.

Los documentos son procesados mediante OCR y posteriormente analizados mediante Inteligencia Artificial para comparar la información y detectar posibles inconsistencias.

## 2. Funcionalidades principales

### Recursos Humanos
- Inicio de sesión.
- Registro de empleados.
- Asignación de área y puesto.
- Generación y envío de invitaciones.
- Regeneración de invitaciones expiradas.
- Consulta de expedientes.
- Visualización de documentos.

### Empleado
- Acceso mediante invitación.
- Creación de contraseña.
- Inicio de sesión.
- Verificación de sus datos.
- Carga de documentos PDF.
- Consulta del estado de sus documentos.

### Procesamiento documental
- Validación del tipo de documento cargado.
- Procesamiento de documentos mediante OCR.
- Extracción de información relevante.
- Comparación de datos entre documentos.
- Validación documental mediante Inteligencia Artificial.
- Detección de inconsistencias entre la información extraída.

## 3. Documentos contemplados

El sistema está enfocado en el procesamiento y validación de documentos oficiales de México.

Los documentos contemplados son:

- Acta de nacimiento.
- CURP.
- INE.
- RFC / Constancia de Situación Fiscal.
- Comprobante de domicilio.
- Documento bancario para nómina.
- Documento de Seguridad Social, de forma condicional.

Los documentos emitidos en otros países o que no correspondan con los formatos contemplados por el sistema no se consideran documentos válidos para el proceso de validación.

## 4. Tecnologías

- Python + FastAPI.
- React + Vite.
- PostgreSQL.
- PaddleOCR.
- PaddlePaddle.
- Ollama.
- Qwen3:4b-instruct.
- Git / GitHub.

## 5. Seguridad

- Autenticación mediante JWT.
- Contraseñas protegidas mediante hash.
- Invitaciones con vigencia de 72 horas.
- Almacenamiento local de la información y documentos.
- Control de acceso según el tipo de usuario.

## 6. Estado actual del MVP

El proyecto cuenta con la estructura principal del backend y frontend, autenticación, registro de empleados, generación de invitaciones, carga y consulta de documentos, procesamiento OCR y validación mediante Inteligencia Artificial.

El MVP se encuentra en etapa de integración y pruebas del flujo completo de ingreso documental.

## 7. Fuera del alcance

El sistema no contempla:

- Reclutamiento y selección.
- Entrevistas.
- Nómina.
- Vacaciones.
- Evaluaciones de desempeño.
- Gestión de personal posterior al proceso de ingreso documental.
- Validación de documentos oficiales emitidos por otros países.