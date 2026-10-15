"""Inicia la aplicación web persistente con Waitress, sin modo de depuración."""
import argparse

from waitress import serve
from web import crear_app


def main() -> None:
    """Arranca el servidor local con puerto configurable."""
    parser = argparse.ArgumentParser(description="Savia - Control de plagas en plátano")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--puerto", type=int, default=8000)
    args = parser.parse_args()
    app = crear_app()
    print(f"Savia está disponible en http://{args.host}:{args.puerto}", flush=True)
    print("Para detenerla presiona Ctrl+C. Los datos se conservan.", flush=True)
    serve(app, host=args.host, port=args.puerto, threads=4, max_request_body_size=11 * 1024 * 1024)


if __name__ == "__main__":
    main()
