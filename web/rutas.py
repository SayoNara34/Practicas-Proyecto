"""US1-US11: rutas, formularios y vistas del portal Savia."""
from functools import wraps
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from flask import (Blueprint, abort, current_app, flash, g, redirect,
                   render_template, request, send_file, send_from_directory, session, url_for)

from app import archivos, diagnosticos, estadisticas, exportaciones, notificaciones, perfiles, portal, reportes, sesiones
from app.errores import ErrorDominio, ErrorPermiso, ErrorValidacion
from app.estados import ESTADOS
from . import conexion

portal_web = Blueprint("portal", __name__)


def acceso(rol: str | None = None):
    """Protege una ruta con sesión vigente y, cuando aplica, el rol indicado."""
    def decorar(funcion):
        @wraps(funcion)
        def protegida(*args, **kwargs):
            if not g.usuario:
                flash("Ingresa a tu cuenta para continuar.", "info")
                return redirect(url_for("portal.ingresar", next=request.path), code=303)
            if rol and g.usuario["rol"] != rol:
                raise ErrorPermiso("Tu cuenta no tiene permiso para realizar esta acción.")
            return funcion(*args, **kwargs)
        return protegida
    return decorar


def _destino(valor: str) -> str:
    destino = urlsplit(valor or "")
    if destino.scheme or destino.netloc or not valor.startswith("/") or valor.startswith("//") or "\\" in valor:
        return url_for("portal.panel")
    return valor


def _datos() -> dict:
    return {k: v for k, v in request.form.items() if k not in ("password", "confirmacion", "actual", "nueva", "csrf_token")}


@portal_web.get("/")
def inicio():
    """Presenta el servicio y las rutas de acceso."""
    return render_template("inicio.html", titulo="Sanidad para el cultivo de plátano")


@portal_web.get("/orientacion")
def orientacion():
    """Explica cómo reportar y seguir un caso sin dar diagnósticos automáticos."""
    return render_template("orientacion.html", titulo="Cómo funciona")


@portal_web.get("/privacidad")
def privacidad():
    """Informa qué datos se recogen y cómo se usan en el servicio."""
    return render_template("privacidad.html", titulo="Tratamiento de datos")


@portal_web.route("/registro", methods=["GET", "POST"])
def registro():
    """US1: registra un agricultor con perfil, sin permitir elegir rol."""
    if g.usuario:
        return redirect(url_for("portal.panel"))
    if request.method == "POST":
        try:
            # Se fija en el servidor: modificar el formulario no crea profesionales.
            perfiles.registrar_perfil(conexion(), request.form.to_dict(), rol="campesino")
        except ErrorDominio as error:
            conexion().rollback()
            flash(str(error), "error")
            return render_template("registro.html", titulo="Crear cuenta", datos=_datos(), departamentos=perfiles.DEPARTAMENTOS), 400
        flash("Tu cuenta fue creada. Ya puedes ingresar con tu correo y contraseña.", "success")
        return redirect(url_for("portal.ingresar"), code=303)
    return render_template("registro.html", titulo="Crear cuenta", datos={}, departamentos=perfiles.DEPARTAMENTOS)


@portal_web.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    """US1: autentica y emite una sesión revocable, sin IDs de usuario en la URL."""
    if g.usuario:
        return redirect(url_for("portal.panel"))
    if request.method == "POST":
        email = request.form.get("email", "")[:255]
        try:
            token = sesiones.autenticar(conexion(), email, request.form.get("password", "")[:129], request.remote_addr or "local")
        except ErrorDominio as error:
            flash(str(error), "error")
            return render_template("ingresar.html", titulo="Ingresar", email=email), 400
        session.clear()
        session["sid"] = token
        session.permanent = True
        return redirect(_destino(request.args.get("next", "")), code=303)
    return render_template("ingresar.html", titulo="Ingresar", email="")


@portal_web.post("/salir")
@acceso()
def salir():
    """Cierra y revoca la sesión en el servidor."""
    sesiones.revocar(conexion(), session.get("sid", ""))
    session.clear()
    return redirect(url_for("portal.inicio"), code=303)


