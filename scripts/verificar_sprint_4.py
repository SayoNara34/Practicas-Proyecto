"""US10 - Verifica el flujo de descarga contra un servidor HTTP real de la demo."""
import socket
import subprocess
import sys
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from openpyxl import load_workbook
from pypdf import PdfReader


def main() -> None:
    """Inicia una demo aislada, verifica archivos y permisos y cierra el proceso."""
    with socket.socket() as reserva:
        reserva.bind(("127.0.0.1", 0))
        puerto = reserva.getsockname()[1]
    raiz = Path(__file__).resolve().parents[1]
    proceso = subprocess.Popen([sys.executable, "demo_web.py", str(puerto)], cwd=raiz,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{puerto}"
    try:
        for _ in range(100):
            try:
                with urlopen(base, timeout=1):
                    break
            except URLError:
                if proceso.poll() is not None:
                    raise RuntimeError("La demo no pudo iniciarse.")
                time.sleep(.05)
        else:
            raise RuntimeError("La demo no respondió a tiempo.")
        filtro = "u=2&zona=Acac%C3%ADas&tipo_plaga=Picudo+negro"
        with urlopen(base + "/panel?" + filtro) as respuesta:
            panel = respuesta.read()
        assert b"Reportado: 1" in panel
        for formato in ("pdf", "xlsx"):
            with urlopen(base + "/exportar?" + filtro + "&formato=" + formato) as respuesta:
                assert "attachment" in respuesta.headers["Content-Disposition"]
                datos = respuesta.read()
                assert len(datos) == int(respuesta.headers["Content-Length"])
            if formato == "pdf":
                texto = " ".join(p.extract_text() for p in PdfReader(BytesIO(datos)).pages)
                assert "Total\n1" in texto and "Acacías" in texto
            else:
                hoja = load_workbook(BytesIO(datos)).active
                assert hoja["B11"].value == 1 and hoja["B3"].value == "Acacías"
        with urlopen(base + "/panel?" + filtro) as respuesta:
            assert respuesta.read() == panel
        try:
            urlopen(base + "/exportar?u=1&formato=pdf")
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("El campesino pudo exportar.")
        print("US10: panel filtrado, PDF y XLSX válidos (total 1), sin cambios y permisos verificados.")
    finally:
        proceso.terminate()
        proceso.wait(timeout=5)


if __name__ == "__main__":
    main()
