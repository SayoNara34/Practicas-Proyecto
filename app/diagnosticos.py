"""US5, US8 y US11 - Diagnóstico, cierre y consulta de resultados."""
import sqlite3

from . import usuarios
from .db import ahora_iso
from .errores import ErrorPermiso, ErrorTransicion, ErrorValidacion
from .estados import cambiar_estado
from .reportes import obtener_reporte


def iniciar_revision(conn: sqlite3.Connection, reporte_id: int, profesional_id: int) -> None:
    """Pasa un reporte de "Reportado" a "En revisión"."""
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    cambiar_estado(conn, reporte_id, "En revisión")
    conn.commit()


def registrar_diagnostico(conn: sqlite3.Connection, reporte_id: int, profesional_id: int,
                          texto: str, recomendacion: str) -> int:
    """Registra el diagnóstico y deja el reporte en "Diagnosticado" (US5).

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorValidacion: Falta el texto del diagnóstico o la recomendación.
        ErrorTransicion: El reporte ya estaba diagnosticado o resuelto.
    """
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    texto = (texto or "").strip()
    recomendacion = (recomendacion or "").strip()
    if not texto:
        raise ErrorValidacion("El diagnóstico es obligatorio.")
    if not recomendacion:
        raise ErrorValidacion("La recomendación es obligatoria.")
    obtener_reporte(conn, reporte_id)
    cambiar_estado(conn, reporte_id, "Diagnosticado")
    cur = conn.execute(
        "INSERT INTO diagnostico (reporte_id, profesional_id, texto, recomendacion, creado_en) "
        "VALUES (?, ?, ?, ?, ?)",
        (reporte_id, profesional_id, texto, recomendacion, ahora_iso()))
    conn.commit()
    return cur.lastrowid


def marcar_resuelto(conn: sqlite3.Connection, reporte_id: int, profesional_id: int) -> None:
    """Cierra un caso diagnosticado como "Resuelto" (US8).

    Raises:
        ErrorPermiso: El usuario no es profesional.
        ErrorTransicion: El reporte no está en estado "Diagnosticado".
    """
    usuarios.exigir_rol(conn, profesional_id, "profesional")
    if obtener_reporte(conn, reporte_id)["estado"] != "Diagnosticado":
        raise ErrorTransicion("Solo se puede resolver un reporte diagnosticado.")
    cambiar_estado(conn, reporte_id, "Resuelto")
    conn.commit()


def consultar_diagnostico(conn: sqlite3.Connection, reporte_id: int,
                          campesino_id: int) -> sqlite3.Row | None:
    """Consulta el diagnóstico de un reporte propio, incluso después del cierre (US11).

    Args:
        conn: Conexión a SQLite.
        reporte_id: Reporte que desea consultar el campesino.
        campesino_id: Usuario dueño del reporte.

    Returns:
        Diagnóstico, recomendación, profesional y fecha; None si aún no existe.

    Raises:
        ErrorPermiso: El usuario no es campesino o el reporte no le pertenece.
        ErrorNoEncontrado: El usuario o el reporte no existe.
    """
    usuarios.exigir_rol(conn, campesino_id, "campesino")
    reporte = obtener_reporte(conn, reporte_id)
    if reporte["usuario_id"] != campesino_id:
        raise ErrorPermiso("Solo puedes consultar el diagnóstico de tus propios reportes.")
    return conn.execute(
        "SELECT d.texto, d.recomendacion, d.creado_en, u.nombre AS profesional "
        "FROM diagnostico d JOIN usuario u ON u.id = d.profesional_id "
        "WHERE d.reporte_id = ? ORDER BY d.id DESC LIMIT 1", (reporte_id,)).fetchone()
