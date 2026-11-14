"""Carga usuarios de demostración (y reportes de ejemplo) en la base de datos local.

Uso:
    python cargar_demo.py                  Crea los usuarios de datos_demo/usuarios_demo.json.
    python cargar_demo.py --con-reportes   Además crea reportes de ejemplo en distintos estados.
    python cargar_demo.py --reiniciar      Borra la base local y las fotos para empezar desde cero.

Los usuarios que ya existen se omiten, así que puedes ejecutarlo varias veces.
"""
import argparse
import json
import random
import sys
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFilter

from app import db, diagnosticos, perfiles, reportes
from app.errores import ErrorDominio
from web import crear_app

RAIZ = Path(__file__).resolve().parent
DATOS = RAIZ / "datos_demo" / "usuarios_demo.json"

# Colores de las manchas según el tipo de foto de ejemplo.
MANCHAS = {
    "manchas": ((92, 64, 38), 38), "base": ((48, 36, 28), 14), "amarillas": ((214, 190, 72), 26),
    "fruto": ((120, 88, 46), 30), "raices": ((40, 32, 26), 18),
}


def foto_ejemplo(tipo: str, carpeta: Path, semilla: int) -> str:
    """Dibuja una hoja con manchas y la guarda como JPG con nombre interno aleatorio."""
    azar = random.Random(semilla)
    ancho, alto = 1200, 900
    imagen = Image.new("RGB", (ancho, alto), (214, 226, 196))
    pincel = ImageDraw.Draw(imagen)
    for y in range(alto):  # Fondo con degradado suave.
        tono = int(30 * y / alto)
        pincel.line([(0, y), (ancho, y)], fill=(206 - tono, 222 - tono, 188 - tono))
    pincel.ellipse([140, 120, 1060, 780], fill=(70, 128, 76))
    pincel.line([(170, 760), (1040, 150)], fill=(176, 204, 128), width=10)
    for i in range(14):  # Nervaduras.
        x = 260 + i * 55
        pincel.line([(x, 680 - i * 38), (x + 140, 560 - i * 38 - 120)], fill=(108, 160, 98), width=3)
    color, cantidad = MANCHAS.get(tipo, MANCHAS["manchas"])
    for _ in range(cantidad):
        x, y = azar.randint(240, 960), azar.randint(200, 700)
        r = azar.randint(10, 34)
        pincel.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=color)
    imagen = imagen.filter(ImageFilter.GaussianBlur(1.2))
    nombre = uuid4().hex + ".jpg"
    imagen.save(carpeta / nombre, format="JPEG", quality=85)
    return nombre


def reiniciar(app) -> None:
    """Elimina la base de datos local y las fotos guardadas, previa confirmación."""
    base, fotos = Path(app.config["DATABASE"]), Path(app.config["UPLOAD_FOLDER"])
    print(f"Se borrará la base de datos {base}")
    print(f"y todas las fotos de {fotos}.")
    if input("Escribe BORRAR para confirmar: ").strip().lstrip("﻿").upper() != "BORRAR":
        print("Cancelado. No se borró nada.")
        sys.exit(1)
    for sufijo in ("", "-wal", "-shm"):
        Path(str(base) + sufijo).unlink(missing_ok=True)
    for archivo in fotos.glob("*"):
        if archivo.is_file():
            archivo.unlink()
    print("Listo. La base quedó vacía; se volverá a crear al iniciar la aplicación.")


def cargar_usuarios(conn, datos: dict) -> dict:
    """Registra campesinos y profesionales; devuelve {email: id} de todos."""
    ids = {}
    for rol, lista in (("campesino", datos["campesinos"]), ("profesional", datos["profesionales"])):
        for persona in lista:
            email = persona["email"].lower()
            fila = conn.execute("SELECT id FROM usuario WHERE email = ?", (email,)).fetchone()
            if fila:
                ids[email] = fila["id"]
                print(f"  ya existía   {rol:<12} {email}")
                continue
            registro = dict(persona, confirmacion=persona["password"], consentimiento="si")
            ids[email] = perfiles.registrar_perfil(conn, registro, rol=rol)
            print(f"  creado       {rol:<12} {email}")
    return ids


def cargar_reportes(conn, datos: dict, ids: dict, carpeta: Path) -> None:
    """Crea reportes de ejemplo y los lleva hasta el estado indicado en el JSON."""
    existentes = {fila[0] for fila in conn.execute("SELECT descripcion FROM reporte")}
    for i, caso in enumerate(datos["reportes"]):
        if caso["descripcion"] in existentes:
            print(f"  ya existía   reporte de {caso['campesino']}")
            continue
        fotos = [foto_ejemplo(caso["foto"], carpeta, i * 10 + n) for n in range(2)]
        rid = reportes.crear_reporte(conn, ids[caso["campesino"]], caso["descripcion"], caso["ubicacion"],
                                     fotos, tipo_plaga=caso.get("tipo_plaga"), zona=caso.get("zona"))
        estado = caso["estado"]
        if estado != "Reportado":
            profesional = ids[caso["profesional"]]
            diagnosticos.iniciar_revision(conn, rid, profesional)
            if estado in ("Diagnosticado", "Resuelto"):
                diagnosticos.registrar_diagnostico(conn, rid, profesional, caso["diagnostico"], caso["recomendacion"])
            if estado == "Resuelto":
                diagnosticos.marcar_resuelto(conn, rid, profesional)
        print(f"  creado       reporte SV-{rid:04d} ({estado})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga usuarios de demostración en Savia.")
    parser.add_argument("--con-reportes", action="store_true", help="crea también reportes de ejemplo")
    parser.add_argument("--reiniciar", action="store_true", help="borra la base local antes de continuar")
    parser.add_argument("--solo-reiniciar", action="store_true", help="borra la base local y no carga nada")
    args = parser.parse_args()

    app = crear_app()
    if args.reiniciar or args.solo_reiniciar:
        reiniciar(app)
        if args.solo_reiniciar:
            return
        app = crear_app()  # Vuelve a crear las tablas vacías.

    datos = json.loads(DATOS.read_text(encoding="utf-8"))
    conn = db.conectar(app.config["DATABASE"])
    try:
        print("Usuarios:")
        ids = cargar_usuarios(conn, datos)
        if args.con_reportes:
            print("Reportes de ejemplo:")
            cargar_reportes(conn, datos, ids, Path(app.config["UPLOAD_FOLDER"]))
    except ErrorDominio as error:
        conn.rollback()
        sys.exit(f"No se pudo cargar la demostración: {error}")
    finally:
        conn.close()
    print("\nListo. Las credenciales están en datos_demo/USUARIOS_DEMO.txt")


if __name__ == "__main__":
    main()
