# Savia: instalación y comprobación de la aplicación web

Esta es la aplicación persistente del proyecto Control de Plagas en Plátano. Se ejecuta con `ejecutar.py`. Los archivos `demo.py` y `demo_web.py` se conservan como demostraciones anteriores y no son el punto de entrada de la nueva aplicación.

## Qué debes tener antes de empezar

- Un computador con Windows, Linux o macOS y un navegador actualizado.
- **Python 3.12 recomendado**, con pip. La aplicación utiliza sintaxis de Python 3.10 o superior; la validación de esta entrega se hizo con Python 3.12.
- Internet para instalar las dependencias la primera vez. Después, la aplicación usa sus estilos, fuentes e ilustraciones locales.
- La carpeta completa de esta entrega, descomprimida en una ubicación donde puedas guardar archivos.

**No necesitas Node.js, MySQL, Workbench, Postman, una cuenta en la nube ni una API de pago.** SQLite viene con Python. No es necesario crear manualmente tablas o importar SQL: se preparan automáticamente.

## 1. Obtener la versión correcta

Puedes descomprimir el ZIP entregado o descargar la rama `web-institucional-persistente` del repositorio. Si usas Git:

```bash
git clone --branch web-institucional-persistente https://github.com/SayoNara34/Practicas-Proyecto.git
cd Practicas-Proyecto
```

Si descargaste el ZIP, abre la carpeta que contiene `ejecutar.py`, `gestionar.py`, `requirements-lock.txt`, `app/` y `web/`. Abre una terminal dentro de esa carpeta; no ejecutes los comandos desde `app/` ni desde `web/`.

## 2. Instalar en Windows

En una terminal de VS Code, PowerShell o CMD:

```powershell
py -3 --version
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
```

Si tu instalación usa `python` en lugar de `py`, los dos primeros comandos son:

```powershell
python --version
python -m venv .venv
```

No necesitas activar el entorno virtual: los comandos utilizan directamente su ejecutable. Esto evita el bloqueo de `Activate.ps1` en algunas configuraciones de PowerShell.

`requirements-lock.txt` fija las versiones verificadas. `requirements.txt` conserva los rangos de compatibilidad para el mantenimiento del proyecto. Para comprobar esta entrega, usa el archivo con versiones fijas.

## 3. Crear una cuenta de profesional

El registro público crea agricultores. Un usuario no puede convertirse en profesional cambiando el formulario. Antes de hacer la presentación, ejecuta:

```powershell
.venv\Scripts\python.exe gestionar.py crear-profesional
```

El comando solicita nombres y apellidos, correo, cédula sin puntos, teléfono de 10 dígitos, dirección, departamento y municipio. Después pide una contraseña de 10 a 128 caracteres con letras y números y su confirmación. **La contraseña no se muestra al escribirla.** Elige los datos de la persona que hará la revisión. Para ensayar, usa exclusivamente información ficticia.

Por defecto, el departamento es Meta y el municipio es Villavicencio; puedes escribir otro. La cuenta se guarda en la misma base de datos que usará la web. No se incluyen contraseñas predeterminadas ni cuentas de ejemplo habilitadas automáticamente.

Si la cédula o el correo ya existen, el comando lo informa sin crear una cuenta parcial.

## 4. Iniciar la aplicación

```powershell
.venv\Scripts\python.exe ejecutar.py
```

Abre **http://127.0.0.1:8000** en el navegador. Verás la página de inicio de Savia. Mantén la terminal abierta mientras uses la aplicación. Para detenerla, presiona Ctrl+C.

Después de instalar, también puedes abrir `INICIAR_WINDOWS.bat` con doble clic. Ese archivo inicia la aplicación con el entorno `.venv` de esta carpeta.

Si el puerto 8000 está ocupado:

```powershell
.venv\Scripts\python.exe ejecutar.py --puerto 8080
```

En ese caso abre http://127.0.0.1:8080.

## 5. Recorrido para presentarla

### Agricultor

