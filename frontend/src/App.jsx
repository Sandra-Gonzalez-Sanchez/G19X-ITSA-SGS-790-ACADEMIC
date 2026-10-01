import { useEffect, useState } from 'react'
import './App.css'
function App() {
  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [mensajeLogin, setMensajeLogin] = useState('')
  const rutaActual = window.location.pathname
const [mostrarRecuperacion, setMostrarRecuperacion] = useState(false)
const [correoRecuperacion, setCorreoRecuperacion] = useState('')
const [mensajeRecuperacion, setMensajeRecuperacion] = useState('')
const [enlaceRecuperacion, setEnlaceRecuperacion] = useState('')

const [esRestablecimiento, setEsRestablecimiento] = useState(
  rutaActual.startsWith('/restablecer-password/')
)

const tokenRecuperacion = rutaActual.startsWith('/restablecer-password/')
  ? rutaActual.split('/restablecer-password/')[1]
  : null

const [passwordRestablecida, setPasswordRestablecida] = useState('')
const [confirmarPasswordRestablecida, setConfirmarPasswordRestablecida] = useState('')
 const [rol, setRol] = useState(() => {
  return localStorage.getItem('rol')
  })
  const [empleado, setEmpleado] = useState(null)
  const [mostrarCorreccion, setMostrarCorreccion] = useState(false)
  const [mensajeCorreccion, setMensajeCorreccion] = useState('')
  const [nombreSolicitado, setNombreSolicitado] = useState('')
  const [mostrarAltaEmpleado, setMostrarAltaEmpleado] = useState(false)
  const [nuevoNombre, setNuevoNombre] = useState('')
const [nuevoApellidoPaterno, setNuevoApellidoPaterno] = useState('')
const [nuevoApellidoMaterno, setNuevoApellidoMaterno] = useState('')
const [nuevoCorreo, setNuevoCorreo] = useState('')
const [nuevaArea, setNuevaArea] = useState('')
const [nuevoPuesto, setNuevoPuesto] = useState('')
const [nuevaFechaIngreso, setNuevaFechaIngreso] = useState('')
const [mensajeEmpleado, setMensajeEmpleado] = useState('')
const [empleados, setEmpleados] = useState([])
const [solicitudes, setSolicitudes] = useState([])
const [areas, setAreas] = useState([])
const [puestos, setPuestos] = useState([])
const [nombreNuevaArea, setNombreNuevaArea] = useState('')
const [nombreNuevoPuesto, setNombreNuevoPuesto] = useState('')
const [seccionRH, setSeccionRH] = useState('empleados')
const [seccionEmpleado, setSeccionEmpleado] = useState('inicio')
const esInvitacion = rutaActual.startsWith('/invitacion/')
const tokenInvitacion = esInvitacion
  ? rutaActual.split('/invitacion/')[1]
  : null
const [invitacionValida, setInvitacionValida] = useState(null)
const [mensajeInvitacion, setMensajeInvitacion] = useState('')
const [nuevaPassword, setNuevaPassword] = useState('')
const [confirmarPassword, setConfirmarPassword] = useState('')
const passwordMinimo = nuevaPassword.length >= 8
const passwordMayuscula = /[A-Z]/.test(nuevaPassword)
const passwordMinuscula = /[a-z]/.test(nuevaPassword)
const passwordNumero = /[0-9]/.test(nuevaPassword)
const passwordEspecial = /[@#$%&!]/.test(nuevaPassword)
const passwordSinEspacios = !/\s/.test(nuevaPassword)

const passwordSegura =
  passwordMinimo &&
  passwordMayuscula &&
  passwordMinuscula &&
  passwordNumero &&
  passwordEspecial &&
  passwordSinEspacios
const [apellidoPaternoSolicitado, setApellidoPaternoSolicitado] = useState('')
const [apellidoMaternoSolicitado, setApellidoMaternoSolicitado] = useState('')
const [motivoCorreccion, setMotivoCorreccion] = useState('')
const [cuentaCreada, setCuentaCreada] = useState(false)
const [tipoDocumentoSeleccionado, setTipoDocumentoSeleccionado] = useState('')
const [archivoSeleccionado, setArchivoSeleccionado] = useState(null)
const [mensajeDocumento, setMensajeDocumento] = useState('')
const [documentos, setDocumentos] = useState([])
const [expedienteSeleccionado, setExpedienteSeleccionado] = useState(null)
const [cargandoExpediente, setCargandoExpediente] = useState(false)

const documentosRequeridos = [
  {
    tipo: 'ACTA_NACIMIENTO',
    nombre: 'Acta de nacimiento',
    descripcion: 'Documento obligatorio'
  },
  {
    tipo: 'CURP',
    nombre: 'CURP',
    descripcion: 'Documento obligatorio'
  },
  {
    tipo: 'INE',
    nombre: 'INE',
    descripcion: 'Documento obligatorio'
  },
  {
    tipo: 'RFC',
    nombre: 'RFC / Constancia de Situación Fiscal',
    descripcion: 'Documento obligatorio'
  },
  {
    tipo: 'COMPROBANTE_DOMICILIO',
    nombre: 'Comprobante de domicilio',
    descripcion: 'Documento obligatorio'
  },
  {
    tipo: 'DOCUMENTO_BANCARIO',
    nombre: 'Documento bancario para nómina',
    descripcion: 'Documento obligatorio'
  },
  {
    tipo: 'SEGURIDAD_SOCIAL',
    nombre: 'Documento de Seguridad Social',
    descripcion: 'Documento condicional'
  }
]


  const iniciarSesion = async (e) => {
  e.preventDefault()

  setMensajeLogin('')

 console.log("🚨 SE EJECUTÓ iniciarSesion")
  try {
    const respuesta = await fetch(
      'http://127.0.0.1:8001/usuarios/login',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          correo: correo,
          password: password
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      localStorage.setItem('access_token', datos.access_token)
      localStorage.setItem('rol', datos.rol)
      setRol(datos.rol)

      if (datos.rol === 'EMPLEADO') {
          await cargarPerfilEmpleado(datos.access_token)
      }

      if (datos.rol === 'RH') {
          await cargarEmpleados()
      }

      console.log('Inicio de sesión correcto')
      console.log('Rol:', datos.rol)
    } else {
      setMensajeLogin(datos.detail || 'Correo o contraseña incorrectos')
    }

  } catch (error) {
    console.error('Error al iniciar sesión:', error)
  }
}

const cargarPerfilEmpleado = async (token) => {
  try {
    const respuesta = await fetch(
      'http://127.0.0.1:8001/empleados/mi-perfil',
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setEmpleado(datos)
    } else {
      console.error('Error al obtener el perfil:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar el perfil:', error)
  }
}

const subirDocumento = async () => {
    console.log('🚨 SE EJECUTÓ subirDocumento')
  if (!archivoSeleccionado || !tipoDocumentoSeleccionado) {
    setMensajeDocumento('Selecciona un archivo PDF.')
    return
  }

  try {
    const token = localStorage.getItem('access_token')

    const formData = new FormData()
    formData.append('tipo_documento', tipoDocumentoSeleccionado)
    formData.append('archivo', archivoSeleccionado)

    const respuesta = await fetch(
      'http://127.0.0.1:8001/documentos/subir',
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
  if (datos.documento_aceptado === false) {
    setMensajeDocumento(datos.mensaje)
    setArchivoSeleccionado(null)
    await cargarDocumentos()
    return
  }

  if (datos.estado === 'EN REVISION') {
    setMensajeDocumento(
      datos.motivo_revision ||
      'El documento requiere revisión por parte de Recursos Humanos.'
    )
  } else {
    setMensajeDocumento(
      datos.mensaje || 'Documento cargado correctamente.'
    )
  }

  setArchivoSeleccionado(null)
  setTipoDocumentoSeleccionado('')
  await cargarDocumentos()
} else {
  setMensajeDocumento(
    datos.detail || 'No fue posible cargar el documento.'
  )
}
  } catch (error) {
    console.error('Error al subir documento:', error)
    setMensajeDocumento('No fue posible conectar con el servidor.')
  }
}

const cargarDocumentos = async () => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/documentos/mis-documentos',
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setDocumentos(datos)
      console.log('Documentos cargados:', datos)
    } else {
      console.error('Error al cargar documentos:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar documentos:', error)
  }
}

const verDocumento = async (documentoId) => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      `http://127.0.0.1:8001/documentos/archivo/${documentoId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    if (!respuesta.ok) {
      const datos = await respuesta.json()
      alert(datos.detail || 'No fue posible abrir el documento.')
      return
    }

    const archivo = await respuesta.blob()
    const urlArchivo = URL.createObjectURL(archivo)

    window.open(urlArchivo, '_blank')
  } catch (error) {
    console.error('Error al visualizar documento:', error)
    alert('No fue posible abrir el documento.')
  }
}

const marcarSeguridadSocialNoAplica = async () => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/documentos/empleado/seguridad-social/no-aplica',
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setMensajeDocumento('Seguridad Social marcada como No aplica.')
      await cargarDocumentos()
    } else {
      setMensajeDocumento(
        datos.detail || 'No fue posible actualizar el documento.'
      )
    }
  } catch (error) {
    console.error('Error al actualizar Seguridad Social:', error)
    setMensajeDocumento('No fue posible conectar con el servidor.')
  }
}

const enviarSolicitudCorreccion = async () => {
    if (
      !nombreSolicitado.trim() &&
      !apellidoPaternoSolicitado.trim() &&
      !apellidoMaternoSolicitado.trim()
    ) {
      setMensajeCorreccion(
        'Debes indicar al menos un dato que deseas corregir.'
      )
      return
    }

    if (!motivoCorreccion.trim()) {
      setMensajeCorreccion(
        'Debes indicar el motivo de la corrección.'
      )
      return
    }

  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/solicitudes-correccion/',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre_solicitado: nombreSolicitado || null,
          apellido_paterno_solicitado: apellidoPaternoSolicitado || null,
          apellido_materno_solicitado: apellidoMaternoSolicitado || null,
          motivo: motivoCorreccion
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      console.log('Solicitud enviada correctamente:', datos)
      setMensajeCorreccion('Solicitud enviada correctamente.')
      setNombreSolicitado('')
      setApellidoPaternoSolicitado('')
      setApellidoMaternoSolicitado('')
      setMotivoCorreccion('')
      setMostrarCorreccion(false)

    } else {
      console.error('Error al enviar la solicitud:', datos.detail)
    }

  } catch (error) {
    console.error('Error al enviar la solicitud:', error)
  }
}

const registrarEmpleado = async () => {

    if (
  !nuevoNombre.trim() ||
  !nuevoApellidoPaterno.trim() ||
  !nuevoCorreo.trim() ||
  !nuevaArea.trim() ||
  !nuevoPuesto.trim() ||
  !nuevaFechaIngreso
) {
  alert('Completa todos los campos obligatorios.')
  return
}

  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/empleados/',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: nuevoNombre,
          apellido_paterno: nuevoApellidoPaterno,
          apellido_materno: nuevoApellidoMaterno,
          correo: nuevoCorreo,
          area: nuevaArea,
          puesto: nuevoPuesto,
          fecha_ingreso: nuevaFechaIngreso
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      console.log('Empleado registrado correctamente:', datos)
      setMensajeEmpleado('Empleado registrado correctamente.')
      setNuevoNombre('')
      setNuevoApellidoPaterno('')
      setNuevoApellidoMaterno('')
      setNuevoCorreo('')
      setNuevaArea('')
      setNuevoPuesto('')
      setNuevaFechaIngreso('')

      setMostrarAltaEmpleado(false)

    } else {
      console.error('Error al registrar empleado:', datos.detail)
    }

  } catch (error) {
    console.error('Error al registrar empleado:', error)
  }
}

const cargarEmpleados = async () => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/empleados/',
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setEmpleados(datos)
      console.log('Empleados cargados:', datos)
    } else {
      console.error('Error al cargar empleados:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar empleados:', error)
  }
}

const cargarAreas = async () => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/catalogos/areas',
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setAreas(datos.filter((area) => area.activo))
    } else {
      console.error('Error al cargar áreas:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar áreas:', error)
  }
}


const cargarPuestos = async () => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/catalogos/puestos',
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setPuestos(datos.filter((puesto) => puesto.activo))
    } else {
      console.error('Error al cargar puestos:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar puestos:', error)
  }
}

const crearArea = async () => {
  if (!nombreNuevaArea.trim()) {
    alert('Ingresa el nombre del área.')
    return
  }

  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/catalogos/areas',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: nombreNuevaArea
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setNombreNuevaArea('')
      await cargarAreas()
    } else {
      alert(datos.detail || 'No fue posible registrar el área.')
    }

  } catch (error) {
    console.error('Error al crear área:', error)
    alert('No fue posible conectar con el servidor.')
  }
}


const crearPuesto = async () => {
  if (!nombreNuevoPuesto.trim()) {
    alert('Ingresa el nombre del puesto.')
    return
  }

  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/catalogos/puestos',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          nombre: nombreNuevoPuesto
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setNombreNuevoPuesto('')
      await cargarPuestos()
    } else {
      alert(datos.detail || 'No fue posible registrar el puesto.')
    }

  } catch (error) {
    console.error('Error al crear puesto:', error)
    alert('No fue posible conectar con el servidor.')
  }
}


const cargarExpediente = async (empleadoId) => {
  try {
    setCargandoExpediente(true)

    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      `http://127.0.0.1:8001/documentos/empleado/${empleadoId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      console.log('EXPEDIENTE RECIBIDO:', datos)
      setExpedienteSeleccionado(datos)
    } else {
      console.error('Error al cargar expediente:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar expediente:', error)
  } finally {
    setCargandoExpediente(false)
  }
}

