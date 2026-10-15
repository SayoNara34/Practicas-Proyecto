"""US1-US11 web: persistencia, acceso real, evidencias y atención de casos."""
import hashlib
import io
import re
import sqlite3
from pathlib import Path

import pytest
from openpyxl import load_workbook
from PIL import Image
from pypdf import PdfReader

from app import db, perfiles, sesiones, usuarios
from web import crear_app


def datos_persona(indice=1):
    """Construye datos ficticios exclusivamente para las pruebas aisladas."""
    return dict(nombre=f"Agricultor Prueba {indice}", cedula=f"10000000{indice}",
                telefono="3001234567", direccion="Vereda de pruebas, finca de prueba",
                departamento="Meta", municipio="Acacías", vereda="La Esperanza", finca="El Porvenir",
                email=f"prueba{indice}@ejemplo.co", password="Pruebas2026seguras",
                confirmacion="Pruebas2026seguras", consentimiento="si")


@pytest.fixture
def aplicacion(tmp_path):
    """Aísla la base de datos, fotografías y clave de las pruebas web."""
    return crear_app(dict(TESTING=True, DATA_DIR=str(tmp_path), DATABASE=str(tmp_path / "savia.db"),
                         UPLOAD_FOLDER=str(tmp_path / "fotos"), SECRET_KEY="pruebas-aisladas-" * 4))


def csrf(cliente, ruta="/ingresar"):
    """Extrae el token real del formulario, sin desactivar CSRF en pruebas."""
    pagina = cliente.get(ruta)
    encontrado = re.search(rb'name="csrf_token" value="([^"]+)"', pagina.data)
    assert encontrado, (ruta, pagina.status_code)
    return encontrado[1].decode()


def enviar(cliente, ruta, datos, origen="/ingresar", **kwargs):
    """Envía el formulario con la misma protección que utiliza el navegador."""
    return cliente.post(ruta, data={**datos, "csrf_token": csrf(cliente, origen)}, **kwargs)


def crear_persona(aplicacion, indice=1, profesional=False):
    """Registra un perfil completo directamente en la capa de dominio."""
    datos = datos_persona(indice)
    conn = db.conectar(aplicacion.config["DATABASE"])
    try:
        uid = perfiles.registrar_perfil(conn, datos, "profesional" if profesional else "campesino")
    finally:
        conn.close()
    return uid, datos


def ingresar(cliente, datos):
    """Autentica por el formulario real y comprueba el destino."""
    respuesta = enviar(cliente, "/ingresar", {"email": datos["email"], "password": datos["password"]})
    assert respuesta.status_code == 303
    return respuesta


def imagen():
    """Genera una imagen PNG válida, sin recursos externos."""
    salida = io.BytesIO()
    Image.new("RGB", (80, 60), "green").save(salida, format="PNG")
    salida.seek(0)
    return salida


def crear_caso(cliente):
    """Crea un reporte mediante multipart y devuelve el identificador real."""
    respuesta = enviar(cliente, "/reportes/nuevo", {
        "descripcion": "Hojas con manchas oscuras desde hace tres días.",
        "ubicacion": "4.15, -73.63", "zona": "Acacías", "tipo_plaga": "Por identificar",
        "fotos": (imagen(), "evidencia.png")}, origen="/reportes/nuevo", content_type="multipart/form-data")
    assert respuesta.status_code == 303, respuesta.data.decode()
    return int(respuesta.headers["Location"].rsplit("/", 1)[1])


@pytest.mark.parametrize("ruta", ["/", "/registro", "/ingresar", "/orientacion", "/privacidad"])
def test_paginas_publicas_sin_emojis_ni_eventos_inline(aplicacion, ruta):
    respuesta = aplicacion.test_client().get(ruta)
    assert respuesta.status_code == 200
    texto = respuesta.data.decode()
    assert '<html lang="es-CO">' in texto
    assert not re.search(r"[\U0001F300-\U0001FAFF]", texto)
    assert not re.search(r'\son(?:click|error|load|submit)\s*=', texto)
    assert "frame-ancestors 'none'" in respuesta.headers["Content-Security-Policy"]


