"""Aplicación web de presentación (US1-US11) sobre la lógica de app/."""
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, g, render_template, request, session
from flask_wtf.csrf import CSRFError, CSRFProtect

from app import db, sesiones
from app.errores import ErrorDominio, ErrorNoEncontrado, ErrorPermiso


def conexion():
    """Devuelve una conexión SQLite por petición/contexto Flask."""
    if "conexion" not in g:
        from flask import current_app
        g.conexion = db.conectar(current_app.config["DATABASE"])
        g.conexion.execute("PRAGMA busy_timeout = 5000")
    return g.conexion


def crear_app(config: dict | None = None) -> Flask:
    """Construye la aplicación y prepara datos persistentes sin insertar ejemplos."""
    raiz = Path(__file__).resolve().parent.parent
    carpeta = Path(os.environ.get("SAVIA_DATA_DIR", str(raiz / "instance"))).resolve()
    app = Flask(__name__, instance_path=str(carpeta))
    app.config.from_mapping(
        DATA_DIR=str(carpeta), DATABASE=str(carpeta / "savia.db"),
        UPLOAD_FOLDER=str(carpeta / "evidencias"), MAX_CONTENT_LENGTH=11 * 1024 * 1024,
        MAX_FORM_MEMORY_SIZE=1024 * 1024, MAX_FORM_PARTS=40,
        SESSION_COOKIE_NAME="savia_session", SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=os.environ.get("SAVIA_HTTPS") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8), WTF_CSRF_TIME_LIMIT=28800,
    )
    if config:
        app.config.update(config)
    directorio = Path(app.config["DATA_DIR"])
    directorio.mkdir(parents=True, mode=0o700, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, mode=0o700, exist_ok=True)
    secreto = directorio / "secret_key"
    if not app.config.get("SECRET_KEY"):
        clave = os.environ.get("SAVIA_SECRET_KEY")
        if not clave:
            # La clave se conserva al reiniciar; no se publica ni se versiona.
            try:
                descriptor = os.open(secreto, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                clave = secreto.read_text(encoding="utf-8").strip()
            else:
                with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
                    clave = secrets.token_hex(32)
                    archivo.write(clave)
        if not clave or len(clave) < 32:
            raise RuntimeError("La clave SAVIA_SECRET_KEY debe tener al menos 32 caracteres.")
        app.config["SECRET_KEY"] = clave
    conn = db.conectar(app.config["DATABASE"])
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        db.inicializar(conn)
    finally:
        conn.close()
    CSRFProtect(app)

    @app.before_request
    def cargar_usuario() -> None:
        g.usuario = sesiones.resolver(conexion(), session.get("sid", ""))
        g.perfil = None
        if g.usuario:
            g.perfil = conexion().execute("SELECT * FROM perfil WHERE usuario_id = ?", (g.usuario["id"],)).fetchone()

    @app.teardown_appcontext
    def cerrar_conexion(error: Exception | None) -> None:
        conn = g.pop("conexion", None)
        if conn is not None:
            conn.close()

    @app.context_processor
    def contexto() -> dict:
        usuario = g.get("usuario")
        sin_leer = 0
        if usuario:
            sin_leer = conexion().execute("SELECT COUNT(*) FROM notificacion WHERE usuario_id = ? AND leida = 0",
                                          (usuario["id"],)).fetchone()[0]
        return dict(usuario=usuario, perfil=g.get("perfil"), sin_leer=sin_leer,
                    anio=datetime.now().year, ahora=datetime.now(ZoneInfo("America/Bogota")))

    @app.template_filter("fecha")
    def fecha(valor: str | None, completa: bool = False) -> str:
        if not valor:
            return "Sin registrar"
        momento = datetime.fromisoformat(valor).astimezone(ZoneInfo("America/Bogota"))
        return momento.strftime("%d/%m/%Y · %I:%M %p" if completa else "%d/%m/%Y")

    @app.template_filter("estado_css")
    def estado_css(valor: str) -> str:
        return {"Reportado": "reportado", "En revisión": "revision", "Diagnosticado": "diagnosticado", "Resuelto": "resuelto"}.get(valor, "")

    @app.after_request
    def encabezados(respuesta):
        respuesta.headers["X-Content-Type-Options"] = "nosniff"
        respuesta.headers["X-Frame-Options"] = "DENY"
        respuesta.headers["Referrer-Policy"] = "same-origin"
        respuesta.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(self)"
        respuesta.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; font-src 'self'; object-src 'none'; "
            "base-uri 'self'; form-action 'self'; frame-ancestors 'none'")
        if request.endpoint != "static":
            respuesta.headers["Cache-Control"] = "no-store"
        if app.config["SESSION_COOKIE_SECURE"]:
            respuesta.headers["Strict-Transport-Security"] = "max-age=31536000"
        return respuesta

    @app.errorhandler(ErrorDominio)
    def error_dominio(error):
        conexion().rollback()
        codigo = 403 if isinstance(error, ErrorPermiso) else 404 if isinstance(error, ErrorNoEncontrado) else 400
        return render_template("error.html", codigo=codigo, mensaje=str(error)), codigo

    @app.errorhandler(CSRFError)
    def error_csrf(error):
        return render_template("error.html", codigo=400, mensaje="Tu formulario venció. Regresa, actualiza la página y vuelve a intentarlo."), 400

    @app.errorhandler(413)
    def archivo_grande(error):
        return render_template("error.html", codigo=413, mensaje="Las fotografías superan el tamaño permitido. Adjunta máximo 10 MB en total."), 413

    @app.errorhandler(404)
    def no_encontrado(error):
        return render_template("error.html", codigo=404, mensaje="La página que buscas no está disponible."), 404

    @app.errorhandler(500)
    def error_interno(error):
        conexion().rollback()
        return render_template("error.html", codigo=500, mensaje="No pudimos completar la solicitud. Inténtalo nuevamente en unos minutos."), 500

    from .rutas import portal_web
    from .comandos import registrar_comandos
    app.register_blueprint(portal_web)
    registrar_comandos(app)
    return app