1. Desde el inicio, selecciona **Crear cuenta**.
2. Completa Identificación, Contacto y Acceso. Cédula: 5 a 12 dígitos sin puntos. Teléfono: 10 dígitos sin +57. La vereda y el nombre de la finca son opcionales.
3. Autoriza el uso de datos para el servicio. El sistema solicita nombre, documento y contacto; no pide una fotografía de la cédula.
4. Ingresa con el correo y la contraseña que acabas de crear.
5. En **Nuevo reporte**, describe la afectación, indica municipio y ubicación del cultivo y adjunta fotografías reales JPG o PNG.
6. Se admiten de 1 a 6 fotografías y máximo 10 MB entre todas. Puedes arrastrarlas, ver sus miniaturas y quitar una antes de enviar. La ubicación del cultivo puede ser distinta a tu dirección de contacto.
7. Al enviar se abre la ficha del caso: estado, información, fotografías e historial. Mientras no exista diagnóstico aparece un aviso de espera.
8. Desde **Mis reportes**, busca y filtra tus casos. Desde **Mi cuenta**, actualiza los datos de contacto o cambia la contraseña.

### Profesional agrónomo

1. Cierra la sesión del agricultor o usa otro perfil del navegador. Dos pestañas de una misma ventana comparten sesión; para usar dos cuentas a la vez, usa una ventana privada o un segundo navegador.
2. Ingresa con la cuenta profesional creada mediante el comando de administración.
3. En **Gestión de casos**, abre el reporte del agricultor. Puedes revisar las fotografías y su información de contacto.
4. Selecciona **Iniciar revisión** o registra directamente un diagnóstico y una recomendación. No es obligatorio pasar antes por En revisión.
5. El agricultor recibe una notificación interna y puede consultar el resultado con tu nombre y la fecha.
6. Cuando la atención termine, selecciona **Marcar como resuelto** y confirma la acción. El diagnóstico no se elimina.
7. En **Estadísticas**, consulta los conteos por estado, filtra por zona y tipo de plaga, y descarga PDF o Excel. Los filtros buscan coincidencias exactas sin distinguir mayúsculas; vacíos incluyen todos los casos.

### Comprobar que sí guarda los datos

1. Crea al menos un usuario y un reporte con fotos.
2. Detén la aplicación con Ctrl+C.
3. Ejecuta nuevamente el mismo comando de inicio desde la misma carpeta.
4. Ingresa con tu usuario: el reporte, las fotografías y el diagnóstico siguen disponibles.

## 6. Dónde se conserva la información

La primera ejecución crea automáticamente una carpeta **`instance/`**:

| Elemento | Función |
|---|---|
| `instance/savia.db` | Usuarios, perfiles, reportes, diagnósticos, notificaciones, historial y sesiones. |
| `instance/evidencias/` | Copias normalizadas de las fotografías de cada reporte. |
| `instance/secret_key` | Clave privada de firma de las cookies y los formularios. |

**No borres `instance/` ni la subas a GitHub.** Está excluida mediante `.gitignore`. La entrega descargable no contiene documentos personales, registros ni claves de usuarios.

Para una copia de respaldo local, detén el servidor y copia toda la carpeta `instance/` a una ubicación privada. Para restaurarla, con el servidor detenido reemplaza la carpeta por tu respaldo. Conserva base de datos, fotografías y clave juntas. Antes de actualizar una instalación que ya tenga datos, crea ese respaldo.

Si mueves el proyecto a otra carpeta y quieres conservar sus registros, mueve también `instance/`. Los datos de las demos en memoria no se importan: desaparecían al cerrarlas y no constituían una base persistente.

## 7. Restablecer una contraseña

El dueño del servidor puede ejecutar:

```powershell
.venv\Scripts\python.exe gestionar.py restablecer-clave
```

Se solicita correo y nueva contraseña, sin mostrarlas en pantalla. El comando revoca las sesiones anteriores de esa cuenta. La aplicación no simula un envío de correo: no hay un proveedor de correo configurado.