def test_registro_persistente_con_identidad_y_rol_fijado(aplicacion):
    cliente = aplicacion.test_client()
    datos = datos_persona()
    respuesta = enviar(cliente, "/registro", {**datos, "rol": "profesional"}, origen="/registro")
    assert respuesta.status_code == 303
    conn = db.conectar(aplicacion.config["DATABASE"])
    usuario = conn.execute("SELECT * FROM usuario").fetchone()
    perfil = conn.execute("SELECT * FROM perfil").fetchone()
    assert usuario["rol"] == "campesino"
    assert usuario["password_hash"] != datos["password"]
    assert perfil["cedula"] == datos["cedula"]
    assert perfil["direccion"] == datos["direccion"]
    conn.close()
    reiniciada = crear_app(dict(aplicacion.config))
    ingresar(reiniciada.test_client(), datos)


@pytest.mark.parametrize("campo,valor", [("cedula", "abc"), ("telefono", "123"),
    ("direccion", "x"), ("consentimiento", "no"), ("confirmacion", "otra"),
    ("departamento", "inventado"), ("password", "sololetraslargas")])
def test_registro_rechaza_datos_invalidos_sin_usuario_parcial(aplicacion, campo, valor):
    cliente = aplicacion.test_client()
    datos = {**datos_persona(), campo: valor}
    respuesta = enviar(cliente, "/registro", datos, origen="/registro")
    assert respuesta.status_code == 400
    conn = db.conectar(aplicacion.config["DATABASE"])
    assert conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] == 0
    conn.close()
    assert datos["password"].encode() not in respuesta.data


def test_cedula_unica_y_transaccion_atomica(aplicacion):
    crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    datos = {**datos_persona(2), "cedula": datos_persona()["cedula"]}
    respuesta = enviar(cliente, "/registro", datos, origen="/registro")
    assert respuesta.status_code == 400
    conn = db.conectar(aplicacion.config["DATABASE"])
    assert conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] == 1
    conn.close()


def test_csrf_y_url_no_sustituyen_autenticacion(aplicacion):
    cliente = aplicacion.test_client()
    assert cliente.post("/registro", data=datos_persona()).status_code == 400
    for ruta in ("/panel?u=1", "/reportes", "/cuenta", "/estadisticas"):
        assert cliente.get(ruta).status_code == 303


def test_logout_revoca_sesion_reutilizada(aplicacion):
    _, datos = crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    ingresar(cliente, datos)
    cookie = cliente.get_cookie("savia_session").value
    respuesta = enviar(cliente, "/salir", {}, origen="/panel")
    assert respuesta.status_code == 303
    cliente.set_cookie("savia_session", cookie)
    assert cliente.get("/panel").status_code == 303


def test_fotografia_y_reporte_privados_y_persistentes(aplicacion):
    _, datos = crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    ingresar(cliente, datos)
    rid = crear_caso(cliente)
    detalle = cliente.get(f"/reportes/{rid}")
    assert detalle.status_code == 200 and b"Hojas con manchas" in detalle.data
    conn = db.conectar(aplicacion.config["DATABASE"])
    foto = conn.execute("SELECT nombre_archivo FROM foto WHERE reporte_id = ?", (rid,)).fetchone()[0]
    conn.close()
    assert foto != "evidencia.png" and foto.endswith(".jpg")
    ruta_foto = Path(aplicacion.config["UPLOAD_FOLDER"]) / foto
    with Image.open(ruta_foto) as archivo:
        assert archivo.format == "JPEG"
    assert cliente.get(f"/evidencias/{foto}").status_code == 200
    _, datos2 = crear_persona(aplicacion, 2)
    otro = aplicacion.test_client()
    ingresar(otro, datos2)
    assert otro.get(f"/reportes/{rid}").status_code == 403
    assert otro.get(f"/evidencias/{foto}").status_code == 403
    assert b"Hojas con manchas" not in otro.get("/reportes").data
    reiniciada = crear_app(dict(aplicacion.config))
    nuevo = reiniciada.test_client()
    ingresar(nuevo, datos)
    assert nuevo.get(f"/reportes/{rid}").status_code == 200
    assert nuevo.get(f"/evidencias/{foto}").status_code == 200


@pytest.mark.parametrize("tipo", ["falso", "cantidad", "ubicacion"])
def test_evidencias_invalidas_no_dejan_casos_ni_archivos(aplicacion, tipo):
    _, datos = crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    ingresar(cliente, datos)
    formulario = dict(descripcion="Descripción válida de una afectación de hojas", zona="Acacías", ubicacion="Finca de prueba")
    formulario["fotos"] = (io.BytesIO(b"<script>no es foto</script>"), "falsa.png") if tipo == "falso" else [(imagen(), f"foto{i}.png") for i in range(7 if tipo == "cantidad" else 1)]
    if tipo == "ubicacion":
        formulario["ubicacion"] = "95, -73"
    respuesta = enviar(cliente, "/reportes/nuevo", formulario, origen="/reportes/nuevo", content_type="multipart/form-data")
    assert respuesta.status_code == 400
    conn = db.conectar(aplicacion.config["DATABASE"])
    assert conn.execute("SELECT COUNT(*) FROM reporte").fetchone()[0] == 0
    conn.close()
    assert not list(Path(aplicacion.config["UPLOAD_FOLDER"]).iterdir())


