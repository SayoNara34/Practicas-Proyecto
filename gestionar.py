"""Ejecuta comandos de administración: python gestionar.py crear-profesional."""
from web import crear_app

if __name__ == "__main__":
    aplicacion = crear_app()
    with aplicacion.app_context():
        aplicacion.cli.main(prog_name="python gestionar.py")
