# MVP — Sistema Inteligente de Gestión Documental para Ingreso de Personal

## 1. Objetivo del MVP

El MVP tiene como objetivo implementar el flujo básico de gestión documental para el ingreso de personal ya contratado, permitiendo que 
Recursos Humanos registre al empleado, envíe una invitación y consulte su expediente, mientras que el empleado pueda acceder al sistema,
cargar la documentación requerida y consultar el estado de sus documentos.

## 2. Funcionalidades incluidas

### 2.1 Recursos Humanos

- Inicio de sesión mediante correo y contraseña.
- Registro de empleados.
- Asignación de área y puesto.
- Envío de invitaciones por correo electrónico.
- Consulta de empleados registrados.
- Consulta del expediente documental de un empleado.
- Consulta de los documentos cargados y sus estados.

### 2.2 Empleado

- Acceso mediante invitación.
- Creación de contraseña.
- Inicio de sesión.
- Consulta de sus datos registrados.
- Carga de documentos en formato PDF.
- Consulta del estado de sus documentos.
- Visualización de los motivos cuando un documento solicita corrección.

### 2.3 Procesamiento y validación documental


- Carga de documentos en formato PDF.
- Procesamiento mediante OCR.
- Extracción de información relevante.
- Comparación de datos entre documentos.
- Validación mediante Inteligencia Artificial utilizando Ollama y Qwen3:4b-instruct.
- Identificación de inconsistencias.
- Asignación del estado correspondiente al documento.

## 3. Documentos contemplados

El MVP contempla los siguientes documentos oficiales de México:

- Acta de nacimiento.
- CURP.
- INE.
- RFC / Constancia de Situación Fiscal.
- Comprobante de domicilio.
- Documento bancario para nómina.
- Documento de Seguridad Social, cuando el empleado cuente con este documento.

## 4. Estados de los documentos

Los documentos pueden presentar los siguientes estados:

- **PENDIENTE:** el documento aún no se ha cargado o está pendiente de procesamiento o validación.
- **VALIDADO:** el documento ha sido procesado y validado correctamente.
- **SOLICITA CORRECCION:** se han encontrado inconsistencias en el documento y es necesario cargar nuevamente el documento.
- **NO APLICA:** se utiliza únicamente para el documento de Seguridad Social cuando el empleado no cuenta con este documento.

## 5. Funcionalidades fuera del MVP

El MVP no contempla funcionalidades relacionadas con:

- Reclutamiento y selección de personal.
- Entrevistas.
- Firma de contratos.
- Procesamiento de nómina.
- Control de pagos o prestaciones.
- Gestión de personal que no corresponda al proceso documental de ingreso.

## 6. Flujo de prueba del MVP

Para comprobar el funcionamiento del MVP se realiza el siguiente flujo:

1. Recursos Humanos inicia sesión en el sistema.
2. Recursos Humanos registra a un empleado.
3. El sistema envía una invitación al correo del empleado.
4. El empleado accede mediante la invitación.
5. El empleado crea su contraseña.
6. El empleado verifica sus datos registrados (nombre y apellidos).
7. El empleado carga los documentos requeridos en formato PDF.
8. El sistema procesa los documentos mediante OCR.
9. El sistema extrae la información relevante de cada documento.
10. El sistema realiza las validaciones correspondientes mediante reglas e Inteligencia Artificial.
11. El sistema asigna un estado al documento.
12. Si existen inconsistencias, el sistema muestra el motivo y solicita la corrección del documento.
13. Recursos Humanos consulta el expediente y puede revisar el estado de la documentación.

## 7. Resultado esperado

El MVP permite organizar los documentos de un empleado. Recursos Humanos registra al empleado, el empleado carga sus documentos y el sistema
los procesa y valida. Finalmente, Recursos Humanos puede consultar el expediente y revisar el estado de cada documento.