def test_limite_del_cuerpo_multipart(aplicacion):
    _, datos = crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    ingresar(cliente, datos)
    respuesta = enviar(cliente, "/reportes/nuevo", {"fotos": (io.BytesIO(b"x" * (12 * 1024 * 1024)), "grande.png")}, origen="/reportes/nuevo", content_type="multipart/form-data")
    assert respuesta.status_code == 413


def test_recorrido_profesional_diagnostico_notificacion_cierre_exportacion(aplicacion):
    _, datos = crear_persona(aplicacion)
    _, agronomo = crear_persona(aplicacion, 3, profesional=True)
    agricultor = aplicacion.test_client()
    profesional = aplicacion.test_client()
    ingresar(agricultor, datos)
    rid = crear_caso(agricultor)
    ingresar(profesional, agronomo)
    for ruta in ("/panel", "/reportes", "/estadisticas", "/cuenta", f"/reportes/{rid}"):
        assert profesional.get(ruta).status_code == 200
    ruta = f"/reportes/{rid}/atender"
    assert enviar(agricultor, ruta, {"accion": "resolver"}, origen=f"/reportes/{rid}").status_code == 403
    assert enviar(profesional, ruta, {"accion": "resolver"}, origen=f"/reportes/{rid}").status_code == 400
    assert enviar(profesional, ruta, {"accion": "revisar"}, origen=f"/reportes/{rid}").status_code == 303
    texto = "Resultado profesional con <script>texto</script>"
    assert enviar(profesional, ruta, {"accion": "diagnosticar", "texto": texto, "recomendacion": "Orientación registrada para el cultivo."}, origen=f"/reportes/{rid}").status_code == 303
    assert enviar(profesional, ruta, {"accion": "resolver"}, origen=f"/reportes/{rid}").status_code == 303
    resultado = agricultor.get(f"/reportes/{rid}").data
    assert b"Orientaci" in resultado and b"&lt;script&gt;" in resultado and b"<script>texto" not in resultado
    assert agricultor.get("/notificaciones").status_code == 200
    conn = db.conectar(aplicacion.config["DATABASE"])
    notas = conn.execute("SELECT * FROM notificacion").fetchall()
    eventos = conn.execute("SELECT estado FROM evento_reporte ORDER BY id").fetchall()
    assert len(notas) == 3
    assert [e[0] for e in eventos] == ["Reportado", "En revisión", "Diagnosticado", "Resuelto"]
    conn.close()
    assert enviar(agricultor, f"/notificaciones/{notas[0]['id']}/leer", {}, origen="/notificaciones").status_code == 303
    assert b"Hojas con manchas" in agricultor.get("/reportes?buscar=ACAC%C3%8DAS").data
    pdf = profesional.get("/estadisticas/exportar/pdf?zona=ACAC%C3%8DAS")
    assert pdf.status_code == 200 and pdf.data.startswith(b"%PDF")
    assert "Total\n1" in PdfReader(io.BytesIO(pdf.data)).pages[0].extract_text()
    excel = profesional.get("/estadisticas/exportar/xlsx?zona=ACAC%C3%8DAS")
    hoja = load_workbook(io.BytesIO(excel.data)).active
    assert hoja["B11"].value == 1 and hoja["B10"].value == 1
    assert agricultor.get("/estadisticas/exportar/pdf").status_code == 403
    assert profesional.get("/estadisticas/exportar/csv").status_code == 400


def test_notificacion_ajena_no_se_modifica(aplicacion):
    uid, datos = crear_persona(aplicacion)
    _, otros = crear_persona(aplicacion, 2)
    cliente = aplicacion.test_client()
    ingresar(cliente, datos)
    rid = crear_caso(cliente)
    conn = db.conectar(aplicacion.config["DATABASE"])
    conn.execute("INSERT INTO notificacion (usuario_id,reporte_id,mensaje,creado_en) VALUES (?,?,?,?)", (uid, rid, "Aviso de prueba", db.ahora_iso()))
    conn.commit()
    nid = conn.execute("SELECT id FROM notificacion").fetchone()[0]
    conn.close()
    otro = aplicacion.test_client()
    ingresar(otro, otros)
    assert enviar(otro, f"/notificaciones/{nid}/leer", {}, origen="/notificaciones").status_code == 403


