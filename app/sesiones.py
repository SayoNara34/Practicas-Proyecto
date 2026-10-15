"""US1 web: sesiones revocables y límite persistente de intentos de acceso."""
import hashlib
import secrets
import sqlite3
import time

from . import usuarios
from .errores import ErrorAutenticacion, ErrorValidacion


def huella(token: str) -> str:
    """Calcula la huella que se almacena en lugar del token de sesión."""
    return hashlib.sha256(token.encode()).hexdigest()


def autenticar(conn: sqlite3.Connection, email: str, password: str,
                direccion_ip: str, duracion: int = 28800) -> str:
    """Valida credenciales y emite una sesión de ocho horas.

    Raises:
        ErrorAutenticacion: Credenciales incorrectas.
        ErrorValidacion: Demasiados intentos en los últimos quince minutos.
    """
    ahora = int(time.time())
    claves = (huella("correo:" + direccion_ip + ":" + email.strip().lower()),
              huella("ip:" + direccion_ip))
    conn.execute("DELETE FROM intento_acceso WHERE creado_en < ?", (ahora - 900,))
    conn.execute("DELETE FROM sesion_web WHERE vence_en <= ?", (ahora,))
    for clave, limite in zip(claves, (8, 40)):
        total = conn.execute("SELECT COUNT(*) FROM intento_acceso WHERE clave = ?",
                             (clave,)).fetchone()[0]
        if total >= limite:
            conn.commit()
            raise ErrorValidacion("Demasiados intentos. Espera 15 minutos y vuelve a ingresar.")
    try:
        usuario = usuarios.iniciar_sesion(conn, email, password)
    except ErrorAutenticacion:
        conn.executemany("INSERT INTO intento_acceso (clave, creado_en) VALUES (?, ?)",
                         [(clave, ahora) for clave in claves])
        conn.commit()
        raise
    token = secrets.token_urlsafe(32)
    conn.execute("DELETE FROM intento_acceso WHERE clave = ?", (claves[0],))
    conn.execute("INSERT INTO sesion_web (token_hash, usuario_id, vence_en) VALUES (?, ?, ?)",
                 (huella(token), usuario["id"], ahora + duracion))
    conn.commit()
    return token


def resolver(conn: sqlite3.Connection, token: str) -> sqlite3.Row | None:
    """Devuelve el usuario de una sesión vigente, sin confiar en IDs de la URL."""
    if not token:
        return None
    return conn.execute(
        "SELECT u.* FROM usuario u JOIN sesion_web s ON s.usuario_id = u.id "
        "WHERE s.token_hash = ? AND s.vence_en > ?", (huella(token), int(time.time()))).fetchone()


def revocar(conn: sqlite3.Connection, token: str) -> None:
    """Invalida la sesión en el servidor al cerrar el acceso."""
    conn.execute("DELETE FROM sesion_web WHERE token_hash = ?", (huella(token),))
    conn.commit()
