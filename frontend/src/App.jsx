import { useEffect, useState } from 'react'
import './App.css'
function App() {
  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
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
const [seccionRH, setSeccionRH] = useState('empleados')
const [seccionEmpleado, setSeccionEmpleado] = useState('inicio')
const rutaActual = window.location.pathname
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
      console.error(datos.detail)
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

  setMensajeDocumento('Documento cargado correctamente.')
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

const cerrarSesion = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('rol')
  setRol(null)
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

    {seccionRH === 'empleados' && (
        <div>

    <div className="page-header">
      <div>
        <h1>Empleados</h1>
        <p>Administra el registro y acceso de los empleados.</p>
      </div>

      <button
        className="primary-button"
        onClick={() => setMostrarAltaEmpleado(true)}
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
          <input
            type="text"
            value={nuevaArea}
            onChange={(e) => setNuevaArea(e.target.value)}
          />
        </div>

        <div>
          <label>Puesto</label>
          <input
            type="text"
            value={nuevoPuesto}
            onChange={(e) => setNuevoPuesto(e.target.value)}
          />
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


{seccionRH === 'expedientes' && (
  <div>

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

        {documento.motivos_revision.map((motivo, index) => (
          <div key={index}>
            {motivo.campo === 'NOMBRE_EMPLEADO' ? (
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

  {documento.estado === 'EN REVISION' && (
    <>
      <button
        className="primary-button"
        onClick={() =>
          cambiarEstadoDocumento(documento.id, 'aprobar')
        }
      >
        Aprobar
      </button>

      <button
        className="secondary-button"
        onClick={() =>
          cambiarEstadoDocumento(
            documento.id,
            'solicitar-correccion'
          )
        }
      >
        Solicitar corrección
      </button>
    </>
  )}

  {documento.tipo_documento === 'SEGURIDAD_SOCIAL' &&
    documento.estado !== 'VALIDADO' &&
    documento.estado !== 'NO APLICA' && (
      <button
        className="secondary-button"
        onClick={() =>
          cambiarEstadoDocumento(documento.id, 'no-aplica')
        }
      >
        No aplicas
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
        <div className="page-header">
            <div>
              <h1>Bienvenido</h1>
              <p>Completa tu proceso de ingreso a la empresa.</p>
            </div>
          </div>
        )}

       {seccionEmpleado === 'datos' && (
        <div>

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
      </div>

      <div className="document-actions">
        <span className="status status-pending">
          {documentoGuardado?.estado || 'PENDIENTE'}
        </span>

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

                <p>
                  {estado === 'VALIDADO' &&
                    'Documento validado correctamente.'}

                  {estado === 'EN REVISION' &&
                    'El documento está siendo revisado.'}

                  {estado === 'PENDIENTE' &&
                    'Documento pendiente de completar.'}

                  {estado === 'NO APLICA' &&
                    'Este documento no es requerido para tu expediente.'}
                </p>
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