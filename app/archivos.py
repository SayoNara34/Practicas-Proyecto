"""US2 web: valida fotografías reales y conserva evidencia en disco privado."""
import io
import warnings
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from .errores import ErrorValidacion

MAX_ARCHIVOS = 6
MAX_TOTAL = 10 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000


def guardar_fotos(archivos: list, carpeta: Path) -> list[str]:
    """Valida todas las imágenes antes de guardar sus copias normalizadas.

    Raises:
        ErrorValidacion: Tipo, peso, dimensiones o cantidad no permitidos.
    """
    seleccionados = [archivo for archivo in archivos if archivo.filename]
    if not 1 <= len(seleccionados) <= MAX_ARCHIVOS:
        raise ErrorValidacion("Adjunta entre 1 y 6 fotografías de la afectación.")
    preparados = []
    total = 0
    for archivo in seleccionados:
        contenido = archivo.stream.read(MAX_TOTAL + 1)
        total += len(contenido)
        if total > MAX_TOTAL:
            raise ErrorValidacion("Las fotografías deben pesar máximo 10 MB en total.")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(contenido)) as original:
                    if original.format not in ("JPEG", "PNG"):
                        raise ErrorValidacion("Solo se aceptan imágenes JPG, JPEG o PNG reales.")
                    original.verify()
                with Image.open(io.BytesIO(contenido)) as original:
                    imagen = ImageOps.exif_transpose(original).convert("RGB")
                    imagen.thumbnail((2560, 2560))
                    salida = io.BytesIO()
                    # Re-encode evita conservar scripts incrustados y metadatos GPS.
                    imagen.save(salida, format="JPEG", quality=88, optimize=True)
                    preparados.append((uuid4().hex + ".jpg", salida.getvalue()))
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError,
                Image.DecompressionBombWarning) as error:
            raise ErrorValidacion("Una fotografía no es válida o sus dimensiones son demasiado grandes.") from error
    guardados = []
    try:
        for nombre, contenido in preparados:
            ruta = carpeta / nombre
            ruta.write_bytes(contenido)
            guardados.append(nombre)
    except OSError:
        eliminar_fotos(guardados, carpeta)
        raise
    return guardados


def eliminar_fotos(nombres: list[str], carpeta: Path) -> None:
    """Elimina exclusivamente los nombres internos de un intento fallido."""
    for nombre in nombres:
        (carpeta / nombre).unlink(missing_ok=True)