const cambiarEstadoDocumento = async (documentoId, accion) => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      `http://127.0.0.1:8001/documentos/${documentoId}/${accion}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (!respuesta.ok) {
      alert(datos.detail || 'No fue posible actualizar el documento.')
      return
    }

    // Recarga el expediente para mostrar el nuevo estado
    await cargarExpediente(expedienteSeleccionado.empleado.id)

  } catch (error) {
    console.error('Error al actualizar documento:', error)
    alert('No fue posible conectar con el servidor.')
  }
}

const cargarSolicitudes = async () => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      'http://127.0.0.1:8001/solicitudes-correccion/',
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setSolicitudes(datos)
      console.log('Solicitudes cargadas:', datos)
    } else {
      console.error('Error al cargar solicitudes:', datos.detail)
    }

  } catch (error) {
    console.error('Error al consultar solicitudes:', error)
  }
}

const resolverSolicitud = async (solicitudId, accion) => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      `http://127.0.0.1:8001/solicitudes-correccion/${solicitudId}/resolver`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          decision: accion
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      console.log('Solicitud resuelta:', datos)

      await cargarSolicitudes()
      await cargarEmpleados()
    } else {
      console.error('Error al resolver solicitud:', datos.detail)
    }

  } catch (error) {
    console.error('Error al resolver solicitud:', error)
  }
}