@portal_web.get("/panel")
@acceso()
def panel():
    """US4/US6/US9: muestra el resumen y los reportes del rol autenticado."""
    conteos = portal.resumen(conexion(), g.usuario)
    estado = "Reportado" if g.usuario["rol"] == "profesional" else ""
    recientes = portal.listar_casos(conexion(), g.usuario, estado=estado)["filas"][:4]
    return render_template("panel.html", titulo="Mi espacio" if g.usuario["rol"] == "campesino" else "Centro de atención",
                           conteos=conteos, total=sum(conteos.values()), recientes=recientes)


@portal_web.get("/reportes")
@acceso()
def casos():
    """US4/US6: lista los casos con búsqueda, filtro y paginación autorizados."""
    estado, buscar = request.args.get("estado", ""), request.args.get("buscar", "")
    try:
        pagina = int(request.args.get("pagina", "1"))
    except ValueError:
        raise ErrorValidacion("La página solicitada no es válida.")
    listado = portal.listar_casos(conexion(), g.usuario, estado, buscar, pagina)
    return render_template("reportes.html", titulo="Mis reportes" if g.usuario["rol"] == "campesino" else "Gestión de casos",
                           listado=listado, estados=ESTADOS, estado=estado, buscar=buscar)


@portal_web.route("/reportes/nuevo", methods=["GET", "POST"])
@acceso("campesino")
def nuevo_reporte():
    """US2/US3: valida el reporte, guarda fotografías y registra el caso."""
    datos = dict(g.perfil) if g.perfil else {}
    datos["zona"] = datos.get("municipio", "")
    if request.method == "POST":
        guardados = []
        carpeta = Path(current_app.config["UPLOAD_FOLDER"])
        try:
            validados = portal.datos_reporte(request.form.to_dict())
            guardados = archivos.guardar_fotos(request.files.getlist("fotos"), carpeta)
            rid = reportes.crear_reporte(conexion(), g.usuario["id"], fotos=guardados, **validados)
        except ErrorDominio as error:
            conexion().rollback()
            archivos.eliminar_fotos(guardados, carpeta)
            flash(str(error), "error")
            return render_template("nuevo_reporte.html", titulo="Nuevo reporte", datos=_datos()), 400
        except Exception:
            conexion().rollback()
            archivos.eliminar_fotos(guardados, carpeta)
            raise
        flash("Tu reporte fue enviado. Puedes seguir su atención desde esta página.", "success")
        return redirect(url_for("portal.ver_reporte", reporte_id=rid), code=303)
    return render_template("nuevo_reporte.html", titulo="Nuevo reporte", datos=datos)


@portal_web.get("/reportes/<int:reporte_id>")
@acceso()
def ver_reporte(reporte_id: int):
    """US5/US6/US8/US11: presenta evidencia, diagnóstico e historial del caso."""
    return render_template("detalle.html", titulo=f"Reporte {reporte_id:04d}",
                           **portal.detalle(conexion(), g.usuario, reporte_id))


@portal_web.post("/reportes/<int:reporte_id>/atender")
@acceso("profesional")
def atender(reporte_id: int):
    """US5/US8: ejecuta la acción profesional con transición validada en app/."""
    portal.autorizar_reporte(conexion(), g.usuario, reporte_id)
    accion = request.form.get("accion", "")
    try:
        if accion == "revisar":
            diagnosticos.iniciar_revision(conexion(), reporte_id, g.usuario["id"])
            mensaje = "El caso está en revisión. El agricultor recibió una notificación."
        elif accion == "diagnosticar":
            texto = perfiles.validar_texto(request.form.get("texto"), "Diagnóstico", 5, 4000)
            recomendacion = perfiles.validar_texto(request.form.get("recomendacion"), "Recomendación", 5, 4000)
            diagnosticos.registrar_diagnostico(conexion(), reporte_id, g.usuario["id"], texto, recomendacion)
            mensaje = "Diagnóstico registrado y notificación enviada al agricultor."
        elif accion == "resolver":
            diagnosticos.marcar_resuelto(conexion(), reporte_id, g.usuario["id"])
            mensaje = "El caso fue cerrado como resuelto."
        else:
            raise ErrorValidacion("Selecciona una acción válida.")
    except ErrorDominio as error:
        conexion().rollback()
        flash(str(error), "error")
        return render_template("detalle.html", titulo=f"Reporte {reporte_id:04d}", datos_atencion=_datos(),
                               **portal.detalle(conexion(), g.usuario, reporte_id)), 400
    flash(mensaje, "success")
    return redirect(url_for("portal.ver_reporte", reporte_id=reporte_id), code=303)


