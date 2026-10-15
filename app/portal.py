"""US2-US9 web: consultas autorizadas y validaciones del portal persistente."""
import math
import sqlite3

from . import reportes, usuarios
from .errores import ErrorNoEncontrado, ErrorPermiso, ErrorValidacion
from .estados import ESTADOS
from .perfiles import validar_texto


def autorizar_reporte(conn: sqlite3.Connection, usuario: sqlite3.Row,
                       reporte_id: int) -> sqlite3.Row:
    """Devuelve el reporte si pertenece al agricultor o el rol es profesional.

    Raises:
        ErrorPermiso: Se solicita el caso de otro agricultor.
        ErrorNoEncontrado: No existe el reporte.
    """
    reporte = reportes.obtener_reporte(conn, reporte_id)
    if usuario["rol"] != "profesional" and reporte["usuario_id"] != usuario["id"]:
        raise ErrorPermiso("No tienes acceso a este reporte.")
    return reporte


def datos_reporte(datos: dict) -> dict:
    """Valida las longitudes y la ubicación del formulario de reporte.

    Raises:
        ErrorValidacion: Descripción o localización inválidas.
    """
    descripcion = validar_texto(datos.get("descripcion"), "Descripción", 15, 3000)
    ubicacion = reportes.validar_ubicacion(validar_texto(datos.get("ubicacion"), "Ubicación", 3, 250))
    municipio = validar_texto(datos.get("zona"), "Municipio del cultivo", 2, 100)
    tipo = validar_texto(datos.get("tipo_plaga"), "Posible afectación", 0, 100)
    return dict(descripcion=descripcion, ubicacion=ubicacion, zona=municipio, tipo_plaga=tipo)


def listar_casos(conn: sqlite3.Connection, usuario: sqlite3.Row,
                 estado: str = "", buscar: str = "", pagina: int = 1) -> dict:
    """US4/US6: pagina los casos autorizados y permite buscar o filtrar.

    Raises:
        ErrorValidacion: Estado, búsqueda o página inválidos.
    """
    if estado and estado not in ESTADOS:
        raise ErrorValidacion("Selecciona un estado válido.")
    if len(buscar) > 150 or pagina < 1 or pagina > 100000:
        raise ErrorValidacion("La búsqueda o la página no es válida.")
    condiciones, valores = [], []
    if usuario["rol"] != "profesional":
        condiciones.append("r.usuario_id = ?")
        valores.append(usuario["id"])
    if estado:
        condiciones.append("r.estado = ?")
        valores.append(estado)
    if buscar:
        condiciones.append("(instr(CASEFOLD(r.descripcion), CASEFOLD(?)) > 0 OR "
                           "instr(CASEFOLD(r.ubicacion), CASEFOLD(?)) > 0 OR "
                           "instr(CASEFOLD(r.zona), CASEFOLD(?)) > 0)")
        valores.extend([buscar.strip()] * 3)
    donde = " WHERE " + " AND ".join(condiciones) if condiciones else ""
    total = conn.execute("SELECT COUNT(*) FROM reporte r" + donde, valores).fetchone()[0]
    orden = "r.creado_en ASC" if usuario["rol"] == "profesional" and estado == "Reportado" else "r.creado_en DESC"
    filas = conn.execute(
        "SELECT r.*, u.nombre AS agricultor, (SELECT f.nombre_archivo FROM foto f "
        "WHERE f.reporte_id = r.id ORDER BY f.id LIMIT 1) AS portada "
        "FROM reporte r JOIN usuario u ON u.id = r.usuario_id" + donde +
        " ORDER BY " + orden + ", r.id DESC LIMIT 12 OFFSET ?", [*valores, (pagina - 1) * 12]).fetchall()
    return dict(filas=filas, total=total, paginas=max(1, math.ceil(total / 12)), pagina=pagina)


def resumen(conn: sqlite3.Connection, usuario: sqlite3.Row) -> dict:
    """US6/US9: devuelve conteos reales dentro del alcance autorizado."""
    clausula, valores = ("", ()) if usuario["rol"] == "profesional" else (" WHERE usuario_id = ?", (usuario["id"],))
    conteos = dict.fromkeys(ESTADOS, 0)
    for fila in conn.execute("SELECT estado, COUNT(*) AS total FROM reporte" + clausula + " GROUP BY estado", valores):
        conteos[fila["estado"]] = fila["total"]
    return conteos


def detalle(conn: sqlite3.Connection, usuario: sqlite3.Row, reporte_id: int) -> dict:
    """US5/US8/US11: compone evidencia, resultado e historial del caso autorizado."""
    reporte = autorizar_reporte(conn, usuario, reporte_id)
    persona = conn.execute(
        "SELECT u.nombre, u.email, p.telefono, p.municipio, p.finca FROM usuario u "
        "LEFT JOIN perfil p ON p.usuario_id = u.id WHERE u.id = ?", (reporte["usuario_id"],)).fetchone()
    resultado = conn.execute(
        "SELECT d.*, u.nombre AS profesional FROM diagnostico d JOIN usuario u "
        "ON u.id = d.profesional_id WHERE d.reporte_id = ?", (reporte_id,)).fetchone()
    eventos = conn.execute(
        "SELECT e.*, u.nombre AS actor FROM evento_reporte e LEFT JOIN usuario u ON u.id = e.actor_id "
        "WHERE e.reporte_id = ? ORDER BY e.id", (reporte_id,)).fetchall()
    fotos = conn.execute("SELECT * FROM foto WHERE reporte_id = ? ORDER BY id", (reporte_id,)).fetchall()
    return dict(reporte=reporte, persona=persona, resultado=resultado, eventos=eventos, fotos=fotos)