const enviarInvitacion = async (empleadoId) => {
  try {
    const token = localStorage.getItem('access_token')

    const respuesta = await fetch(
      `http://127.0.0.1:8001/empleados/${empleadoId}/invitacion`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      console.log('Invitación enviada correctamente:', datos)
    } else {
      console.error('Error al enviar invitación:', datos.detail)
    }

  } catch (error) {
    console.error('Error al enviar invitación:', error)
  }
}

const validarInvitacion = async () => {
  try {
    const respuesta = await fetch(
      `http://127.0.0.1:8001/invitaciones/${tokenInvitacion}/validar`
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      setInvitacionValida(true)
      setMensajeInvitacion('Invitación válida')
      console.log('Invitación válida:', datos)
    } else {
      setInvitacionValida(false)
      setMensajeInvitacion(datos.detail)
      console.error('Invitación inválida:', datos.detail)
    }

  } catch (error) {
    setInvitacionValida(false)
    setMensajeInvitacion('No fue posible validar la invitación.')
    console.error('Error al validar invitación:', error)
  }
}

useEffect(() => {
  const token = localStorage.getItem('access_token')

  if (!token || esInvitacion) {
    return
  }

  if (rol === 'RH') {
    cargarEmpleados()
  }

  if (rol === 'EMPLEADO') {
  cargarPerfilEmpleado(token)
  cargarDocumentos()
    }
}, [rol])

useEffect(() => {
  if (esInvitacion && tokenInvitacion) {
    validarInvitacion()
  }
}, [])

const crearPasswordEmpleado = async () => {
  if (!nuevaPassword || !confirmarPassword) {
    alert('Completa ambos campos de contraseña.')
    return
  }

  if (!passwordSegura) {
  alert('La contraseña no cumple con todos los requisitos de seguridad.')
  return
}

  if (nuevaPassword !== confirmarPassword) {
    alert('Las contraseñas no coinciden.')
    return
  }

  try {
    const respuesta = await fetch(
      `http://127.0.0.1:8001/invitaciones/${tokenInvitacion}/crear-password`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          password: nuevaPassword
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      console.log('Cuenta creada correctamente:', datos)
      setMensajeInvitacion('Cuenta creada correctamente.')
      setCuentaCreada(true)
    } else {
      console.error('Error al crear la cuenta:', datos.detail)
      setMensajeInvitacion(datos.detail)
    }

  } catch (error) {
    console.error('Error al crear la cuenta:', error)
    setMensajeInvitacion('No fue posible crear la cuenta.')
  }
}