@portal_web.get("/evidencias/<nombre>")
@acceso()
def evidencia(nombre: str):
    """US2: sirve una fotografía únicamente al dueño o a un profesional."""
    foto = conexion().execute("SELECT reporte_id FROM foto WHERE nombre_archivo = ?", (nombre,)).fetchone()
    if not foto:
        abort(404)
    portal.autorizar_reporte(conexion(), g.usuario, foto["reporte_id"])
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], nombre, conditional=False)


@portal_web.get("/notificaciones")
@acceso("campesino")
def avisos():
    """US7: consulta avisos propios, con filtro de no leídos."""
    solo_nuevas = request.args.get("nuevas") == "1"
    notas = notificaciones.listar_notificaciones(conexion(), g.usuario["id"], solo_nuevas)
    return render_template("notificaciones.html", titulo="Notificaciones", notas=notas, solo_nuevas=solo_nuevas)


@portal_web.post("/notificaciones/<int:notificacion_id>/leer")
@acceso("campesino")
def leer_aviso(notificacion_id: int):
    """US7: marca una notificación propia como leída."""
    notificaciones.marcar_leida(conexion(), notificacion_id, g.usuario["id"])
    return redirect(url_for("portal.avisos"), code=303)


@portal_web.get("/estadisticas")
@acceso("profesional")
def indicadores():
    """US9: presenta indicadores reales con filtros exactos opcionales."""
    zona, tipo_plaga = _filtros_estadisticas()
    conteos = estadisticas.reportes_por_estado(conexion(), g.usuario["id"], zona, tipo_plaga)
    return render_template("estadisticas.html", titulo="Estadísticas", conteos=conteos,
                           total=sum(conteos.values()), zona=zona, tipo_plaga=tipo_plaga)


def _filtros_estadisticas() -> tuple[str, str]:
    zona, tipo = request.args.get("zona", "").strip(), request.args.get("tipo_plaga", "").strip()
    if len(zona) > 200 or len(tipo) > 200:
        raise ErrorValidacion("Los filtros deben tener máximo 200 caracteres.")
    return zona, tipo


@portal_web.get("/estadisticas/exportar/<formato>")
@acceso("profesional")
def descargar(formato: str):
    """US10: descarga PDF/XLSX con los mismos filtros del panel."""
    zona, tipo = _filtros_estadisticas()
    contenido = exportaciones.exportar_estadisticas(conexion(), g.usuario["id"], formato, zona, tipo)
    mime, nombre = exportaciones.FORMATOS[formato]
    return send_file(BytesIO(contenido), mimetype=mime, as_attachment=True, download_name=nombre)


@portal_web.route("/cuenta", methods=["GET", "POST"])
@acceso()
def cuenta():
    """US1 ampliada: consulta y actualiza datos de contacto del perfil."""
    datos = dict(g.perfil) if g.perfil else {}
    datos["nombre"] = g.usuario["nombre"]
    if request.method == "POST":
        try:
            perfiles.actualizar_perfil(conexion(), g.usuario["id"], request.form.to_dict())
        except ErrorDominio as error:
            flash(str(error), "error")
            return render_template("cuenta.html", titulo="Mi cuenta", datos=_datos(), departamentos=perfiles.DEPARTAMENTOS), 400
        flash("Tus datos de contacto fueron actualizados.", "success")
        return redirect(url_for("portal.cuenta"), code=303)
    return render_template("cuenta.html", titulo="Mi cuenta", datos=datos, departamentos=perfiles.DEPARTAMENTOS)


@portal_web.post("/cuenta/clave")
@acceso()
def actualizar_clave():
    """Cambia la contraseña, revoca sesiones y solicita un nuevo acceso."""
    try:
        perfiles.cambiar_password(conexion(), g.usuario["id"], request.form.get("actual", ""),
                                  request.form.get("nueva", ""), request.form.get("confirmacion", ""))
    except ErrorDominio as error:
        flash(str(error), "error")
        return redirect(url_for("portal.cuenta"), code=303)
    session.clear()
    flash("Contraseña actualizada. Ingresa nuevamente a tu cuenta.", "success")
    return redirect(url_for("portal.ingresar"), code=303)