def test_actualizar_perfil_y_password_revoca_las_otras_sesiones(aplicacion):
    _, datos = crear_persona(aplicacion)
    cliente, otro = aplicacion.test_client(), aplicacion.test_client()
    ingresar(cliente, datos)
    ingresar(otro, datos)
    respuesta = enviar(cliente, "/cuenta", {**datos, "direccion": "Nueva dirección rural de prueba", "cedula": "99999999", "email": "otro@ejemplo.co"}, origen="/cuenta")
    assert respuesta.status_code == 303
    cuenta = cliente.get("/cuenta").data
    assert datos["cedula"].encode() not in cuenta
    assert datos["email"].encode() in cuenta
    assert enviar(cliente, "/cuenta/clave", dict(actual=datos["password"], nueva="OtraPassword2026", confirmacion="OtraPassword2026"), origen="/cuenta").status_code == 303
    assert otro.get("/panel").status_code == 303
    ingresar(cliente, {**datos, "password": "OtraPassword2026"})


def test_limitacion_de_intentos_persistente(aplicacion):
    _, datos = crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    for _ in range(8):
        assert enviar(cliente, "/ingresar", {"email": datos["email"], "password": "incorrecta"}).status_code == 400
    respuesta = enviar(aplicacion.test_client(), "/ingresar", {"email": datos["email"], "password": datos["password"]})
    assert respuesta.status_code == 400 and b"15 minutos" in respuesta.data


def test_redireccion_de_login_no_abre_dominio_externo(aplicacion):
    _, datos = crear_persona(aplicacion)
    cliente = aplicacion.test_client()
    respuesta = enviar(cliente, "/ingresar?next=https://example.com", {"email": datos["email"], "password": datos["password"]})
    assert respuesta.headers["Location"] == "/panel"


def test_inicializacion_sobre_esquema_anterior_no_borra_datos(tmp_path):
    ruta = tmp_path / "anterior.db"
    conn = db.conectar(str(ruta))
    esquema = db.RUTA_SCHEMA.read_text().split("-- Perfil adicional")[0]
    conn.executescript(esquema)
    usuarios.registrar_usuario(conn, "Usuario anterior", "anterior@ejemplo.co", "ClaveAnterior2026")
    salt = bytes.fromhex("00112233445566778899aabbccddeeff")
    digest = hashlib.pbkdf2_hmac("sha256", b"ClaveAnterior2026", salt, 100000).hex()
    conn.execute("UPDATE usuario SET password_hash = ?", (f"{salt.hex()}${digest}",))
    conn.commit()
    conn.close()
    app = crear_app(dict(TESTING=True, DATA_DIR=str(tmp_path), DATABASE=str(ruta), UPLOAD_FOLDER=str(tmp_path / "fotos")))
    cliente = app.test_client()
    ingresar(cliente, dict(email="anterior@ejemplo.co", password="ClaveAnterior2026"))
    assert cliente.get("/panel").status_code == 200


def test_comando_crea_profesional_sin_registro_publico(aplicacion):
    resultado = aplicacion.test_cli_runner().invoke(args=["crear-profesional", "--nombre", "Profesional de prueba", "--email", "prof@ejemplo.co", "--cedula", "123456789", "--telefono", "3001234567", "--direccion", "Dirección de prueba", "--departamento", "Meta", "--municipio", "Acacías"], input="Profesional2026\nProfesional2026\n")
    assert resultado.exit_code == 0, resultado.output
    cliente = aplicacion.test_client()
    ingresar(cliente, dict(email="prof@ejemplo.co", password="Profesional2026"))
    assert cliente.get("/estadisticas").status_code == 200


def test_clave_automatica_se_conserva_y_app_no_crea_cuentas_de_ejemplo(tmp_path):
    config = dict(TESTING=True, DATA_DIR=str(tmp_path), DATABASE=str(tmp_path / "real.db"), UPLOAD_FOLDER=str(tmp_path / "fotos"))
    primera = crear_app(config)
    segunda = crear_app(config)
    assert primera.secret_key == segunda.secret_key
    conn = db.conectar(config["DATABASE"])
    assert conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] == 0
    conn.close()
