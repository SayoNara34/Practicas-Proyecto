"""US11 - Consulta de diagnóstico propio y presentación segura del resultado."""
import pytest
from app import diagnosticos, usuarios
from app.errores import ErrorNoEncontrado, ErrorPermiso


def test_sin_diagnostico_devuelve_none(conn, reporte, campesino):
    assert diagnosticos.consultar_diagnostico(conn, reporte, campesino) is None


@pytest.mark.parametrize("cerrado", [False, True])
def test_consulta_resultado_y_lo_conserva_al_cerrar(conn, reporte, campesino, agronomo, cerrado):
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "Sigatoka", "Revisar hojas")
    if cerrado:
        diagnosticos.marcar_resuelto(conn, reporte, agronomo)
    resultado = diagnosticos.consultar_diagnostico(conn, reporte, campesino)
    assert resultado["texto"] == "Sigatoka"
    assert resultado["recomendacion"] == "Revisar hojas"
    assert resultado["profesional"] == "Laura Gómez"
    assert resultado["creado_en"]


def test_otro_campesino_no_consulta(conn, reporte, campesino2):
    with pytest.raises(ErrorPermiso):
        diagnosticos.consultar_diagnostico(conn, reporte, campesino2)


def test_profesional_no_usa_consulta_del_campesino(conn, reporte, agronomo):
    with pytest.raises(ErrorPermiso):
        diagnosticos.consultar_diagnostico(conn, reporte, agronomo)


def test_reporte_inexistente(conn, campesino):
    with pytest.raises(ErrorNoEncontrado):
        diagnosticos.consultar_diagnostico(conn, 999, campesino)


def test_usuario_inexistente(conn, reporte):
    with pytest.raises(ErrorNoEncontrado):
        diagnosticos.consultar_diagnostico(conn, reporte, 999)


def test_panel_escapa_resultado_y_muestra_mensaje_de_espera(monkeypatch, conn, reporte, campesino, agronomo):
    import demo_web
    monkeypatch.setattr(demo_web, "CONN", conn)
    usuario = usuarios.obtener_usuario(conn, campesino)
    assert "Aún no hay diagnóstico" in demo_web.vista_campesino(usuario)
    diagnosticos.registrar_diagnostico(conn, reporte, agronomo, "<script>alert(1)</script>", "<b>Hojas</b>")
    vista = demo_web.vista_campesino(usuario)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in vista
    assert "&lt;b&gt;Hojas&lt;/b&gt;" in vista
    assert "<script>" not in vista
