"""US1 ampliada: registro y actualización del perfil personal del agricultor."""
import re
import sqlite3

from . import usuarios
from .db import ahora_iso
from .errores import ErrorValidacion

DEPARTAMENTOS = (
    "Amazonas", "Antioquia", "Arauca", "Atlántico", "Bogotá D.C.", "Bolívar",
    "Boyacá", "Caldas", "Caquetá", "Casanare", "Cauca", "Cesar", "Chocó",
    "Córdoba", "Cundinamarca", "Guainía", "Guaviare", "Huila", "La Guajira",
    "Magdalena", "Meta", "Nariño", "Norte de Santander", "Putumayo", "Quindío",
    "Risaralda", "San Andrés y Providencia", "Santander", "Sucre", "Tolima",
    "Valle del Cauca", "Vaupés", "Vichada",
)


def validar_texto(valor: str, campo: str, minimo: int = 1, maximo: int = 150) -> str:
    """Normaliza un campo y verifica sus límites.

    Raises:
        ErrorValidacion: La longitud no está dentro del rango.
    """
    texto = (valor or "").strip()
    if not minimo <= len(texto) <= maximo:
        raise ErrorValidacion(f"{campo}: escribe entre {minimo} y {maximo} caracteres.")
    return texto


def validar_password(password: str, confirmacion: str) -> str:
    """Valida una nueva contraseña de la web sin alterar las cuentas anteriores.

    Raises:
        ErrorValidacion: La contraseña es débil o no coincide.
    """
    if not 10 <= len(password or "") <= 128:
        raise ErrorValidacion("La contraseña debe tener entre 10 y 128 caracteres.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        raise ErrorValidacion("La contraseña debe incluir letras y números.")
    if password != confirmacion:
        raise ErrorValidacion("Las contraseñas no coinciden.")
    return password


def validar_contacto(datos: dict) -> dict:
    """Valida los datos de contacto compartidos por registro y perfil.

    Raises:
        ErrorValidacion: Datos personales o de ubicación inválidos.
    """
    telefono = re.sub(r"[\s()-]", "", datos.get("telefono", ""))
    if not re.fullmatch(r"[0-9]{10}", telefono):
        raise ErrorValidacion("El teléfono debe tener 10 dígitos, sin el prefijo +57.")
    departamento = datos.get("departamento", "")
    if departamento not in DEPARTAMENTOS:
        raise ErrorValidacion("Selecciona un departamento de la lista.")
    return {
        "nombre": validar_texto(datos.get("nombre"), "Nombres y apellidos", 3, 100),
        "telefono": telefono,
        "direccion": validar_texto(datos.get("direccion"), "Dirección", 5, 200),
        "departamento": departamento,
        "municipio": validar_texto(datos.get("municipio"), "Municipio", 2, 100),
        "vereda": validar_texto(datos.get("vereda"), "Vereda", 0, 100),
        "finca": validar_texto(datos.get("finca"), "Finca", 0, 100),
    }


def registrar_perfil(conn: sqlite3.Connection, datos: dict,
                      rol: str = "campesino") -> int:
    """Registra usuario y perfil de forma atómica (US1).

    Raises:
        ErrorValidacion: Perfil inválido, cédula duplicada o falta de autorización.
    """
    contacto = validar_contacto(datos)
    cedula = (datos.get("cedula") or "").strip()
    if not re.fullmatch(r"[0-9]{5,12}", cedula):
        raise ErrorValidacion("La cédula debe tener entre 5 y 12 dígitos, sin puntos.")
    if conn.execute("SELECT 1 FROM perfil WHERE cedula = ?", (cedula,)).fetchone():
        raise ErrorValidacion("La cédula ya está registrada. Ingresa con tu cuenta.")
    if datos.get("consentimiento") != "si":
        raise ErrorValidacion("Debes autorizar el tratamiento de tus datos para crear la cuenta.")
    email = validar_texto(datos.get("email"), "Correo electrónico", 5, 254)
    password = validar_password(datos.get("password", ""), datos.get("confirmacion", ""))
    try:
        with conn:
            uid = usuarios.registrar_usuario(conn, contacto["nombre"], email,
                                             password, rol, confirmar=False)
            conn.execute(
                "INSERT INTO perfil (usuario_id, cedula, telefono, direccion, departamento, "
                "municipio, vereda, finca, consentimiento_en) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (uid, cedula, contacto["telefono"], contacto["direccion"],
                 contacto["departamento"], contacto["municipio"], contacto["vereda"],
                 contacto["finca"], ahora_iso()))
    except sqlite3.IntegrityError as error:
        raise ErrorValidacion("El correo o la cédula ya están registrados.") from error
    return uid


def actualizar_perfil(conn: sqlite3.Connection, uid: int, datos: dict) -> None:
    """Actualiza contacto sin modificar correo, cédula ni rol.

    Raises:
        ErrorValidacion: No existe un perfil completo o los campos son inválidos.
    """
    contacto = validar_contacto(datos)
    if not conn.execute("SELECT 1 FROM perfil WHERE usuario_id = ?", (uid,)).fetchone():
        raise ErrorValidacion("Esta cuenta anterior no tiene un perfil completo. Contacta al administrador.")
    with conn:
        conn.execute("UPDATE usuario SET nombre = ? WHERE id = ?", (contacto["nombre"], uid))
        conn.execute(
            "UPDATE perfil SET telefono = ?, direccion = ?, departamento = ?, municipio = ?, "
            "vereda = ?, finca = ? WHERE usuario_id = ?",
            (contacto["telefono"], contacto["direccion"], contacto["departamento"],
             contacto["municipio"], contacto["vereda"], contacto["finca"], uid))


def cambiar_password(conn: sqlite3.Connection, uid: int, actual: str,
                     nueva: str, confirmacion: str) -> None:
    """Cambia la clave y revoca todas las sesiones del usuario.

    Raises:
        ErrorAutenticacion: La contraseña actual es incorrecta.
        ErrorValidacion: La nueva contraseña no cumple los requisitos.
    """
    usuario = usuarios.obtener_usuario(conn, uid)
    usuarios.iniciar_sesion(conn, usuario["email"], actual)
    validar_password(nueva, confirmacion)
    with conn:
        conn.execute("UPDATE usuario SET password_hash = ? WHERE id = ?",
                     (usuarios._hashear(nueva), uid))
        conn.execute("DELETE FROM sesion_web WHERE usuario_id = ?", (uid,))