const restablecerPassword = async () => {

  if (!passwordRestablecida || !confirmarPasswordRestablecida) {
    alert('Completa ambos campos de contraseña.')
    return
  }

  if (passwordRestablecida !== confirmarPasswordRestablecida) {
    alert('Las contraseñas no coinciden.')
    return
  }

  const passwordValida =
    passwordRestablecida.length >= 8 &&
    /[A-Z]/.test(passwordRestablecida) &&
    /[a-z]/.test(passwordRestablecida) &&
    /[0-9]/.test(passwordRestablecida) &&
    /[@#$%&!]/.test(passwordRestablecida) &&
    !/\s/.test(passwordRestablecida)

  if (!passwordValida) {
    alert(
      'La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y carácter especial.'
    )
    return
  }

  try {
    const respuesta = await fetch(
      `http://127.0.0.1:8001/usuarios/restablecer-password/${tokenRecuperacion}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          password: passwordRestablecida
        })
      }
    )

    const datos = await respuesta.json()

    if (respuesta.ok) {
      alert('Contraseña actualizada correctamente.')

      window.location.href = '/'
    } else {
      alert(
        datos.detail ||
        'No fue posible actualizar la contraseña.'
      )
    }

  } catch (error) {
    console.error('Error al restablecer contraseña:', error)

    alert('No fue posible conectar con el servidor.')
  }
}

const cerrarSesion = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('rol')
  setRol(null)
}

if (esRestablecimiento) {
  return (
    <div className="login-page">

      <div className="login-card">

        <h1>Restablecer contraseña</h1>

        <p>
          Crea una nueva contraseña para tu cuenta.
        </p>

        <div>
          <label>Nueva contraseña</label>

          <input
            type="password"
            placeholder="Nueva contraseña"
            value={passwordRestablecida}
            onChange={(e) =>
              setPasswordRestablecida(e.target.value)
            }
          />
        </div>

        <div>
          <label>Confirmar contraseña</label>

          <input
            type="password"
            placeholder="Confirma tu contraseña"
            value={confirmarPasswordRestablecida}
            onChange={(e) =>
              setConfirmarPasswordRestablecida(e.target.value)
            }
          />
        </div>

        <p>
          Mínimo 8 caracteres, mayúscula, minúscula,
          número y carácter especial.
        </p>

        <button onClick={restablecerPassword}>
          Cambiar contraseña
        </button>

      </div>

    </div>
  )
}

if (esInvitacion) {
  return (
    <div className="invitation-page">
      <h1>Crear cuenta de empleado</h1>

      {invitacionValida === null && (
        <p>Validando invitación...</p>
      )}

      {invitacionValida === false && (
        <p>{mensajeInvitacion}</p>
      )}

      {invitacionValida === true && !cuentaCreada && (
        <div className="invitation-card">
          <p>
            Tu invitación es válida. Crea una contraseña para acceder
            al Sistema de Ingreso de Personal.
          </p>

          <div>
            <label>Nueva contraseña</label>
            <input
              type="password"
              value={nuevaPassword}
              onChange={(e) => setNuevaPassword(e.target.value)}
            />

            <div className="password-requisitos">
              <p>{passwordMinimo ? '✅' : '❌'} Mínimo 8 caracteres</p>
              <p>{passwordMayuscula ? '✅' : '❌'} Una letra mayúscula</p>
              <p>{passwordMinuscula ? '✅' : '❌'} Una letra minúscula</p>
              <p>{passwordNumero ? '✅' : '❌'} Un número</p>
              <p>{passwordEspecial ? '✅' : '❌'} Un carácter especial (@ # $ % & !)</p>
              <p>{passwordSinEspacios ? '✅' : '❌'} Sin espacios</p>
            </div>
          </div>

          <div>
            <label>Confirmar contraseña</label>
            <input
              type="password"
              value={confirmarPassword}
              onChange={(e) => setConfirmarPassword(e.target.value)}
            />
          </div>

          <p>
            La contraseña debe tener mínimo 8 caracteres, mayúscula,
            minúscula, número y un carácter especial.
          </p>

          <button onClick={crearPasswordEmpleado}>
              Crear contraseña
          </button>

          {mensajeInvitacion && (
          <p>{mensajeInvitacion}</p>
          )}

        </div>
      )}

        {cuentaCreada && (
      <div className="invitation-card invitation-success">
        <h2>Cuenta creada correctamente</h2>

        <p>
          Tu cuenta ha sido creada. Ya puedes iniciar sesión con tu correo
          y la contraseña que acabas de registrar.
        </p>

        <button
          onClick={() => {
            localStorage.removeItem('access_token')
            localStorage.removeItem('rol')
            setRol(null)
            window.location.href = '/'
          }}
        >
          Ir a iniciar sesión
        </button>

      </div>
    )}

    </div>
  )
}

if (rol === 'RH') {
  return (
      <div className="dashboard">
        <aside className="sidebar">

            <div className="sidebar-header">
              <h2>Ingreso de Personal</h2>
              <p>Recursos Humanos</p>
            </div>

    <nav className="sidebar-menu">
      <button
          className={seccionRH === 'inicio' ? 'active' : ''}
          onClick={() => setSeccionRH('inicio')}
        >
          Inicio
      </button>

      <button
          className={seccionRH === 'empleados' ? 'active' : ''}
          onClick={() => setSeccionRH('empleados')}
        >
          Empleados
      </button>


      <button
  className={seccionRH === 'catalogos' ? 'active' : ''}
  onClick={() => {
    setSeccionRH('catalogos')
    cargarAreas()
    cargarPuestos()
  }}
>
  Catálogos
</button>

     <button
      className={seccionRH === 'expedientes' ? 'active' : ''}
      onClick={() => {
        setSeccionRH('expedientes')
        setExpedienteSeleccionado(null)
        cargarEmpleados()
      }}
    >
      Expedientes
    </button>

      <button
          className={seccionRH === 'solicitudes' ? 'active' : ''}
          onClick={() => {
            setSeccionRH('solicitudes')
            cargarSolicitudes()
          }}
        >
          Solicitudes
      </button>

    </nav>

    <button
      className="logout-button"
      onClick={cerrarSesion}
    >
      Cerrar sesión
    </button>

  </aside>

  <main className="dashboard-content">

      {seccionRH === 'inicio' && (
  <div>
    <div className="page-header">
      <div>
        <h1>Bienvenido</h1>
        <p>
          Consulta el estado general del proceso de ingreso de personal.
        </p>
      </div>
    </div>

    <div className="dashboard-summary">

      <div className="summary-card">
        <span className="summary-label">Empleados registrados</span>
        <strong className="summary-number">
          {empleados.length}
        </strong>
        <p>Empleados dados de alta en el sistema.</p>
      </div>

      <div className="summary-card">
        <span className="summary-label">Expedientes</span>
        <strong className="summary-icon">📁</strong>
        <p>Consulta la documentación de los empleados.</p>

        <button
          className="summary-link"
          onClick={() => {
            setSeccionRH('expedientes')
            setExpedienteSeleccionado(null)
            cargarEmpleados()
          }}
        >
          Ver expedientes
        </button>
      </div>

      <div className="summary-card">
        <span className="summary-label">Solicitudes</span>
        <strong className="summary-icon">📋</strong>
        <p>Revisa las solicitudes de corrección recibidas.</p>

        <button
          className="summary-link"
          onClick={() => {
            setSeccionRH('solicitudes')
            cargarSolicitudes()
          }}
        >
          Ver solicitudes
        </button>
      </div>

    </div>

    <div className="quick-actions-card">
      <h2>Acciones rápidas</h2>
      <p>Accede a las funciones principales del sistema.</p>

      <div className="quick-actions">
        <button
          className="primary-button"
          onClick={() => {
            setSeccionRH('empleados')
            setMostrarAltaEmpleado(true)
            cargarAreas()
            cargarPuestos()
          }}
        >
          + Dar de alta empleado
        </button>

        <button
          className="secondary-button"
          onClick={() => {
            setSeccionRH('catalogos')
            cargarAreas()
            cargarPuestos()
          }}
        >
          Administrar catálogos
        </button>
      </div>
    </div>
  </div>
)}

    {seccionRH === 'empleados' && (
  <div>

    <button
      className="secondary-button back-button"
      onClick={() => setSeccionRH('inicio')}
    >
      ← Volver al inicio
    </button>

    <div className="page-header">
      <div>
        <h1>Empleados</h1>
        <p>Administra el registro y acceso de los empleados.</p>
      </div>

      <button
        className="primary-button"
        onClick={() => {
        setMostrarAltaEmpleado(true)
        cargarAreas()
        cargarPuestos()
        }}
      >
        + Dar de alta empleado
      </button>
    </div>

    {mensajeEmpleado && (
      <p>{mensajeEmpleado}</p>
    )}

      {mostrarAltaEmpleado && (
      <div className="employee-form-card">
        <h3>Dar de alta empleado</h3>

        <p>Ingresa los datos del nuevo empleado.</p>

        <div className="employee-form-grid">

        <div>
          <label>Nombre</label>
          <input
            type="text"
            value={nuevoNombre}
            onChange={(e) => setNuevoNombre(e.target.value)}
          />
        </div>

        <div>
          <label>Apellido paterno</label>
          <input
            type="text"
            value={nuevoApellidoPaterno}
            onChange={(e) => setNuevoApellidoPaterno(e.target.value)}
          />
        </div>

        <div>
          <label>Apellido materno</label>
          <input
            type="text"
            value={nuevoApellidoMaterno}
            onChange={(e) => setNuevoApellidoMaterno(e.target.value)}
          />
        </div>

        <div>
          <label>Correo electrónico</label>
          <input
            type="email"
            value={nuevoCorreo}
            onChange={(e) => setNuevoCorreo(e.target.value)}
          />
        </div>

        <div>
  <label>Área</label>
  <select
    value={nuevaArea}
    onChange={(e) => setNuevaArea(e.target.value)}
  >
    <option value="">Selecciona un área</option>

    {areas.map((area) => (
      <option key={area.id} value={area.nombre}>
        {area.nombre}
      </option>
    ))}
  </select>
</div>

        <div>
  <label>Puesto</label>
  <select
    value={nuevoPuesto}
    onChange={(e) => setNuevoPuesto(e.target.value)}
  >
    <option value="">Selecciona un puesto</option>

    {puestos.map((puesto) => (
      <option key={puesto.id} value={puesto.nombre}>
        {puesto.nombre}
      </option>
    ))}
  </select>
</div>

        <div>
          <label>Fecha de ingreso</label>
          <input
            type="date"
            value={nuevaFechaIngreso}
            onChange={(e) => setNuevaFechaIngreso(e.target.value)}
          />
        </div>
        </div>

        <div className="form-actions">
          <button
            className="secondary-button"
            onClick={() => setMostrarAltaEmpleado(false)}
          >
            Cancelar
          </button>

          <button
            className="primary-button"
            onClick={registrarEmpleado}
          >
            Registrar empleado
          </button>
        </div>

      </div>
    )}

        <h2 className="section-title">Empleados registrados</h2>

    {empleados.length === 0 ? (
      <p>No hay empleados registrados.</p>
    ) : (
      <div className="employees-card">
        {empleados.map((empleado) => (
  <div className="employee-row" key={empleado.id}>

    <div className="employee-info">
      <strong>
        {empleado.nombre} {empleado.apellido_paterno} {empleado.apellido_materno}
      </strong>
      <span>{empleado.correo}</span>
    </div>

    <div>
      <span className="employee-label">Área</span>
      <p>{empleado.area}</p>
    </div>

    <div>
      <span className="employee-label">Puesto</span>
      <p>{empleado.puesto}</p>
    </div>

    <div>
      <span className="employee-label">Estado</span>

      {empleado.usuario_id === null ? (
        <span className="status status-pending">
          Pendiente
        </span>
      ) : (
        <span className="status status-active">
          Cuenta activa
        </span>
      )}
    </div>

    <div className="employee-action">
      {empleado.usuario_id === null ? (
        <button
          className="invite-button"
          onClick={() => enviarInvitacion(empleado.id)}
        >
          Enviar invitación
        </button>
      ) : (
        <span>—</span>
      )}
    </div>

  </div>
))}


      </div>
    )}
            </div>
  )}

{seccionRH === 'catalogos' && (
  <div>

    <button
      className="secondary-button back-button"
      onClick={() => setSeccionRH('inicio')}
    >
      ← Volver al inicio
    </button>

    <div className="page-header">
      <div>
        <h1>Catálogos</h1>
        <p>Administra las áreas y puestos disponibles para el registro de empleados.</p>
      </div>
    </div>

    <div className="catalog-card">
      <h2>Áreas</h2>

      <div className="catalog-form">
        <input
          type="text"
          placeholder="Nombre del área"
          value={nombreNuevaArea}
          onChange={(e) => setNombreNuevaArea(e.target.value)}
        />

        <button
          className="primary-button"
          onClick={crearArea}
        >
          Agregar área
        </button>
      </div>

      <div className="documents-list">
        {areas.length === 0 ? (
          <p>No hay áreas registradas.</p>
        ) : (
          areas.map((area) => (
            <div className="document-row" key={area.id}>
              <strong>{area.nombre}</strong>

              <span className="status status-active">
                Activa
              </span>
            </div>
          ))
        )}
      </div>
    </div>


    <div className="catalog-card">
      <h2>Puestos</h2>

      <div className="catalog-form">
        <input
          type="text"
          placeholder="Nombre del puesto"
          value={nombreNuevoPuesto}
          onChange={(e) => setNombreNuevoPuesto(e.target.value)}
        />

        <button
          className="primary-button"
          onClick={crearPuesto}
        >
          Agregar puesto
        </button>
      </div>

      <div className="documents-list">
        {puestos.length === 0 ? (
          <p>No hay puestos registrados.</p>
        ) : (
          puestos.map((puesto) => (
            <div className="document-row" key={puesto.id}>
              <strong>{puesto.nombre}</strong>

              <span className="status status-active">
                Activo
              </span>
            </div>
          ))
        )}
      </div>
    </div>

  </div>
)}

{seccionRH === 'expedientes' && (
  <div>

    <button
      className="secondary-button back-button"
      onClick={() => setSeccionRH('inicio')}
    >
      ← Volver al inicio
    </button>

    <div className="page-header">
      <div>
        <h1>Expedientes</h1>
        <p>
          Consulta y revisa la documentación de ingreso de los empleados.
        </p>
      </div>
    </div>

    {!expedienteSeleccionado ? (
      <>
        <h2 className="section-title">Empleados</h2>

        {empleados.length === 0 ? (
          <p>No hay empleados registrados.</p>
        ) : (
          <div className="employees-card">

            {empleados.map((empleado) => (
              <div className="employee-row" key={empleado.id}>

                <div className="employee-info">
                  <strong>
                    {empleado.nombre} {empleado.apellido_paterno}{' '}
                    {empleado.apellido_materno}
                  </strong>

                  <span>{empleado.correo}</span>
                </div>

                <div>
                  <span className="employee-label">Área</span>
                  <p>{empleado.area}</p>
                </div>

                <div>
                  <span className="employee-label">Puesto</span>
                  <p>{empleado.puesto}</p>
                </div>

                <div className="employee-action">
                  <button
                    className="primary-button"
                    onClick={() => cargarExpediente(empleado.id)}
                  >
                    Ver expediente
                  </button>
                </div>

              </div>
            ))}

          </div>
        )}
      </>
    ) : (

      <div>

        <button
          className="secondary-button"
          onClick={() => setExpedienteSeleccionado(null)}
        >
          ← Volver a expedientes
        </button>

        <div className="employee-profile-card">

          <h2>
            {expedienteSeleccionado.empleado.nombre}{' '}
            {expedienteSeleccionado.empleado.apellido_paterno}{' '}
            {expedienteSeleccionado.empleado.apellido_materno}
          </h2>

          <div className="profile-grid">

            <p>
              <strong>Correo:</strong>{' '}
              {expedienteSeleccionado.empleado.correo}
            </p>

            <p>
              <strong>Área:</strong>{' '}
              {expedienteSeleccionado.empleado.area}
            </p>

            <p>
              <strong>Puesto:</strong>{' '}
              {expedienteSeleccionado.empleado.puesto}
            </p>

            <p>
              <strong>Fecha de ingreso:</strong>{' '}
              {expedienteSeleccionado.empleado.fecha_ingreso}
            </p>

          </div>
        </div>

        <h2 className="section-title">
          Documentación
        </h2>

        <div className="documents-list">

          {expedienteSeleccionado.documentos.map((documento) => (

            <div
              className="document-row"
              key={documento.id}
            >

              <div>
  <strong>
    {documentosRequeridos.find(
      (item) => item.tipo === documento.tipo_documento
    )?.nombre || documento.tipo_documento}
  </strong>

  {documento.estado === 'EN REVISION' &&
    documento.motivos_revision?.length > 0 && (
      <div>
        <p>
          <strong>Motivo de revisión:</strong>
        </p>

        {documento.motivos_revision.slice(0, 1).map((motivo, index) => (
        <div key={index}>
  {motivo.motivo ? (
    <p>{motivo.motivo}</p>
  ) : motivo.campo === 'NOMBRE_EMPLEADO' ? (
    <p>
      El nombre detectado en el documento no coincide con el
      nombre registrado del empleado.
      <br />
      <strong>Registrado:</strong> {motivo.valor_origen}
      <br />
      <strong>Detectado:</strong> {motivo.valor_comparado}
    </p>
  ) : (
    <p>
      <strong>{motivo.campo}:</strong>{' '}
      {motivo.resultado}
    </p>
  )}
</div>
        ))}
      </div>
    )}
</div>

        <div className="document-actions">

  <span className="status status-pending">
    {documento.estado}
  </span>

  {documento.estado !== 'NO APLICA' && (
    <button
      className="secondary-button"
      onClick={() => verDocumento(documento.id)}
    >
      Ver documento
    </button>
  )}


</div>

            </div>

          ))}

        </div>

      </div>
    )}

    {cargandoExpediente && (
      <p>Cargando expediente...</p>
    )}

  </div>
)}

    {seccionRH === 'solicitudes' && (
  <div>

    <button
      className="secondary-button back-button"
      onClick={() => setSeccionRH('inicio')}
    >
      ← Volver al inicio
    </button>

    <div className="page-header">
          <div>
            <h1>Solicitudes de corrección</h1>
            <p>
              Revisa las solicitudes de modificación enviadas por los empleados.
            </p>
          </div>
        </div>

        {solicitudes.length === 0 ? (
  <p>No hay solicitudes de corrección.</p>
) : (
  <div>
    {solicitudes.map((solicitud) => (
        <div className="request-card" key={solicitud.id}>
        <p>
          <strong>Empleado:</strong> {solicitud.empleado_id}
        </p>

        <p>
          <strong>Nombre solicitado:</strong>{' '}
          {solicitud.nombre_solicitado || 'Sin cambio'}
        </p>

        <p>
          <strong>Apellido paterno:</strong>{' '}
          {solicitud.apellido_paterno_solicitado || 'Sin cambio'}
        </p>

        <p>
          <strong>Apellido materno:</strong>{' '}
          {solicitud.apellido_materno_solicitado || 'Sin cambio'}
        </p>

        <p>
          <strong>Motivo:</strong> {solicitud.motivo}
        </p>

        <p>
          <strong>Estado:</strong>{' '}
          <span className={`status-badge ${solicitud.estado.toLowerCase()}`}>
            {solicitud.estado}
          </span>
        </p>

        {solicitud.estado === 'PENDIENTE' && (
      <div className="form-actions">

        <button
          className="primary-button"
          onClick={() => resolverSolicitud(solicitud.id, 'APROBAR')}
        >
          Aprobar
        </button>

        <button
          className="secondary-button"
          onClick={() => resolverSolicitud(solicitud.id, 'RECHAZAR')}
        >
          Rechazar
        </button>

      </div>
    )}
      </div>
    ))}
  </div>
)}

      </div>
    )}

      </main>
    </div>
  )
}

if (rol === 'EMPLEADO') {
  return (

    <div className="dashboard">

  <aside className="sidebar">

    <div className="sidebar-header">
      <h2>Ingreso de Personal</h2>
      <p>Portal del Empleado</p>
    </div>

    <nav className="sidebar-menu">

      <button
        className={seccionEmpleado === 'inicio' ? 'active' : ''}
        onClick={() => setSeccionEmpleado('inicio')}
      >
        Inicio
      </button>

      <button
        className={seccionEmpleado === 'datos' ? 'active' : ''}
        onClick={() => setSeccionEmpleado('datos')}
      >
        Mis datos
      </button>

      <button
          className={seccionEmpleado === 'documentos' ? 'active' : ''}
          onClick={() => {
            setSeccionEmpleado('documentos')
            cargarDocumentos()
          }}
      >
        Documentos
      </button>

      <button
          className={seccionEmpleado === 'seguimiento' ? 'active' : ''}
          onClick={() => {
            setSeccionEmpleado('seguimiento')
            cargarDocumentos()
          }}
        >
          Seguimiento
       </button>

</nav>

    <button
      className="logout-button"
      onClick={cerrarSesion}
    >
      Cerrar sesión
    </button>

  </aside>

  <main className="dashboard-content">

    {seccionEmpleado === 'inicio' && (
  <div>
    <div className="page-header">
      <div>
        <h1>
          Bienvenido{empleado ? `, ${empleado.nombre}` : ''}
        </h1>
        <p>
          Consulta y completa tu proceso de ingreso a la empresa.
        </p>
      </div>
    </div>

    <div className="dashboard-summary">

      <div className="summary-card">
        <span className="summary-label">Mis datos</span>
        <strong className="summary-icon">👤</strong>
        <p>
          Verifica la información registrada por Recursos Humanos.
        </p>

        <button
          className="summary-link"
          onClick={() => setSeccionEmpleado('datos')}
        >
          Ver mis datos
        </button>
      </div>

      <div className="summary-card">
        <span className="summary-label">Documentos</span>
        <strong className="summary-icon">📄</strong>
        <p>
          Carga los documentos requeridos para completar tu expediente.
        </p>

        <button
          className="summary-link"
          onClick={() => {
            setSeccionEmpleado('documentos')
            cargarDocumentos()
          }}
        >
          Ir a documentos
        </button>
      </div>

      <div className="summary-card">
        <span className="summary-label">Seguimiento</span>

        <strong className="summary-number">
          {
            documentosRequeridos.filter((documentoRequerido) => {
              const documentoGuardado = documentos.find(
                (documento) =>
                  documento.tipo_documento === documentoRequerido.tipo
              )

              return (
                documentoGuardado?.estado === 'VALIDADO' ||
                documentoGuardado?.estado === 'NO APLICA'
              )
            }).length
          }/{documentosRequeridos.length}
        </strong>

        <p>Documentos resueltos de tu expediente.</p>

        <button
          className="summary-link"
          onClick={() => {
            setSeccionEmpleado('seguimiento')
            cargarDocumentos()
          }}
        >
          Ver seguimiento
        </button>
      </div>

    </div>
  </div>
)}

      {seccionEmpleado === 'datos' && (
  <div>

    <button
      className="secondary-button back-button"
      onClick={() => setSeccionEmpleado('inicio')}
    >
      ← Volver al inicio
    </button>

    {empleado ? (
      <div className="employee-profile-card">

        <div className="profile-header">
          <h2>Mis datos</h2>
          <p>Verifica que tu información registrada sea correcta.</p>
        </div>

        <div className="profile-grid">
          <p>
            <strong>Nombre:</strong>{' '}
            {empleado.nombre} {empleado.apellido_paterno} {empleado.apellido_materno}
          </p>

          <p>
            <strong>Correo:</strong> {empleado.correo}
          </p>

          <p>
            <strong>Área:</strong> {empleado.area}
          </p>

          <p>
            <strong>Puesto:</strong> {empleado.puesto}
          </p>

          <p>
            <strong>Fecha de ingreso:</strong> {empleado.fecha_ingreso}
          </p>
        </div>

        {mensajeCorreccion && (
          <p>{mensajeCorreccion}</p>
        )}

        <button
          className="secondary-button"
          onClick={() => setMostrarCorreccion(true)}
        >
          Solicitar corrección
        </button>

        {mostrarCorreccion && (
          <div className="correction-form-card">
            <h3>Solicitud de corrección</h3>

            <p>
              Puedes solicitar una corrección en tu nombre o apellidos.
              Recursos Humanos revisará tu solicitud.
            </p>

            <div>
              <label>Nombre corregido</label>
              <input
                type="text"
                value={nombreSolicitado}
                onChange={(e) => setNombreSolicitado(e.target.value)}
              />
            </div>

            <div>
              <label>Apellido paterno corregido</label>
              <input
                type="text"
                value={apellidoPaternoSolicitado}
                onChange={(e) => setApellidoPaternoSolicitado(e.target.value)}
              />
            </div>

            <div>
              <label>Apellido materno corregido</label>
              <input
                type="text"
                value={apellidoMaternoSolicitado}
                onChange={(e) => setApellidoMaternoSolicitado(e.target.value)}
              />
            </div>

            <div>
              <label>Motivo de la corrección</label>
              <textarea
                value={motivoCorreccion}
                onChange={(e) => setMotivoCorreccion(e.target.value)}
              />
            </div>

            <div className="form-actions">
              <button
                className="primary-button"
                onClick={enviarSolicitudCorreccion}
              >
                Enviar solicitud
              </button>

              <button
                className="secondary-button"
                onClick={() => setMostrarCorreccion(false)}
              >
                Cancelar
              </button>
            </div>

          </div>
        )}

      </div>
    ) : (
      <p>Cargando información...</p>
    )}

  </div>
)}

{seccionEmpleado === 'documentos' && (
  <div>

      <button
      className="secondary-button back-button"
      onClick={() => setSeccionEmpleado('inicio')}
    >
      ← Volver al inicio
    </button>

    <div className="page-header">
      <div>
        <h1>Mis documentos</h1>
        <p>
          Carga los documentos requeridos para completar tu expediente.
        </p>
      </div>
    </div>

    <div className="employee-profile-card">
  <h2>Documentación requerida</h2>
  <p>
    Los documentos deberán cargarse en formato PDF.
  </p>

  {mensajeDocumento && (
  <p>{mensajeDocumento}</p>
   )}

  <div className="documents-list">
    {documentosRequeridos.map((documentoRequerido) => {
  const documentoGuardado = documentos.find(
    (documento) =>
      documento.tipo_documento === documentoRequerido.tipo
  )

  const estaSeleccionado =
    tipoDocumentoSeleccionado === documentoRequerido.tipo &&
    archivoSeleccionado

  return (
    <div
      className="document-row"
      key={documentoRequerido.tipo}
    >
      <div>
        <strong>{documentoRequerido.nombre}</strong>
        <p>{documentoRequerido.descripcion}</p>
        {documentoGuardado?.estado === 'EN REVISION' &&
  documentoGuardado?.motivos_revision?.length > 0 && (
    <div className="document-review-message">
      <strong>Motivo de revisión:</strong>

      <p>
      {documentoGuardado.motivos_revision[0]?.motivo ||
        'Se detectó una inconsistencia en los datos del documento.'}
      </p>
    </div>
)}
      </div>

      <div className="document-actions">
        <span className="status status-pending">
          {documentoGuardado?.estado || 'PENDIENTE'}
        </span>

        {documentoGuardado &&
          documentoGuardado.estado !== 'NO APLICA' && (
            <button
              className="secondary-button"
              onClick={() => verDocumento(documentoGuardado.id)}
            >
              Ver documento
            </button>
        )}

        {documentoRequerido.tipo === 'SEGURIDAD_SOCIAL' &&
  documentoGuardado?.estado !== 'NO APLICA' && (
    <button
      className="secondary-button"
      onClick={marcarSeguridadSocialNoAplica}
    >
      No cuento con este documento
    </button>
)}

        {estaSeleccionado ? (
          <>
            <span className="file-name">
              {archivoSeleccionado.name}
            </span>

            <button
              className="primary-button"
              onClick={subirDocumento}
            >
              Subir documento
            </button>
          </>
        ) : (
          <label className="upload-button">
            Seleccionar PDF

            <input
              type="file"
              accept=".pdf,application/pdf"
              hidden
              onChange={(e) => {
                setTipoDocumentoSeleccionado(
                  documentoRequerido.tipo
                )
                setArchivoSeleccionado(e.target.files[0])
                setMensajeDocumento('')
              }}
            />
          </label>
        )}
      </div>
    </div>
  )
})}

  </div>
</div>
</div>
)}

{seccionEmpleado === 'seguimiento' && (
  <div>

      <button
          className="secondary-button back-button"
          onClick={() => setSeccionEmpleado('inicio')}
        >
          ← Volver al inicio
      </button>


    <div className="page-header">
      <div>
        <h1>Seguimiento de mi expediente</h1>
        <p>
          Consulta el estado de los documentos de tu proceso de ingreso.
        </p>
      </div>
    </div>

    <div className="employee-profile-card">
      <h2>Avance de documentación</h2>

      <p>
        {
          documentosRequeridos.filter((documentoRequerido) => {
            const documentoGuardado = documentos.find(
              (documento) =>
                documento.tipo_documento === documentoRequerido.tipo
            )

            return (
              documentoGuardado?.estado === 'VALIDADO' ||
              documentoGuardado?.estado === 'NO APLICA'
            )
          }).length
        } de {documentosRequeridos.length} documentos resueltos
      </p>

      <div className="documents-list">
        {documentosRequeridos.map((documentoRequerido) => {
          const documentoGuardado = documentos.find(
            (documento) =>
              documento.tipo_documento === documentoRequerido.tipo
          )

          const estado = documentoGuardado?.estado || 'PENDIENTE'

          return (
            <div
              className="document-row"
              key={documentoRequerido.tipo}
            >
              <div>
                <strong>{documentoRequerido.nombre}</strong>

                <div>
  {estado === 'VALIDADO' && (
    <p>Documento validado correctamente.</p>
  )}

  {estado === 'EN REVISION' && (
    <>
      <p>El documento requiere revisión.</p>

      {documentoGuardado?.motivos_revision?.length > 0 && (
        <div className="document-review-message">
          <strong>Motivo de revisión:</strong>

          <p>
          {documentoGuardado.motivos_revision[0]?.motivo ||
            'Se detectó una inconsistencia en los datos del documento.'}
          </p>
        </div>
      )}
    </>
  )}

  {estado === 'PENDIENTE' && (
    <p>Documento pendiente de completar.</p>
  )}

  {estado === 'NO APLICA' && (
    <p>Este documento no es requerido para tu expediente.</p>
  )}
</div>
              </div>

              <div className="document-actions">
                <span className="status status-pending">
                  {estado === 'EN REVISION'
                    ? 'EN REVISIÓN'
                    : estado}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  </div>
)}

  </main>

</div>
  )
}

  return (
    <div className="login-page">

      <div className="login-card">

        <h1>Sistema de Ingreso de Personal</h1>

        <p>
          PluriOne - Develop Talent & Technology
        </p>

        <form onSubmit={iniciarSesion}>

          <div>
            <label>Correo electrónico</label>
            <input
              type="email"
              placeholder="correo@ejemplo.com"
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
            />
          </div>

          <div>
            <label>Contraseña</label>
            <input
              type="password"
              placeholder="Ingresa tu contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit">
            Iniciar sesión
          </button>

        </form>

      </div>

    </div>
  )
}

export default App