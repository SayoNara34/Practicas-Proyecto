"""Comandos locales para crear profesionales y restablecer accesos (US1)."""
import click

from app import perfiles, usuarios
from app.errores import ErrorDominio
from . import conexion


def registrar_comandos(app) -> None:
    """Registra tareas administrativas que no se exponen al público."""
    @app.cli.command("crear-profesional")
    @click.option("--nombre", prompt="Nombres y apellidos")
    @click.option("--email", prompt="Correo electrónico")
    @click.option("--cedula", prompt="Cédula (sin puntos)")
    @click.option("--telefono", prompt="Teléfono (10 dígitos)")
    @click.option("--direccion", prompt="Dirección")
    @click.option("--departamento", prompt="Departamento", default="Meta")
    @click.option("--municipio", prompt="Municipio", default="Villavicencio")
    @click.password_option(prompt="Contraseña (10 caracteres, letras y números)")
    def crear_profesional(**datos) -> None:
        """Crea una cuenta profesional con contraseña elegida por el administrador."""
        datos.update(confirmacion=datos["password"], consentimiento="si")
        try:
            perfiles.registrar_perfil(conexion(), datos, rol="profesional")
        except ErrorDominio as error:
            raise click.ClickException(str(error)) from error
        click.echo("Cuenta profesional creada. Ya puede ingresar a la aplicación.")

    @app.cli.command("restablecer-clave")
    @click.option("--email", prompt="Correo de la cuenta")
    @click.password_option(prompt="Nueva contraseña (10 caracteres, letras y números)")
    def restablecer_clave(email: str, password: str) -> None:
        """Cambia una contraseña mediante acceso administrativo al servidor."""
        try:
            perfiles.validar_password(password, password)
            persona = conexion().execute("SELECT id FROM usuario WHERE email = ?", (email.strip().lower(),)).fetchone()
            if not persona:
                raise click.ClickException("No existe una cuenta con ese correo.")
            with conexion():
                conexion().execute("UPDATE usuario SET password_hash = ? WHERE id = ?", (usuarios._hashear(password), persona["id"]))
                conexion().execute("DELETE FROM sesion_web WHERE usuario_id = ?", (persona["id"],))
        except ErrorDominio as error:
            raise click.ClickException(str(error)) from error
        click.echo("Contraseña restablecida y sesiones anteriores revocadas.")