## 8. Ejecutar las pruebas

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Esta entrega pasó **98 pruebas**: 69 anteriores y 29 casos web, incluyendo sus parametrizaciones. Usan datos y archivos temporales y no tocan tu base persistente. Se comprueban registro, unicidad, contraseñas, CSRF, sesiones, roles, fotos reales, acceso a reportes ajenos, límites de carga, notificaciones, diagnóstico, cierre, PDF/XLSX y conservación al reiniciar la aplicación.

Además se comprobó la sintaxis JavaScript y se ejercitaron las interacciones principales en un DOM aislado. **No se realizó una inspección visual en un navegador real en el entorno de entrega.** Antes de la reunión conviene recorrer las pantallas en tu navegador y probar el tamaño de pantalla que usarás.

## 9. Linux o macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python gestionar.py crear-profesional
.venv/bin/python ejecutar.py
```

## 10. Variables opcionales y acceso desde otro dispositivo

La instalación local funciona sin definir variables. Solo para una configuración distinta:

| Variable | Uso |
|---|---|
| `SAVIA_DATA_DIR` | Ruta absoluta alternativa para guardar la base, fotografías y clave. Define siempre la misma ruta al crear profesionales y al iniciar el servidor. |
| `SAVIA_SECRET_KEY` | Clave externa de al menos 32 caracteres. Si no se define, se genera y conserva una clave privada en disco. |
| `SAVIA_HTTPS=1` | Marca las cookies como Secure; úsala únicamente cuando el acceso real se haga mediante HTTPS. En HTTP local se debe dejar sin definir. |

Para probar desde un teléfono en la misma red privada:

```powershell
.venv\Scripts\python.exe ejecutar.py --host 0.0.0.0
```

Desde el teléfono abre `http://IP-LOCAL-DEL-COMPUTADOR:8000`. El computador debe estar encendido y el firewall debe permitir ese acceso en tu red privada. `0.0.0.0` es la dirección de escucha, no la dirección que escribes en el teléfono. No abras puertos del router para esta prueba. La obtención de ubicación puede no estar disponible en HTTP desde otro dispositivo; puedes escribir la referencia rural.

## 11. Problemas frecuentes

| Situación | Solución |
|---|---|
| `py` o `python` no se reconoce | Instala Python y habilita su acceso desde la terminal. Reinicia la terminal después de instalar. |
| `No module named flask` | Instala las dependencias con el Python de `.venv`, no con otro intérprete. |
| La pantalla se ve sin estilos | Ejecuta desde la carpeta completa. Debe existir `web/static/` con CSS, JS, fuentes y SVG. |
| `Address already in use` / puerto ocupado | Detén el otro servidor o usa `--puerto 8080`. |
| El formulario venció | Actualiza la página y completa el formulario de nuevo. Las sesiones y tokens tienen duración limitada. |
| Demasiados intentos de acceso | Espera 15 minutos y vuelve a ingresar con la contraseña correcta. |
| Las fotografías son rechazadas | Usa JPG/PNG reales. Renombrar otro archivo a `.jpg` no lo convierte en imagen. Máximo 6 y 10 MB en total. |
| No puedo crear una cuenta profesional desde la página | Es intencional. Se crea mediante `gestionar.py crear-profesional`. |
| Parece que los registros se perdieron | Comprueba que arrancaste `ejecutar.py` desde la misma instalación y con el mismo directorio de datos; las demos anteriores usan memoria. |

## 12. Alcance de la entrega

Es una versión funcional para presentar y comprobar localmente: persiste la información y separa las interfaces y los permisos. Utiliza Waitress, sin depuración, sesiones revocables, CSRF y validación real de imágenes. No pretende ser una entidad oficial del Gobierno ni diagnosticar automáticamente.

Para habilitar un servicio público con datos reales se debe configurar un alojamiento Python con disco persistente, HTTPS, respaldos y los datos/canal del responsable de privacidad. No se han configurado dominio, correo transaccional, verificación documental ni publicación en Internet. El diagnóstico lo registra un profesional; la creación de su cuenta no acredita una validación de credenciales profesionales.
